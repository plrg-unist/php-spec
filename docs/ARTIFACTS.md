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

Keep future compressed raw traces, source snapshots and tool copies in this
external archive (using new paths for new evidence) or in ignored `.tools/`.
Commit concise reports and manifests with hashes and locations. Preserve raw
failures and interrupted runs externally; do not force-add their archives.
The coverage compression patterns in `.gitignore` guard against reintroduction.

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
