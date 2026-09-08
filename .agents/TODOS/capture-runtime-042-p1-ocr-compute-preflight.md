# Capture Runtime 0.4.2 P1 OCR compute preflight TODO

- [x] Add red probe/decision tests for dedicated, integrated, and software-only
  adapter snapshots plus DML availability/fallback reasons.
- [x] Add the typed `RuntimeReady.ocrCompute` contract and runtime-owned
  injectable probe implementation.
- [x] Add authenticated readiness integration coverage for contract identity and
  missing bearer credentials.
- [x] Regenerate canonical runtime/SDK contract artifacts; do not hand-edit
  consumer clients or UI.
- [x] Run runtime lint, typecheck, unit, integration, and contract gates with
  `--skip-nx-cache`; record a read-only machine probe without model OCR.
- [x] Commit the closed slice with explicit paths, cached diff/secret audit, and
  no push or publish.
