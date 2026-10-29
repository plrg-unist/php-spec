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
directories under `reached-raw/`. Earlier stage/timing probes are diagnostic-only;
the late full-source timeout retains zero credit alongside its later justified
75-second exact comparison. Maintained sources/protocols regenerate the behavior;
external archives are evidence, not build inputs.
