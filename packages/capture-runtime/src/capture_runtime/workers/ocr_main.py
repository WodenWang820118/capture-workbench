"""Separately packaged WindowsML OCR worker."""

# Imports are deliberately staged below so the packaged worker can report the
# exact failing import boundary before loading heavyweight model dependencies.
# ruff: noqa: E402, I001

from __future__ import annotations

import sys
import importlib
import re
import warnings
from io import BytesIO
from pathlib import Path
from threading import Event
from collections.abc import Iterable, Iterator
from typing import Any

STAGE_PREFIX = "capture-worker-stage:"


def _report_stage(stage: str) -> None:
    sys.stderr.write(f"{STAGE_PREFIX}{stage}\n")
    sys.stderr.flush()


_report_stage("worker-entry-start")

_report_stage("python-import-pdfium-start")
import pypdfium2 as pdfium  # type: ignore[import-untyped]

_report_stage("python-import-pdfium-complete")

_report_stage("python-import-pillow-start")
from PIL import Image, ImageOps, UnidentifiedImageError

_report_stage("python-import-pillow-complete")

_report_stage("python-import-capture-runtime-start")
from capture_runtime.engine_adapters import (
    WindowsMLOcrAdapter,
    _install_offline_aistudio_stubs,
    _install_offline_huggingface_stubs,
)
from capture_runtime.image_normalization import bounded_scaled_dimensions
from capture_runtime.worker_contracts import WorkerRequest
from capture_runtime.workers.server import serve

_report_stage("python-import-capture-runtime-complete")

MAX_SOURCE_BYTES = 50 * 1024 * 1024


def _import_ocr_runtime() -> None:
    _install_offline_aistudio_stubs()
    _install_offline_huggingface_stubs()
    for module, stage in (
        ("onnxruntime", "python-import-onnxruntime"),
        ("paddleocr", "python-import-paddleocr"),
    ):
        _report_stage(f"{stage}-start")
        try:
            importlib.import_module(module)
        except Exception as error:
            detail = type(error).__name__.lower()
            missing_name = getattr(error, "name", None)
            if isinstance(missing_name, str) and re.fullmatch(r"[A-Za-z0-9_.]+", missing_name):
                detail += "-missing-" + re.sub(r"[._]+", "-", missing_name.lower())
            traceback_cursor = error.__traceback__
            failure_module = None
            while traceback_cursor is not None:
                candidate = traceback_cursor.tb_frame.f_globals.get("__name__")
                if isinstance(candidate, str) and re.fullmatch(r"[A-Za-z0-9_.]+", candidate):
                    failure_module = candidate
                traceback_cursor = traceback_cursor.tb_next
            if failure_module is not None:
                detail += "-in-" + re.sub(r"[._]+", "-", failure_module.lower())
            _report_stage(f"{stage}-failed-{detail}")
            raise
        _report_stage(f"{stage}-complete")


def _payload(request: WorkerRequest, expected: set[str]) -> dict[str, Any]:
    if set(request.payload) != expected:
        raise ValueError("OCR worker payload fields are invalid")
    return request.payload


def _model_path(value: object, *, required: bool) -> Path | None:
    if value is None and not required:
        return None
    if not isinstance(value, str):
        raise ValueError("OCR modelPath is invalid")
    path = Path(value)
    if not path.is_absolute() or not path.is_dir():
        raise ValueError("OCR modelPath must be an existing absolute directory")
    return path


def _probe(request: WorkerRequest) -> dict[str, Any]:
    base_fields = {"requirementId", "artifactVersion", "modelPath"}
    payload_fields = frozenset(request.payload)
    if payload_fields not in {frozenset(base_fields), frozenset(base_fields | {"options"})}:
        raise ValueError("OCR worker payload fields are invalid")
    payload = request.payload
    if payload["requirementId"] != "windowsml-ocr":
        raise ValueError("OCR requirementId is invalid")
    options = payload.get("options", {})
    if not isinstance(options, dict) or set(options) - {"deviceId"}:
        raise ValueError("OCR probe options are invalid")
    device_id = options.get("deviceId", 0)
    if not isinstance(device_id, int) or isinstance(device_id, bool) or device_id < 0:
        raise ValueError("OCR probe deviceId is invalid")
    model_path = _model_path(payload["modelPath"], required=False)
    if model_path is None:
        import importlib.util

        missing = [
            item
            for item in ("onnxruntime", "paddleocr", "pypdfium2", "PIL")
            if importlib.util.find_spec(item) is None
        ]
        return {
            "ready": not missing,
            "codeReady": not missing,
            "assetsReady": False,
            "detail": (
                "OCR worker code is ready."
                if not missing
                else "OCR worker dependencies are unavailable."
            ),
            "device": None,
        }
    adapter = WindowsMLOcrAdapter(model_path, device_id=device_id)
    probe = adapter.probe()
    device = None
    if probe.ready:
        providers = adapter._providers()
        device = "windowsml-dml" if "DmlExecutionProvider" in providers else "cpu"
    return {
        "ready": probe.ready,
        "codeReady": probe.code_ready,
        "assetsReady": probe.assets_ready,
        "detail": probe.detail,
        "device": device,
    }


def _normalized_png(source: Path, max_pixels: int, scale: float = 1) -> bytes:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(source) as image:
                if (image.format or "").upper() not in {"PNG", "JPEG", "WEBP"}:
                    raise ValueError("unsupported image format")
                width, height = image.size
                if width <= 0 or height <= 0 or width * height > max_pixels:
                    raise ValueError("image dimensions exceed limit")
                if getattr(image, "n_frames", 1) != 1 or bool(getattr(image, "is_animated", False)):
                    raise ValueError("animated images are unsupported")
                image.seek(0)
                image.load()
                oriented = ImageOps.exif_transpose(image)
                if "A" in oriented.getbands() or "transparency" in oriented.info:
                    rgba = oriented.convert("RGBA")
                    normalized = Image.new("RGB", rgba.size, "white")
                    normalized.paste(rgba, mask=rgba.getchannel("A"))
                else:
                    normalized = oriented.convert("RGB")
                if scale != 1:
                    normalized_width, normalized_height = normalized.size
                    scaled_width, scaled_height = bounded_scaled_dimensions(
                        normalized_width,
                        normalized_height,
                        scale,
                        max_pixels,
                    )
                    normalized = normalized.resize(
                        (scaled_width, scaled_height),
                        Image.Resampling.LANCZOS,
                    )
                output = BytesIO()
                normalized.save(output, format="PNG")
                return output.getvalue()
    except (
        OSError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as error:
        raise ValueError("uploaded image is not readable") from error


def _pdf_page_images(
    source: Path,
    max_pages: int,
    scale: float,
    cancellation: Event,
) -> Iterator[tuple[int, bytes]]:
    document = None
    try:
        document = pdfium.PdfDocument(str(source))
        page_count = len(document)
        if page_count < 1:
            raise ValueError("uploaded PDF has no pages")
        if page_count > max_pages:
            raise ValueError(f"PDF has {page_count} pages; limit is {max_pages}")
        for page_number in range(1, page_count + 1):
            if cancellation.is_set():
                raise InterruptedError
            _report_stage("ocr-pdf-render-start")
            bitmap = None
            try:
                bitmap = document[page_number - 1].render(scale=scale)
                image = bitmap.to_pil().convert("RGB")
                output = BytesIO()
                image.save(output, format="PNG")
            except Exception as error:
                raise ValueError(f"could not render PDF page {page_number}") from error
            finally:
                if bitmap is not None:
                    bitmap.close()
            _report_stage("ocr-pdf-render-complete")
            yield page_number, output.getvalue()
    except (ValueError, InterruptedError):
        raise
    except Exception as error:
        raise ValueError("uploaded PDF is not readable") from error
    finally:
        if document is not None:
            document.close()


def _run(request: WorkerRequest, cancellation: Event) -> dict[str, Any]:
    payload = _payload(
        request,
        {
            "requirementId",
            "artifactVersion",
            "modelPath",
            "sourcePath",
            "mediaType",
            "options",
        },
    )
    if payload["requirementId"] != "windowsml-ocr":
        raise ValueError("OCR requirementId is invalid")
    model_path = _model_path(payload["modelPath"], required=True)
    assert model_path is not None
    source_value = payload["sourcePath"]
    if not isinstance(source_value, str):
        raise ValueError("OCR sourcePath is invalid")
    source = Path(source_value)
    if not source.is_absolute() or not source.is_file() or source.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("OCR sourcePath is invalid")
    media_type = payload["mediaType"]
    options = payload["options"]
    if not isinstance(media_type, str) or not isinstance(options, dict):
        raise ValueError("OCR run mediaType/options are invalid")
    adapter = WindowsMLOcrAdapter(
        model_path,
        device_id=int(options.get("deviceId", 0)),
        stage_reporter=_report_stage,
    )
    images: Iterable[tuple[int, bytes]]
    if media_type == "application/pdf":
        max_pages = options.get("maxPages")
        render_scale = options.get("renderScale")
        if (
            set(options) != {"deviceId", "maxPages", "renderScale"}
            or not isinstance(max_pages, int)
            or isinstance(max_pages, bool)
            or not 1 <= max_pages <= 500
            or not isinstance(render_scale, int | float)
            or isinstance(render_scale, bool)
            or not 0.5 <= float(render_scale) <= 8
        ):
            raise ValueError("OCR PDF options are invalid")
        images = _pdf_page_images(source, max_pages, float(render_scale), cancellation)
    elif media_type in {"image/png", "image/jpeg", "image/webp"}:
        max_pixels = options.get("maxImagePixels")
        scale = options.get("renderScale", 1)
        if not isinstance(max_pixels, int) or isinstance(max_pixels, bool) or max_pixels < 1:
            raise ValueError("OCR image pixel limit is invalid")
        if (
            not isinstance(scale, int | float)
            or isinstance(scale, bool)
            or not 1 <= float(scale) <= 4
        ):
            raise ValueError("OCR image renderScale is invalid")
        images = [(1, _normalized_png(source, max_pixels, float(scale)))]
    else:
        raise ValueError("OCR mediaType is unsupported")
    segments: list[dict[str, Any]] = []
    results = []
    warning_values: list[str] = []
    for page, image in images:
        if cancellation.is_set():
            raise InterruptedError
        result = adapter.extract_png(image)
        results.append(result)
        if result.text.strip():
            segments.append(
                {
                    "order": len(segments),
                    "text": result.text.strip(),
                    "page": page,
                    "startMs": None,
                    "endMs": None,
                }
            )
        if result.warning:
            warning_values.append(result.warning)
    if not results:
        raise ValueError("OCR produced no results")
    if not segments:
        _report_stage("ocr-output-empty")
        raise ValueError("OCR produced no non-empty segments")
    provenance = results[0]
    return {
        "segments": segments,
        "provenance": {
            "engine": "windowsml-ocr",
            "model": provenance.model,
            "digest": provenance.digest,
            "device": provenance.device,
        },
        "warnings": list(dict.fromkeys(warning_values)),
    }


def handle(request: WorkerRequest, cancellation: Event) -> dict[str, Any]:
    if request.operation == "probe":
        return _probe(request)
    if request.operation == "run":
        return _run(request, cancellation)
    raise ValueError("unsupported OCR operation")


def prepare(request: WorkerRequest) -> None:
    if request.operation == "run":
        _import_ocr_runtime()


if __name__ == "__main__":
    serve(handle, prepare=prepare)
