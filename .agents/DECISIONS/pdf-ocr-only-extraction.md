# PDF OCR-only extraction decisions

## Context

The repository 2024-07 N1 fixture renders normal Japanese but
contains an incorrect embedded text mapping. Capture Runtime accepted any
non-empty `pypdf.extract_text()` result, so corrupt text bypassed PaddleOCR.

## Decision

Use PDFium rendering plus PaddleOCR for every PDF page. Remove the embedded-text
fast path and the production `pypdf` dependency. Require `windowsml-ocr` before
Cert Prep dispatches PDF capture.

## Rejected alternatives

- Character-quality heuristics: valid Unicode can still be semantically wrong,
  and this fixture contains plausible CJK code points that are not visible text.
- Prefer PDFium text extraction: it fixes some pages but reproduces the broken
  text layer on others.
- Compare multiple text extractors: agreement between two consumers of the same
  invalid mapping does not establish visual correctness.

## Change checkpoint

- Change mode: mixed.
- Existing owners: Capture Runtime extractor/OCR worker and Cert Prep capture
  admission policy.
- Delete candidates: embedded PDF extraction branches, digest helpers,
  production `pypdf`, and embedded-only acceptance assertions.
- New owner needed: yes, only these durable cross-repository decision/spec/TODO
  artifacts.
- Token posture: compact quality.
- Verification floor: focused Nx tests, runtime lint/typecheck, local release
  consumer checks, separately collected unit/integration tests, and distinct
  local-package plus online-package real-fixture semantic OCR proof.
