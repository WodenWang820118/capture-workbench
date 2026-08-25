# PDF OCR-only extraction spec

## Purpose

Make the rendered PDF page the only source of truth for PDF capture. Every PDF
page is rendered by PDFium and recognized by the existing PaddleOCR 3.7
WindowsML worker. Embedded PDF text is never read or returned.

## Non-goals

- Do not add another OCR engine or a second PDF parsing service.
- Do not preserve `pdf-embedded-text` or mixed embedded/OCR extraction modes.
- Do not change the public Capture Runtime v2 HTTP or document schema.
- Do not claim a local candidate is published or installed-package evidence.

## Interfaces

- The public PDF upload and result contracts remain unchanged.
- The internal OCR worker PDF request receives `maxPages` and `renderScale` and
  processes every page in source order.
- PDF capture requires the `windowsml-ocr` runtime requirement to be ready.
- Successful PDF extraction reports the existing `windowsml-ocr` engine and
  PaddleOCR model/device provenance.

## Key decisions

- Remove `pypdf` from production dependencies and extraction code.
- Keep PDFium inside the separately packaged OCR worker; the core executable
  does not absorb PDF rendering or PaddleOCR dependencies.
- Reuse the existing bounded, cancellable, one-page-at-a-time worker path.
- Cert Prep rejects PDF capture before upload when WindowsML OCR is not ready,
  matching its existing image admission policy.

## Edge cases and failure modes

- Unreadable, empty, oversized, or over-page-limit PDFs fail in the OCR worker.
- Cancellation is checked before each page render and recognition operation.
- A page with no recognized text does not create an empty segment; a document
  with no non-empty OCR segments fails closed.
- Worker/model unavailability is reported as the existing typed runtime
  requirement failure before Cert Prep dispatches the upload.

## Acceptance criteria

- No production source or dependency imports `pypdf`.
- A PDF with a non-empty but incorrect text layer still invokes PaddleOCR for
  every page and returns only OCR worker text.
- The OCR worker enforces the configured PDF page limit and preserves page
  order while holding at most one rendered page image at a time.
- Cert Prep blocks PDF and image capture when `windowsml-ocr` is not ready.
- Separately collected Nx unit and integration targets pass without Nx cache.
- One opt-in Nx E2E target launches the real local-package executable, installs
  the real OCR worker/model through runtime APIs, and never substitutes a fake
  runtime or OCR adapter. Its exact test-only loopback worker URL must match the
  locked OCR worker filename, and the server must observe the actual download.
- A second opt-in Nx E2E target downloads the official online package, strips
  every local worker override, and installs the OCR worker from the catalog
  HTTPS URL.
- A local-package run of the real 2024-07 N1 PDF returns OCR text for all 44
  pages. Eight manually transcribed samples from rendered pages 2, 8, 15, 22,
  29, 36, 41, and 44 must match as exact substrings after NFKC normalization
  and whitespace removal; embedded-text provenance is rejected.

## Test boundaries

### Unit tests (`tests/unit`)

- Runtime tests fake worker dispatch for all-page routing and PDF limit
  validation; they do not constitute OCR acceptance.
- Cert Prep frontend/backend tests use fake runtime clients to prove PDF
  admission is OCR-gated and no upload is dispatched when unavailable.
- Node unit tests validate E2E option parsing, environment isolation, and
  evidence shape only.

### Integration tests (`tests/integration`)

- Installer/catalog/downloader/worker tests prove the local E2E worker URL maps
  only `windowsml-ocr`, leaves Whisper and model URLs locked, and rejects a
  mismatched catalog filename.

### Real runtime E2E (`tests/e2e`)

- `capture-runtime:e2e-local-package-pdf-ocr` depends on a freshly built local
  release and proves the exact loopback worker request plus all-page OCR.
- `capture-runtime:e2e-online-package-pdf-ocr` downloads the official release
  core, uses only the embedded catalog HTTPS worker transport, and runs the
  same real PDF semantics.
- Reports are separate under `tmp/capture-runtime/pdf-ocr-e2e/local-package`
  and `online-package`; they contain only hashes, page/sample/matched-character
  counts, provenance, transport, and cleanup flags, never source paths, expected
  samples, or OCR text.
- A V2 watchdog reports only changes to capture status, progress, partial
  revision, event sequence, and update time. Five minutes without any movement
  fails as stalled instead of waiting only on the 30-minute terminal timeout.
