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
