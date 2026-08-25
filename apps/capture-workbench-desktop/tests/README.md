# Capture Workbench desktop test levels

- `unit/`: deterministic script, process, and artifact tests.
- `integration/`: package-QA, staging, contract, and consumer checks.
- `e2e/local-package/`: installed/local-runtime acceptance, smoke, and real
  OCR/media journeys. Every journey owns cleanup and must leave no process or
  listener residue.
- `e2e/online-package/`: reserved for a hash-bound online package.

The existing script helper topology is retained to keep relative imports and
the Tauri harness contract stable; Nx target names and evidence use these
level labels.
