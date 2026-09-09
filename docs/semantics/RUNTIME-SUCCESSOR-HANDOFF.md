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
and deep prepass barriers. That checkpoint catalog had 1,484 sources. Independent
private gates include 177 value/location cases, 71 context cases, eight dense
programs/4,152 assertions and compiler alternatives. Canonical production helper,
compiler, ownership/origin/bridge gates pass; the final source/raw audit passes all1,484 exact originals and25 negatives. Original prepass, callable-line and computed-line failures are retained.

## Accepted compound source checkpoint

Code `63028b5a`, reports `76129823` add all twelve compound source forms in 55,
using pure 54 integer/byte/concat/power operations and 06–09 power helpers. The
independent evidence is `d61eccde`; review/status is `3c0ab4e7`. Final 2,639 exact source
comparisons and 25 negatives pass on `c394a6e7`; no semantic family closes.
Canonical compound.py has 951 runtime programs/13,454 assertions and 1,155 unique
new source selections; the full source catalog is 2,639. Dedicated compiler tests
cover 289 lints, 34 access paths, 24 emission observations and 12 context boundaries.
Independent tests cover 277 programs/5,393 assertions and 324 lints/156 access paths.
The prior source filename failure was infrastructure: operator-bearing logical IDs
contained slashes. validate.py now prewrites all sources to unique ordinal paths,
retaining original logical IDs/bytes; independent hostile-ID checks cover collisions,
separators, NUL, Unicode, surrogates and long names. All twelve canonical/independent final reports share the new closure; earlier
passing reports are historical.

Production 20/30/39/45/46/54/55 and modules.json are the accepted implementation.
Old compound drafts and generators are historical: do not restore old this guards
or parent-line behavior. Corrected private baselines are 46-compound-checked and
55-compound-checked. [UPDATES](UPDATES.md) records the value/location protocol.
Target/name/key preparation occurs once; delayed CV reads, self-CV dimensions and
eager direct FETCH_THIS preserve engine ordering. Array += retains same-table no-op
and separates before union so reference singleton ownership stays exact.

Two independently exposed draft defects are retained with separate resolutions.
Compound direct/literal $this is lint-valid, then fails at eager global FETCH_THIS;
there is NO static direct-this rebinding guard, unlike plain assignment/unset.
An invalid RHS can therefore fail during compilation first. Final dimension
operator diagnostics use the captured DIM/APPEND opcode line, while the compiler
expression descriptor retains its final context after RHS compilation. Computed
name acquisition retains its own stored line. Immutable 72 this originals, 72 line
observations and three exact runtime line failures are bound to canonical sources.
No defect is an engine disagreement.

## Immediate next interfaces

Compiler4 owns private nullable ordinary-array items and parser-concat metadata,
including exact constant-prepass traversal/omission ordering. Keep these snapshots
outside watched inputs until its own reviewed publication, then rebase all widened syntax
consumers by structural type identity. ARRAY_NEXT ABSENT needs an explicit raw
helper boundary; reached source omissions are compiler errors, not runtime errors.

Private array-unpack-transfer.watsup defines array_unpack(state,target,value,line).
It borrows source/target roots, preserves source iteration order, renumbers integer
keys, replaces string keys, uses merge_item singleton-reference unwrapping and stops
on append overflow. Scalars throw Error with value-specific true/false type names.
Its 25 state/owner assertions are helper-only evidence. Compiler scalar errors apply
only to fully constant arrays; overflow defers. Runtime task admission, Traversables
and source differential/resumption tests remain pending.

Private 56-casts-checked.watsup defines cast_apply(state,pcast,value,line) with
CASTBOOL/CASTINT/CASTFLOAT/CASTSTRING/CASTARRAY; enum belongs in 20. It returns KNOWN
values and exact diagnostics, preserves existing array IDs, allocates scalar/null
arrays and passes abrupt states through. Its 155 native observations/496 assertions
are helper-only evidence. The initial missing NaN-to-array warning is retained in
cast-array-nan-original.json, then repaired in the distinct checked helper.
Compiler eligibility remains separate: all NaNs, out-of-range float-to-int,
float/array-to-string and object casts do not constant-fold. Ordinary casts compile
an operand then emit a conversion; void is discard with delayed-CV behavior, while
unset has distinct early-prepass versus late-ordinary static rejection.

Private 57-bitnot.watsup uses separate bitnot_apply(state,value,line), avoiding
numeric-unary rejection overlap; 31 native cases/87 assertions pass. Independent
19-input/57-assertion review adds every byte, raw byte strings, subnormals, maximum
finite values and signed64 conversion boundaries (bitnot-independent-review.json). Private
30-ordinary-runtime adds CAST_RESULT, BITNOT_RESULT, CONCAT_LEFT and CONCAT_RIGHT;
39-ordinary-runtime adds the captured concat operand root. 58-ordinary-expressions
schedules seven binaries through existing BINARY_LEFT/RIGHT, five casts, bitnot and
void via EVAL+DISCARD. 59-concat-expressions captures constant flags from compiled_read
child origins, evaluates both operands, preconverts constants left-to-right, then
resolves delayed operands and concatenates. Constant scalar conversion is warning-free
because the compiler emitted those warnings; constant arrays stringify at final
operator line. These task drafts elaborate but have NOT passed source execution.
805 exact native source originals are in ordinary-runtime-originals.json, awaiting
the joint compiler snapshot. Compiler4 separately retains 28 concat timing originals.

The task drafts still use production generated phpType names. Reapply their tiny
30/39 edits to compiler4's nullable-remapped snapshots before a joint source gate;
58/59 have no generated phpType references. Compiler4's ordinary-operator-draft
snapshot is currently unelaborated: its precompound 20 lacks power_complete required
by current 54. Rebase from accepted compound 20, preserving all existing helpers,
pbin variants and twelve update projections; do not restore stale precompound code. draft-ordinary-runtime.py regenerates
30/39/58 against current production; do not use it blindly after nullable publication.
56-casts-checked is the fixed helper; 56-casts retains the original NaN-array omission.
Private helper/task input hashes are in runtime-next-inputs.json (same .tools directory).
Independent cast review includes ten core-only NaN attribution sources and 62 owner,
reference, cycle, signed-zero and abrupt-state assertions. Source frames/objects remain
unadmitted; pure helper validation does not close source obligations.

Connect remaining ordinary binary/bitnot/casts and array unpack in bounded source
milestones after required compiler prerequisites. Concat has per-constant-operand
compile conversions and constant-array CAST timing, so generic binary scheduling
alone is insufficient. Literal-concat variable names need parser provenance;
ternary-computed names differ. Computed plain this binding/unset remains an owned
existing environment boundary. ??= needs quiet-read/memoized-write semantics.
Destructuring, foreach stable cursors, frames/calls, declarations/linking, objects,
dynamic sources, callbacks, lifetime and source GC remain pending. Complete core
is unfinished; preserve the documented namespace-relative static divergence.
