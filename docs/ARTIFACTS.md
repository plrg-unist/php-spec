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
