# Runtime continuation

Read PLAN, PROGRESS, AGENTS and the php/php-spec/p4-spectec skills first. Root
orchestrates; compiler owns static/frontend work and reviewer owns independent
evidence/PROGRESS. Never push. The oracle is pinned local PHP 8.5.10 CLI NTS64;
semantic answers after checked syntax are pure executable `.watsup`. Complete core
remains unfinished. Read [runtime interfaces](RUNTIME-BRIDGE-HANDOFF.md),
[compiler continuation](COMPILER-HANDOFF.md) and the current review checkpoint.

## Preserved corrections

Comparison code `0e065cc6`, reports `c94459fd`, review `390ad301` connect seven
operators for six current values. [COMPARISONS](COMPARISONS.md) records unordered
values, recursion, reversed greater operands and overflow-prefix provenance.
Both consumed comparison archives remain fingerprint-bound and byte-identical;
never erase original disagreement records or relabel stale fingerprints.

Wrapper code `3585707a` and review `5b0dc0f2` repaired five original FETCH/UNSET
differences, but inadvertently marked ordinary computed-name writes as references.
Correction `84d70299`, reports `fa691044`, review `24c681d7` separate initialized
`fetch_write_name` from true `acquire_name`: only the latter adds wrapper history.
All seven callers were audited; WRITE_DYNAMIC is the sole ordinary-fetch caller.
The bounded correction passed 40 independent sources, prior 79 wrapper sources,
49 state assertions and ownership; its full source refresh is shared with inc/dec.
All original failures remain archived, with resolutions separate.

[REFERENCE-WRAPPERS](REFERENCE-WRAPPERS.md) defines stable REFCELLS history.
Writes and singleton unset preserve markers; fresh ordinary bindings are unmarked.
Copying may unwrap a singleton ALIAS without erasing its original wrapper. Markers
add no roots and cannot enter isolated compiler pools. Generic FETCH/intermediate
UNSET differ from final ASSIGN_DIM/UNSET_DIM false-conversion warnings. Collection
checks remain graph-helper evidence, not source GC admission.

## Accepted inc/dec source checkpoint

Code `7d5718fb`, reports `5b24a5f8` integrate 05 and new 53 with
20/30/40/41/45/46. Independent review accepts 1,484 exact sources +25 negatives
on `d399263a`; see incdec-review.json and PROGRESS. [UPDATES](UPDATES.md) defines captured RW
locations, copied prefix/postfix results, diagnostics and current global `$this`.
Four PFSTOP barriers stop constant preparation without suppressing later ordinary
compilation. PPRW allows append and uses separate target/key access descriptors.
Callable-expression line metadata and disjoint nullsafe rejection priority are
required even for statically rejected targets.

Direct/literal `$this` uses eager FETCH_THIS in the global-only source machine;
computed reads and updates use distinct local-name protocols. BASE_NAME carries
its own compiler line: dynamic RW fetching uses that stored line, while direct CV
fetching keeps its containing opcode line. Seven retained multiline originals
expose four earlier draft differences; canonical cases include all seven exactly.
No arbitrary constant-fact equality may classify a computed name as direct.

Canonical `incdec.py` has 154 runtime programs/2,226 assertions and 271 source
selections including all 108 compiler phase originals, eight emission originals
and deep prepass barriers. The complete catalog has 1,484 sources. Independent
private gates include 177 value/location cases, 71 context cases, eight dense
programs/4,152 assertions and compiler alternatives. Canonical production helper,
compiler, ownership/origin/bridge gates pass; the final source/raw audit passes all1,484 exact originals and25 negatives. Original prepass, callable-line and computed-line failures are retained.

## Next bounded work

Twelve compound assignments have an actual private prototype, not source admission:
`.tools/draft-compound-source.py` writes 30/39/55-compound drafts;
`.tools/draft-remaining-operators.py` writes 20/54 numeric/byte/power dispatch.
`.tools/probe-compound-source.py` previously passed 81 originals/1,204 assertions,
recorded in `.tools/compound-source.json`. Its loaded drafts predate current code:
never restore old acquisition or dynamic-name lines. A distinct current rebase in
`.tools/rebase-compound-runtime.py` writes `20-compound-runtime`,
`30-compound-rebased`, `39-compound-rebased`, `55-compound-rebased`; it consumes the
fresh compiler `20/45/46-compound-compiler` drafts and production 53.
`python3 .tools/probe-compound-rebased.py` now repeats all 81 originals/1,204 checks
successfully, with actual loaded hashes in `.tools/compound-rebased-source.json`.
This is author-only prototype evidence, still requiring independent source/phase
review and expanded coverage before publication.
The scalar-key warning draft failure remains in
`.tools/compound-order-draft-original.json`; the prototype repairs it.

Compiler needs fresh twelve shape projections, PFSTOP barriers, PPRW order and
explicit direct `$this` compound rebinding rejection. Old 46-update predates the
nullsafe/this fixes. Runtime captures target/name/key once, distinguishes delayed
CV RHS reads and self-CV dimension cases, retains generic FETCH versus final
DIM_OP errors, and gives array `+=` its same-table no-op/in-place separation path.
Ordinary binary dispatch, casts, computed plain `$this` binding/unset and exact
parser-folded concatenation names remain owned follow-ups. Concat names are an
existing explicit compiler-line boundary; ternary-computed names differ. `??=`
requires its separate quiet-read and memoized write protocol.

Destructuring/unpack runtime remains pending after compatible metadata fixes.
Foreach needs stable bucket/cursor identity and mutation ownership. Calls/frames,
declarations/linking, objects, dynamic sources, callbacks, lifetime and source GC
remain pending. Preserve the documented namespace-relative `static` divergence;
none of the corrections above is an engine disagreement.
