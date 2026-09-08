from __future__ import annotations

import hashlib
from collections.abc import Iterator
from io import BytesIO
from pathlib import Path
from threading import Event

import pytest
from PIL import Image

import capture_runtime.workers.ocr_main as ocr_main
from capture_runtime.contracts import (
    OcrAdapterClass,
    OcrComputeMode,
    OcrComputePreflightV2,
    OcrProvenanceV3,
)
from capture_runtime.engine_adapters import OcrTextResult
from capture_runtime.ocr_preflight import (
    OcrComputePlan,
    OcrGpuAdapter,
    OcrGpuCapabilitySnapshot,
)
from capture_runtime.worker_client import (
    WorkerResultError,
    parse_ocr_compute_preflight,
    parse_ocr_progress,
    parse_run_result,
)
from capture_runtime.worker_contracts import WorkerRequest


def _request(operation: str) -> WorkerRequest:
    return WorkerRequest(
        request_id="ocr-prepare-test",
        operation=operation,  # type: ignore[arg-type]
        payload={},
    )


class _StaticProbe:
    def __init__(self, snapshot: OcrGpuCapabilitySnapshot) -> None:
        self.snapshot = snapshot

    def probe(self) -> OcrGpuCapabilitySnapshot:
        return self.snapshot


def _gpu_plan_dict() -> dict[str, object]:
    adapter = OcrGpuAdapter(
        index=0,
        adapter_class=OcrAdapterClass.DEDICATED,
        is_software=False,
        luid="00000000000000aa",
        high_performance_rank=0,
        vendor_id=0x10DE,
        pci_device_id=0x2204,
        subsystem_id=1,
        revision=1,
        description="test-gpu",
        assessment="positive-usable",
    )
    selection = OcrComputePlan(
        contract_sha256="a" * 64,
        worker_sha256="b" * 64,
        capability_probe=_StaticProbe(
            OcrGpuCapabilitySnapshot(
                adapters=(adapter,),
                high_performance_adapters=(adapter,),
                ordinary_adapters=(adapter,),
                dml_provider_available=True,
                ort_version="1.24.4",
            )
        ),
    ).select()
    assert selection is not None
    return selection.execution_plan.to_dict()


def _resolved_test_provenance() -> OcrProvenanceV3:
    return OcrProvenanceV3(
        status="resolved",
        engine="windowsml-ocr",
        model="test-model",
        model_digest="sha256:" + "1" * 64,
        device="windowsml-dml",
        profile_id="capture-workbench-ocr-pipeline-v1",
        profile_spec_sha256="c" * 64,
    )


def _worker_page_result(
    page: dict[str, object], *, include_segment: bool = True
) -> dict[str, object]:
    return {
        "segments": [
            {
                "order": 0,
                "text": page["text"],
                "page": page["page"],
                "startMs": None,
                "endMs": None,
            }
        ]
        if include_segment
        else [],
        "provenance": _resolved_test_provenance().model_dump(mode="json", by_alias=True),
        "warnings": [],
        "pages": [page],
    }


def _worker_box(index: int, confidence: object = 0.93) -> dict[str, object]:
    left = 1 + index * 4
    return {
        "polygon": [
            {"x": left, "y": 2},
            {"x": left + 20, "y": 2},
            {"x": left + 20, "y": 20},
            {"x": left, "y": 20},
        ],
        "text": f"region-{index}",
        "confidence": confidence,
    }


def _recognized_worker_page(
    *,
    boxes: list[object],
    region_confidences: list[object],
    confidence: object = None,
) -> dict[str, object]:
    return {
        "page": 1,
        "status": "recognized",
        "text": "recognized page",
        "boxes": boxes,
        "regionConfidences": region_confidences,
        "confidence": confidence,
        "raster": {
            "width": 120,
            "height": 80,
            "scale": 1,
            "coordinateSystem": "pixel",
        },
        "failure": None,
    }


def test_worker_page_parser_rejects_confidence_cardinality_without_prefix() -> None:
    page = _recognized_worker_page(
        boxes=[_worker_box(index) for index in range(10)],
        region_confidences=[0.93] * 9,
    )

    with pytest.raises(WorkerResultError, match="cardinality"):
        parse_run_result(_worker_page_result(page))


@pytest.mark.parametrize(
    ("boxes", "region_confidences", "message"),
    [
        ([_worker_box(0), _worker_box(1)], [0.93], "cardinality"),
        ([_worker_box(0)], [0.93, 0.92], "cardinality"),
        ([_worker_box(0, None)], [0.93], "does not match"),
        ([_worker_box(0, 0.92)], [0.93], "does not match"),
        ([_worker_box(0, 0.93)], [], "requires a matching"),
    ],
)
def test_worker_page_parser_enforces_box_score_index_mapping(
    boxes: list[object],
    region_confidences: list[object],
    message: str,
) -> None:
    page = _recognized_worker_page(
        boxes=boxes,
        region_confidences=region_confidences,
    )

    with pytest.raises(WorkerResultError, match=message):
        parse_run_result(_worker_page_result(page))


@pytest.mark.parametrize(
    "bad_score",
    [None, True, float("nan"), float("inf"), 10**1000, -0.1, 1.1, "0.93"],
)
def test_worker_page_parser_rejects_invalid_region_score(bad_score: object) -> None:
    page = _recognized_worker_page(
        boxes=[_worker_box(0, bad_score)],
        region_confidences=[bad_score],
    )

    with pytest.raises(WorkerResultError, match="confidence"):
        parse_run_result(_worker_page_result(page))


@pytest.mark.parametrize("page_confidence", [None, 0.0])
def test_worker_page_parser_accepts_explicit_no_score_page(page_confidence: float | None) -> None:
    page = _recognized_worker_page(
        boxes=[_worker_box(0, None)],
        region_confidences=[],
        confidence=page_confidence,
    )

    result = parse_run_result(_worker_page_result(page))

    assert result.pages[0].status == "recognized"
    assert result.pages[0].confidence == page_confidence
    assert result.pages[0].region_confidences == ()
    assert result.pages[0].boxes[0].confidence is None


def test_worker_page_parser_rejects_empty_page_with_recognized_payload() -> None:
    page = _recognized_worker_page(
        boxes=[_worker_box(0, 0.93)],
        region_confidences=[0.93],
    )
    page.update({"status": "empty", "text": "", "confidence": None})

    with pytest.raises(WorkerResultError, match="empty worker OCR pages"):
        parse_run_result(_worker_page_result(page, include_segment=False))


def test_worker_page_parser_rejects_failed_page_with_recognized_scores() -> None:
    page = _recognized_worker_page(
        boxes=[_worker_box(0, 0.93)],
        region_confidences=[0.93],
    )
    page.update(
        {
            "status": "failed",
            "text": "",
            "confidence": None,
            "failure": {
                "code": "ocr_page_failed",
                "message": "OCR page processing failed.",
                "stage": "extraction",
                "retryable": True,
            },
        }
    )

    with pytest.raises(WorkerResultError, match="failed worker OCR pages"):
        parse_run_result(_worker_page_result(page, include_segment=False))


def test_ocr_progress_rejects_unavailable_header_before_recognized_page() -> None:
    header = {
        "type": "ocr-header",
        "pageCount": 1,
        "provenance": {
            "status": "unavailable",
            "profileId": "capture-workbench-ocr-pipeline-v1",
            "profileSpecSha256": "c" * 64,
            "reason": "protocol_failure",
        },
        "pages": [
            {
                "page": 1,
                "raster": {
                    "width": 120,
                    "height": 80,
                    "scale": 1,
                    "coordinateSystem": "pixel",
                },
            }
        ],
    }
    page = {
        "type": "ocr-page",
        "page": _recognized_worker_page(boxes=[], region_confidences=[]),
    }

    with pytest.raises(WorkerResultError, match="resolved provenance"):
        parse_ocr_progress([header, page])


@pytest.mark.parametrize("missing_field", ["modelDigest", "device", "profileSpecSha256"])
def test_ocr_progress_rejects_resolved_header_missing_identity(missing_field: str) -> None:
    provenance = _resolved_test_provenance().model_dump(mode="json", by_alias=True)
    del provenance[missing_field]
    header = {
        "type": "ocr-header",
        "pageCount": 1,
        "provenance": provenance,
        "pages": [
            {
                "page": 1,
                "raster": {
                    "width": 120,
                    "height": 80,
                    "scale": 1,
                    "coordinateSystem": "pixel",
                },
            }
        ],
    }

    with pytest.raises(WorkerResultError, match="unexpected fields"):
        parse_ocr_progress([header])


def test_ocr_progress_keeps_typed_failed_page_after_resolved_header() -> None:
    header = {
        "type": "ocr-header",
        "pageCount": 1,
        "provenance": _resolved_test_provenance().model_dump(mode="json", by_alias=True),
        "pages": [
            {
                "page": 1,
                "raster": {
                    "width": 120,
                    "height": 80,
                    "scale": 1,
                    "coordinateSystem": "pixel",
                },
            }
        ],
    }
    failed_page = _recognized_worker_page(boxes=[], region_confidences=[])
    failed_page.update(
        {
            "status": "failed",
            "text": "",
            "failure": {
                "code": "ocr_page_failed",
                "message": "OCR page processing failed.",
                "stage": "extraction",
                "retryable": True,
            },
        }
    )

    progress = parse_ocr_progress([header, {"type": "ocr-page", "page": failed_page}])

    assert progress is not None
    assert progress.provenance is not None and progress.provenance.is_resolved
    assert progress.pages[0].status == "failed"
    assert progress.pages[0].failure is not None
    assert progress.pages[0].failure.code == "ocr_page_failed"


def test_worker_result_parser_preserves_canonical_polygon_wire_shape() -> None:
    polygon = [
        {"x": 11.25, "y": 20.5},
        {"x": 91.75, "y": 18.0},
        {"x": 104.0, "y": 61.25},
        {"x": 4.5, "y": 64.0},
    ]
    result = parse_run_result(
        {
            "segments": [
                {"order": 0, "text": "perspective", "page": 1, "startMs": None, "endMs": None}
            ],
            "provenance": _resolved_test_provenance().model_dump(mode="json", by_alias=True),
            "warnings": [],
            "pages": [
                {
                    "page": 1,
                    "status": "recognized",
                    "text": "perspective",
                    "boxes": [{"polygon": polygon, "text": "perspective", "confidence": 0.93}],
                    "regionConfidences": [0.93],
                    "confidence": 0.93,
                    "raster": {
                        "width": 120,
                        "height": 80,
                        "scale": 1,
                        "coordinateSystem": "pixel",
                    },
                    "failure": None,
                }
            ],
        }
    )

    assert result.pages[0].boxes[0].polygon == tuple((point["x"], point["y"]) for point in polygon)


def test_ocr_run_prepares_native_runtime_before_cancellation_listener(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(ocr_main, "_import_ocr_runtime", lambda: calls.append("prepared"))

    ocr_main.prepare(_request("run"))
    ocr_main.prepare(_request("probe"))

    assert calls == ["prepared"]


def test_ocr_compute_preflight_uses_worker_capability_probe_without_model_initialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class StaticProbe:
        def probe(self) -> OcrGpuCapabilitySnapshot:
            return OcrGpuCapabilitySnapshot(
                adapters=(OcrGpuAdapter(0, OcrAdapterClass.DEDICATED),),
                dml_provider_available=True,
            )

    monkeypatch.setattr(ocr_main, "NativeOcrGpuCapabilityProbe", StaticProbe)

    class FailingAdapter:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("compute preflight must not initialize the OCR adapter")

    monkeypatch.setattr(ocr_main, "WindowsMLOcrAdapter", FailingAdapter)
    result = ocr_main.handle(
        WorkerRequest(
            request_id="ocr-compute-preflight-test",
            operation="preflight",
            payload={
                "requirementId": "windowsml-ocr",
                "artifactVersion": "0.4.2",
                "modelPath": None,
                "contractSha256": "a" * 64,
                "options": {},
            },
        ),
        Event(),
    )

    expected_worker_sha256 = hashlib.sha256(Path(ocr_main.__file__).read_bytes()).hexdigest()
    expected_readiness = OcrComputePreflightV2(
        contract_sha256="a" * 64,
        worker_sha256=expected_worker_sha256,
        mode=OcrComputeMode.GPU_DML,
        adapter_class=OcrAdapterClass.DEDICATED,
        user_notice_required=False,
    ).model_dump(mode="json", by_alias=True)
    assert result["readiness"] == expected_readiness
    assert result["executionPlan"]["mode"] == "gpu-dml"
    assert result["selectionProof"]["dmlDeviceId"] == 0
    assert (
        parse_ocr_compute_preflight(result).model_dump(mode="json", by_alias=True)
        == expected_readiness
    )


@pytest.mark.parametrize(
    ("snapshot", "reason_code", "adapter_class"),
    [
        (
            OcrGpuCapabilitySnapshot(),
            "no_compatible_gpu",
            OcrAdapterClass.UNKNOWN,
        ),
        (
            OcrGpuCapabilitySnapshot(
                adapters=(OcrGpuAdapter(0, OcrAdapterClass.INTEGRATED),),
                dml_provider_available=False,
            ),
            "dml_provider_unavailable",
            OcrAdapterClass.INTEGRATED,
        ),
    ],
)
def test_ocr_compute_preflight_worker_reports_typed_cpu_reason(
    monkeypatch: pytest.MonkeyPatch,
    snapshot: OcrGpuCapabilitySnapshot,
    reason_code: str,
    adapter_class: OcrAdapterClass,
) -> None:
    class StaticProbe:
        def probe(self) -> OcrGpuCapabilitySnapshot:
            return snapshot

    monkeypatch.setattr(ocr_main, "NativeOcrGpuCapabilityProbe", StaticProbe)
    result = ocr_main.handle(
        WorkerRequest(
            request_id="ocr-compute-cpu-test",
            operation="preflight",
            payload={
                "requirementId": "windowsml-ocr",
                "artifactVersion": "0.4.2",
                "modelPath": None,
                "contractSha256": "a" * 64,
                "options": {},
            },
        ),
        Event(),
    )

    assert result["readiness"]["mode"] == "cpu-fallback"
    assert result["readiness"]["reasonCode"] == reason_code
    assert result["readiness"]["adapterClass"] == adapter_class
    assert result["readiness"]["userNoticeRequired"] is True


def test_ocr_compute_preflight_parser_rejects_malformed_worker_result() -> None:
    with pytest.raises(WorkerResultError, match="OCR compute preflight"):
        parse_ocr_compute_preflight(
            {
                "contractSha256": "a" * 64,
                "mode": "cpu-fallback",
                "adapterClass": "unknown",
                "userNoticeRequired": False,
            }
        )


def test_ocr_compute_preflight_rejects_a_catalog_worker_digest_mismatch() -> None:
    with pytest.raises(ValueError, match="worker executable identity mismatch"):
        ocr_main.handle(
            WorkerRequest(
                request_id="ocr-compute-worker-identity-test",
                operation="preflight",
                payload={
                    "requirementId": "windowsml-ocr",
                    "artifactVersion": "0.4.2",
                    "modelPath": None,
                    "contractSha256": "a" * 64,
                    "options": {},
                    "expectedWorkerSha256": "0" * 64,
                },
            ),
            Event(),
        )


def test_ocr_compute_preflight_rejects_retired_device_id_only_request() -> None:
    with pytest.raises(ValueError, match="options are invalid"):
        ocr_main.handle(
            WorkerRequest(
                request_id="ocr-retired-device-id-test",
                operation="preflight",
                payload={
                    "requirementId": "windowsml-ocr",
                    "artifactVersion": "0.4.2",
                    "modelPath": None,
                    "contractSha256": "a" * 64,
                    "options": {"deviceId": 0},
                },
            ),
            Event(),
        )


def test_ocr_worker_does_not_emit_header_or_pages_before_dml_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    source = tmp_path / "public-fixture.pdf"
    source.write_bytes(b"public test fixture")
    progress: list[dict[str, object]] = []

    monkeypatch.setattr(
        ocr_main,
        "_pdf_page_images",
        lambda *_args: iter([(1, b"page")]),
    )

    class FailingAdapter:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def extract_png(self, _image: bytes) -> OcrTextResult:
            raise RuntimeError("DML inference failed")

    monkeypatch.setattr(ocr_main, "WindowsMLOcrAdapter", FailingAdapter)

    with pytest.raises(RuntimeError, match="DML inference failed"):
        ocr_main.handle(
            WorkerRequest(
                request_id="ocr-evidence-order-test",
                operation="run",
                payload={
                    "requirementId": "windowsml-ocr",
                    "artifactVersion": "0.4.2",
                    "modelPath": str(model_path),
                    "sourcePath": str(source),
                    "mediaType": "application/pdf",
                    "options": {
                        "computePlan": _gpu_plan_dict(),
                        "maxPages": 1,
                        "renderScale": 2,
                        "pageManifest": [
                            {
                                "page": 1,
                                "raster": {
                                    "width": 1,
                                    "height": 1,
                                    "scale": 2,
                                    "coordinateSystem": "pixel",
                                },
                            }
                        ],
                    },
                },
            ),
            Event(),
            progress,
        )

    assert progress == []


def test_ocr_worker_rejects_unproven_dml_result_before_emitting_header(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    source = tmp_path / "public-fixture.png"
    Image.new("RGB", (1, 1), "white").save(source, format="PNG")
    progress: list[dict[str, object]] = []

    class UnprovenAdapter:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def extract_png(self, _image: bytes) -> OcrTextResult:
            return OcrTextResult(
                text="must not be projected",
                model="test-model",
                digest="sha256:" + "1" * 64,
                device="windowsml-dml",
                warning=None,
                raster_width=1,
                raster_height=1,
            )

    monkeypatch.setattr(ocr_main, "WindowsMLOcrAdapter", UnprovenAdapter)

    with pytest.raises(ValueError, match="missing resolved provenance"):
        ocr_main.handle(
            WorkerRequest(
                request_id="ocr-unproven-result-test",
                operation="run",
                payload={
                    "requirementId": "windowsml-ocr",
                    "artifactVersion": "0.4.2",
                    "modelPath": str(model_path),
                    "sourcePath": str(source),
                    "mediaType": "image/png",
                    "options": {
                        "computePlan": _gpu_plan_dict(),
                        "maxImagePixels": 1,
                        "renderScale": 1,
                        "pageManifest": [
                            {
                                "page": 1,
                                "raster": {
                                    "width": 1,
                                    "height": 1,
                                    "scale": 1,
                                    "coordinateSystem": "pixel",
                                },
                            }
                        ],
                    },
                },
            ),
            Event(),
            progress,
        )

    assert progress == []


def test_model_worker_pyinstaller_specs_do_not_collect_public_contract_package_data() -> None:
    pyinstaller_root = Path(__file__).resolve().parents[2] / "pyinstaller"

    for name in ("capture-engine-ocr.spec", "capture-engine-whisper.spec"):
        spec = (pyinstaller_root / name).read_text(encoding="utf-8")
        retired_package = "capture_" + "contracts"
        assert f'collect_data_files("{retired_package}")' not in spec


def test_ocr_worker_pyinstaller_spec_packages_canonical_profile_asset() -> None:
    pyinstaller_root = Path(__file__).resolve().parents[2] / "pyinstaller"
    spec = (pyinstaller_root / "capture-engine-ocr.spec").read_text(encoding="utf-8")

    assert "ocr-profile.json" in spec
    assert "capture_runtime/assets" in spec


def test_ocr_pdf_renders_one_page_at_a_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    source = tmp_path / "public-fixture.pdf"
    source.write_bytes(b"public test fixture")
    resident_pages = 0
    peak_resident_pages = 0

    def page_images(
        _source: Path, max_pages: int, scale: float, _cancellation: Event
    ) -> Iterator[tuple[int, bytes]]:
        assert max_pages == 3
        assert scale == 2
        nonlocal resident_pages, peak_resident_pages
        for page_number in range(1, 4):
            resident_pages += 1
            peak_resident_pages = max(peak_resident_pages, resident_pages)
            yield page_number, f"page-{page_number}".encode()

    class TestAdapter:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def extract_png(self, _image: bytes) -> OcrTextResult:
            nonlocal resident_pages
            resident_pages -= 1
            return OcrTextResult(
                text="public fixture text",
                model="test-model",
                digest="1" * 64,
                device="windowsml-dml",
                warning=None,
                raster_width=1,
                raster_height=1,
                provenance=_resolved_test_provenance(),
            )

    monkeypatch.setattr(ocr_main, "_pdf_page_images", page_images)
    monkeypatch.setattr(ocr_main, "WindowsMLOcrAdapter", TestAdapter)

    result = ocr_main.handle(
        WorkerRequest(
            request_id="ocr-streaming-test",
            operation="run",
            payload={
                "requirementId": "windowsml-ocr",
                "artifactVersion": "0.4.2",
                "modelPath": str(model_path),
                "sourcePath": str(source),
                "mediaType": "application/pdf",
                "options": {
                    "computePlan": _gpu_plan_dict(),
                    "maxPages": 3,
                    "renderScale": 2,
                    "pageManifest": [
                        {
                            "page": page,
                            "raster": {
                                "width": 1,
                                "height": 1,
                                "scale": 2,
                                "coordinateSystem": "pixel",
                            },
                        }
                        for page in (1, 2, 3)
                    ],
                },
            },
        ),
        Event(),
    )

    assert peak_resident_pages == 1
    assert resident_pages == 0
    assert [segment["page"] for segment in result["segments"]] == [1, 2, 3]


def test_ocr_pdf_page_stream_enforces_configured_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    closed = False

    class TestDocument:
        def __len__(self) -> int:
            return 4

        def close(self) -> None:
            nonlocal closed
            closed = True

    monkeypatch.setattr(ocr_main.pdfium, "PdfDocument", lambda _source: TestDocument())

    with pytest.raises(ValueError, match="PDF has 4 pages; limit is 3"):
        list(ocr_main._pdf_page_images(tmp_path / "source.pdf", 3, 2, Event()))

    assert closed


def test_ocr_pdf_page_stream_rasterizes_only_requested_pages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    accessed_pages: list[int] = []

    class TestImage:
        def convert(self, _mode: str) -> TestImage:
            return self

        def save(self, output: BytesIO, format: str) -> None:
            assert format == "PNG"
            output.write(b"page-one-png")

    class TestBitmap:
        def to_pil(self) -> TestImage:
            return TestImage()

        def close(self) -> None:
            pass

    class TestPage:
        def render(self, *, scale: float) -> TestBitmap:
            assert scale == 2
            return TestBitmap()

    class TestDocument:
        def __len__(self) -> int:
            return 46

        def __getitem__(self, index: int) -> TestPage:
            accessed_pages.append(index)
            return TestPage()

        def close(self) -> None:
            pass

    monkeypatch.setattr(ocr_main.pdfium, "PdfDocument", lambda _source: TestDocument())

    images = list(
        ocr_main._pdf_page_images(
            tmp_path / "source.pdf",
            46,
            2,
            Event(),
            page_numbers=(1,),
        )
    )

    assert accessed_pages == [0]
    assert images == [(1, b"page-one-png")]


def test_ocr_pdf_page_stream_without_selection_rasterizes_every_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    accessed_pages: list[int] = []

    class TestImage:
        def convert(self, _mode: str) -> TestImage:
            return self

        def save(self, output: BytesIO, format: str) -> None:
            assert format == "PNG"
            output.write(f"page-{len(accessed_pages)}-png".encode())

    class TestBitmap:
        def to_pil(self) -> TestImage:
            return TestImage()

        def close(self) -> None:
            pass

    class TestPage:
        def render(self, *, scale: float) -> TestBitmap:
            assert scale == 2
            return TestBitmap()

    class TestDocument:
        def __len__(self) -> int:
            return 3

        def __getitem__(self, index: int) -> TestPage:
            accessed_pages.append(index)
            return TestPage()

        def close(self) -> None:
            pass

    monkeypatch.setattr(ocr_main.pdfium, "PdfDocument", lambda _source: TestDocument())

    images = list(ocr_main._pdf_page_images(tmp_path / "source.pdf", 3, 2, Event()))

    assert accessed_pages == [0, 1, 2]
    assert [page for page, _image in images] == [1, 2, 3]


@pytest.mark.parametrize(
    ("media_type", "page_numbers", "page_count", "expected_scope"),
    [
        ("image/png", None, 1, None),
        ("application/pdf", None, 2, None),
        ("application/pdf", [1], 2, (1,)),
        ("application/pdf", [1, 2], 2, (1, 2)),
    ],
)
def test_ocr_worker_passes_requested_page_scope_from_explicit_worker_options(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    media_type: str,
    page_numbers: list[int] | None,
    page_count: int,
    expected_scope: tuple[int, ...] | None,
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    source = tmp_path / ("source.pdf" if media_type == "application/pdf" else "source.png")
    if media_type == "application/pdf":
        source.write_bytes(b"public test fixture")

        def page_images(
            _source: Path,
            _max_pages: int,
            _scale: float,
            _cancellation: Event,
            *,
            page_numbers: tuple[int, ...] | None = None,
        ) -> Iterator[tuple[int, bytes]]:
            selected = tuple(range(1, page_count + 1)) if page_numbers is None else page_numbers
            return iter((page, b"page") for page in selected)

        monkeypatch.setattr(ocr_main, "_pdf_page_images", page_images)
    else:
        Image.new("RGB", (1, 1), "white").save(source, format="PNG")

    manifest_count = len(page_numbers) if page_numbers is not None else page_count
    manifest = [
        {
            "page": page,
            "raster": {
                "width": 1,
                "height": 1,
                "scale": 1,
                "coordinateSystem": "pixel",
            },
        }
        for page in range(1, manifest_count + 1)
    ]
    options: dict[str, object] = {
        "computePlan": _gpu_plan_dict(),
        "pageManifest": manifest,
    }
    if media_type == "application/pdf":
        options.update({"maxPages": page_count, "renderScale": 1})
        if page_numbers is not None:
            options["pageNumbers"] = page_numbers
    else:
        options.update({"maxImagePixels": 1, "renderScale": 1})

    captured_scopes: list[tuple[int, ...] | None] = []

    class RecordingAdapter:
        def __init__(
            self,
            *_args: object,
            requested_page_scope: tuple[int, ...] | None = None,
            **_kwargs: object,
        ) -> None:
            captured_scopes.append(requested_page_scope)

        def extract_png(self, _image: bytes) -> OcrTextResult:
            return OcrTextResult(
                text="public fixture text",
                model="test-model",
                digest="1" * 64,
                device="windowsml-dml",
                warning=None,
                raster_width=1,
                raster_height=1,
                provenance=_resolved_test_provenance(),
            )

    monkeypatch.setattr(ocr_main, "WindowsMLOcrAdapter", RecordingAdapter)

    result = ocr_main.handle(
        WorkerRequest(
            request_id="ocr-page-scope-test",
            operation="run",
            payload={
                "requirementId": "windowsml-ocr",
                "artifactVersion": "0.4.2",
                "modelPath": str(model_path),
                "sourcePath": str(source),
                "mediaType": media_type,
                "options": options,
            },
        ),
        Event(),
    )

    assert result["pages"]
    assert captured_scopes == [expected_scope]


def test_ocr_worker_records_requested_scope_before_selection_manifest_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    source = tmp_path / "source.pdf"
    source.write_bytes(b"public test fixture")
    captured_scopes: list[tuple[int, ...] | None] = []

    def page_images(
        _source: Path,
        _max_pages: int,
        _scale: float,
        _cancellation: Event,
        *,
        page_numbers: tuple[int, ...] | None = None,
    ) -> Iterator[tuple[int, bytes]]:
        assert page_numbers == (1,)
        return iter([(1, b"page")])

    monkeypatch.setattr(ocr_main, "_pdf_page_images", page_images)

    class RecordingAdapter:
        def __init__(
            self,
            *_args: object,
            requested_page_scope: tuple[int, ...] | None = None,
            **_kwargs: object,
        ) -> None:
            captured_scopes.append(requested_page_scope)

        def extract_png(self, _image: bytes) -> OcrTextResult:
            return OcrTextResult(
                text="public fixture text",
                model="test-model",
                digest="1" * 64,
                device="windowsml-dml",
                warning=None,
                raster_width=1,
                raster_height=1,
                provenance=_resolved_test_provenance(),
            )

    monkeypatch.setattr(ocr_main, "WindowsMLOcrAdapter", RecordingAdapter)

    with pytest.raises(ValueError, match="OCR worker did not complete the page manifest"):
        ocr_main.handle(
            WorkerRequest(
                request_id="ocr-selection-manifest-mismatch-test",
                operation="run",
                payload={
                    "requirementId": "windowsml-ocr",
                    "artifactVersion": "0.4.2",
                    "modelPath": str(model_path),
                    "sourcePath": str(source),
                    "mediaType": "application/pdf",
                    "options": {
                        "computePlan": _gpu_plan_dict(),
                        "maxPages": 2,
                        "renderScale": 1,
                        "pageNumbers": [1],
                        "pageManifest": [
                            {
                                "page": 1,
                                "raster": {
                                    "width": 1,
                                    "height": 1,
                                    "scale": 1,
                                    "coordinateSystem": "pixel",
                                },
                            },
                            {
                                "page": 2,
                                "raster": {
                                    "width": 1,
                                    "height": 1,
                                    "scale": 1,
                                    "coordinateSystem": "pixel",
                                },
                            },
                        ],
                    },
                },
            ),
            Event(),
        )

    assert captured_scopes == [(1,)]


@pytest.mark.parametrize("page_numbers", [[2], [1, 3]])
def test_ocr_worker_rejects_invalid_page_numbers_before_adapter_construction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    page_numbers: list[int],
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    source = tmp_path / "source.pdf"
    source.write_bytes(b"public test fixture")
    constructed = False

    class UnexpectedAdapter:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            nonlocal constructed
            constructed = True

    monkeypatch.setattr(ocr_main, "WindowsMLOcrAdapter", UnexpectedAdapter)

    with pytest.raises(ValueError, match="OCR PDF page selection is invalid"):
        ocr_main.handle(
            WorkerRequest(
                request_id="ocr-invalid-page-scope-test",
                operation="run",
                payload={
                    "requirementId": "windowsml-ocr",
                    "artifactVersion": "0.4.2",
                    "modelPath": str(model_path),
                    "sourcePath": str(source),
                    "mediaType": "application/pdf",
                    "options": {
                        "computePlan": _gpu_plan_dict(),
                        "maxPages": 3,
                        "renderScale": 1,
                        "pageNumbers": page_numbers,
                        "pageManifest": [
                            {
                                "page": 1,
                                "raster": {
                                    "width": 1,
                                    "height": 1,
                                    "scale": 1,
                                    "coordinateSystem": "pixel",
                                },
                            }
                        ],
                    },
                },
            ),
            Event(),
        )

    assert constructed is False


def test_ocr_run_reports_empty_output_stage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    source = tmp_path / "public-fixture.pdf"
    source.write_bytes(b"public test fixture")
    stages: list[str] = []

    monkeypatch.setattr(ocr_main, "_report_stage", stages.append)
    monkeypatch.setattr(
        ocr_main,
        "_pdf_page_images",
        lambda *_args: iter([(1, b"page")]),
    )

    class EmptyAdapter:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def extract_png(self, _image: bytes) -> OcrTextResult:
            return OcrTextResult(
                text="   ",
                model="test-model",
                digest="1" * 64,
                device="windowsml-dml",
                warning=None,
                raster_width=1,
                raster_height=1,
                provenance=_resolved_test_provenance(),
            )

    monkeypatch.setattr(ocr_main, "WindowsMLOcrAdapter", EmptyAdapter)

    with pytest.raises(ValueError, match="non-empty segments"):
        ocr_main.handle(
            WorkerRequest(
                request_id="ocr-empty-output-test",
                operation="run",
                payload={
                    "requirementId": "windowsml-ocr",
                    "artifactVersion": "0.4.2",
                    "modelPath": str(model_path),
                    "sourcePath": str(source),
                    "mediaType": "application/pdf",
                    "options": {
                        "computePlan": _gpu_plan_dict(),
                        "maxPages": 1,
                        "renderScale": 2,
                        "pageManifest": [
                            {
                                "page": 1,
                                "raster": {
                                    "width": 1,
                                    "height": 1,
                                    "scale": 2,
                                    "coordinateSystem": "pixel",
                                },
                            }
                        ],
                    },
                },
            ),
            Event(),
        )

    assert "ocr-output-empty" in stages


def test_ocr_image_scale_adapts_to_the_pixel_limit(
    tmp_path: Path,
) -> None:
    source = tmp_path / "large-image.jpg"
    Image.new("RGB", (5_000, 3_000), "white").save(source, format="JPEG")

    normalized = ocr_main._normalized_png(source, 50_000_000, scale=2)

    with Image.open(BytesIO(normalized)) as image:
        width, height = image.size
        assert width * height <= 50_000_000
        assert width > 5_000
        assert height > 3_000
