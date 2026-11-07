# Historical evidence and Git history

The 2026-09-15 local history cleanup moved 135 generated compressed coverage
archives (1,142,997,942 bytes) out of Git. Reports, manifests, regression inputs,
source, vendored dependencies and the pinned application corpus remain tracked.
Normal builds and maintained tests do not read the removed compressed archives.
Required JSON oracle inputs remain in their original locations.

## Artifact lookup

[The archive manifest](../coverage/semantics/artifact-archives.json) records each
original repository-relative path, byte length and SHA-256. On this workspace,
those paths are mirrored beneath `../php-spec-evidence-archive/`; its
`manifest.json` duplicates this inventory. For example, the archived arrow review
is `../php-spec-evidence-archive/coverage/semantics/arrows-review-originals.tar.xz`.
These files are local external evidence, not files supplied by a fresh Git clone.
Copy that directory separately when transferring the full research evidence.

COMP188 Closure-default originals, callback-family failures and focused checks
are retained uncompressed under `../php-spec-evidence-archive/comp188/`.
The [review](../coverage/semantics/deprecated-closure-default-review.json) binds
the preserved source cuts, interrupted-campaign extraction, affected corrections
and strict-state results. Raw artifacts retain exact source paths/cwd and process
records; they are evidence, not build/runtime inputs.

COMP189 same-scope bound-default originals and its single validated binder/cache
budget front remain under `../php-spec-evidence-archive/comp189/`.
The [review](../coverage/semantics/deprecated-bound-closure-default-review.json)
records source/state cuts and preserves fixture/entry-diagnostic failures with
zero acceptance credit; the promoted COMP188 native original retains its exact path.

COMP190 private/mixed cache originals, pending-handle/quiet lifetime checks and
same/different-owner receive histories are under `../php-spec-evidence-archive/comp190/`.
The [review](../coverage/semantics/deprecated-private-closure-default-review.json)
records authentic promotions and complete-row recovery, without renewing old
campaigns; incorrect boundary expectations and initial strict failures remain separate.

COMP191 ordinary nongenerator `Closure::call` default originals and exact
invocation-cache/free-front checks are under `../php-spec-evidence-archive/comp191/`.
The [review](../coverage/semantics/deprecated-closure-call-default-review.json)
keeps source comparisons separate from reached-state checks and preserves the
initial read refusal and DSL/diagnostic failures with zero acceptance credit.

GC61's generic TEMP pop-law originals and quiet-protocol control are under
`../php-spec-evidence-archive/gc61-temp-consumption/author/`.
Independent originals, actual pre-fix Some/Extra states and the sole fixed
receipt/decrement/budget front are under
`../php-spec-evidence-archive/gc-temp-consumption-peer-61/`.
The [review](../coverage/semantics/gc-temp-release-consumption-review.json)
also links the untouched motivating ATTR63 failure and its one affected regression.

COMP192 direct scoped REAL default originals and private-cache/This lifetime
checks are under `../php-spec-evidence-archive/comp192/`.
The [review](../coverage/semantics/deprecated-scoped-closure-default-review.json)
records ordinary staged/quiet release, late-called scopes and the separate
receiver-free fixture correction; held Generator-close behavior earns no credit.

COMP193 public method FCC originals, selected-entry history and borrowed-static
lifetime checks are under `../php-spec-evidence-archive/comp193/`.
The [review](../coverage/semantics/deprecated-method-fcc-default-review.json)
keeps the cold-cache golden and body-fixture corrections, missing-child-entry
counterexample and held pending-invoke failure separate from accepted cuts.
Promoted192 native data keeps its original context with an explicit
no-file-identity-effects bridge.

COMP194 class-constant originals, lookup receipts, reentrant replacement and
compiler-prefix checks are under `../php-spec-evidence-archive/comp194/`.
The [review](../coverage/semantics/deprecated-class-constant-owned-review.json)
separates the failed object-transfer proof and fixture/load corrections from
accepted source cuts. Cache-only historical values retain explicit refusal credit0;
raw streams, source snapshots and recorders remain external.

COMP195 computed class-cache images and staged replacement evidence are under
`../php-spec-evidence-archive/comp195/`. The [review](../coverage/semantics/computed-class-cache-replacement-review.json)
distinguishes completed normal rows in a failed native aggregate, the unchanged194
native promotion, affected fixture/validator corrections, and a separate
inconclusive throwing-child timeout with zero agreement. Raw streams and the
single bounded stack sample remain external; neither requires a native replay.

COMP196 static-default source and cell/publication evidence is under
`../php-spec-evidence-archive/comp196/`. The [review](../coverage/semantics/deprecated-static-property-default-review.json)
separates guarded completed rows from failed aggregates and records the corrected
explicit-exit classification, array-identity counterexample and unified-phase
fix. Earlier source/state cuts retain their actual identities; raw data stays external.

COMP197 instance-template sources and independent alias/copy/history/release
checks are under `../php-spec-evidence-archive/comp197/`. The
[review](../coverage/semantics/deprecated-instance-property-default-review.json)
binds nine exact originals and 79/73/46/82 strict457 conditions to their actual
cuts, including a later legacy-write barrier and exact event-position guard.
Original preparation failures remain zero credit; completed sources are not replayed.

COMP198 constructor sources and independent receiver/cache/history/exit checks
are under `../php-spec-evidence-archive/comp198/`. The
[review](../coverage/semantics/deprecated-constructor-default-review.json) binds
eight exact originals and 91/51/106 strict458 conditions to their actual cuts.
Guarded completed rows stay distinct from failed aggregates; both failed-exit
discrepancies and fixture diagnostics remain external with zero credit.

COMP199 initialized-CV class-string constructor sources and selection/history
checks are under `../php-spec-evidence-archive/comp199/`. The
[review](../coverage/semantics/deprecated-class-string-constructor-default-review.json)
binds four exact originals and 70/73/53 strict459 conditions to their actual cuts.
The final named-class guard retains completed named-source cuts; the corrected
string-carrier observer's original failure remains zero credit.

COMP200 keyword-factory constructor sources and scope/history checks are under
`../php-spec-evidence-archive/comp200/`. The
[review](../coverage/semantics/deprecated-keyword-constructor-default-review.json)
binds four exact originals and 63/63/52/23 strict460 conditions to their cuts.
The child-witness omission diagnostic remains zero credit; only its affected
front ran after the guard, retaining genuine-child/no-child paths without replay.

COMP201 CV method-name default sources and function/scope/history checks are under
`../php-spec-evidence-archive/comp201/`. The
[review](../coverage/semantics/deprecated-cv-method-default-review.json) binds four
exact normal originals and 55/57/56 strict461 conditions to their actual cuts.
All comparisons and novel fronts passed first try; no source/native or older
matrix replay was needed.

COMP202 shutdown method-default sources and registry/history checks are under
`../php-spec-evidence-archive/comp202/`. The
[review](../coverage/semantics/deprecated-shutdown-method-default-review.json)
binds five exact originals and 86/78/83 strict462 conditions. The completed registry
row is guarded separately from its failed aggregate. Only the qualified DEFINE
fixture was remeasured; baseline and preparation failures retain zero credit.

COMP203 error/exception method-default sources and ownership/history checks are
under `../php-spec-evidence-archive/comp203/`. The
[review](../coverage/semantics/deprecated-handler-method-default-review.json)
binds four exact normal originals, including the typed case's builtin stderr,
and 86/76/90 strict463 conditions. Diagnostic/fixture failures retain zero credit;
the actual fa5139bf5c joined463 load and inventory pass. Closed-helper erased
storage views stay distinct from the genuine retirement checkpoints. No native
or accepted source replay was needed.

COMP204 autoload default sources and ownership/history checks are under
`../php-spec-evidence-archive/comp204/`. The
[review](../coverage/semantics/deprecated-autoload-method-default-review.json)
binds four exact originals and 76/96/86 strict464 conditions. Current-owner and
publication-cut/string-carrier diagnostics retain their zero credit; earlier
fallback failures are not startup-fact rejections. Only affected comparisons
were repeated after fixes, with original native bytes/path/CWD reused. The actual
67b944566d joined465 load composes accepted475+476 and inventory passes.

COMP205 tick method-default sources and marker/owner/history checks are under
`../php-spec-evidence-archive/comp205/`. The
[review](../coverage/semantics/deprecated-tick-method-default-review.json)
binds four exact normal originals and 72/96/91 strict466 conditions. The old
attributed-donor planning dependency, baseline entry and pre-execution elaboration
failure retain zero credit. Native bytes/path/CWD were reused without replay;
registry retirement is distinct from erased-storage helper controls. Actual
50f1ee75a joined466 and inventory pass.

COMP206 named-function callback sources and current/history checks are under
`../php-spec-evidence-archive/comp206/`. The
[review](../coverage/semantics/deprecated-named-callback-default-review.json)
binds six exact normal originals and 59/58/52 author plus 85/89 independent strict467
conditions. All natives passed first attempt and were not replayed. Source type/
capture failures and the final-cache observer error retain zero credit; only
reentry repeated after that observer correction, with autoload59 retained. Actual
714d1bd8c joined467 and inventory pass.

COMP207 raw callable-CV defaults are recorded under
`../php-spec-evidence-archive/comp207/`. The
[review](../coverage/semantics/deprecated-raw-callable-default-review.json)
binds five normal originals and 63/52/47 author plus 93/87 independent strict468
conditions. Four source cuts retain the exact raw-mint/unchanged-owner bridge;
only the new mixed raw/FCC source repeated after its reached omission control.
Native originals were not replayed. Active-child versus closed-child diagnostics
and the pre-execution observer failure retain zero agreement credit. Actual
e3d2c106c joined468 and inventory pass.

COMP208 nullsafe-method default sources and current/history checks are under
`../php-spec-evidence-archive/comp208/`. The
[review](../coverage/semantics/deprecated-nullsafe-default-review.json) binds four
first-attempt normal originals and 63/58 author plus 77/83 independent strict469
conditions. The nil GLOBALTABLE observer failure retains zero credit; only that
observer changed before the affected check passed. No native/source replay occurred.
Erased-storage views test pure helper independence, separately from actual receiver
retirement. Actual92b1f5fb8 joined469 and inventory pass.

COMP209 class-value static defaults are recorded under
`../php-spec-evidence-archive/comp209/`. The
[review](../coverage/semantics/deprecated-class-value-default-review.json) binds
four first-attempt normal originals and 62/60 author plus 86/74 independent
strict470 conditions. One optional-head observer correction repeated only its
affected scope group; native/source originals were not replayed. Existing
string/object normalization and actual object retirement are distinct from
erased-storage history helper controls. Actual864b8f335 joined470 and inventory pass.

COMP210 interface-constant sources and reached checks are under
`../php-spec-evidence-archive/comp210/`. The
[review](../coverage/semantics/deprecated-interface-constant-review.json) binds
four first-attempt normal originals and 72/62 author plus 76/71 independent
strict471 conditions, no failures/replay. Native preparation retains5ecf paths;
all model/state executions first merged passed864 plus482. Actual94e7 joined471
and inventory pass; its additional accepted guard changes retain explicit bounds.
Computed-old retirement is separate from eval-prefix and history-erasure controls;
the global Closure remains permanently donor-rooted.

COMP211 class-constant fetch notices are under
`../php-spec-evidence-archive/comp211/`. The
[review](../coverage/semantics/deprecated-class-constant-fetch-review.json) binds
four normal originals, 229 reached-state conditions and 18 model-only conditions
for three held `constant()` controls. Baseline Unsupported, before-execution
elaboration, wrong diagnostic-level observer and three state-observer failures
retain zero credit. Only changed or previously unrun checks repeated; all final
runtime execution uses b78/private472. Actual1e667065e joined472 and inventory pass;
its additional accepted branches retain explicit scope bounds. No value/owner is
stored in the notice task.

COMP212 interface notices are under `../php-spec-evidence-archive/comp212/`.
The [review](../coverage/semantics/deprecated-interface-constant-fetch-review.json)
binds four first-attempt normal originals and 73/45 author plus 72/58 independent
strict473 conditions. No failures, native/source replay or shared runtime edits
occurred. The field3 decoder and interface-request proof reuse the original
declaring guard, compiler vetoes and value-free continuation. Actual17901f10d
joined473/inventory pass; additional accepted guarded consumers retain an explicit
private/current bridge.

COMP213 scalar class-constant API evidence is under
`../php-spec-evidence-archive/comp213/`. The
[review](../coverage/semantics/deprecated-class-constant-api-review.json) binds
five normal originals and 340 strict474 conditions:313 positive-state and27
model-only controls. The old entry36 and silent-keyword7 diagnostics remain
separate0, alongside setup/structuring and observer failures. Source5 and peer185
retain an explicit nonkeyword bridge through the exact400 refusal fence. Captured
request-string metadata has0nodes; no physical string retirement is claimed.
Actualcfba409e joined474/inventory pass; its additional accepted guarded consumers
retain a separate private/current bridge.

COMP214 literal-array API evidence is under `../php-spec-evidence-archive/comp214/`.
The [review](../coverage/semantics/deprecated-class-constant-array-api-review.json)
binds three first-attempt normals and234 strict475 conditions:227positive-state
plus7directly affected model-only array controls. No failure/replay/shared runtime
edit occurred. Permanent pool owners are distinct from retired mutable copies and
new result edges. Actualfba6 joined475/inventory pass;301/456 current changes retain
bounded qualifications without fresh source or whole-state/GC credit.

Historical reports and handoffs retain original paths, hashes, implementation
identities and commit IDs. References to compressed archives, including claims
that originals are retained, resolve through this manifest and external archive.
They do not assert that the compressed bytes remain tracked. To run an older
ad hoc audit requiring its original coverage path, copy the corresponding file
back from the mirror after checking its SHA-256; the restored file is ignored.
This relocation does not upgrade historical or interrupted results to passes.
The paused agents' unfinished runs remain under the existing ignored `.tools/`.

Source117's fixed-name construction during reentrant class linking is retained
uncompressed under `../php-spec-evidence-archive/source117-reentrant-unlinked-new/`.
Its `manifest.json` binds source, strict/reached and preservation reports, raw
failures and tested inputs; the concise [review](../coverage/semantics/reentrant-unlinked-new-review.json)
records their hashes and recovery commands.

Source118's dynamic-name counterpart is retained uncompressed under
`../php-spec-evidence-archive/source118-reentrant-dynamic-new/`. Its manifest
preserves the original acquisition Warning and independent fixture failure,
separate corrected/temporary-carrier checks and tested inputs. The
[dynamic-name review](../coverage/semantics/reentrant-dynamic-new-review.json)
records the exact source and reached cuts without renewing earlier evidence.

Source119's interface/trait construction lookup evidence is retained under
`../php-spec-evidence-archive/source119-construction-lookup/`. Its manifest
preserves four frozen native/unchanged/changed originals, authored reached
rows, the failed budget seeker and its corrected independent cut. The
[construction lookup review](../coverage/semantics/reentrant-nominal-new-review.json)
records hashes, tested inputs and recovery commands.

Enum core raw cuts are retained under
`../php-spec-evidence-archive/enum-core-stable-117/`. Its `manifest.json`
(SHA-256 `32dde8a4e1e9cdcbac019ef98f5df4ae4060e2a2765a0b2afe438bd3d1266f1e`)
lists 60 small report/source/state directories and selected report hashes. It
preserves failed and partial M4 attempts without promoting them to agreement;
copy a required `raw/enum-*` directory back into ignored `.tools/` for recovery.
The final joined gate's argv used `taskset -c 1`, the project numeric runner,
`--sl`, all 428 absolute module paths in `spec/semantics/modules.json` order,
then `raw/enum-joined-strict-428-final/main.watsup`; its `result.json` binds
the tested tip/base, exit and output. The runner group was fully reaped.

Captured enum `cases(...)` cuts are under
`../php-spec-evidence-archive/enum-cases-fcc-117/`. Its `manifest.json`
(SHA-256 `f7028af79cde92e20df542a0e7f1ad3b9a5ef5d9257c9704d4e47c0fc06c0fd3`)
lists 11 raw directories, including the accepted cache/history checks, joined
430-module gate, and zero-agreement cold `from(...)` and pipe boundaries.

Captured enum `from(...)`/`tryFrom(...)` cold-table cuts are under
`../php-spec-evidence-archive/enum-cold-from-117/`. Its `manifest.json`
(SHA-256 `934643b994b69bad3f50f472f70fa81c97333d2ac51da8db127dafa26622656d`)
lists 31 raw directories. Keep the original failed/timeout cuts separate from
the accepted queue, bind, table, Alias, inherited-owner and cross-file strictness
checks. Its earlier captured Stringable lookup and conditional constant-transfer
results are explicit Unsupported, with no agreement credit. The joined `--sl`
gate used CPU 1 and all 430 manifest modules;
`raw/enum-cold-joined-430-v1/result.json` records its
tested revision, command and output. The runner process group was fully reaped.

Captured Stringable lookup cuts are under
`../php-spec-evidence-archive/enum-captured-stringable-117/`. Its `manifest.json`
(SHA-256 `c821fb4ff827854fbca193fa62eedb050afb57b5502f701b037df6e52ec5189a`)
lists eight raw directories, preserving the earlier Unsupported and strict
binding failures separately from exact one-line, multiline, closure-owner and
`tryFrom()` results. The reached multiline check authenticates callback source,
selection, owner roots and argument retirement before the backed table. The
joined `--sl` gate checks all 430 manifest modules and records its clean result.

Source-certified enum conditional-transfer cuts are under
`../php-spec-evidence-archive/enum-conditional-transfer-117/`. Its `manifest.json`
(SHA-256 `752b6bfea7f70ae3bfb65e4206a101f491e70252bb2e4d93376a7625fdfee7c8`)
lists eight raw directories. Original object and scalar Unsupported results
remain separate from their exact affected checks; cross-enum and negated-case
sources, selected-case/history negatives and post-bind cache checks retain
their individual cuts. The joined `--sl` receipt records the composed 430-module
candidate, true result and fully reaped process group.

Generated enum array callable cuts are under
`../php-spec-evidence-archive/enum-array-callable-117/`. Its `manifest.json`
(SHA-256 `7237a68b42022feefdcf203d8c450676b66e434755f2a260433b9991db39eb6a`)
lists 14 raw directories. The original Unsupported and Stringable failure remain
separate from exact source results. The target-state v5 packet has 40 substantive
true checks; v6 confirms its two manually resolved intermediate states were
fixture errors. The ownerless Stringable reached packet passes 31 checks. The
joined v1 duplicated the manifest's first module and has zero semantic credit;
v2 records `--sl` over all 431 modules, `true`, and a fully reaped CPU 1 group.

Generated enum string-callable cuts are under
`../php-spec-evidence-archive/enum-string-callable-117/`. Its `manifest.json`
(SHA-256 `4729ec1a12e44429a58c83fa29c38d621df7ad32825cd71c40c35c83969d18c3`)
binds a 3,782,657-byte archive containing 42 raw directories. Six normal originals,
one zero-agreement packed-source refusal and 159 state/guard conditions retain
their separate cuts. Original 136/137 failures and fixture corrections remain
distinct from the separately reviewed 301 normalization and affected acceptance.
The actual-tail joined strict431 result pins `e09c05010` over `08439f073`,
with exact `true` output, stable inputs and a fully reaped CPU1 group. Extract the
archive and copy a required `raw/enum-*` directory back into ignored `.tools/`;
recorded commands, tested inputs, runtime/compiler identities and absolute paths
preserve recovery. See the [string review](../coverage/semantics/enum-string-callable-review.json).

Generated enum string-capture cuts are under
`../php-spec-evidence-archive/enum-string-capture-117/`. Its `manifest.json`
(SHA-256 `049171cb6ad89f82ab1467a56a110b37e8151b345adbc8223d7aa6ac4d7c78dd`)
binds a 613,293-byte archive with seven raw directories. Four exact originals,
114 state/guard conditions and private strict431 retain their original cuts; the
initial Unsupported has zero agreement credit. Actual-tail joined strict432
pins `d52de3fd9` over `0d5e7de23`, with exact `true`, stable inputs and full reap.
The [capture review](../coverage/semantics/enum-string-capture-review.json) records
the applicable GC07 copied-target/cache-borrowing seam and the remaining partial
routes. Extract the archive and restore the selected `raw/enum-string-capture-*`
directory under ignored `.tools/` to recover recorded commands and tested inputs.

Generated enum array-capture cuts are under
`../php-spec-evidence-archive/enum-array-capture-117/`. Its `manifest.json`
(SHA-256 `a11cf492df4b11db78d1673c7d20e7545bba44433853e0bd8633286189248cf5`)
binds a 638,573-byte archive with seven raw directories. Four fresh originals,
123 state/guard conditions and private432 retain their original cuts; the
initial Unsupported has zero agreement credit. Actual-tail joined433 pins
`32aa103b7` over `16124e8e1`, with exact `true`, stable inputs and full reap.
The [array review](../coverage/semantics/enum-array-capture-review.json) records
the GC08/OB444/clone seams and GC09-open boundary. Extract the archive and restore
the selected `raw/enum-array-capture-*` directory under ignored `.tools/` for
recorded commands, original paths and tested inputs.

The guarded getter-recursion milestone retains source/native observations,
focused checks, all fixture failures and diagnostics in
`../php-spec-evidence-archive/magic-get-recursion-119/manifest.json`.
Its 14,711,985-byte archive has SHA-256
`95fdd8cbfd591039fe1a104525a964de568feccfdc8aa73ec720827a5e9b194b`.

Declared-UNSET getter recursion is retained in
`../php-spec-evidence-archive/magic-get-unset-recursion-120/manifest.json`, including
the original fixture compiler failure and observer limitations. Its 5,212,465-byte
archive has SHA-256
`e94cc096c40b1a22af50f5823ea8e2ea6b64991819ba470bfbdaf03de6a812c5`.

Typed recursive-getter Error evidence is retained in
`../php-spec-evidence-archive/magic-get-recursive-error-121/manifest.json`: native6,
the unchanged-model PHP-error mismatch, four source agreements, the zero-evaluation
fixture failure and 496 focused premises. The archive includes tested-input snapshots.

Denied getter-reentry visibility Errors are retained in
`../php-spec-evidence-archive/magic-get-denied-recursion-122/manifest.json`:
native5/baseline5, three source agreements, the original false/carrier diagnostic,
405 focused premises and tested-input snapshots.

Caller-scoped UNSET getter selection is retained in
`../php-spec-evidence-archive/magic-get-scoped-unset-123/manifest.json`: native4,
unchanged baseline4, source3, 330 focused premises and tested-input snapshots.
The same-object scoped/denied distinction and INITIAL control keep separate credit.

Literal-this Get entry/history/lifetime evidence is retained in
`../php-spec-evidence-archive/magic-get-direct-this-124/manifest.json`: native5,
unchanged baseline5, source4, 488 focused premises, original false and both
diagnostic attempts. Tested414 snapshots retain the two unchanged fixture helpers
and323 certificate;415 composition adds no execution credit.

Caller-selected Get declaration/type evidence is retained in
`../php-spec-evidence-archive/magic-get-lexical-selection-125/manifest.json`:
native5/baseline5 (including genuine normal wrong result), source3, 413 focused
conditions, original runtime nondeterminism and peer pre-main binder failure.
Tested415 snapshots retain the failed runtime and exact helper/input identities.

Owned-factory nonpublic/denied Get evidence is retained in
`../php-spec-evidence-archive/magic-get-owned-access-126/manifest.json`: native5,
unchanged baseline5, source3 and477 focused conditions at their original415 cuts.
The archive preserves tested380/manifest, exact maintained inputs, unchanged
helpers, raw processes and zero-credit preparation stops. Composition over416
adds no execution credit.

Scoped CV Get reference verification is retained in
`../php-spec-evidence-archive/magic-get-scoped-reference-127/manifest.json`:
native4/baseline4, new source3 and432 focused conditions at their original416 cuts.
The archive preserves380/384/manifest, exact maintained inputs, unchanged helpers
and all raw processes. Its native-only owned-BYREF boundary keeps zero credit
at that cut; composition over417 adds no execution credit.

Owned nonpublic/reference Get lifetime evidence is retained in
`../php-spec-evidence-archive/magic-get-owned-reference-128/manifest.json`:
native5/baseline5, changed source5 and586 focused conditions at their original417
cuts. The archive preserves380/384/manifest, nine maintained inputs, unchanged
helpers, raw processes and the three Unsupported/two genuine wrong-PHP-error
baselines. Composition over419 adds no execution credit.

Literal-this reference Get evidence is retained in
`../php-spec-evidence-archive/magic-get-this-reference-129/manifest.json`: native3/
baseline3, changed source3 and496 focused conditions at their original419 cuts.
It preserves380/384/manifest, six maintained inputs, the imported recursion/
scoped-unset/owned-reference helpers and raw processes. Native/baseline launcher
provenance stays distinct from changed/focused actual affinity samples. Later
composition adds no execution credit.

Parameter-backed reference Get evidence is retained in
`../php-spec-evidence-archive/magic-get-param-reference-130/manifest.json`: native3/
baseline3, changed source3 and 511 focused conditions at their original 419 cuts.
It preserves eleven tested-input snapshots, six supporting reports, both fixture
failures and the zero-credit diagnostic. Detached 165 retains `706cc866f`; corrected
conflict 169/peer 177 retain `b23055fcd`. Later composition adds no execution credit.

Returned receiver-cell Get evidence is retained in
`../php-spec-evidence-archive/magic-get-receiver-cell-131/manifest.json`: separate
native/baseline3+payload1 packets, changed4 and 714 focused conditions at original
420 cuts. Eight reports and thirteen tested snapshots preserve runtime/schema,
sources, helpers, profiles and all raw processes. Every executed group passed
first time; Unsupported baselines and derived KNOWN-RV checks add no source credit.
Later composition adds no execution credit.

Keep future compressed raw traces, source snapshots and tool copies in this
external archive (using new paths for new evidence) or in ignored `.tools/`.
Commit concise reports and manifests with hashes and locations. Preserve raw
failures and interrupted runs externally; do not force-add their archives.
The coverage compression patterns in `.gitignore` guard against reintroduction.

I78 real Closure factory Generator evidence retains frozen authored/dependency
native, unchanged baseline, private/joined strict, source and reached-state cuts
under `../php-spec-evidence-archive/generator-closure-factory-78/`. The independent
bound-reference/Fiber peer and its exact native/model comparison are under
`../php-spec-evidence-archive/generator-closure-factory-78-review/`.
The [Closure factory ledger](../coverage/semantics/generator-closure-factory-review.json)
binds tested revisions, hashes and remaining scope.

I79 rebound Closure method-creation evidence retains authored native, unchanged
private/public controls, private strict, source and reached-state cuts under
`../php-spec-evidence-archive/generator-closure-method-79/`. The independent
distinct-receiver BYREF/Fiber peer is under
`../php-spec-evidence-archive/generator-closure-method-79-review/`.
The [rebound method ledger](../coverage/semantics/generator-closure-method-review.json)
binds tested revisions, hashes and remaining scope.

I80 captured-method Generator factory evidence retains authored native,
unchanged refusal/control, private and CLASS151-tail joined strict, source and
reached-state cuts under
`../php-spec-evidence-archive/generator-captured-method-factory-80/`. The
independent by-reference SEND/Fiber-abort peer is under
`../php-spec-evidence-archive/generator-captured-method-factory-80-review/`.
The [captured factory ledger](../coverage/semantics/generator-captured-factory-review.json)
binds revisions, hashes and remaining scope.

I81 array/string factory native, unchanged gate/projection, private/actual-tail
joined strict and new-only model/state evidence is under
`../php-spec-evidence-archive/generator-array-string-factory-81/`; the independent
private-array BYREF SEND peer is under
`../php-spec-evidence-archive/generator-array-string-factory-81-review/`.
The [array/string ledger](../coverage/semantics/generator-array-string-factory-review.json)
separates accepted observations from pending checks and preserves the original
wire-byte assertion failure with zero agreement credit.

I82 compatible bound-method factory native, unchanged refusal, private strict
and new source/state evidence is retained across
`../php-spec-evidence-archive/generator-bound-method-factory-82/` and
`../php-spec-evidence-archive/generator-bound-method-factory-82-review/`.
The [bound factory ledger](../coverage/semantics/generator-bound-factory-review.json)
separates completed cuts from pending checks; raw originals remain external.

I83 invokable-object factory native, unchanged refusal, private strict and new
source/state evidence is retained across
`../php-spec-evidence-archive/generator-invokable-factory-83/` and
`../php-spec-evidence-archive/generator-invokable-factory-83-review/`.
The [invokable ledger](../coverage/semantics/generator-invokable-factory-review.json)
keeps native predictions/observations, tested cuts and pending checks separate.

I84 magic-handler factory native, unchanged refusal, private strict and new
source/state evidence is retained across
`../php-spec-evidence-archive/generator-magic-method-factory-84/` and
`../php-spec-evidence-archive/generator-magic-method-factory-84-review/`.
The `actual-tail-f405/` and `actual-tail-5e33/` subdirectories under the
first archive retain current-tail strict, source and reached-state reports.
The [magic ledger](../coverage/semantics/generator-magic-factory-review.json)
binds tested cuts and preserves the initial syntax and missed-stage fixture
failures with zero credit.

I85 direct magic-Generator native, unchanged refusal, private compiler and new
source/state evidence is retained under
`../php-spec-evidence-archive/generator-direct-magic-method-85/` and
`../php-spec-evidence-archive/generator-direct-magic-method-85-review/`.
The first archive's `actual-tail-bd274/` retains joined strict, source and
reached-state reports.
The [direct magic ledger](../coverage/semantics/generator-direct-magic-review.json)
keeps original compiler, COUNT, Fiber-consumer and fixture-prefix failures
separate from corrected and new checks.

I86 captured-method body native, unchanged refusal, private compiler and new
source/state evidence is retained under
`../php-spec-evidence-archive/generator-captured-method-body-86/` and
`../php-spec-evidence-archive/generator-captured-method-body-86-review/`.
The first archive's `actual-tail-4462/` retains joined strict, source and
reached-state reports.
The [captured body ledger](../coverage/semantics/generator-captured-method-body-review.json)
records the shared ATTR07 borrowing dependency and original compiler/storage
failures alongside their narrow corrections.

I87 raw method native, private compiler, source and reached-state evidence is
retained under `../php-spec-evidence-archive/generator-raw-method-factory-87/`
and `../php-spec-evidence-archive/generator-raw-method-factory-87-review/`.
The first archive's `actual-tail-833e/` and `joined-state-1f0e/` retain the
joined reports, including the strengthened empty-shutdown closed-history state.
The [raw method ledger](../coverage/semantics/generator-raw-method-factory-review.json)
keeps original failures separate from accepted checks.

I88 raw method cache and THROW evidence is retained under
`../php-spec-evidence-archive/generator-raw-method-cache-88/` and
`../php-spec-evidence-archive/generator-raw-method-cache-88-review/`.
The first archive's `actual-tail-1ecc/` retains joined strict, three sources,
affected old fresh/warm states and an independent reached state.
The [raw cache ledger](../coverage/semantics/generator-raw-method-cache-review.json)
keeps original failures and the calibrated owner diagnostic separate.

I89 captured method THROW evidence is retained under
`../php-spec-evidence-archive/generator-captured-method-throw-89/` and
`../php-spec-evidence-archive/generator-captured-method-throw-89-review/`.
The first archive's `actual-tail-c81b/` retains joined strict, three exact
sources and fresh/closed reached-state reports.
The [captured THROW ledger](../coverage/semantics/generator-captured-method-throw-review.json)
keeps original nominal, bindTo and interpreter failures separate.

I90 direct magic Generator THROW evidence is retained under
`../php-spec-evidence-archive/generator-direct-magic-throw-90/` and
`../php-spec-evidence-archive/generator-direct-magic-throw-90-review/`.
The first archive's `actual-tail-dfa4/` retains joined strict, three exact
sources, fresh/closed states and the affected I85 SEND state.
The [magic THROW ledger](../coverage/semantics/generator-direct-magic-throw-review.json)
keeps the unchanged Unsupported separate from accepted checks.

I91 string-method Closure evidence is retained under
`../php-spec-evidence-archive/generator-string-method-closure-91/` and
`../php-spec-evidence-archive/generator-string-method-closure-91-review/`.
The first archive's `actual-tail-ee4b/` and `actual-tail-5610/` retain joined
strict, three exact sources and parked/closed states, including the GC09 marker.
The [string Closure ledger](../coverage/semantics/generator-string-method-closure-review.json)
keeps original nominal and binding failures separate.

I92 real Generator Closure::call copy evidence is retained under
`../php-spec-evidence-archive/generator-call-copy-92/` and
`../php-spec-evidence-archive/generator-call-copy-92-review/`.
The first archive's `actual-tail-a84b/` retains joined strict, four exact
sources and API-entry, unused-result and sibling closed states.
The [call-copy ledger](../coverage/semantics/generator-call-copy-review.json)
keeps original Unsupported, native receive error and two fixture failures separate.

I77 receiver-bearing scoped Generator evidence retains authored native,
unchanged baseline, private/joined strict, source and reached-state cuts under
`../php-spec-evidence-archive/generator-keyword-receiver-77/`. The independent
peer source, original provisional native expectation mismatch and exact model
comparison are under
`../php-spec-evidence-archive/generator-keyword-receiver-77-review/`.
The [receiver ledger](../coverage/semantics/generator-keyword-receiver-review.json)
binds the tested revisions, raw flags, hashes and remaining scope.

I76 keyword factory-chain evidence retains native, unchanged baseline, strict,
source and state cuts under
`../php-spec-evidence-archive/generator-keyword-factory-chain-76/`; the
independent peer is under
`../php-spec-evidence-archive/generator-keyword-factory-chain-76-review/`.
The [chain ledger](../coverage/semantics/generator-keyword-chain-review.json)
keeps tested revisions, hashes and the retained I75 chain promotion distinct.

I75 keyword Generator creation retains native, strict and original baseline
records under `../php-spec-evidence-archive/generator-keyword-creation-75/`,
accepted/failing source and state raw cuts under its `validated/` directory, and
the independent peer under `../php-spec-evidence-archive/generator-keyword-creation-75-review/`.
The [review ledger](../coverage/semantics/generator-keyword-creation-review.json)
identifies hashes and the peer's unchanged-input bridge across a fixture-only
HEAD change. No source or state cut is renewed by this index.

I74 fresh NEXT/SEND evidence is retained uncompressed under
`../php-spec-evidence-archive/generator-fiber-fresh-advance-74/`. Its manifest binds
fifteen reports covering nine native sources, six representative baseline cases,
disjoint changed 3+8 cuts, four accepted state fronts plus the failed selector,
peer native/setup/240s stop/600s success, and private 425/joined 426. Original I73
anchor paths/status cuts remain untouched; only their affected model expectations
are promoted.

I73 static CURRENT/NEXT/SEND transfer evidence is retained uncompressed under
`../php-spec-evidence-archive/generator-fiber-static-transfer-73/`. Its manifest
binds eleven reports, including the representative baseline 5, changed 6 plus two
zero-credit phase gates, four reached cuts, peer SEND abort and joined 425. No I72
source/state/native cut is renewed.

I72 static-method Generator THROW evidence is retained uncompressed under
`../php-spec-evidence-archive/generator-fiber-static-throw-72/`. Its `manifest.json`
binds nine reports, including the failed pending fixture and corrected-only cut,
the peer scoped-copy abort originals/streams, and joined 425; old cuts are retained.

I71 fresh named by-reference Generator THROW evidence is retained uncompressed
under `../php-spec-evidence-archive/generator-fiber-fresh-reference-throw-71/`.
Its `manifest.json` identifies seven private reports and the separate peer
alias/formal-unset originals and streams; I69/I70 cuts are not renewed.
The additional `joined-strict/report.json` records actual-tail compilation.

I70 fresh by-value method Generator THROW evidence is retained uncompressed under
`../php-spec-evidence-archive/generator-fiber-fresh-method-throw-70/`.
Its `manifest.json` identifies seven raw private reports, including the separate
peer inherited-abort originals and streams; accepted I69 cuts are not renewed.
The additional `joined-strict/report.json` records actual-tail compilation.

I69 fresh method by-reference Generator THROW evidence is retained uncompressed
under `../php-spec-evidence-archive/generator-fiber-fresh-method-reference-throw-69/`.
Its `manifest.json` identifies ten private reports and the separate peer originals/streams.
The additional `joined-strict/report.json` records actual-tail compilation.
Initial native-transport and returned-fixture failures remain alongside accepted
source, parked and corrected returned cuts with their original revision identities.

I68 method by-reference Generator THROW evidence is retained uncompressed under
`../php-spec-evidence-archive/generator-fiber-method-reference-throw-68/`.
Its `manifest.json` identifies eleven raw reports, including both failed reached
fixtures, the independent recorder correction and joined strict compilation,
with SHA-256 hashes.

M106's normal partial-pair cleanup evidence is in
`../php-spec-evidence-archive/lifecycle-normal-partial-pair-106/manifest.json`.
Its 410,489-byte archive has SHA-256
`957fd480d8578832d6b4458094477b600b8ea4675c72a861b871f2086b6b1176`;
it retains the source packets, successful proofs, original fixture failure and
field diagnosis under `.tools/m106/`, without a checkout or build tree.
The final-pair sibling is in
`../php-spec-evidence-archive/lifecycle-normal-final-pair-107/manifest.json`:
283,128 bytes under `.tools/m107/`, SHA-256
`1fc094d0b1b79d90d4a63d79a4e19ee7878ac8a751af539695500eaa1a149e2c`.
The single-cursor sibling is in
`../php-spec-evidence-archive/lifecycle-normal-cursor-108/manifest.json`:
271,278 bytes under `.tools/m108/`, SHA-256
`bf8cb58209c01ac4e495337633ffc441ee51202229246ef511a0b3b2c529ad21`.
The pending single-cursor final-release evidence is in
`../php-spec-evidence-archive/lifecycle-pending-cursor-109/manifest.json`:
286,021 bytes under `.tools/m109/`, SHA-256
`a8b5638d3fc6b6d1171226ab8d188b3ee4b54c36917324c36db91c1a6e5c52ff`.
Its auxiliary-operation interval sibling is in
`../php-spec-evidence-archive/lifecycle-pending-cursor-110/manifest.json`:
290,603 bytes under `.tools/m110/`, SHA-256
`5904fbea170d1bf4c2e2f48386205656b2dd6218da742af02cf194c704aefb1b`.
The pending final-pair interval is in
`../php-spec-evidence-archive/lifecycle-pending-final-pair-111/manifest.json`:
297,082 bytes under `.tools/m111/`, SHA-256
`85de0f4debc4c3fc0d91018e99e9e2d46639edb0293a6081bc5071a84906a7cf`.
The pending still-owning partial-pair interval is in
`../php-spec-evidence-archive/lifecycle-pending-partial-pair-112/manifest.json`:
317,000 bytes under `.tools/m112/`, SHA-256
`c56ef7c478f526ccd2e0ed4b273e382b596a6cea563cf500fef9fa1866528190`.

The fresh interposed scalar/dormant-destructor regression and public cleanup proof
are in `../php-spec-evidence-archive/lifecycle-interposed-capture-113/manifest.json`:
617,423 bytes under `.tools/m113/`, eight distinct actor reports and selected runtime
patches, SHA-256 `6f291adecb3455f5140c3bf1d460f35155369dea3e1d69bb38b36af858d0c0db`.

Normal three-owning computed returns are validated in
`../php-spec-evidence-archive/lifecycle-three-owning-114/manifest.json`:
398,023 bytes under `.tools/m114/`, six distinct actor reports including two
fixture failures, SHA-256 `62aaa027e78aaea3c957a968db2509de829d7fbb8a91f5ada7421b0bdd532ccb`.

First-C pending three-owning replay is in
`../php-spec-evidence-archive/lifecycle-pending-three-owning-115/manifest.json`:
640,934 bytes under `.tools/m115/`, nine reports retaining the original diagnostic,
binding and timeout failures plus runtime patches, SHA-256
`993cb5c5d8f5417ea4e4a6b9b8b67457aa68c73a62151c86a639466db4e0214d`.

The nested C→D destructor return-history proof is in
`../php-spec-evidence-archive/lifecycle-reentrant-three-owning-116/manifest.json`:
579,650 bytes under `.tools/m116/`, eight reports including both strict-only fixture
failures and the runtime patch, SHA-256
`ddad5ee4e9af8e7ffe8b0475db2923f8fb0b0d8258fca42a4a127f9fd5a14547`.

The finite nested Exception constructor-kind proof is in
`../php-spec-evidence-archive/lifecycle-exception-width-117/manifest.json`:
442,184 bytes under `.tools/m117/`, six first-attempt actor reports and the runtime
patch, SHA-256 `1e17bd769bc00db84384ca464599754e3e43864f16c2a754bad394c1d69edb9f`.

The supplied-global nested Throwable identity proof is in
`../php-spec-evidence-archive/lifecycle-supplied-exception-118/manifest.json`:
530,730 bytes under `.tools/m118/`, seven reports retaining the zero-evaluation source
failure and both runtime patches, SHA-256 `3d0e7c69bd73fa711370672453cd46d2e96a5a2500b3ded8f9e94b046388e61e`.

The recursive four-owning return-history proof is in
`../php-spec-evidence-archive/lifecycle-four-owning-119/manifest.json`:
556,432 bytes under `.tools/m119/`, seven reports retaining the pre-state
diagnostic failure and exact runtime patch, SHA-256 `8c14a312f25ee839f32183e5778257c51fd558f4972cbcf49ac8898d326b9aa7`.

The mixed global-cell/object return-history proof is in
`../php-spec-evidence-archive/lifecycle-mixed-owning-120/manifest.json`:
501,562 bytes under `.tools/m120/`, six reports with original source
packets, accepted state snapshots and runtime patch, SHA-256 `ad1387df1535f45c813b05c52be87aa2574d867a6d7eb0d6b6d2131dc189ecea`.

The repeated global-alias return-history proof is in
`../php-spec-evidence-archive/lifecycle-aliased-owning-121/manifest.json`:
489,309 bytes under `.tools/m121/`, six reports with original packets,
accepted state snapshots and the two-guard runtime patch, SHA-256 `2fd91a9f24363656f5feae940e70fac9fb5e9ef52212ac57e3abfee77ea346fb`.

The typed object-property alias return-history proof is in
`../php-spec-evidence-archive/lifecycle-property-alias-122/manifest.json`:
621,616 bytes under `.tools/m122/`, seven reports retaining the original
author fixture failure, corrected/accepted snapshots and exact runtime patch,
SHA-256 `b0b79d39cc6cead5bba949e7b7495223aa22036f64cd7f42aa493a3eb1a75e4c`.

The holder type-source detachment and return-history proof is in
`../php-spec-evidence-archive/lifecycle-holder-detach-123/manifest.json`:
706,808 bytes under `.tools/m123/`, eight reports retaining the peer
compile failure,420s timeout, exact snapshots and runtime/declaration patch,
SHA-256 `05e40c928872590ab47a4d3b25d3f985d3457afc3dfc86f2ede99e3f923ae7e5`.

The partial property-source return-history proof is in
`../php-spec-evidence-archive/lifecycle-property-intersection-124/manifest.json`:
668,822 bytes under `.tools/m124/`, seven reports retaining the original
diagnostic failure, corrected/accepted snapshots and exact270 patch,
SHA-256 `e65400aad708e13d816d830c3d48c5c19c6c694269b30e400837b9bea4e2af0e`.

The normal holder-destructor return-history proof is in
`../php-spec-evidence-archive/lifecycle-holder-destructor-125/manifest.json`:
587,291 bytes under `.tools/m125/`, six reports with original
packets, accepted snapshots, both bounded worker transports and exact270 patch,
SHA-256 `eec0237203109c5115cac3bf3c2271efb914137478a271dcb1010ac61b0a0da6`.

The throwing Holder return-history proof is in
`../php-spec-evidence-archive/lifecycle-holder-throw-126/manifest.json`:
949,527 bytes under `.tools/m126/`, seven reports retaining the original
AST-binder diagnostic failure, corrected/accepted snapshots and exact270 patch,
SHA-256 `fcd882047933f85ffdeb1f6b8a515a4662d294e812ad1b7c836f8e4ec665418b`.

The distinct supplied Holder authority proof is in
`../php-spec-evidence-archive/lifecycle-holder-replacement-127/manifest.json`:
772,650 bytes under `.tools/m127/`, eight reports retaining parser and
interpreter failures, accepted snapshots, worker180 and both runtime patches,
SHA-256 `7813593edb0b96ffbe342abd638404e5e7957af40cbddbfa4546e66d831fcc37`.

The real held-Holder validation is in
`../php-spec-evidence-archive/lifecycle-holder-held-128/manifest.json`:
393,761 bytes under `.tools/m128/`, four fresh reports, original packets and
accepted snapshots with the 240s worker transport; no runtime patch,
SHA-256 `632a98f8a09c7aa110b2ad523cac30680e85b59d7d2d7ce3fec5f20120ad1a9a`.

The generated Holder typed-write TypeError proof is in
`../php-spec-evidence-archive/lifecycle-holder-write-129/manifest.json`:
716,332 bytes under `.tools/m129/`, seven reports including the original peer
fixture failure, original packets, accepted snapshots, worker240 and the
isolated270 runtime patch,
SHA-256 `81813f0b3fab83016de8a81e302445543ce305dd11e28f7ee59ea962db9d6988`.

The later owning-retirement proof is in
`../php-spec-evidence-archive/lifecycle-later-retirement-130/manifest.json`:
805,680 bytes/159 members under `.tools/m130/`, ten reports retaining
all three peer fixture failures, original packets, immutable snapshots, worker120,
combined runtime patch and the separate two-premise narrowing patch,
SHA-256 `cb5018d95cd9cc4b5bf5943f3f159c8746ec61d1d5aeae8e715c3233bd86e0e0`.

The recursive completed-prefix retirement proof is in
`../php-spec-evidence-archive/lifecycle-double-retirement-131/manifest.json`:
500,623 bytes/104 members under `.tools/m131/`, six reports,
original packets, immutable author/peer snapshots, worker120 and the isolated
three-file runtime patch,
SHA-256 `024ccd1c4835d69185db414a83588eeb42fa5515424b0c9c0e782b030817c035`.

The short remaining-slot completed-prefix proof is in
`../php-spec-evidence-archive/lifecycle-short-retirement-132/manifest.json`:
642,917 bytes/138 members under `.tools/m132/`, six complete reports,
original packets, immutable author/peer snapshots, the zero-credit interrupted
author output/receipt, worker120 and the isolated two-file runtime patch,
SHA-256 `18f98564d69dcfd2ec6c1961d1d213e0e583d45a3d4db03dedc11f94cf0dd81b`.

The first-retirement singleton REF/object proof is in
`../php-spec-evidence-archive/lifecycle-reference-remainder-133/manifest.json`:
821,114 bytes/175 members under `.tools/m133/`, nine reports (seven complete,
two preserved failures), original packets, immutable diagnostic/author/peer
snapshots, worker120 and the isolated two-file runtime patch,
SHA-256 `c6805d52873b73b03a5211809310df0c024eb6aafd5b8e5e8d5d4d12ef22a1ea`.

The WeakMap HCELL backedge/Key-only discovery proof is in
`../php-spec-evidence-archive/weakmap-hcell-backedge-134/manifest.json`:
653,225 bytes/238 members under `.tools/m134/`, twelve complete reports,
original packets and Unsupported observations, immutable diagnosis/author/peer
snapshots, worker120 and the isolated386 runtime patch,
SHA-256 `9a8da0cb235155fe26ae69ba55a553718a9f94c1143b96834035c91bffff0f8e`.

The ARRAY-valued WeakMap ephemeron proof is in
`../php-spec-evidence-archive/weakmap-array-ephemeron-135/manifest.json`:
336,514 bytes/136 members under `.tools/m135/`, six reports (five complete and
the preserved SL binding failure), original packets, immutable author/peer
snapshots, worker120 and the isolated386 runtime patch,
SHA-256 `37e6499d641e08f7b9be18c52c714afa4433813278c2a2ab58e7659a0a522236`.

The WeakMap foreach DATA/copy lifetime proof is in
`../php-spec-evidence-archive/weakmap-foreach-lifetime-136/manifest.json`:
631,246 bytes/199 members under `.tools/m136/`, ten reports (eight complete and
two preserved compiler stops), original3 packets, application0 preflight,
immutable author/peer snapshots, worker120 and the isolated129/386 runtime patch,
SHA-256 `ee02a4668b8b0c45f89d373c834bb454fb821b17a83c2ba4216c28f8d8e80b3e`.

The WeakMap entry-reference lifetime proof is in
`../php-spec-evidence-archive/weakmap-foreach-reference-137/manifest.json`:
746,694 bytes/165 members under `.tools/m137/`, nine reports (seven complete,
the original mixed repair packet and finder failure), two sources at separate cuts,
two application0 preflights, immutable author/peer snapshots and the isolated
30/129/270/386/420 patch. SHA-256
`f16ce3022c405cff998f4ade3da5866b367969e2afbe3f7545b4c1638aaadc06`.

The quiet direct-entry WeakMap Key-retirement proof is in
`../php-spec-evidence-archive/weakmap-quiet-key-retirement-138/manifest.json`:
371,981 bytes/114 members under `.tools/m138/`, five complete reports, original2
packets, immutable author/peer snapshots and the isolated386 guard patch.
SHA-256 `691eac64219e670a8a38c9a5d29fda2c6c05965b43cf8400e1f3d0fa730173c8`.

The WeakMap array-property/COW collection proof is in
`../php-spec-evidence-archive/weakmap-property-array-backedge-139/manifest.json`:
424,627 bytes/122 members under `.tools/m139/`, six reports (five complete and
the preserved author syntax stop), original2 packets, immutable author/peer
snapshots and the isolated386 admission patch. SHA-256
`d26cbd2334748526fb24f32f77dc729e3edf9fe2439f500dfc2c23cc314515f3`.

The shared-entry WeakMap ephemeron proof is in
`../php-spec-evidence-archive/weakmap-entry-reference-ephemeron-140/manifest.json`:
360,469 bytes/114 members under `.tools/m140/`, five complete reports, original2
packets, immutable author/peer snapshots and the isolated386 reference-entry patch.
SHA-256 `96aadbea9e3f28b2ca3fcf7a069824fdb54cf5d389974ff01ebaadb2275cd601`.

The multiple-entry WeakMap ownership/Key-retirement proof is in
`../php-spec-evidence-archive/weakmap-multiple-entry-lifetime-141/manifest.json`:
637,926 bytes/138 members under `.tools/m141/`, eight reports (six complete and
two preserved compile stops), original2 packets, app0 results, immutable
failed/corrected author and peer snapshots and the isolated30/386/422/manifest patch.
SHA-256 `aaf7bf4352b61aec50600cc0a1bac5c5ac30e7a40867a930694c4c0bd181e03b`.

The multiple-entry WeakMap last-owner teardown proof is in
`../php-spec-evidence-archive/weakmap-multiple-entry-teardown-142/manifest.json`:
441,658 bytes/114 members under `.tools/m142/`, five complete reports, original2
packets, immutable author/peer snapshots and the isolated422 teardown patch.
SHA-256 `35c83747a9c98d004d549d571678fb38c6a1a402396366428d3c451bba463b73`.

The multiple-entry WeakMap foreach proof is in
`../php-spec-evidence-archive/weakmap-multiple-entry-foreach-143/manifest.json`:
589,652 bytes/123 members under `.tools/m143/`, six complete reports, original2
packets, app0 preflight, immutable author/peer snapshots and the isolated30/422 patch.
SHA-256 `29eb262d43a3fe1e17e5fa88029e22b67ab347b459f982cc1c0de1d165a2fed2`.

The multiple-entry WeakMap reference-sharing proof is in
`../php-spec-evidence-archive/weakmap-multiple-entry-reference-144/manifest.json`:
572,000 bytes/123 members under `.tools/m144/`, six complete reports, original2
packets, app0 preflight, immutable author/peer snapshots and the isolated30/422 patch.
SHA-256 `208676595b098ca4d8a593ddebf3b0641e27f7ecb294389c31c0e27b985c03ca`.

The selective multiple-entry WeakMap ephemeron proof is in
`../php-spec-evidence-archive/weakmap-multiple-entry-ephemeron-145/manifest.json`:
483,023 bytes/123 members under `.tools/m145/`, six complete reports, original2
packets, app0 preflight, immutable author/peer snapshots and the isolated422 patch.
SHA-256 `fd18be8469986efff7089777ce8f7f9522c01bad623f6c8a7d33f40629fe349a`.

CALL124's original PHP requests, candidate/strict reports, failed fixture cuts
and eight accepted reached traces are under
`../php-spec-evidence-archive/call124-author-native/`. The independent sources,
retained-native comparisons and handler projections are under
`../php-spec-evidence-archive/call124-review-native/`. The concise
[review](../coverage/semantics/magic-iterator-unpack-review.json) records tested
revisions, hashes and the recovery paths. The joined A64 strict425 report is
`call124-author-native/joined-a64-9742d77b0/report.json` under the same archive.

CALL125's frozen original requests, candidate/strict reports, failures and
diagnostics are under `../php-spec-evidence-archive/call125-author-native/`;
`accepted-summary.json` binds individual complete source observations and eleven
reached groups, whose raw directories moved intact to `reached-raw/`.
Independent native/model probes are under `call125-review-native/` in the same
archive. The [producer review](../coverage/semantics/magic-producer-unpack-review.json)
records their hashes, tested revisions, limits and recovery.
The joined actual-tail strict425 report is
`call125-author-native/joined-09ffc-b37bdd972/report.json` under the same archive.

CALL126 native requests, retained comparisons, strict failures and accepted
source/state cuts are under
../php-spec-evidence-archive/call126-author-native/ and call126-review-native/.
The author accepted-summary.json binds 14 exact original outcomes and eight
reached groups with 245 reported assertions. All twelve finished state raw
directories, including four failed attempts, moved intact to the author
reached-raw/ directory. The
[Aggregate call review](../coverage/semantics/aggregate-call-unpack-review.json)
records hashes, tested revisions, compatibility bridges and recovery commands.
The actual CLASS146-tail joined strict426 report is
call126-author-native/joined-class146-3e6ab7fc8/report.json under the same archive.

## Commit provenance and recovery

[The commit map](history-commit-map.tsv) maps all 428 pre-cleanup commits to the
filtered history. Commit messages and historical report IDs deliberately retain
their original provenance. All old trees differ only by the archived paths;
authorship, timestamps, messages and parent topology are retained. The cleanup
policy/documentation commit follows the mapped old tip.

The local full backup is `../php-spec-history-backup-20260915/`: `git-dir/`
contains original objects, refs, configuration, index and reflogs; `worktree/`
contains the complete pre-cleanup working directory, including ignored tools and
unfinished evidence. Parent index/config snapshots, the commit map, removal list,
checksums and verification records are retained there too. The backup preserves
the original submodule configuration, so commands inspecting it must supply
both paths, for example from this project root:

```sh
git --git-dir=../php-spec-history-backup-20260915/git-dir \
    --work-tree=../php-spec-history-backup-20260915/worktree fsck --full
git clone --local --no-hardlinks ../php-spec-history-backup-20260915/git-dir ../php-spec-before-cleanup
```

The clone recovers original tracked history; ignored tools/evidence are available
separately in the backup worktree. Full submodule restoration also requires its
original `.git` indirection and the parent gitlink; consult the saved parent index
before replacing a newer workspace. The rewrite never changed the backup refs.

This operation is local and does not push. The restored `origin/master` reference
is mapped local history, not a claim that the remote was updated. Publishing needs
a coordinated remote history replacement, followed by the parent repository's
updated submodule pointer. Existing clones must adopt the rewritten history;
merging or fetching old refs can bring the removed objects back. Keep the backup
until that coordination is complete. The pinned corpus still contains a 96 MiB
TeamPass database log, so this cleanup does not eliminate every large-file warning.

OB01 request-end output evidence is retained uncompressed under
`../php-spec-evidence-archive/ob01-author-native/` and `ob01-review-native/`.
The [review](../coverage/semantics/output-request-end-review.json) binds the
15 exact normal source cuts, six reached groups/238 assertions, private strict427
and actual-tail joined strict429.
`accepted-summary.json` maps all nine original state directories to their intact
external locations. The failed/stopped packets, 90/40-second abnormal timeouts
and model-unrun captured-throw boundary retain their separate zero-credit status.

OB02 evidence is under `../php-spec-evidence-archive/ob02-author-native/` and
`ob02-review-native/`. The [review](../coverage/semantics/output-final-throw-review.json)
links four exact fatal sources, three reached groups/131 assertions and the
original failed packets. `accepted-summary.json` maps the three intact state
directories and both affected actual-tail guard cuts under `reached-raw/`.
The joined431 record pins candidate `1262bd31b`; no native or differential source reruns were needed.
Earlier stage/timing probes are diagnostic-only;
the late full-source timeout retains zero credit alongside its later justified
75-second exact comparison. Maintained sources/protocols regenerate the behavior;
external archives are evidence, not build inputs.

CLASS169 finite anonymous trait adaptations retain their native originals in
`.tools/class169-review-artifacts/` and supervised runs in
`.tools/class169-artifacts/`. Its `recovered-private-raw/locations.json` maps the
26 reaped private raw roots; the review artifact root has a separate
`recovered-state/locations.json` for the three review attempts. Restore a mapped
root at its original path with the retained Git cut and pinned local tools to
reproduce source identities. The [feature record](../coverage/semantics/anonymous-trait-adaptations-review.json)
separates exact agreements, reached checks, compatibility bridges and failures;
raw files stay outside Git.

CLASS170 inferred anonymous Stringable views retain eight frozen originals under
`.tools/class170-review-artifacts/` and supervised runs under
`.tools/class170-artifacts/`. Its `recovered-private-raw/locations.json` maps 16
reaped source/contract roots; the review artifact root's `recovered-state/locations.json`
maps the accepted four-group fixture. The [feature record](../coverage/semantics/anonymous-trait-stringable-review.json)
binds exact source agreements, scope/forgery and contract checks, and the original
interpreter/Unsupported/fixture failures. Raw files stay outside Git; restore a
mapped root at its original path with the retained Git cut and pinned local tools
for its original source context.

CLASS171 dynamic anonymous trait views retain native originals under
`.tools/class171-review-artifacts/` and `.tools/class171-artifacts/`; the latter's
`recovered-private-raw/locations.json` maps 14 completed source/state roots,
including failures. The review root's `recovered-state/locations.json` locates
its three-group fixture. The [feature record](../coverage/semantics/dynamic-anonymous-traits-review.json)
binds nine exact originals, strict433, author82, independent263 and affected79.
The original own-constant example remains native-only; its failed state, the
display mismatch and source timeout retain zero credit. Restore original mapped
paths at the retained cuts and pinned local tools for replay. Raw stays outside Git.

CLASS172 own anonymous constants retain eleven native pins under
`.tools/class172-review-artifacts/` and the reused author original under
`.tools/class171-artifacts/`. Supervised runs are in `.tools/class172-artifacts/`;
its `recovered-private-raw/locations.json` maps thirteen source/state roots,
including the failed author sort-prefix fixture. The review root's
`recovered-state/locations.json` maps its five-group fixture.
The [feature record](../coverage/semantics/anonymous-own-constants-review.json)
binds eleven exact originals, strict433, author75 and independent192. Earlier171
native-only/failure credit remains unchanged. Restore original mapped paths and
retained cuts with the pinned local tools for replay; raw remains outside Git.

GC56's finite direct WeakMap foreach originals and raw failures are under
`../php-spec-evidence-archive/gc56-finite-byvalue-foreach/`; independent source
and fetch/budget evidence is under
`../php-spec-evidence-archive/gc-finite-byvalue-foreach-peer-56/`.
The [review](../coverage/semantics/gc-finite-byvalue-foreach-review.json) records
the tested cuts, source/semantic/report hashes and exact recovery commands.
These external packets are evidence only; no earlier GC52–55 evidence is renewed.

GC57's active direct-foreach current-Key read originals are under
`../php-spec-evidence-archive/gc57-active-foreach-read/`; independent source
and result-owner/budget evidence is under
`../php-spec-evidence-archive/gc-current-key-foreach-read-peer-57/`.
The [review](../coverage/semantics/gc-foreach-current-read-review.json) binds
the implementation, source/refusal/owner evidence and recovery commands.
GC56's accepted source and fetch evidence retains its original cuts.

GC58's protected current-row replacement originals, baseline and native-only GC
probe are under `../php-spec-evidence-archive/gc58-current-row-replacement/`.
Independent source and the sole 169-condition publication/release/budget front
are under `../php-spec-evidence-archive/gc-current-row-replace-peer-58/`.
The [review](../coverage/semantics/gc-foreach-current-replacement-review.json)
binds the source/runtime cuts and raw recovery paths; earlier GC evidence is unchanged.

GC59's last-owner current-row originals, native tuples, failed fresh-case
localization and affected retry are under
`../php-spec-evidence-archive/gc59-current-row-last-owner/author/`.
Independent originals and the sole actual callback/owner/budget front are under
`../php-spec-evidence-archive/gc-current-row-last-owner-peer-59/`.
The [review](../coverage/semantics/gc-foreach-last-owner-read-review.json)
binds the borrowed claim protocol, tested cuts and raw recovery paths.

GC60's quiet-primitive originals, native tuples and sole preimplementation baseline
are under `../php-spec-evidence-archive/gc60-current-row-quiet-scalars/author/`.
Independent present-NULL originals and the sole no-incoming-owner/claim/budget
front are under `../php-spec-evidence-archive/gc-current-row-scalar-peer-60/`.
The [review](../coverage/semantics/gc-foreach-quiet-scalar-review.json) binds the
grouped scalar scope, exact runtime/source cuts and raw recovery paths.

GC62 direct old-Value destructor originals and the single weak-live/call/storage
ownership front are under `../php-spec-evidence-archive/gc62-current-row-own-destructor/author/`
and `../php-spec-evidence-archive/gc-current-row-own-peer-62/`.
The [review](../coverage/semantics/gc-foreach-own-destructor-review.json) records
the exact source cuts and preserves the initial producer/baseline fixture refusal
with zero agreement; earlier GC59–61 evidence is unchanged.

GC63 own-Value declared-slot originals and the actual own-to-Child ownership
front remain under `../php-spec-evidence-archive/gc63-own-declared-slots/author/`
and `../php-spec-evidence-archive/gc-own-slots-peer-63/`.
The [review](../coverage/semantics/gc-own-declared-slots-review.json) retains
native/source cuts, the genuine fresh Child/inner/outer snapshot and zero-credit
preparation failures; earlier GC59–62 evidence is unchanged.

GC64 Child/own pending-Exception originals and the actual Previous/parent-owner
front remain under `../php-spec-evidence-archive/gc64-child-pending-handoff/author/`
and `../php-spec-evidence-archive/gc-child-pending-peer-64/`.
The [review](../coverage/semantics/gc-child-pending-handoff-review.json) records
the genuine pre-fix pending/Previous state, native handoff and current source/front
cuts; its baseline/diagnostics retain zero agreement and GC63 is not replayed.

GC65 finite fresh Previous-chain source and focused second-handoff ownership
front remain under `../php-spec-evidence-archive/gc65-finite-previous-handoff/author/`
and `../php-spec-evidence-archive/gc-finite-previous-peer-65/`.
The [review](../coverage/semantics/gc-finite-previous-handoff-review.json) records
the promoted exact GC64 boundary original/native identity and new model cut;
its historical native reference and GC65 baseline retain zero credit. Previously
accepted GC64 originals and its invariant matrix retain their recorded cuts.

GC66 retained incoming-array originals and the focused outer-copy/CV-release
front remain under `../php-spec-evidence-archive/gc66-retained-array-callback/author/`
and `../php-spec-evidence-archive/gc-retained-array-peer-66/`.
The [review](../coverage/semantics/gc-retained-array-callback-review.json) retains
the one preimplementation Unsupported cut and exact normal/fresh source, shared
descendant, nonlast-release and candidate observations. Earlier GC65 sources
and invariant matrix keep their original cuts.

GC67 own-Value array-slot originals and the actual retired-array/Child-release
front remain under `../php-spec-evidence-archive/gc67-own-array-slots/author/`
and `../php-spec-evidence-archive/gc-own-array-peer-67/`.
The [review](../coverage/semantics/gc-own-array-slots-review.json) retains the one
preimplementation baseline, genuine descendant shape, corrected interpreter/
dispatch/fixture failures and fixed-cap timeout as zero-credit cuts;
earlier GC63–66 originals and invariant matrices keep their recorded identities.

GC68's single retained raw-NAME overwrite observation is under
`../php-spec-evidence-archive/query-lost-rc-assessment/native-witness-v1/`.
Its model promotion and focused native-count kernel checks are under
`../php-spec-evidence-archive/gc-native-rc-excess-68/author/`; the independent
actual-state front is under `../php-spec-evidence-archive/gc-native-rc-peer-68/`.
The [review](../coverage/semantics/gc-native-rc-excess-review.json) separates that
one source agreement from constructed controls and preserves the original
owning-NAME refusal and preparation failures at zero credit. No native rerun
or earlier source matrix is claimed.

GC69 declared-property excess originals and the focused graph/GC/store front
remain under `../php-spec-evidence-archive/gc-native-rc-properties-69/author/`
and `../php-spec-evidence-archive/gc-native-rc-graph-peer-69/`.
The [review](../coverage/semantics/gc-native-rc-property-graph-review.json) keeps
both allocation-order comparisons and the original owning-NAME refusal distinct.
Earlier GC68 source and invariant checks retain their recorded cuts.

GC70 COW/unpack reference-copy originals and the actual shared-cell front remain
under `../php-spec-evidence-archive/gc-hidden-reference-copy-70/author/`
and `../php-spec-evidence-archive/gc-native-reference-peer-70/`.
The [review](../coverage/semantics/gc-hidden-reference-copy-review.json) retains
the original supported-but-wrong COW result at zero credit and separates the
corrected source comparisons from singleton/self-reference countercontrols.
Earlier GC68/69 sources and matrices are not replayed.

GC71 retained-array raw-NAME originals and the actual old/new-header COW front
remain under `../php-spec-evidence-archive/gc-array-native-cow-71/author/`
and `../php-spec-evidence-archive/gc-array-native-peer-71/`.
The [review](../coverage/semantics/gc-array-native-cow-review.json) separates the
single old owning-NAME refusal from exact original comparisons and physical
header/descendant count controls. It also preserves the driven old-header GC visit
counterexample and its exact separation-receipt correction. Earlier source
matrices retain their cuts.

GC72 ordinary item-reference COW originals and the focused CELL/header receipt
front remain under `../php-spec-evidence-archive/gc-item-reference-native-72/author/`
and `../php-spec-evidence-archive/gc-item-reference-peer-72/`.
The [review](../coverage/semantics/gc-item-reference-cow-review.json) separates the
already-matching pre-edit console comparison from the actual unbuffered old-header
visit counterexample. Acquisition's borrowed CELL and REF_NAME's later result
are separate phases; earlier array-credit and reference-copy matrices keep their cuts.

GC73 singleton/shared quiet scalar reference-array originals and the two-facet
copy/write front remain under `../php-spec-evidence-archive/gc-array-alias-native-73/author/`
and `../php-spec-evidence-archive/gc-scalar-alias-peer-73/`.
The [review](../coverage/semantics/gc-scalar-alias-cow-review.json) keeps the old
DIRECT-only NAME refusal separate from exact comparisons, singleton old-cell
preservation and shared external/sibling write-through. Earlier matrices retain their cuts.

GC74 inline-Child COW originals and the selected-target/sibling state front stay
under `../php-spec-evidence-archive/gc-cow-child-decrement-74/author/` and
`../php-spec-evidence-archive/gc-copied-target-peer-74/`.
The [review](../coverage/semantics/gc-copied-target-decrement-review.json) separates
the already-matching pre-edit console result from the genuine unbuffered-Child
candidate omission; the diagnostic has zero acceptance credit.

GC75's borrowed-root lookup contrast and affected GC74 native-v2 promotion stay
under `../php-spec-evidence-archive/gc-borrowed-array-writeback-75/author/` and
`../php-spec-evidence-archive/gc-borrowed-root-peer-75/`.
The [review](../coverage/semantics/gc-borrowed-array-writeback-review.json) keeps
earlier partial/zero records unchanged and distinguishes the borrowed phase
from real variable, reference-payload and Child replacement events.

GC76's retained owning-reference original and actual unused-result prefix stay
under `../php-spec-evidence-archive/gc-unused-reference-result-76/author/`;
the independent genuine-CV-removal contrast and focused state checks stay under
`../php-spec-evidence-archive/gc-unused-reference-peer-76/`.
The [review](../coverage/semantics/gc-unused-reference-result-review.json) preserves
all GC75 preparation records and records new comparisons separately. The prefix
has zero agreement credit; it confirms the earlier hypothesis at the real release.

GC77's singleton owning-ALIA original and the existing admission baseline stay
under `../php-spec-evidence-archive/gc-owning-alias-77/author/`; the repeated shared
cell original and actual mixed-release/frame prefix stay under
`../php-spec-evidence-archive/gc-owning-alias-peer-77/`.
The [review](../coverage/semantics/gc-owning-alias-cow-review.json) separates
singleton unwrap from shared payload destruction, constructed extra-owner
and copied-sibling counters, and source-native job order. It retains separate
positive-subset/extension cuts and all preparation/compile zeros.

GC78's assignment/view original and actual pre-edit header-count mismatch stay
under `../php-spec-evidence-archive/gc-header-owners-78/author/`; the quiet-slot
reference/view contrast and focused owner/progress checks stay under
`../php-spec-evidence-archive/gc-header-owners-peer-78/`.
The [review](../coverage/semantics/gc-shared-header-owner-review.json) keeps the
actual unbuffered-header baseline separate from two source comparisons and real
old-view removal. Current 280/265 conditions retain a literal 55/50 slice and
affected 225/215 checks; the failed facets and post-report recorder failure stay
zero. Prior GC77 and earlier cuts are not replayed or relabeled.

COMP215 attributed owning class/interface initializer originals and strict476
checks remain under `../php-spec-evidence-archive/comp215/`.
The [review](../coverage/semantics/deprecated-owned-class-constant-notice-review.json)
binds four first-attempt normal originals,287 positive-state conditions and the
sole test-observer elaboration zero. Runtime16e changes only the source gate;
normal replacement/retry and existing update consumers retain their prior laws.

GC79's singleton-owning-alias original and pre-edit COW-delete tuple stay under
`../php-spec-evidence-archive/gc-unset-copy-79/author/`; the shared/repeated-alias
contrast, focused checks and same-table scratch-cache localization stay under
`../php-spec-evidence-archive/gc-array-unset-peer-79/`.
The [review](../coverage/semantics/gc-array-unset-copy-review.json) records two
final source comparisons, retained90/85 plus affected201/196 conditions, and
all compiler/semantic/diagnostic zeros. The actual combined476 load is separate.

COMP216 direct-global owning API originals and strict477 checks remain under
`../php-spec-evidence-archive/comp216/`. The
[review](../coverage/semantics/deprecated-owned-class-constant-api-review.json)
binds two normal originals,220 positive-state conditions and three precise zero
records: copied native directory selector, old acquisition Unsupported and test
namespace escaping. Actual da125a43/477 load-only evidence stays distinct.

COMP217 multi-constant group originals and strict478 checks remain under
`../php-spec-evidence-archive/comp217/`. The
[review](../coverage/semantics/deprecated-multi-constant-group-review.json)
binds two first-positive normal originals,185 state conditions and precise
baseline/setup/peer-observer zeros. Native435, testedda125+489 and actualbee478
cuts stay distinct; no original native/source replay.

GC80's ordinary assignment/view original, actual zero-unit mismatch and strict
load records stay under `../php-spec-evidence-archive/gc-ordinary-cow-80/author/`;
the reference/view original and single focused front stay under
`../php-spec-evidence-archive/gc-ordinary-cow-peer-80/`.
The [review](../coverage/semantics/gc-ordinary-direct-cow-review.json) records two
first complete sources and one whole282/267 state run, including a state-only
DIRECT deletion slice and real last-view retirement. Baseline/structuring zeros
and the separate actual joined478 load keep their own identities.

GC81's ordinary singleton quiet-reference original, pre-edit header-visit tuple
and strict load stay under `../php-spec-evidence-archive/gc-ordinary-alias-81/author/`;
the shared/repeated original and whole first state packet stay under
`../php-spec-evidence-archive/gc-ordinary-alias-peer-81/`.
The [review](../coverage/semantics/gc-ordinary-quiet-alias-review.json) pins two
first complete comparisons and365/350 conditions, including state-only deletion,
constructed caller-authentication controls and genuine ARRAY/CELL retirement.
The baseline remains diagnostic0. Actual combined63a9/479 load0 and its narrow
source-default composition bridge remain separate; no historical replay.

GC82's singleton quiet-ALIA acquisition original, actual pre-edit header tuple
and strict480 load stay under `../php-spec-evidence-archive/gc-alias-reference-82/author/`;
the shared/repeated original and whole first state packet stay under
`../php-spec-evidence-archive/gc-ordinary-alias-reference-peer-82/`.
The [review](../coverage/semantics/gc-ordinary-alias-reference-review.json) pins
two first complete comparisons and290/280 conditions: fresh versus reused CELL,
nonvisiting header TEMP and real wrapper retirement. The baseline is diagnostic0;
the first peer runner stops before PHP and remains preparation0. Actual post82
combinedb773/480 load0 and its thin source-default bridge are separate.

GC83's second-binding original, actual pre-edit count tuple and two strict loads
stay under `../php-spec-evidence-archive/gc-reference-result-count-83/author/`;
the third-binding/rebinding original and whole first state packet stay under
`../php-spec-evidence-archive/gc-reference-result-count-peer-83/`.
The [review](../coverage/semantics/gc-unused-reference-owner-count-review.json)
pins two first complete comparisons and 244/234 conditions, including both
directly superseded owner-cap controls, real binding/unused-pop separation and
genuine CV VALUE cleanup. The earlier peer original is preparation; the prefix
has diagnostic credit zero. Historical GC76 198/193 raw/hash/cuts are unchanged;
only its two superseded current expectations change, without an old-suite replay.

Root scalar-DAG originals, pre-edit tuple and strict482 load stay under
`../php-spec-evidence-archive/gc-scalar-array-dag-85/author/` and
`../php-spec-evidence-archive/gc-scalar-array-dag-peer-85/`.
Two-DIM originals, pre-edit tuple and strict484 load stay under
`../php-spec-evidence-archive/gc-nested-scalar-array-86/author/` and
`../php-spec-evidence-archive/gc-nested-scalar-cow-peer-86/`.
The [root-copy review](../coverage/semantics/gc-quiet-scalar-array-dag-review.json)
retains two comparisons and 198/188 at private 482; the
[nested-copy review](../coverage/semantics/gc-nested-scalar-array-cow-review.json)
retains two comparisons and 221/211 at private 484. Both whole packets passed on
first execution. Pre-edit tuples have diagnostic/source credit zero. Accepted
composition and the pre86 257f/485 load0 do not renew either private cut.

COMP218 keyword method-body originals and strict479 checks remain under
`../php-spec-evidence-archive/comp218/`. The
[review](../coverage/semantics/deprecated-keyword-class-constant-review.json)
binds two originals,208 state conditions, old Unsupported/before-execution parser/
constructor-cache observer zeros, and the unchanged-assertion peer helper cleanup.
Actual2b408/479 load-only evidence does not renew the private source/state cuts.

COMP219 nonpublic constant originals and strict480 checks remain under
`../php-spec-evidence-archive/comp219/`. The
[review](../coverage/semantics/deprecated-nonpublic-class-constant-review.json)
binds two originals,187 state conditions and the old Unsupported/relation-emitter
zeros. Protected DIRECT COW remains a real source contour; actual1e384/480 load-only
evidence does not renew private cuts or claim whole-GC identity.

COMP220 originals, pre-installation pool localization and focused state checks
remain under `../php-spec-evidence-archive/comp220/`. The
[review](../coverage/semantics/deprecated-class-constant-message-review.json) binds
two originals/240 conditions, three failed attempts and two completed diagnostic
partitions at zero credit, plus actual joined481 load-only facts. Git refs and
raw inputs/results are retained; normal tools do not depend on private trees.

COMP221 originals, the current-selection partition and two focused state fronts
remain under `../php-spec-evidence-archive/comp221/`. The
[review](../coverage/semantics/deprecated-cv-class-constant-review.json) binds
two originals/208 conditions, the baseline and operand-observer failures plus
corrected diagnostic partition at zero credit, and actual joined482 load-only
facts. Exact raw inputs/results and Git refs remain; private trees are not tools.

COMP222 native originals, the unchanged-model baseline and two focused state
fronts remain under `../php-spec-evidence-archive/comp222/`. The
[review](../coverage/semantics/deprecated-cv-member-constant-review.json) binds
two originals/225 conditions, the sole Unsupported baseline at zero credit,
request-carrier representation limits and actual joined483 load-only facts.
Exact raw inputs/results and Git refs remain outside the normal runtime.

COMP223 native originals, the unchanged-model baseline, completed pair partition
and two focused state fronts remain under `../php-spec-evidence-archive/comp223/`.
The [review](../coverage/semantics/deprecated-dual-cv-constant-review.json) binds
two originals/224 conditions, the baseline and diagnostic at zero credit, exact
pre-consumption pair authority and actual joined484 load-only facts. Original
bytes/path/CWD, raw results and Git refs remain separate from runtime inputs.

COMP224 originals, the old-model Unsupported baseline and two focused state
fronts remain under `../php-spec-evidence-archive/comp224/`. The
[review](../coverage/semantics/deprecated-keyword-cv-member-constant-review.json)
binds two originals/288 conditions and the separate actual joined485 load-only
cut. Exact inputs, raw process records and Git refs remain outside runtime inputs.

COMP225 originals, the old-model Unsupported baseline, fixture parse failure and
affected focused-state results remain under `../php-spec-evidence-archive/comp225/`.
The [review](../coverage/semantics/deprecated-pooled-member-constant-review.json)
binds two originals/234 conditions and the separate actual joined486 load-only
cut. Original inputs, raw process records and Git refs remain outside runtime inputs.

COMP226 originals, the old-model Unsupported baseline and two focused state
fronts remain under `../php-spec-evidence-archive/comp226/`. The
[review](../coverage/semantics/deprecated-compiled-class-constant-review.json)
binds two originals/246 conditions, exact class-string normalization and the
separate joined487 load-only cut. Original inputs, raw records and Git refs remain.

COMP227 originals, the old-model Unsupported baseline and two focused state
fronts remain under `../php-spec-evidence-archive/comp227/`. The
[review](../coverage/semantics/deprecated-call-member-constant-review.json) binds
two originals/247 conditions, closed-producer/captured-result limits and the
separate joined488 load-only cut. Original inputs, raw records and Git refs remain.

COMP228 originals, the old-model Unsupported baseline and two focused state
fronts remain under `../php-spec-evidence-archive/comp228/`. The
[review](../coverage/semantics/deprecated-rvalue-member-constant-review.json) binds
two originals/223 conditions, original-operand and completed-continuation bounds,
and the separate joined489 load-only cut. Original inputs, raw records and refs remain.

COMP229 originals, the old-model Unsupported baseline, two before-execution
failures and affected checks remain under `../php-spec-evidence-archive/comp229/`.
The [review](../coverage/semantics/deprecated-rvalue-class-constant-review.json)
binds two originals/268 conditions, original-string normalization and saved-class
authority, plus the separate joined490 load-only cut. Original inputs, raw records
and Git refs remain.

COMP230 originals, old-model Unsupported baseline, completed 36-premise diagnostic
and its import-path setup failure remain under `../php-spec-evidence-archive/comp230/`.
The [review](../coverage/semantics/deprecated-rvalue-class-member-constant-review.json)
binds two originals/274 conditions, actual orphan-marker cleanup and the separate
joined491 load-only cut. Diagnostic/setup packets earn no source credit; original
inputs, raw records and Git refs remain.

COMP231 originals, the old-model Unsupported baseline and two focused state
fronts remain under `../php-spec-evidence-archive/comp231/`. The
[review](../coverage/semantics/deprecated-cv-class-rvalue-member-constant-review.json)
binds two originals/231 conditions, object retirement before notice and inherited
CV-acquisition limits, plus the separate joined492 load-only cut. Original inputs,
raw records and Git refs remain.

COMP232 originals, the old-model Unsupported baseline and two focused state
fronts remain under `../php-spec-evidence-archive/comp232/`. The
[review](../coverage/semantics/deprecated-keyword-rvalue-member-constant-review.json)
binds two originals/308 conditions, actual caller-method CODE/scopes and normal
receiver lifetime, plus the separate joined493 load-only cut. Original inputs,
raw records and Git refs remain.

COMP233 originals, old-model Unsupported baseline, missing-service-response fixture
and affected checked-response group remain under `../php-spec-evidence-archive/comp233/`.
The [review](../coverage/semantics/deprecated-compiled-class-rvalue-member-constant-review.json)
binds two originals/240 conditions, late class publication after member effects,
raw FIELD0 authority and the separate joined494 load-only cut. Original inputs,
raw records and Git refs remain.
