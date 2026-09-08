# Capture Runtime 0.4.2 reopened Phase 1 GPU gate and deferred Phase 2 decisions

## Session boundary

This checkpoint is implementation-scoped to the reopened Phase 1 compute
selection and installed Capture Workbench proof. Phase 2 decisions and TODOs
remain durable repo-local documents, but Phase 2 code, broad refactors,
performance work, candidate/release publication, and consumer changes are
deferred until the ordered Phase 1 evidence is current and reviewed.

The sole CPU/GPU selection truth table is the `Canonical compute decision truth
table` in `.agents/SPECS/capture-runtime-042-p2-hardening.md`. Other SPEC,
DECISION, TODO, and guide files reference that table rather than defining a
second policy.

## Chosen decisions

1. **The GPU-selection requirement reopens Phase 1 for one blocker.**
   `P1-GPU-SELECTION-PROOF` unlocks only the minimal runtime-owned compute-
   selection plus private-proof slice and the ordered installed Capture
   Workbench proof. The prior aggregate remains immutable historical evidence,
   but it does not close this new gate. Canonical OCR deepening, performance,
   `OwnedRuntimeSession`/reconciliation, candidate, release, and publication
   remain deferred Phase 2. OCR-only extraction, DirectML failure semantics,
   API `2.0`, and projection schema `3` remain the behavioral floor.
2. **Component evidence invalidates locally.** A source change invalidates the
   affected component's evidence. It does not mutate the immutable Phase 1
   aggregate or automatically invalidate unrelated artifact hashes.
3. **No consumer-specific producer work.** LAW and Cert integrations consume
   the runtime contract from their own repositories. Capture Workbench does not
   gain LAW-specific candidate assembly, routing, or OCR policy.
4. **Deepen by replacement.** `OcrPipeline` is deepened in place. Superseded
   raster/planning/normalization policy and implementation-coupled tests are
   removed after equivalent behavior is green at the canonical interface; a
   second coordinator layered over the old call graph is rejected.
5. **One compute selection owns readiness, session configuration, and proof.**
   `OcrComputePlan` returns one immutable internal plan, existing public
   `OcrComputePreflightV2` projection, and private selection-proof value. The
   plan identity that produces readiness must configure inference. A separate
   immutable execution receipt proves post-session facts without mutating the
   selection. A host or UI cannot make a second selection. The current
   settings -> worker-preflight and settings -> capture paths, which separately
   forward the same number, must be replaced by this retained plan flow.
6. **Unknown is not unavailable.** Each adapter assessment is
   `positive-usable`, `positive-unavailable`, or `indeterminate`.
   Positive-unavailable requires affirmative software/unsupported/provider-
   absent evidence. Timeout, exception, unknown class, inconclusive mapping,
   or unexpected status is indeterminate and never contributes evidence for
   CPU fallback. A structurally invalid snapshot is readiness-unavailable.
7. **Automatic GPU priority is usable dedicated, then usable integrated, then
   noticed CPU.** Runtime-owned GPU preference and normalized hardware identity
   break same-class ties. A lower-priority choice is legal only after every
    candidate that could outrank/change it is positive-unavailable or
    authoritatively absent. CPU is legal only after all hardware is
    positive-unavailable/authoritatively absent, or the completed provider
    query positively proves `DmlExecutionProvider` absent.
   Neither numeric adapter `0` nor a display name is the default policy. This
   supersedes the historic default-`0` statements in `gpu-ocr-directml.md`
   without rewriting that earlier evidence record.
8. **The historic ordinary-ordinal override is retired.** The runtime rejects
   `CAPTURE_WINDOWSML_DEVICE_ID` and all worker `deviceId`-only requests. There
   is no implicit `0`, compatibility ordinal path, or host-derived numeric
   selection. Worker-owned automatic selection retains one immutable plan;
   CPU fallback is represented by an explicit CPU plan. Hosts do not
   calculate or persist the ordinary ordinal.
9. **CPU fallback and post-selection failure remain distinct.** CPU is allowed
   only for the canonical table's two pre-selection rows: authoritative
   positive evidence proves no usable GPU (including no hardware), or the
   completed provider query positively proves `DmlExecutionProvider` absent.
   CPU fallback always requires the existing user notice. Indeterminate
   evidence yields readiness unavailable without a CPU notice. Once a GPU plan
   exists, identity drift, DML construction, assignment, or inference failure
   fails that capture, invalidates the plan, and permits no other-GPU selection
   or CPU-only retry for the failed operation.
10. **Exact device proof stays private and privacy-safe.** The canonical
   identity is class, LUID, PCI IDs/revision, and a bounded observational DXGI
   label. High-performance preference rank and ordinary `EnumAdapters1`
   ordinal are distinct coordinates joined only by exact LUID; only the latter
   becomes ORT `device_id`. A selection digest binds policy, identity, both
   coordinates, the complete adapter-map digest, pinned ORT mapping contract,
   worker, and contract. A later worker must reproduce that complete map before
   use. The execution proof brackets the owned synchronous Paddle pipeline
   construction with a current ordinary LUID map. For every returned ORT
   session it observes the planned provider `device_id`, disables that session's
   implicit fallback before prediction, and binds that session's post-
   prediction DML node evidence. Lazy/unobservable sessions are terminal. A
   separate execution digest binds those session records to source/page scope
   and exact runtime/worker/model/profile/contract hashes. Missing, changed,
   or cross-session evidence is terminal, never a receipt. Owned worker stdio
   and an acceptance-only artifact sink carry the receipt without a public
   endpoint.
   Proof excludes paths, tokens, OCR/truth text, host/user names, environment
   dumps, and arbitrary diagnostics.
11. **Public contracts remain byte-compatible.** API `2.0`,
   `OcrComputePreflightV2` schema `1`, and OCR projection schema `3` do not gain
   device fields. Generated schemas/SDKs and `contractSetSha256` remain
   unchanged; implementation and private evidence hashes change. A future
   public identity field requires a separate contract decision and full
   regeneration.
12. **Native process policy has one owner.** `OwnedRuntimeSession` owns the Job,
   descendants, monitoring, termination, retry, and cleanup proof. Launchers
   sequence attempts and hosts project product status without duplicating OS
   process policy.
13. **Cleanup is identity-scoped.** Normal/window close, readiness failure,
    root crash, and host termination converge on the same owned-session finish
    behavior. Baseline processes survive and broad process-name termination is
    forbidden.
14. **Performance facts are internal evidence.** Timing/memory counters and
    identities may be recorded; OCR text, tokens, paths, and arbitrary
    diagnostics may not. Public OCR contracts do not grow merely to support a
    benchmark.
15. **Measure before optimizing.** The first performance slice changes no
    production behavior. Each optimization declares its metric and noise rule
    before implementation and keeps per-fixture semantic/cleanup gates.
16. **The reopened producer gate precedes every consumer model run.** Installed
    Capture Workbench proves the canonical JPEG and then original PDF page 1 on
    the automatic RTX 4060 plan and releases memory. No Cert or LAW model
    process may start before that exact gate passes; only then may Cert run,
    followed by LAW after Cert cleanup. Prior LAW integrated-adapter evidence
    cannot satisfy or bypass the producer gate. Full-document OCR is reserved
    for changes whose risk requires it.
17. **Fresh contexts and bounded commits are required.** Each accepted design
    or implementation checkpoint moves to a fresh worker. Necessary changes
    are committed by explicit path; user/unknown and line-ending-only state is
    preserved.
18. **Review approval is exact-HEAD evidence.** Standards and Specification
    reviews are independent. Any commit, generated artifact update, or rebase
    makes prior approval stale and requires focused review again.
19. **Phase 2 starts with canonical version identity.** The first Phase 2
    implementation slice is one generated version inventory plus a deterministic
    next-version upgrade/check command and stale-literal CI. It covers runtime,
    contract/schema, all language clients, desktop metadata, catalogs, manifests,
    and consumer expectations. Local package E2E uses tiered identity: URL/port
    identify transport, while contract, package boundary, provenance, and loaded
    executable identity remain required; published release checks retain strict
    immutable-byte identity.
20. **OCR proof and structuring success are separate terminals.** For a
    host-structured capture, the runtime emits the validated private execution
    proof exactly once after raw and OCR projection persistence and the
    `awaiting_structuring` transition succeed. It does not await host LLM,
    candidate commit, or release completion. Failures before that checkpoint
    emit no success proof; cancellation/deletion afterward cannot duplicate it.
    Host commit persistence and installed acceptance finalization remain
    separate gates, and the private proof is never a public contract field.

## Rejected alternatives

- Classifying the new GPU-selection/proof requirement as Phase 2 hardening: it
  falsely leaves current Phase 1 green and lets workers schedule unrelated OCR,
  performance, or lifecycle work beside the blocker.
- Running or crediting LAW integrated-adapter evidence before the installed
  Capture Workbench RTX 4060 gate: consumer evidence cannot prove the producer's
  canonical default or unlock the reopened Phase 1 gate.
- Host-side GPU probing or selection: duplicates runtime policy and can diverge
  from actual inference.
- Treating adapter index zero as automatic priority: DXGI enumeration order is
  not the product policy and may put an iGPU before a dGPU.
- Passing `EnumAdapterByGpuPreference(HIGH_PERFORMANCE)` rank as ORT
  `device_id`: the preference call reorders adapters, while pinned ORT 1.24.4
  resolves `device_id` through ordinary `EnumAdapters1`; the coordinates are
  not interchangeable.
- Calling a receipt's planned LUID actual-device proof merely because an ORT
  profile contains a DML node: the profile proves provider assignment, not the
  ordinal/LUID mapping. The pipeline-construction bracket, per-session
  configured ordinal, and that same session's post-prediction evidence must all
  validate.
- Assuming a later worker or compatible ORT version preserves the mapping: a
  later worker must reproduce the complete adapter-map digest, and any ORT
  version/build change requires a new reviewed mapping-contract identifier.
- Selecting by DXGI display name: labels are observational evidence, not a
  stable selector, and driver updates can change them.
- Re-running priority policy independently during inference: readiness could
  prove one device while OCR configures another. Execution validates and uses
  the one immutable plan instead.
- Treating timeout/exception/unknown as “not usable”: it confuses absence of
  evidence with positive-unavailable evidence. If the unresolved adapter could
  change the winner or fallback conclusion, readiness is unavailable; CPU is
  forbidden.
- Treating a total/structurally invalid inventory as “no GPU”: enumeration did
  not produce an authoritative decision input, so CPU would be silent
  uncertainty.
- CPU retry after DirectML construction/inference failure: hides a broken GPU
  path and creates false provenance.
- Exposing adapter index or raw performance diagnostics publicly: adds a
  shallow interface without a product caller.
- Adding exact device identity to API `2.0` or OCR schema `3` for acceptance:
  changes every generated client and contract hash when a private sanitized
  receipt can prove the same execution fact.
- Mutating the selection proof after inference: post-session fields would make
  readiness evidence circular. Emit a separately digested execution receipt.
- Adding a second OCR orchestration module while retaining Phase 1 policy in
  existing callers: fails the deletion test and increases shotgun surgery.
- Making host applications own Job handles or terminate by executable name:
  breaks ownership locality and risks external processes.
- Running all 46 PDF pages for every development iteration: consumes model
  memory and time without increasing proof for page-1 parser/contract slices.
- Removing unknown worktree files to make status clean: ownership cannot be
  inferred from Git status alone.

## Review and rollback

This design requires one-question-at-a-time grill review plus independent
Standards and Specification review before implementation. Approval must be
bound to the exact documentation commit and unlocks only the reopened Phase 1
compute-selection/proof slice; it does not authorize deferred Phase 2.

Rollback is the prior reviewed transition commit for the affected slice. Use
additive revert commits; do not rewrite shared history or alter the immutable
historical Phase 1 aggregate.
