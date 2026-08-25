# Capture Runtime test levels

The directory is intentionally split by failure boundary:

- `unit/`: hermetic functions, validators, adapters, and deterministic contract fixtures.
- `integration/`: multiple runtime components wired together with controlled downloaders, workers, processes, or API clients.
- `e2e/local-package/`: the package built from the current checkout. PDF OCR uses the test-only `CAPTURE_PDF_OCR_E2E_LOCAL_WORKER_*` exact loopback URL contract and proves that the packaged runtime actually downloads those checksum-locked worker bytes.
- `e2e/online-package/`: the official GitHub release package and its catalog HTTPS worker. Every local worker override is removed from the child environment.
- `e2e/support/`: journey code shared by the two package provenance variants; package acquisition and worker transport remain in their respective entrypoints.

Nx targets collect one level at a time:

```text
capture-runtime:test-unit
capture-runtime:test-integration
capture-runtime:e2e-local-package-pdf-ocr
capture-runtime:e2e-online-package-pdf-ocr
```

Both PDF OCR E2E targets require:

```text
CAPTURE_PDF_OCR_E2E_PDF=<absolute real PDF path>
CAPTURE_PDF_OCR_E2E_EXPECTED_PAGES=<positive page count>
CAPTURE_PDF_OCR_E2E_EXPECTED_ANCHORS_JSON=[{"page":2,"text":"semantic anchor"}]
```

The online target accepts only the exact official release base through
`CAPTURE_PDF_OCR_E2E_ONLINE_RELEASE_BASE_URL`; by default the URL is derived
from the required version in the `gx-capture/capture-workbench` repository. It also requires
`CAPTURE_PDF_OCR_E2E_ONLINE_RUNTIME_VERSION` and
`CAPTURE_PDF_OCR_E2E_ONLINE_RUNTIME_SHA256` so an older or replaced package
cannot be mistaken for the intended publication. The local target may use
`CAPTURE_PDF_OCR_E2E_RELEASE_DIR` to test an already-built local release.

During a real capture, the V2 watchdog prints a checkpoint only when
`status`, `progress`, `partialRevision`, `lastEventSequence`, or `updatedAt`
changes. Five minutes without movement fails as a stalled capture; the output
never includes a capture ID, source path, or OCR text.

PDF accuracy evidence requires every expected page to contain PaddleOCR text.
Each manually transcribed sample must be an exact substring after NFKC
normalization and whitespace removal. The evidence records only sampled page,
sample, and matched-character counts; it does not persist OCR or expected text.
