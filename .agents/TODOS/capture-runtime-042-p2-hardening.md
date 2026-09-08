# Capture Runtime 0.4.2 reopened Phase 1 GPU blocker and deferred Phase 2 TODO

## Transition checkpoint

### Session boundary and current status

- [x] Retain the Phase 1 and deferred Phase 2 SPEC/DECISION/TODO documents in
  this repository for fresh-worker resumption. This session performs no Phase 2
  implementation.
- [ ] Close the ordered Phase 1 gate. Capture Workbench remains in the minimum
  CDP target-loss harness repair/recheck; Cert Prep has one prior real-OCR pass
  but needs the producer-change minimum recheck; GX Law Prep source integration
  is committed but real installed OCR is pending.

- [x] Pin comparison base
  `92572ded5d33963e6405b986e2b9f617a8ac2989` and inventory the 232 committed
  changed paths by responsibility cluster.
- [x] Prove shared-worktree ownership before cleanup. Remove only the
  uncommitted LAW-specific candidate-test hunk; preserve line-ending-only
  tracked state, user/unknown PNGs, proofshot artifacts, and older evidence.
- [x] Repair the pnpm 12 multi-document lockfile in bounded commit `9813d57`.
  Verify exact pnpm `12.0.0`, a single main dependency document, unchanged main
  dependency graph semantics, frozen offline install, and `capture-tools`
  lint/test with `--skip-nx-cache`.
- [x] Rehash the immutable Capture Phase 1 aggregate and on-disk reviewed
  runtime/archive/worker identities without loading PaddleOCR. Confirm the
  aggregate SHA and bound tuple in this specification.
- [ ] Obtain independent Standards and Specification transition reviews for
  the exact reopened-Phase-1/deferred-Phase-2 documentation HEAD. Root grills
  findings one at a time. Approval unlocks only the active lane below.

## Reopened Phase 1 blocker: only executable lane

- [x] Freeze the canonical compute-selection interface: `OcrComputePlan`
  returns one immutable internal execution plan, existing public readiness
  projection, and private selection proof; a separate immutable execution
  receipt owns post-session facts. Define per-adapter usability, dGPU -> iGPU
  -> noticed CPU priority, compatibility-only override behavior,
  post-selection fail-closed semantics, RTX 4060 oracle, private evidence seam,
  privacy fields, a truth table separating positive-unavailable,
  indeterminate, structurally-invalid, and post-selection failure, and
  contract/hash impact without loading Paddle/model assets.
  Verify before commit: `git diff --cached --check -- .agents/SPECS/capture-runtime-042-p2-hardening.md .agents/DECISIONS/capture-runtime-042-p2-hardening.md .agents/TODOS/capture-runtime-042-p2-hardening.md`.
  Verify automatic default: `rg -n --fixed-strings "There is no implicit value" .agents/SPECS/capture-runtime-042-p2-hardening.md`.
  Verify machine oracle: `rg -n --fixed-strings "NVIDIA GeForce RTX 4060" .agents/SPECS/capture-runtime-042-p2-hardening.md`.
  Verify private seam: `rg -n --fixed-strings "OcrExecutionEvidenceSink" .agents/SPECS/capture-runtime-042-p2-hardening.md`.
  Verify uncertainty rule: `rg -n --fixed-strings "Unknown is not unavailable" .agents/DECISIONS/capture-runtime-042-p2-hardening.md`.
  Verify truth table: `rg -n --fixed-strings "### Canonical compute decision truth table" .agents/SPECS/capture-runtime-042-p2-hardening.md`.
  Verify execution binding: `rg -n --fixed-strings "executionSha256" .agents/SPECS/capture-runtime-042-p2-hardening.md`.
  Verify ordinal contract: `rg -n --fixed-strings "Official ordinal and LUID contract" .agents/SPECS/capture-runtime-042-p2-hardening.md`.
  Verify contract identity: `rg -n --fixed-strings "d293a3de26114f1b4fd65ea6d6d3f157fa2f93109b31e1e30d5d15ef0dfdeb40" .agents/SPECS/capture-runtime-042-p2-hardening.md`.
  Verify installed order: `rg -n --fixed-strings "canonical JPEG then the original PDF page 1" .agents/SPECS/capture-runtime-042-p2-hardening.md`.
- [ ] **Compute-plan slice:** red vertical tests at the canonical interface
  prove enumeration-order-independent usable dGPU -> usable iGPU -> noticed
  CPU priority; RTX 4060 automatic selection on this machine; deterministic
  same-class identity tie-breaking; software positive-unavailable versus
  unknown indeterminate evidence;
  positive-unavailable evidence continuing to the next candidate;
  indeterminate evidence blocking any result it could change; total/
  structurally invalid inventory as unavailable; retired ordinal/deviceId
  compatibility requests as unavailable; a complete bijective LUID join between high-performance
  rank and ordinary `EnumAdapters1` ordinal; and identical plan/identity
  reaching readiness and every session configuration. Red cases must include
  iGPU at ordinary ordinal `0` plus RTX 4060 at ordinary ordinal `1` while the
  RTX has high-performance rank `0` (ORT must receive `device_id: 1`), unequal
  or duplicate LUID sets, a false `IDXGIFactory1::IsCurrent`, an ordinal/LUID
  or complete-map-digest change across pipeline construction, a lazy/
  unobservable session, a later worker map mismatch, an ORT version/mapping-
  contract mismatch, a missing/
  mismatched per-session provider `device_id`, missing/failed fallback
  disablement, and DML profile evidence from a session whose binding did not
  validate. They must also include dGPU indeterminate + iGPU usable,
  both adapter probes timeout/throw, all adapters positive-unavailable, and
  structurally-invalid inventory, with CPU emitted only for the explicit
  all-positive-unavailable/no-hardware or authoritative-provider-absent rows.
  DML construction and inference failure after selection must fail closed
  without another GPU or CPU retry.
  Prove retired override rejection, any identity/mapping drift, DML construction, zero
  assigned DML nodes, and inference failure never reselect another GPU or CPU.
  Replace both independent settings-to-worker numeric paths with one retained
  plan; reject the retired `CAPTURE_WINDOWSML_DEVICE_ID` and worker `deviceId`
  paths; pin `ort-directml-1.24.4-enumadapters1-v1` and the complete adapter-map
  digest; remove implicit device `0`; run
  runtime lint/typecheck/unit/integration with `--skip-nx-cache`, and prove the
  generated contract set remains byte-identical. Residual-scan runtime config,
  installer/model probes, worker requests, journeys, and packaging for implicit
  `deviceId: 0`/`CAPTURE_WINDOWSML_DEVICE_ID=0` policy. Review exact HEAD and
  commit.
  Verify: `corepack pnpm nx run capture-runtime:lint --skip-nx-cache`.
  Verify: `corepack pnpm nx run capture-runtime:typecheck --skip-nx-cache`.
  Verify: `corepack pnpm nx run capture-runtime:test-unit --skip-nx-cache`.
  Verify: `corepack pnpm nx run capture-runtime:test-integration --skip-nx-cache`.
  Verify: `corepack pnpm nx run capture-runtime:check-contracts --skip-nx-cache`.
- [ ] **Compute real-proof slice:** on the Capture Workbench app, prove the
  automatic GPU-DML plan selects the dedicated RTX 4060 and is used first by
  the canonical JPEG, then by the original PDF page 1. Preserve semantic
  anchors, the exact sanitized LUID/PCI identity joined to its ordinary ORT
  `device_id`, per-session provider-option and DML-node evidence, unchanged
  before/after pipeline-construction ordinary LUID maps and map digests,
  observational RTX 4060 label, successful per-session fallback disablement,
  plan/identity digests, runtime/worker/model/profile/contract hashes, and
  cleanup. Class-only
  readiness,
  `windowsml-dml` alone, and prior LAW integrated-GPU evidence are insufficient.
  Keep the receipt free of tokens, OCR/truth text, user/host names, local paths,
  environment dumps, and arbitrary diagnostics. Validate
  `ocr-device-proof-v1.json` through its private evidence schema and bind its
  relative artifact/digest in acceptance manifest schema `2`. Stop the model
  before any consumer model starts; review and commit evidence tooling
  separately from generated evidence.
  Add the fail-closed Nx target
  `capture-workbench-desktop:acceptance-real-ocr-gpu-selection` to orchestrate
  the two ordered installed runs and validate each private receipt.
  Verify: `corepack pnpm nx run capture-tools:test --skip-nx-cache`.
  Verify: `corepack pnpm nx run capture-workbench-desktop:typecheck-scripts --skip-nx-cache`.
  Verify: `corepack pnpm nx run capture-workbench-desktop:acceptance-real-ocr-gpu-selection --skip-nx-cache`.

The two unchecked slices above are one reopened Phase 1 gate and the only work
authorized after exact-HEAD design approval. They run in order and end only
when the installed Capture Workbench canonical JPEG then original PDF page 1
both prove the automatic dedicated RTX 4060 selection and cleanup. No Cert or
LAW model process may start before that result. Prior LAW integrated-adapter
evidence cannot satisfy it. A later fresh worker must build one exact candidate
before model acceptance; source changes invalidate prior Capture and Cert Phase
1 manifests, so old manifests or receipts cannot be reused. The required
sequence is Capture Workbench installed RTX4060 JPEG, then original PDF page 1
and cleanup; Cert Prep with the identical candidate bytes and cleanup; then
LAW. None of those model gates may run in this implementation checkpoint. No
item below may be claimed or executed first or combined with this lane.

## Deferred Phase 2 design checkpoints and implementation slices

Everything in this section is blocked until `P1-GPU-SELECTION-PROOF` passes.

- [ ] **Canonical version inventory (first Phase 2 slice):** declare one source
  for runtime, contract/schema, Python/npm/Java/Rust clients, desktop metadata,
  catalogs, manifests, and consumer expectations. Generate and verify a
  next-version upgrade/check command; reject stale literals and mixed
  0.4.1/0.4.2 locks. Local package E2E keeps tiered identity (URL/port are
  transport; contract/provenance/package-boundary identity remains required),
  while published release gates retain strict byte/version/hash identity.
- [ ] Isolate deterministic candidate staging and shared resources so local
  package E2E cannot accidentally import a source tree or sibling artifact.
- [ ] Replace duplicated app journey setup with one canonical acceptance runner
  for build/install/event scope/model transport/uninstall, retaining the
  sequential Capture Workbench -> Cert Prep -> GX Law Prep OCR semaphore.
- [ ] Design and implement the deep `ModelSourceSnapshot` module for immutable
  model/profile/digest provenance without raw OCR, tokens, or machine paths.
- [ ] Run Design It Twice for canonical OCR deepening with at least three
  materially different interfaces. Compare depth, locality, worker seam,
  failure projection, cancellation, migration cost, and deletion test.
- [ ] Run Design It Twice for native owned-session deepening. The accepted
  interface must hide OS handles and converge close, crash, readiness failure,
  and cleanup retry on one terminal proof.
- [ ] Record the deferred public TDD seams before writing Phase 2 implementation
  tests: OCR projection, owned-session proof, and installed-app close journey.
- [ ] **Canonical OCR slice:** replace the accepted policy cluster with the
  deepened `OcrPipeline`; delete superseded shallow paths/tests. Prove predictor
  initialization once, serialized inference, page scope/all-pages default,
  ordering, empty/failed/malformed pages, polygons/confidence, provenance, and
  fail-closed DML behavior through the canonical interface. Review and commit.
- [ ] **Performance baseline slice:** add privacy-safe internal measurement for
  cold initialization, raster, inference, first page, total elapsed, peak
  worker/Job memory, and cleanup. Record real JPEG/PDF page-1 baseline with
  exact identities; do not change production behavior. Review and commit.
- [ ] **Evidence-led optimization slices:** one metric and one vertical change
  per fresh worker. Declare comparison/noise rules before coding, preserve
  per-fixture semantic and cleanup gates, then review and commit each slice.
- [ ] **Owned-session slice:** deepen native lifecycle ownership and remove
  duplicated host cleanup mechanics. Prove suspended assign/verify/resume,
  no-breakaway, readiness failure, root crash, normal/window close, host
  termination, descendant cleanup, retry after failed proof, and baseline
  process survival. Run Rust and desktop gates with `--skip-nx-cache`; review
  and commit.
- [ ] **Next-start reconciliation slice:** preserve durable runtime/model
  assets; remove only identity-proven stale PIDs/listeners/run data/staging.
  Never kill by name. Failure injection, review, and focused commit required.

## Release and cross-project gates

- [ ] Keep this entire section blocked until the installed Capture Workbench
  `P1-GPU-SELECTION-PROOF` gate passes. Consumer validation may then run Cert
  Prep followed by GX Law Prep; no consumer model starts before the producer
  gate, and no consumer evidence substitutes for it.
- [ ] Before generating a new candidate, audit Phase 2 changes again and
  remove unnecessary agent-owned code with additive cleanup commits.
- [ ] Regenerate contract/schema/SDK/release assets only from an accepted
  public contract change. The compute-selection implementation is expected to
  leave API `2.0`, `OcrComputePreflightV2` schema `1`, OCR schema `3`, generated
  SDKs, and `contractSetSha256` byte-identical; fail this checkpoint if they
  drift. Bind changed runtime/worker/private-proof bytes to exact HEAD and
  rerun their no-cache gates.
  Verify: `corepack pnpm nx run capture-runtime:check-contracts --skip-nx-cache`.
- [ ] Run installed model-enabled acceptance separately in order:
  Capture Workbench canonical JPEG -> Capture Workbench original PDF page 1 ->
  Cert Prep -> GX Law Prep. A child must finish cleanup and release model
  memory before the next starts. Do not add Cert/LAW source or consumer-specific
  producer logic from this repository. Update the existing producer-owned
  `acceptance-three-projects` target to require the two-run Capture Workbench
  GPU-selection target before it invokes either unchanged consumer target.
  Verify: `corepack pnpm nx run capture-workbench-desktop:acceptance-three-projects --skip-nx-cache`.
- [ ] Keep stable release promotion blocked until all three Phase 1 journeys,
  Phase 2 lifecycle gates, published-byte identity checks, repository PRs, and
  SHA-specific CI runs are green.
- [ ] Open a focused Capture Workbench PR only after the final exact HEAD has
  both review axes, privacy/path/secret audit, evidence identities, and rollback
  recorded.
