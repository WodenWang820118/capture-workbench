# Capture Runtime 0.4.2 reopened Phase 1 GPU gate and deferred Phase 2 specification

## Purpose and entry gate

The dGPU -> iGPU -> noticed CPU requirement reopens Capture Workbench Phase 1
as blocker `P1-GPU-SELECTION-PROOF`. The only implementation lane this design
unlocks is the minimal runtime-owned `OcrComputePlan` selection/proof module and
the private installed-evidence seam needed to prove it. The installed Capture
Workbench must then select this machine's dedicated RTX 4060 automatically and
run the canonical JPEG followed by the original PDF page 1. No Cert Prep or GX
Law Prep model process may start until that exact Capture Workbench gate passes.

Canonical OCR-pipeline deepening, performance work, `OwnedRuntimeSession`
deepening/reconciliation, candidate assembly, release, and publication remain
deferred Phase 2 work. They are neither prerequisites for nor part of the
reopened Phase 1 slice. The slice must preserve OCR-only extraction, the
authenticated API `2.0` surface, and OCR projection schema `3`.
The existing `p2-hardening` filename is retained only as the stable planning-
document locator; it does not classify the active lane as Phase 2.

### Session implementation boundary

This session implements only the reopened Phase 1 compute-selection/proof
lane. The Phase 2 material in this specification is deliberately retained as
repo-local design for the next fresh worker; it is documentation-only here.
No Phase 2 code, broad refactor, performance optimization, candidate build,
release, or publication may be started before the ordered Phase 1 evidence is
current and reviewed.

The earlier Capture Workbench Phase 1 evidence is the immutable historical
aggregate whose SHA-256 is
`cc5df53d8244d121c1ee96be250948b329211f78b57f3b32587c7c2c03777e29`.
It binds source HEAD `63521d28d38a022140e8b39ceb5f72a8370da1c1`,
runtime `3d37b8507e44069ea6f9f29643b4bc9c3941550fd81481b558df5e2f4c9d029b`,
OCR archive `424d55ea67dcab9eff9e17998426111f0c5ad090e776f4f98e669bef03b1174e`,
OCR executable `b26cbb2d55eae84d00c7bae4aeadf73cb602ef68556face5efefd44fb250d887`,
and contract set
`d293a3de26114f1b4fd65ea6d6d3f157fa2f93109b31e1e30d5d15ef0dfdeb40`.
The reopened requirement does not rewrite this record, but the record cannot
satisfy `P1-GPU-SELECTION-PROOF`. Later source changes invalidate only the
affected component's evidence and require fresh proof before promotion.

Only after the reopened Capture Workbench gate passes may Cert Prep run, then
GX Law Prep after Cert cleanup. Prior LAW integrated-adapter evidence cannot
satisfy the producer gate. Deferred Phase 2 work remains separately gated; the
cross-project release, stable-index, and published-artifact gates remain
blocked until all required sequential acceptance and Phase 2 gates pass.

## Non-goals

- Do not add embedded-PDF text extraction, hybrid arbitration, or LLM OCR
  routing. Embedded text, when present in a PDF fixture, is ignored rather than
  treated as a rejection condition.
- Do not change LAW or Cert source from this repository, and do not add a
  LAW-specific candidate route, fixture, or producer policy.
- Do not expose Paddle kwargs, model paths, raw Job handles, adapter device
  indexes, arbitrary diagnostics, or performance internals through the public
  runtime interface.
- Do not implement the compute module, load Paddle/model assets, run real OCR,
  edit Cert/LAW, generate a candidate, release, or publish during this design
  checkpoint.
- Do not restore NPU selection or retry a failed DirectML initialization or
  inference on a CPU-only pipeline.
- Do not treat unit tests, fake OCR, package QA, screenshots, or a successful
  exit code as fresh real-model acceptance.
- Do not optimize against intuition. A performance implementation slice starts
  only after a reproducible measurement exists.

## Transition inventory

The fixed comparison base is
`92572ded5d33963e6405b986e2b9f617a8ac2989`. The transition inventory at
`9813d57` contains 232 committed paths. The high-responsibility clusters are
the runtime OCR implementation and tests, generated contracts and three SDKs,
the Rust sidecar launcher, the desktop lifecycle and installed acceptance, and
candidate/release tooling. These are committed Phase 1 slices; their size is
not permission to collapse Phase 2 into another broad diff.

The shared worktree may also report tracked files whose blobs are unchanged
because of line-ending metadata, plus user/unknown screenshots and proofshot
artifacts. They are not Phase 2 cleanup targets. A prior uncommitted
LAW-specific candidate test was removed only after its hunk was proven to be
LAW-only; the file now matches HEAD. The pnpm 12 two-document lockfile defect
was a separate necessary slice and is committed as `9813d57`.

Independent Standards and Specification review of the transition remains a
gate. An inventory or a green focused test is not approval.

## Deferred Phase 2 roadmap (documentation only in this session)

The first Phase 2 implementation slice is the recurrent version-upgrade
failure, not another OCR or consumer rewrite. It must establish:

1. one canonical version inventory for runtime, contract/schema, Python/npm/
   Java/Rust clients, desktop metadata, catalogs, manifests, and consumer
   expectations;
2. a deterministic next-version upgrade/check command that generates those
   values and rejects stale hard-coded versions or mixed 0.4.1/0.4.2 locks;
3. isolated deterministic staging for local candidate artifacts and shared
   resources, with local-vs-production URLs treated as transport only;
4. one canonical acceptance runner that owns build/install/event scope/model
   transport/uninstall, while preserving the sequential OCR semaphore;
5. a deep `ModelSourceSnapshot` module that binds model/profile/digest
   provenance without exposing raw OCR or machine paths;
6. the deep `OwnedRuntimeSession` lifecycle and next-start reconciliation
   module, including the full failure matrix and baseline-process survival;
7. measured memory/latency optimization with dGPU -> iGPU -> noticed CPU policy,
   DirectML initialization/inference fail-closed semantics, and no silent CPU
   retry; and
8. immutable 0.4.2 candidate/release bytes, published-consumer/PR gates, and
   rollback without a mutable stable pointer.

No item in this roadmap is an implementation task for the current session.

## Deferred Phase 2 deep module 1: canonical OCR pipeline

`OcrPipeline` remains the canonical OCR module. Phase 1 made it own projection
normalization, page ordering/completeness, box and confidence semantics,
provenance, and typed terminal failures. Phase 2 deepens the same module rather
than adding a second coordinator around it.

The target external interface accepts one capture request and returns one
`CaptureOcrProjectionV3`. Callers supply capture/source identity and optional
ordered PDF page scope. They do not supply a precomputed Paddle profile,
rasterization policy, inference concurrency, region normalization, or failure
projection policy. The implementation hides:

- PDFium rasterization and Pillow RGB normalization;
- canonical profile/model/dictionary validation;
- bounded page planning and all-pages-by-default expansion;
- one-time predictor initialization and serialized inference;
- strict Paddle result normalization;
- page-complete projection, raw-segment compatibility validation, provenance,
  and sanitized failure conversion; and
- worker framing, progress, cancellation, timeout, and cleanup details.

The production worker transport and an in-memory behavior adapter are the two
justified adapters at the internal engine seam. The authenticated HTTP route
and SDKs remain thin adapters over the projection; hosts do not become OCR
adapters. Refactoring must replace superseded planning/normalization paths and
their implementation-coupled tests. It must not layer a new pass-through
module while retaining the old policy in `extractors.py`, `ocr_main.py`, and
worker framing callers.

Because rasterization and inference cross a worker-process seam, the exact
interface must pass a Design It Twice checkpoint before implementation. At
least three substantially different interfaces are compared by depth,
locality, seam placement, failure readability, cancellation, and migration
cost. No interface is accepted merely because it resembles the current call
graph.

## Reopened Phase 1 active module: OCR compute plan

`OcrComputePlan` is the canonical runtime-owned deep decision module for both
readiness and execution. Its small external interface is one operation:
select from an optional operator override and return one immutable
`OcrComputeSelection`. Native inventory is an injected internal seam, with a
DXGI/D3D12/DirectML production adapter and an in-memory behavior adapter. A
host never supplies inventory, ranks adapters, or interprets names/indexes.

`OcrComputeSelection` contains three projections of the same decision:

- an internal `OcrExecutionPlan` consumed by the WindowsML session adapter;
- the existing public `OcrComputePreflightV2` readiness projection; and
- a private immutable `OcrSelectionDeviceProofV1` containing only facts known
  at selection time.

For GPU mode the internal plan carries the selected adapter's high-performance
preference rank, its ordinary DXGI/ORT `dmlDeviceId`, normalized device
identity, complete adapter-map digest, pinned ORT mapping-contract identifier,
selection source, and a canonical `planSha256`. These integers are different
mechanisms, not identity: neither enters the authenticated HTTP contract, an
SDK, a persisted host setting, or UI policy. The same immutable plan is passed
to session construction. The execution worker re-resolves the expected LUID
at that ordinary ordinal, passes only that ordinal as ORT `device_id`, and
rejects identity drift; it does not run selection again. Readiness and
inference therefore cannot independently choose devices.
The engine manager retains that exact `OcrExecutionPlan` after authenticated
worker preflight and passes it in the internal model-install/capture worker
request; neither request has an independent default device value.

The inventory adapter returns one authoritative snapshot whose per-adapter
assessment is the closed union `positive-usable`, `positive-unavailable`, or
`indeterminate`. An adapter is `positive-usable` only when the snapshot proves
all of the following without loading Paddle or model assets:

1. it is a non-software DXGI hardware adapter;
2. D3D12 architecture classification proves `dedicated` or `integrated`;
3. its DXGI LUID correlates unambiguously between one high-performance rank
   and one ordinary DXGI/ORT `dmlDeviceId`;
4. `DmlExecutionProvider` is registered; and
5. an adapter-scoped, non-model D3D12/DirectML capability probe succeeds.

An authoritative snapshot means both DXGI enumerations reached their normal
end-of-list, their non-software hardware LUID sets are identical and unique,
every hardware LUID maps bijectively to one rank and one ordinary ordinal, and
ORT provider discovery returned successfully. A `positive-unavailable`
assessment requires affirmative evidence: a software flag, an allowlisted
terminal unsupported result from a
completed adapter capability probe, or a successfully returned provider list
that omits `DmlExecutionProvider`. An empty authoritative hardware inventory
is also positive evidence that no GPU is present.

Timeout, exception, unknown UMA classification, inconclusive LUID/rank/ordinal
correlation, and unexpected probe status are `indeterminate`. They make the
adapter ineligible for selection but never count as proof that it is
unavailable. A native/provider exception that prevents a complete snapshot,
truncated enumeration, unequal hardware LUID sets, duplicate
rank/ordinal/LUID, or internally inconsistent record makes the whole snapshot
`structurally-invalid`. Neither indeterminate nor structurally-invalid evidence
may accumulate into CPU fallback.

### Canonical compute decision truth table

This is the only CPU/GPU selection policy. A `positive-usable` adapter is a
proven non-software dGPU or iGPU with a known class, unambiguous identity
mapping, registered `DmlExecutionProvider`, and a successful adapter capability
probe.

| Situation | Required evidence | Automatic result | CPU allowed? |
| --- | --- | --- | --- |
| Usable dGPU exists (a usable iGPU may also exist) | Complete `positive-usable` dGPU snapshot | Select the highest-priority usable dGPU and emit `gpu-dml` | No |
| No usable dGPU; usable iGPU exists | Complete `positive-usable` iGPU snapshot and every dGPU that could outrank it is positively unavailable or authoritatively absent | Select the highest-priority usable iGPU and emit `gpu-dml` | No |
| Every hardware candidate is `positive-unavailable`, or the authoritative inventory proves no hardware GPU exists | Complete snapshot plus affirmative software/unsupported evidence, or authoritative empty hardware inventory | Emit explicit `cpu-fallback` with `no_compatible_gpu` and the CPU notice | Yes |
| Hardware is proven, but the completed provider query positively proves `DmlExecutionProvider` is absent | Authoritative provider discovery with no DML provider | Emit explicit `cpu-fallback` with `dml_provider_unavailable` and the CPU notice | Yes |
| Inventory, provider discovery, adapter classification, or identity mapping is indeterminate or structurally invalid | Timeout/exception, unknown class, incomplete mapping/enumeration, failed global provider discovery, or inconsistent snapshot | Readiness unavailable; emit no compute plan and no CPU notice | No |
| A selected GPU plan later fails DML construction, identity validation, assignment, graph proof, or inference | Post-selection failure on the selected operation | Fail the capture, invalidate the plan, and require fresh readiness for a later operation | No; never retry another GPU or CPU for the failed operation |

Both `indeterminate` and `structurally-invalid` blocking outcomes use the
existing unavailable readiness path (`ocrCompute: null`/OCR requirement
unavailable); they do not invent a public reason code, CPU projection, or CPU
notice. API `2.0` remains unchanged.

Consequently, RTX 4060 `indeterminate` plus iGPU `positive-usable` is readiness
unavailable because the unresolved dGPU could outrank the iGPU. If both adapter
probes timeout or throw, readiness is unavailable and no CPU notice is emitted.
RTX 4060 `positive-unavailable` plus iGPU `positive-usable` selects the iGPU.
CPU is selected only for the two explicit CPU-allowed rows: every hardware
candidate is affirmatively unavailable/no hardware is authoritative, or the
completed provider query proves DML absent. A selected usable dGPU is not
blocked by an indeterminate lower-priority iGPU because that iGPU cannot change
the winner. A post-selection DML construction or inference failure is not a
new preflight decision and never authorizes CPU retry.

The default automatic priority is:

1. a usable non-software dedicated GPU;
2. otherwise a usable non-software integrated GPU, but only after every dGPU
   that could outrank it is positively unavailable or authoritatively absent;
3. otherwise explicit CPU fallback, but only for the table's two CPU-allowed
   rows: every hardware adapter is positively unavailable/no hardware is
   authoritative, or the completed provider query proves DML absent. In either
   case emit `userNoticeRequired: true` and
   `noticeCode: "ocr_cpu_fallback"`.

Within a class, the runtime sorts by ascending
`EnumAdapterByGpuPreference(HIGH_PERFORMANCE)` rank, then the lexicographic
unsigned tuple `(vendorId, deviceId, subsystemId, revision, adapterLuid)`.
Neither a display name nor a caller-provided numeric index defines the default.
On this acceptance machine, the no-override result must be the usable
dedicated NVIDIA GeForce RTX 4060 rather than the integrated GPU, independent
of legacy `EnumAdapters1` order.

#### Official ordinal and LUID contract

The production snapshot must treat the two enumeration indices as distinct:

- `highPerformanceRank` is the index supplied to
  `IDXGIFactory6::EnumAdapterByGpuPreference` with
  `DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE`. Microsoft documents that this call
  *reorders* `EnumAdapters1` and that its indices follow the requested
  preference; it does not document those indices as ordinary adapter ordinals
  ([Microsoft DXGI contract](https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_6/nf-dxgi1_6-idxgifactory6-enumadapterbygpupreference)).
- `dmlDeviceId` is the selected adapter's index in the ordinary
  `IDXGIFactory1::EnumAdapters1` order. ONNX Runtime documents numeric DML
  `device_id` as the `IDXGIFactory::EnumAdapters` adapter index, and Windows
  documents that `EnumAdapters` and `EnumAdapters1` enumerate identically on
  Windows 8 and later
  ([ORT DirectML contract](https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html#ortsessionoptionsappendexecutionprovider_dml-function),
  [Microsoft factory contract](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nf-dxgi-createdxgifactory1)).
  The pinned ORT 1.24.4 implementation resolves the number with
  `EnumAdapters1(device_id)` and passes that returned adapter to
  `D3D12CreateDevice`
  ([ORT 1.24.4 source](https://github.com/microsoft/onnxruntime/blob/v1.24.4/onnxruntime/core/providers/dml/dml_provider_factory.cc#L461-L524)).

The inventory adapter therefore creates one fresh DXGI factory, queries its
`IDXGIFactory6` interface, exhaustively records both
`highPerformanceRank -> AdapterLuid` and
`EnumAdapters1 ordinal -> AdapterLuid`, and joins the tables only by exact
LUID. It never copies a high-performance rank into ORT `device_id` and never
assumes the two numbers are equal. A missing, extra, duplicate, or changing
hardware LUID makes the snapshot structurally invalid. RFC 8785 canonical JSON
of both complete joined tables, including class and PCI identity but excluding
the observational label, is `adapterMapSha256`. This is a run-scoped join:
Microsoft defines `DXGI_ADAPTER_DESC1.AdapterLuid` as the value that identifies
the adapter and `ID3D12Device::GetAdapterLuid` as a robust cross-API mapping key
whose uniqueness lasts only until system restart
([Microsoft DXGI identity contract](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/ns-dxgi-dxgi_adapter_desc1),
[Microsoft D3D12 LUID contract](https://learn.microsoft.com/en-us/windows/win32/api/d3d12/nf-d3d12-id3d12device-getadapterluid)).

The preflight factory must return `IsCurrent() == TRUE` after both tables are
complete. The later execution worker creates a fresh factory, recomputes both
complete tables, and requires the same `adapterMapSha256`; it then holds that
factory across the owned synchronous Paddle pipeline-factory invocation that
constructs all OCR ORT sessions. Immediately before the invocation it must be
current and resolve `EnumAdapters1(dmlDeviceId)` to the planned LUID.
Immediately after the invocation returns it must still be current, the
complete map digest must remain unchanged, and the same ordinary ordinal must
resolve to the same LUID. Every ORT session must already be discoverable from
that returned pipeline; lazy or otherwise unobservable session construction is
terminal. Microsoft defines `FALSE` as a signal to recreate the factory and
re-enumerate
([Microsoft factory-currency contract](https://learn.microsoft.com/en-us/windows/win32/api/dxgi/nf-dxgi-idxgifactory1-iscurrent)).
Any false result or exception here invalidates the retained plan and fails the
current operation closed; it does not rebuild a different plan inside that
operation.

Every created session must then return a present
`get_provider_options()["DmlExecutionProvider"]["device_id"]` whose canonical
base-10 integer value equals the planned `dmlDeviceId`
([ORT Python interface](https://onnxruntime.ai/docs/api/python/api_summary.html#onnxruntime.InferenceSession.get_provider_options)).
The owned adapter must successfully call that same session's
[`disable_fallback()`](https://onnxruntime.ai/docs/api/python/api_summary.html#onnxruntime.InferenceSession.disable_fallback)
before its first prediction; a missing method or exception is terminal. After
real prediction, that session must have positive DML node
evidence from its graph-assignment record or owned ORT profile. The complete/
current pre- and post-construction LUID maps, ORT's documented numeric-device
contract, the session-reported option, successful fallback disablement, and
post-run DML evidence together form the actual-device proof. A rank, display
name, provider-list entry, pre-creation map alone, or positive node count from
another session cannot substitute for any link. If Paddle does not expose a
supported way to inspect every synchronously constructed session's provider
configuration and disable implicit fallback, the gate fails closed.

The private mapping contract is
`ort-directml-1.24.4-enumadapters1-v1`. Worker preflight must observe exact ORT
version `1.24.4`; `workerSha256` binds the packaged bytes. Any version/build
change is indeterminate until its official numeric-device implementation is
reviewed and a new mapping-contract identifier is accepted. It cannot reuse
this proof by compatible-version assumption.

At design commit `6ea3e1039d2d1f41229dce1636e3280fea9dcf80`, the current
call graph does not prove this contract. `config.py` supplies default ordinal
`0`; `dependencies.py` sends that number through `EngineInstallationManager`
and `WorkerClient` to worker preflight; `StandaloneRuntimeCaptureExtractor`
separately reads the setting and sends another `deviceId` in the capture
request. Worker preflight's `OcrGpuAdapter` retains only ordinary index and
class, while its public result retains only class/mode. During inference,
`workers/ocr_main.py` builds `WindowsMLOcrAdapter` from that separate capture
number, `OcrProfile.paddle_kwargs` forwards only numeric `device_id`, and
`_PaddleOcrExecutionEvidenceAdapter` checks provider names plus post-prediction
graph/profile node counts. No retained value joins preference rank, ordinary
ordinal, and LUID or brackets pipeline construction with the planned map. Its
existing pipeline-owned per-session fallback disablement preserves the failure
rule but cannot prove the selected device. Existing readiness, profile, and LAW
evidence therefore cannot satisfy `P1-GPU-SELECTION-PROOF`; the minimal
compute-selection/proof slice must replace the duplicate numeric flows with the
retained plan before the installed Capture Workbench gate can run.

The historic `CAPTURE_WINDOWSML_DEVICE_ID` operator override is retired. Its
presence is rejected; there is no implicit value of `0` and no compatibility
ordinal path. Worker preflight accepts an empty options object only. The
runtime-owned automatic selection produces the immutable plan, and a CPU
fallback is carried explicitly as a CPU plan. A host, SDK, or UI must not
derive or persist `dmlDeviceId`.

`DmlExecutionProvider` absence permits CPU fallback only after the hardware
inventory and provider query have completed authoritatively and positively
prove that no adapter is usable for DML. CPU fallback contains no GPU identity
and always projects
`userNoticeRequired: true` plus `noticeCode: "ocr_cpu_fallback"` before import.
The UI renders that existing decision; it does not probe the machine or choose
a device itself.

### Private device identity and execution proof

`OcrSelectedDeviceIdentityV1` is a canonical, privacy-safe value containing:

- `adapterClass`;
- the run-scoped DXGI adapter LUID as exactly 16 lowercase hexadecimal digits;
- PCI `vendorId` and `deviceId` as 4, `subsystemId` as 8, and `revision` as 2
  lowercase hexadecimal digits without `0x`; and
- a control-character-free, bounded DXGI description used only as an
  observational label, never as a selector.

The description is read only from `DXGI_ADAPTER_DESC1.Description`, normalized
to NFKC, trimmed, ASCII-whitespace-collapsed, and capped at 128 Unicode code
points. `identitySha256` is the SHA-256 of UTF-8 RFC 8785 canonical JSON for the
preceding fields. `planSha256` applies the same encoding to the immutable
selection value
`{policyVersion: "1", mode, selectionSource, identitySha256,
highPerformanceRank, dmlDeviceId, adapterMapSha256,
ortMappingContract: "ort-directml-1.24.4-enumadapters1-v1", workerSha256,
contractSetSha256}`; CPU mode uses `null` identity, rank, device ID, and map
digest while retaining the mapping-contract identifier.
`OcrSelectionDeviceProofV1` is the normalized identity, this value, and
`planSha256`. Its raw identity must reproduce `identitySha256`. It contains no
post-session fact.

After every Paddle-owned DML session has successfully produced its assignment
evidence, the WindowsML session adapter returns a separate immutable
`OcrExecutionDeviceProofV1`. It contains the selection proof plus
the pipeline-construction bracket, an ordered `sessionDeviceProofs` value,
`sourceSha256`, requested page scope, aggregate DML-assigned node count, and
exact runtime/worker/model/profile/contract hashes. The bracket contains its
pre- and post-construction mapped adapter LUIDs, `adapterMapSha256` values, and
factory-currency results. Each session proof contains its run-local session
index, provider order, session-reported `dmlDeviceId`,
`fallbackDisabled: true`, DML node count, and graph/profile evidence source.
`executionSha256` is the SHA-256 of RFC 8785 canonical JSON for all those
receipt fields except itself. A receipt is valid only when `planSha256`,
`identitySha256`, preference rank, `dmlDeviceId`, worker hash, and contract hash
match the retained plan; every session reports the planned `dmlDeviceId` and
was synchronously returned from the one bracketed construction; that bracket
maps the ID to the selected LUID before and after construction with a current
factory; both bracket map digests equal the plan's `adapterMapSha256`; every
session proves fallback was disabled before prediction and has a positive DML
node count; provider order is
exactly `["DmlExecutionProvider", "CPUExecutionProvider"]` in every session;
and the aggregate count equals the sum of the session counts. Selection remains
immutable; no caller appends execution facts to it.

The preflight selection proof and each real OCR execution receipt must carry
the same identity and plan digest. The RTX 4060 machine oracle requires
`dedicated`, NVIDIA vendor `10de`, the bounded description identifying RTX
4060, and identical LUID/PCI identity across plan, session configuration, and
execution receipt. The label alone and `windowsml-dml` provenance alone are
insufficient.

### Private installed-evidence seam

The OCR worker returns `OcrExecutionDeviceProofV1` only through its existing
owned length-framed stdio result. `WorkerClient` accepts it only from the
catalog-hash-validated worker process, validates the private schema and both
digests, and associates it with that capture. It is never sent over HTTP/SSE,
written to a product log, or exposed to an SDK/UI.

`OcrExecutionEvidenceSink` is an injected internal seam in the core runtime
with one operation, `record(captureId, sourceRole, proof)`. The in-memory
adapter supports behavior tests. The installed-acceptance adapter is enabled
only by the acceptance build and receives the already-owned run artifact root
at process construction; it rejects any root outside
`output/playwright/capture-workbench/<run-id>`, writes one atomic
`ocr-device-proof-v1.json` after proof validation, and returns only its
relative artifact name and SHA-256. Ordinary product construction has no file
adapter and keeps the validated receipt ephemeral with the runtime job. The
sink uses `captureId` only for in-process correlation and never serializes it.

For host-structured captures, the runtime publishes the validated private
execution receipt at the OCR checkpoint: raw and OCR projection persistence and
the `awaiting_structuring` transition must already have succeeded. This is an
OCR execution-proof terminal only; it does not mean that host structuring or
release succeeded, and it does not wait for the host candidate commit. Failed
or malformed OCR, either persistence/transition failure, or cancel/delete
before that checkpoint emits no proof; cancel/delete afterward cannot emit a
duplicate. Host commit persistence remains a separate host-owned behavior.

The installed harness reads that file only when it finalizes a successful
terminal acceptance run, validates it independently, includes the existing
relative artifact entry/digest in acceptance manifest schema `2`, closes the
proof file before manifest finalization, and never copies it into app data or
the library. Retention/deletion follows the scoped run-artifact lifecycle.
Worker/core authenticity comes from owned stdio plus exact worker hash;
harness/core locality comes from the pre-authorized run root, not a public endpoint or
bearer token. The artifact contains no bearer token, OCR/truth text, user name,
machine name, absolute/local path, raw environment, or arbitrary diagnostics.
Device fields are not copied into the manifest summary or public capture
document.

This slice deliberately leaves API `2.0`, `OcrComputePreflightV2` schema `1`,
and `CaptureOcrProjectionV3` schema `3` byte-compatible. Therefore generated
runtime schemas and the TypeScript/Python/Java SDK contract set must remain
byte-identical and `contractSetSha256` must remain
`d293a3de26114f1b4fd65ea6d6d3f157fa2f93109b31e1e30d5d15ef0dfdeb40`.
Adding a public device field later would be a separate contract change
requiring schema/SDK regeneration and a new contract-set hash. Implementation
will change source, runtime, OCR worker, candidate, and private device-proof
artifact hashes; the fresh installed evidence must bind those new hashes to
the unchanged contract hash. If the acceptance manifest sanitizer gains a
relative proof reference, its repo-local tests must change, but that is not
runtime contract generation.
The new private device-proof schema/validator and its fixtures change only
acceptance tooling; they are not inputs to `contractSetSha256`.

## Deferred Phase 2 deep module 3: native owned runtime session

`OwnedRuntimeSession` remains the only native process-tree ownership module.
One instance owns one launch attempt from suspended root creation through
terminal cleanup proof. Its small semantic interface must hide Windows Job
creation, handle retention, process identity checks, retry cleanup, descendant
enumeration, and OS error translation.

The Phase 2 interface design concentrates three caller intents: launch an
attempt, observe a terminal root event, and finish with an idempotent
`RuntimeTerminationProof`. `OwnedSidecarProcess`, raw Job handles, taskkill
details, and assignment flags remain implementation details. The launcher
owns retry sequencing; the desktop owns product status, but neither duplicates
native cleanup policy or holds a parallel process tree.

Every root is created suspended, assigned to a fresh no-breakaway Job, verified
before resume, and monitored for unexpected exit. Window close, normal app
exit, readiness failure, root crash, and host termination converge on the same
finish path. A failed proof retains the exact ownership identity for retry and
never reports clean. Pre-existing external processes remain alive; cleanup is
identity-scoped and never based on a broad process name.

Next-start reconciliation may remove stale run-scoped state only after identity
checks. Durable installed runtime/model assets remain. OS crash and power loss
do not promise an immediate callback.

## Deferred Phase 2 performance evidence

Performance evidence is an internal, privacy-safe measurement module, not a new
runtime interface. It records only bounded numeric and identity data:

- cold predictor initialization time;
- rasterization time and raster dimensions per requested page;
- inference time per page and total elapsed time;
- time to first completed page;
- peak worker process/Job memory and post-close cleanup result; and
- compute mode, adapter class, runtime/worker/profile/model/contract hashes.

It never records OCR text, truth text, bearer tokens, local paths, or arbitrary
diagnostics. Measurement uses the existing real private JPEG and PDF page 1 for
fast iteration. A full document is processed only when the optimization can
plausibly affect whole-document memory, ordering, or accumulated latency.
Paddle-enabled measurements remain sequential and release model memory before
another app starts.

The first performance slice establishes a reproducible baseline without
changing production behavior. Every later optimization slice declares its
metric, comparison method, and acceptable noise before coding, then proves OCR
semantics, provenance, and cleanup did not regress. Aggregate averages cannot
hide a failed fixture or missing critical anchor.

## Reopened Phase 1 TDD seam and deferred slice order

The confirmed behavior seams are:

1. runtime capture plus `CaptureOcrProjectionV3` through the canonical OCR
   module;
2. `OcrComputePlan` plus authenticated readiness and the actual engine plan;
3. native `OwnedRuntimeSession` terminal proof; and
4. the installed Capture Workbench public journey, including application close.

Tests use public behavior at these seams. Mocks are limited to native
capability snapshots and other external registry/network/time seams. Internal
Paddle collaborators, private methods, and call counts are not test surfaces.
For the reopened Phase 1 blocker, only seams 2 and 4 are executable, and seam 4
is limited to compute-selection proof in the two ordered installed journeys.
Seams 1 and 3 remain deferred Phase 2 work.

Compute-plan behavior tests cover, at minimum:

- usable dGPU plus usable iGPU selects dGPU regardless of enumeration order;
- positive-usable dGPU plus indeterminate lower-priority iGPU selects the dGPU;
- an earlier-ranked indeterminate dGPU plus a later-ranked positive-usable dGPU
  is readiness-unavailable because the same-class winner is unresolved;
- positively unavailable/absent dGPU plus positive-usable iGPU selects iGPU;
- indeterminate dGPU plus positive-usable iGPU is readiness-unavailable;
- two timeout/exception adapter assessments are readiness-unavailable and emit
  no CPU projection or CPU notice;
- an authoritative empty inventory, software-only inventory, successful global
  DML absence, or all-positive-unavailable hardware selects noticed CPU;
- unknown classification, inconclusive mapping, unexpected status, timeout,
  or exception is never asserted as positive-unavailable;
- total inventory failure or a structurally invalid snapshot is readiness-
  unavailable, not CPU; identity drift after selection is terminal;
- absent override uses automatic policy, while a valid explicit override uses
  exactly its normalized usable identity;
- negative, out-of-range, software, unknown, ambiguous, or unusable override
  is unavailable and never silently re-enters automatic policy;
- differing high-performance and ordinary enumeration positions join by exact
  LUID and pass the ordinary `EnumAdapters1` ordinal, not the preference rank,
  as ORT `device_id`; unequal/duplicate LUID sets fail the snapshot closed;
- factory `IsCurrent` false, pre/post pipeline-construction ordinary-ordinal
  LUID drift, a lazy/unobservable session, an absent or mismatched per-session
  reported `device_id`, missing/failed fallback disablement, and any
  unobservable proof link fail closed;
- automatic RTX 4060 identity and plan digest reach both readiness proof and
  the session, while name/index changes cannot steer selection;
- DML construction, a session with zero assigned DML nodes, and inference
  failure after selection fail the capture, invalidate the plan, and never
  attempt another GPU or CPU-only pipeline for that operation;
- a valid post-execution receipt has a positive DML node count and exact
  provider order, binds every execution field in `executionSha256`, reaches the
  private installed-evidence sink, and is rejected for a swapped plan/source,
  changed field, path-bearing field, invalid run root, or failed atomic write.

The reopened Phase 1 work runs in this order:

1. implement only compute-plan priority plus readiness/execution identity and
   its private proof seam;
2. run installed Capture Workbench first: canonical JPEG, then original PDF
   page 1, both on the automatic RTX 4060 plan; then close and release model
   memory; and
3. bind the proof and reviews to the exact bounded commit.

No Phase 2 slice and no Cert/LAW model process may start before step 3 passes.
After the gate, consumer validation may proceed Cert then LAW. Separately, the
deferred Phase 2 sequence is canonical OCR Design It Twice and replace-not-layer
deepening, baseline/performance optimization, owned-session deepening and
reconciliation, contract regeneration only if an accepted public interface
requires it, and finally candidate/release/published-byte gates.

Each slice starts in a fresh worker context, uses red-green vertical tests,
runs focused checks before `--skip-nx-cache` gates, commits immediately, and
invalidates earlier HEAD-bound approvals.

## Reopened Phase 1 acceptance and rollback

`P1-GPU-SELECTION-PROOF` requires all of the following:

- the installed Capture Workbench runs first and, sequentially in the same
  model-enabled lane, the canonical JPEG then the original PDF page 1 return
  semantic anchor evidence with `windowsml-dml`;
- both sources bind the automatic plan and execution receipt to this machine's
  dedicated RTX 4060; class-only readiness or prior LAW integrated-GPU
  evidence cannot satisfy this proof;
- automatic compute selection proves dGPU before iGPU and iGPU before CPU;
- CPU fallback is explicit only for the two canonical CPU-allowed rows:
  authoritative positive evidence proves no usable dGPU/iGPU-DML plan exists,
  or the completed provider query proves `DmlExecutionProvider` absent;
- DML initialization or inference failure has no CPU retry;
- projection ordering, page scope, boxes, confidence, provenance, and typed
  failures remain contract-compatible;
- installed-app close releases model memory and proves the two ordered runs do
  not overlap a later consumer model process; and
- the private device receipt is privacy-safe and bound to exact runtime,
  worker, model, profile, contract, source/page, and compute-plan identities.

Only after that exact Capture Workbench RTX 4060 sequence and cleanup pass may
Cert Prep run, and only after Cert cleanup may GX Law Prep run. Prior LAW iGPU
evidence is historical and cannot unlock or substitute for this gate. Consumers
do not add or override producer selection policy. This checkpoint authorizes
no consumer edit, candidate assembly, release, or publication.

Deferred Phase 2 acceptance separately owns injected startup/root/host cleanup
proof, `OwnedRuntimeSession`/reconciliation behavior, reproducible performance
evidence, candidate construction, release, and published-byte validation. None
may be scheduled into the reopened Phase 1 slice.

Rollback is additive. Revert the focused reopened Phase 1 slice and its
generated artifacts to the immediately preceding reviewed commit. Do not
rewrite historical Phase 1 evidence, mix 0.4.1/0.4.2 identities, restore
embedded-text extraction, or use a host-private OCR path as fallback.
