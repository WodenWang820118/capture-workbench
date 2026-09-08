# Staged OCR Delivery Workflow

This is the canonical development guide for the Capture Runtime 0.4.2 OCR-only
delivery and its three consumers. Product specifications remain the source of
truth for contract details; this guide defines how work is proposed, built,
reviewed, verified, committed, and promoted.

## Outcome and non-negotiable product choices

The first outcome is observable, real PaddleOCR execution in all three installed
apps. Every PDF page and image is rasterized and sent through PaddleOCR. An
embedded text layer is not an alternate route, and an LLM does not choose an
OCR route or score OCR accuracy. Born-digital PDFs may therefore produce less
useful output; that is an accepted product trade-off.

The second outcome is a hardened release: a canonical OCR module, a native
owned-runtime-session module, measurable performance, safe process ownership,
complete contracts and SDKs, and reproducible release artifacts. Do not claim
the second outcome merely because the first outcome works.

### Current checkpoint (2026-08-31)

This session is a Phase 1 implementation session. Phase 2 specifications,
decisions, and TODOs remain intentionally stored in this repository so a fresh
worker can resume from an explicit design, but no Phase 2 implementation is
authorized in this session.

The ordered Phase 1 gate is not closed yet:

- Capture Workbench is the producer proving ground and is still resolving a CDP
  target-loss harness issue before its minimum installed-app recheck.
- Cert Prep has one successful real OCR acceptance, but requires the minimum
  producer-change recheck before its evidence is current.
- GX Law Prep has its source integration commits, but its real installed OCR
  acceptance is still pending.

These are status facts for coordination, not acceptance evidence. The complete
gate remains Capture Workbench, then Cert Prep, then GX Law Prep, with a single
OCR owner at a time and cleanup proven before the next model-enabled run.

The following constraints apply to every slice:

- Runtime jobs are ephemeral. A host owns durable source and domain records.
- A host does not create its own Paddle model, preprocessing policy, inference
  loop, OCR merge policy, or process-cleanup policy.
- No bearer token, raw OCR text, private fixture text, local path, or model
  secret is written to logs, screenshots, manifests, or commits.
- Durable model/runtime caches may remain. Run-scoped data, staging, backups,
  listeners, and owned processes must be reconciled by the relevant hardening
  gate.

## The delivery loop: proof before code

Every non-trivial slice follows this order. A worker may not skip directly to
implementation because the requested change sounds familiar.

1. **Frame the objective and proof.** State the user-visible outcome, the
   non-goals, the evidence that will prove it, and the evidence that would
   disprove it. Record risky assumptions and the rollback target.
2. **Write the technical design.** Before coding, update or create the local
   `SPEC`, `DECISION`, and `TODO` artifacts under `.agents/`. The design names
   interfaces, invariants, ordering, error modes, persistence ownership,
   performance expectations, and test seams. This stage contains no feature
   code.
3. **Run a serious pre-implementation review.** Review the design for
   requirements, failure modes, consumer compatibility, privacy, and rollback.
   Use `grill-me` one question or one finding at a time. Resolve blockers in
   the design before implementation begins.
4. **Create a vertical backlog slice.** A slice has one observable outcome, its
   red tests, implementation scope, verification commands, evidence output,
   and a clear owner. Order slices by risk and by the dependency order below.
5. **Implement with TDD.** Write a failing test at the public interface, make
   the smallest change that turns it green, then refactor without changing the
   observable contract. Tests cross the same seam that production callers use.
6. **Verify and review.** Run the smallest focused checks first, then the
   repository gate appropriate to the slice. Obtain both review axes below.
   Any new commit invalidates a previous HEAD-bound approval.
7. **Commit the closed slice immediately.** A green slice is not complete while
   it is sitting in an unbounded worktree. Stage only explicit paths, inspect
   the cached diff and secret/path audit, and commit with a focused message.
   Generated artifacts belong in the same slice when they are part of its
   interface. The next slice starts from that commit.

The worktree is shared by workers, so first identify ownership of existing
changes. Never use a broad add, reset, checkout, or cleanup to make a status
look tidy. An unrelated dirty file stays untouched and is reported.

## Two delivery phases

### Phase 1 — minimum real PaddleOCR viability

Phase 1 is deliberately narrow. It proves that the runtime and each app can
perform the same OCR-only journey with real model assets and produce a usable,
truthful projection.

- Stabilize the capture → OCR projection journey and its contract. Preserve
  page order and page completeness, raster dimensions, text, boxes,
  confidence, provenance, and typed failure evidence.
- Exercise the installed apps separately and in this strict order:
  **Capture Workbench app → Cert Prep → GX Law Prep**. Capture Workbench is the
  producer/runtime proving ground; Cert Prep is the next consumer; GX Law Prep
  is the most complex consumer and goes last.
- Run model-enabled acceptance sequentially. Start the next app only after the
  prior app has stopped, its owned runtime/model listeners and processes have
  been proven absent, its run-scoped residue has been reconciled, and model
  memory has been released. Do not parallelize PaddleOCR to save wall-clock
  time.
- Use real private JPEG and PDF fixtures for real checks; the efficient Phase 1
  scope is one JPEG and PDF page 1. A PDF's embedded text layer may exist, but
  it is ignored and must never affect the OCR result or cause the input to be
  rejected. A fake OCR adapter, a snapshot update, a package smoke test, or a
  successful exit code is not Phase 1 proof. Full-document OCR is reserved for
  a slice whose risk actually concerns page accumulation, ordering, or memory.
- Record candidate identity, model/profile provenance, contract identity,
  OCR quality metrics and cleanup flags without recording raw sensitive text.
- The canonical local-package acceptance may opt in explicitly with
  `CAPTURE_PDF_OCR_E2E_LOCAL_MODEL_OPT_IN=1` and its private model root; it
  must bind to the approved candidate/catalog and scrub those variables from
  online, release, and published runners. Ambient model overrides remain
  disallowed outside that local opt-in.

Phase 1 can be accepted only per app and then as a complete ordered chain. A
known deferred hardening item is recorded explicitly; it is not silently
treated as complete. If Capture Workbench fails, Cert Prep and GX Law Prep do
not start.

### Phase 2 — hardening and optimization

Phase 2 follows only after Phase 1 has a reproducible candidate. It improves
the design and operational safety without changing the accepted OCR-only
product choice.

- Deepen one canonical OCR module. Its small interface owns rasterization,
  Paddle profile selection, serialized inference, normalization, page
  completeness, confidence and box semantics, provenance, and typed failures.
  Hosts use an adapter at the seam; they do not reimplement policy.
- Deepen the native `OwnedRuntimeSession` module. It owns process trees,
  Windows Job assignment/verification, suspended-root startup, crash
  observation, termination, and proof of cleanup without exposing raw OS
  handles to hosts.
- Measure memory, latency, serialized inference, raster cost, and model
  initialization with the real model. Optimize only against recorded evidence.
  GPU selection follows the sole canonical truth table in
  `.agents/SPECS/capture-runtime-042-p2-hardening.md`: usable dGPU, then usable
  iGPU, then noticed CPU only after authoritative positive-unavailable or
  provider-absent evidence. Indeterminate evidence yields unavailable
  readiness; post-selection DML failure is fail-closed and never retries CPU.
- Make every app close its owned background tree. Preserve pre-existing
  external processes, including a baseline model process, and reconcile stale
  state safely on the next start. Never kill by broad process name.
- Complete contract/schema/SDK generation, packaging, installer provenance,
  privacy-safe evidence, clean-install checks, and release/rollback gates.

Phase 2 starts with the version-upgrade pain observed during the 0.4.2 work:
first establish one canonical version inventory and a generated next-version
upgrade/check command, then add stale-version CI. The remaining deferred slices
are deterministic staging isolation, one canonical acceptance runner,
`ModelSourceSnapshot`, the deep `OwnedRuntimeSession` lifecycle/reconciliation
module, and evidence-led performance/GPU policy hardening. The local package
E2E identity policy remains tiered: URL and port identify transport, while
contract, package boundary, provenance, and loaded executable identity remain
required; release/published checks retain the strict immutable-byte policy.

The deletion test applies to every proposed module: if deleting it merely
reveals the same logic in each caller, it was a pass-through. If deleting it
would make the OCR or lifecycle policy reappear in many callers, the deep
module is earning its keep.

## Module, interface, seam, and adapter rules

Use the codebase-design vocabulary consistently:

- A **module** presents one **interface** containing types plus invariants,
  ordering, error modes, required configuration, and performance behavior.
- Put the **seam** where behavior needs to vary or be substituted. The
  interface is the production and test surface; tests should not reach past it.
- An **adapter** satisfies a seam. Add an adapter only when there are two real
  implementations, normally production and test. One adapter is a hypothetical
  seam and usually adds indirection without leverage.
- Prefer a deep module: a small interface hides substantial policy, giving
  callers leverage and maintainers locality. Keep test-only seams internal.
- Accept dependencies through the interface or an internal seam; do not create
  model/process/network dependencies invisibly inside callers.

For Phase 2 refactors, replace tests for deleted shallow modules with tests at
the deep module's interface. Do not keep a second test surface just because it
is easier to assert internal state.

## Review protocol

Every design and implementation has two independent review axes:

1. **Standards review:** repository conventions, security/privacy, lint/type
   safety, test quality, generated-file discipline, commit scope, and required
   CI commands.
2. **Specification review:** product requirements, contract compatibility,
   ordering, partial/failed output, provenance, process ownership, evidence
   truthfulness, and rollback.

Reviewers must report concrete evidence and blockers, not approval by intuition.
Use `grill-me` to challenge one finding at a time until the worker can state the
counterexample, fix, and regression proof. Review approval is bound to the
exact commit SHA and scope it inspected. Any subsequent commit, generated
artifact change, or rebase requires both axes to be rerun; an old approval is
not transferable.

Root coordinates work, selects reviewers, audits evidence, asks the challenge
questions, and gives recommendations. Root does not directly edit files or
publish artifacts. Luna workers implement, test, commit their owned slices,
and provide concise public evidence. Human approval remains required before
merge or release promotion.

## Evidence tiers and release identity

Label evidence honestly:

- **Fast/local:** focused unit, contract, lint, typecheck, integration, and
  package checks. This proves code-level behavior but not real model accuracy or
  a fresh installation.
- **Local-real:** freshly built/installed app, real Paddle model, scanned
  corpus, semantic OCR assertions, privacy-safe screenshots/manifests, and
  process/listener cleanup proof. Run one project at a time in the required
  order.
- **Published:** the exact candidate bytes are published, downloaded again,
  identity/hash checked, installed in each consumer, and verified by the
  relevant CI and real acceptance gates.

## Identity policy by evidence tier

Identity checks are tier-specific so a local probe cannot masquerade as a
published release. Phase 1 local-package E2E evidence must be labeled
`local-probe` and hard-gates all of the following:

- API `2.0`, schema `3`, and the exact contract hash;
- the packaged archive boundary, with no sibling junction and no source-tree
  import or other local substitution; and
- the loaded runtime executable SHA and loaded OCR worker SHA matching the
  values reported by the local probe.

The local-probe record also captures package semver, the full all-asset byte and
size inventory, the app/desktop hash after a legitimate rebuild, local
`direct_url` metadata, and registry/frozen-lock purity. None of those recorded
facts is a sole Phase 1 hard-fail condition. A source change invalidates
evidence for its affected component; it does not automatically invalidate
unrelated component evidence. Once the same bytes have been hashed, SHA
equality is the identity check and a redundant local byte-by-byte comparison is
not required. These allowances never relax the fake-green protections: fake
OCR, snapshots, successful exit codes, source-tree imports, or archive-boundary
substitution cannot prove real PaddleOCR.

Release and published acceptance restore the strict identity policy: exact
version, every artifact hash and manifest entry, frozen locks, and download-back
byte identity must match, while local paths and `direct_url` metadata are
rejected. The full asset byte/size inventory, legitimate app/desktop rebuild
hashes, registry purity, and all published identities are then release gates.

Every candidate and release records immutable identities: repository HEAD,
artifact hashes, runtime/contract identity, model/profile identity, and a
sanitized manifest. Manifests contain hashes, CER/anchor counts, provenance,
and cleanup flags only. They do not contain raw OCR/truth text, tokens, or
machine-specific paths.

The producer creates a candidate without moving the stable pointer. Consumers
verify that candidate bytes before any publish. The producer then publishes the
same bytes; consumers pin the published 0.4.2 artifacts and regenerate frozen
locks. A stable index moves only after all published-artifact acceptance gates
are green.

## PR, CI, and rollback discipline

Each repository gets its own focused commits and its own PR. A PR names the
exact HEAD, candidate/artifact hashes, evidence tier, deferred gates, and
rollback plan. CI must run against the reviewed SHA; monitor the new SHA until
the required checks are completed successfully. Do not use another repository's
green result as a substitute for the local PR's checks.

If a Phase 1 or Phase 2 gate fails, stop the ordered promotion, preserve the
failure evidence, and fix the owning slice. If recovery is required, restore
the last known-good 0.4.1 pins/assets/locks consistently in all consumers. Do
not mix 0.4.1 and 0.4.2 dependencies, use removed private OCR as a fallback,
or mark a public immutable artifact stable after a failed consumer gate.

## Definition of done for a slice

A slice is closed only when all of the following are true:

- Its design/decision/task artifacts state scope, acceptance, and rollback.
- Red tests cover the public interface and the relevant failure case.
- Focused verification and the required repository gate are green.
- Standards and specification reviews have passed for the exact HEAD.
- Evidence is labeled with the correct tier and contains no sensitive data.
- Explicit paths are staged after a cached diff/secret/path audit.
- The focused commit SHA is recorded for the next slice and eventual PR.

This definition keeps the work agile: small, independently reviewable increments
can move forward while the larger hardening and release gates remain visibly
deferred instead of being hidden in a large unreviewable worktree.

## Sol xhigh escalation

Escalation is tied to a specific blocking condition, not to general slowness.
When the same condition causes more than three consecutive Luna implementation
failures, the Luna worker reports every attempt, command/result, and relevant
evidence to Root. Root may then activate a standby Sol xhigh worker for
read-only diagnosis, options, and proposed tests. Sol xhigh never edits,
commits, pushes, publishes, or takes ownership of the slice. The original Luna
remains the implementer and applies any accepted fix. Different findings or
blocking conditions have separate counters and must not be combined to trigger
an escalation.
