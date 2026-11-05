# Core PHP semantics progress

This project targets PHP 8.5.10 CLI, NTS, 64-bit. Executable core semantics and
source-driven differential validation are active; complete PHP core, the later
Rocq interaction-tree model and BOLA/CRIS verification remain unfinished.
[PLAN](PLAN.md) records settled scope; the [feature inventory](coverage/semantics/features.json)
and current family documents identify implemented routes and remaining obligations.

## Current checkpoint

I84–I91 cover selected typed magic, captured and raw method Generator
factories; Fiber SEND/THROW and reference caches; and array/string method
Closure binding and identity. Joined source and reached-state gates validate
these bounded routes. Original failures retain zero credit in the linked
ledgers. Wider signatures, callback/API entry, delegation and lifecycle
combinations remain partial. [Generators](docs/semantics/GENERATORS.md),
[Fibers](docs/semantics/FIBERS.md), [Closure calls](docs/semantics/CLOSURE-CALL.md);
reviews [I84](coverage/semantics/generator-magic-factory-review.json),
[I85](coverage/semantics/generator-direct-magic-review.json),
[I86](coverage/semantics/generator-captured-method-body-review.json),
[I87](coverage/semantics/generator-raw-method-factory-review.json),
[I88](coverage/semantics/generator-raw-method-cache-review.json),
[I89](coverage/semantics/generator-captured-method-throw-review.json),
[I90](coverage/semantics/generator-direct-magic-throw-review.json), and
[I91](coverage/semantics/generator-string-method-closure-review.json).

Published enum `cases()`/`from()`/`tryFrom()` support admitted direct,
captured and pipe calls through method strings and class/case arrays. Selection
and original bytes survive argument rebinding and named Stringable callbacks;
internal Closure captures add no owner of an input array or receiver. Callable
typed parameters and `Closure::fromCallable` share these generated targets.
The [enum/callable scope](docs/semantics/SOURCE-CLASSES.md) and
[feature inventory](coverage/semantics/features.json) retain the individual cuts.

Published enum `is_callable` queries cover generated, absent and syntax-only
methods, source-certified magic fallback and direct public case methods.
Malformed live arrays return false before syntax-only lookup. Positional name
output accepts admitted literal/string-variable inputs and initialized scalar
CVs, preserving spelling and the captured reference cell. A first-SEND receipt
keeps a variable input fixed through later callbacks, output aliases and nested
queries; argument throws skip the query's assignments.
[Saved-input review](coverage/semantics/enum-is-callable-saved-input-review.json).

Retained childless ordinary output objects delay destruction until their last
owner leaves. Last-owner output clears to NULL before the destructor, then
commits the saved name before return, throw or root VM exit. Unset/rebinding,
resurrection and API trace snapshots retain real cells and owners. Root exit
drains locals before the C pin; nested queries preserve status and skip
interrupted result assignments.
[Retained](coverage/semantics/enum-is-callable-output-retained-review.json),
[unique](coverage/semantics/enum-is-callable-output-unique-review.json) and
[exit](coverage/semantics/enum-is-callable-output-exit-review.json) reviews.

Cleanup throws now cancel exit and commit the name before propagating.
Compiled CV order preserves shared-wrapper decrements and exception previous chains;
integer exit status survives catch and later string exit. Eight new/promoted
source agreements, one affected enum exit-status source, three explicit
controls, strict433 and 256+47 independent guards pass at their recorded cuts.
[Cleanup review](coverage/semantics/enum-is-callable-output-cleanup-review.json).
Nested cleanup exits now return through their own C pins and preserve the
original output receipt. The latest integer exit supplies status; string exit
preserves it. Ordinary Child throws cancel exit while the name still commits;
nested queries commit their separate names without assigning abandoned booleans.
Nine source agreements, three explicit Unsupported controls, strict433 and five
separate reached groups (90+62+35+43+78 checks) pass at recorded cuts.
[Reexit review](coverage/semantics/enum-is-callable-output-reexit-review.json).
Two-entry live enum callable arrays now carry a first-SEND receipt through
positional name output. Class strings preserve spelling, case receivers use the
canonical class, and the sent array survives source rebinding and same-cell
output. Old-output destruction can rebind or throw before the saved name commits.
Seven exact agreements, two explicit Unsupported controls, strict435 and four
separate reached groups (60+53+33+70 checks) pass at recorded cuts.
[Variable-array review](coverage/semantics/enum-is-callable-variable-array-review.json).
An aliased source/output cell can now rebound to a new two-entry direct-string
array after the first SEND. The old selected name overwrites that cell, while a
separate holder keeps the rebound array live; a pre-output throw leaves the
rebound array and result assignment target untouched. Four exact agreements, one explicit
Unsupported owning-object control, strict435 and five separate reached groups
(64+50+53+29+33 checks) pass at recorded cuts.
[Array-alias rebound review](coverage/semantics/enum-is-callable-array-alias-rebound-review.json).
An exact rebound array with one ordinary childless object follows two owner
paths: last-owner output clears the shared cell before destruction, while a
separate holder delays destruction until after the saved name commits. A
throwing child commits the name before exception transfer without assigning
the interrupted result target. Three exact agreements, one excluded-builtin
control, strict435 and three separate reached groups (53+60+87 checks) pass
at recorded cuts. [Owning-array review](coverage/semantics/enum-is-callable-array-alias-owning-review.json).
A rebound array may lose its shared-cell owner while a distinct variable still
owns its ordinary child object. The array's eager release completes before
that variable is cleared, so its destructor sees the committed name; clearing
the variable before output gives the existing null-before-destructor path.
Three exact agreements, strict435 and separate held75/released55 reached
checks pass at recorded cuts. [Retained-child review](coverage/semantics/enum-is-callable-array-alias-retained-child-review.json).
Live two-entry callable arrays now retain their real reference cells through
the first SEND. Invocation reads current receiver/method payloads and freezes
the selected name and boolean before output destruction; later reference
mutation, output aliases and throwing cleanup preserve that selection.
Borrowed snapshots add no owners. Shared and singleton COW keep their ordinary
array behavior. Seventeen originals agree; two explicit controls and four
separate reached groups pass at their recorded cuts.
[Reference-member review](coverage/semantics/enum-is-callable-reference-array-review.json).
Literal, assignment-result and value/reference-return arrays now share that
receipt and invocation snapshot. Actual SEND transfers retain the table without
an extra pin; argument throws release a last referenced child before catch and
skip output/result assignment. Nine originals agree; the
[temporary-array review](coverage/semantics/enum-is-callable-temporary-array-review.json)
records source-bound transfer/owner/resumption checks.
First-SEND capture now accepts initially invalid untyped members and defers
callable admission until invocation. Borrowed old object/array history survives
its actual retirement without adding owners or resolving class names. Current
type-invalid pairs return false/`Array`, including syntax-only queries; output
repair/throw preserves that selection, and argument cleanup runs after the
handler with the result still unassigned. Sixteen originals agree at recorded
cuts, with independent history178 and focused55/37 checks in the
[initial-member review](coverage/semantics/enum-is-callable-initial-members-review.json).
Wrong-length and missing-key arrays now receive false/`Array` through the same
receipt, using one structural check and their real SENT owner. Source repair,
same-cell output, retained holders and owning-entry cleanup preserve the saved
shape and assignment order. Typed payload references are ignored when only the
bad shape matters; typed valid pairs remain partial. The
[structural-array review](coverage/semantics/enum-is-callable-structural-array-review.json)
records the exact source and ownership cuts.
The selected `is_callable` signature now acquires a simple third-output CV by
reference at SEND3 independently of query admission. Missing CVs become null
without an undefined-variable read; real owners preserve retained old aliases,
callback-created outputs and dynamic saved targets. Earlier argument throws
skip acquisition. The [output-acquisition review](coverage/semantics/enum-is-callable-output-acquisition-review.json)
records the bounded source/state cuts and the separate native-only fixed
namespace-fallback target obligation.
Cleanup exit with an ordinary Throwable already pending, switched Fiber
completion/force-close, other owning rebound arrays, late attached type sources,
wider variable arrays, typed/backed/debt valid-pair cells, named/unpacked output,
loading and wider enum
member/lifetime contexts remain partial.

I92 gives real user Generator Closure::call entry its actual copied Closure and
new receiver, with separate API owners and ordered used/ignored-result cleanup.
The saved Gen keeps its copy through CLOSED without an API wrapper or later
API trace. Five native/model originals and private433 pass at recorded cuts;
six reached fronts pass 744 custom/774 reported checks at separate fixture cuts.
Original Unsupported and two fixture failures retain zero credit. Native-only
receive-error retention and reference formals remain partial. Joined strict433,
four exact sources, API-entry99, unused-result81 and independent closed143 checks
pass at a84bf6c0; 3486d56c composition is reviewed. Wider calls remain partial.
[I92 review](coverage/semantics/generator-call-copy-review.json).

I93 extends real Generator Closure::call copies to admitted reference
formals. Copy/static ownership precedes warning callbacks; fresh formal cells
wrap frozen values afterward. Used Generator results survive API cleanup, and
warning traces retain the real handler and call frames. Five private native/model
sources and six reached fronts pass at their recorded cuts; joined strict433,
three exact I93 sources, one affected I92 value SEND source, temporary return92
and independent parked-cache169 states pass at f34d1214a. Original failures
retain zero credit. Receive/callback/mapping errors and wider calls remain
partial. [I93 review](coverage/semantics/generator-call-reference-review.json).

I94–I98 cover fake user-method Generator Closure::call copies, finite bound
source histories and distinct dynamic/folded string policies. Fake copies keep
shared method statics and exact declaring-class receivers; normal/abrupt binding
warnings release actual API owners in native order. Existing reference-warning
cursors also survive Fiber suspension in handlers and owning retval destructors.
Each milestone retains its original native/source/reached cuts and failures.
Joined strict433, four source comparisons and 187 custom/192 reported ownership
checks pass at their recorded cuts; see the [joined review](coverage/semantics/generator-call-series-current-review.json). Wider
call/receiver/signature, mapping, no-Gen receive and abrupt warning contexts remain
partial. Reviews [I94](coverage/semantics/generator-fake-call-copy-review.json),
[I95](coverage/semantics/generator-fake-string-call-review.json),
[I96](coverage/semantics/generator-folded-string-call-review.json),
[I97](coverage/semantics/generator-call-warning-fiber-review.json) and
[I98](coverage/semantics/generator-call-warning-retval-review.json).

I99 handles PHP throws during copied reference warnings, including a Fiber throw
in an owning handler-return destructor. Only the hidden copy stays request-owned;
prepared prefix and API owners release before catch. Four native originals,
three CLI comparisons and two reached fronts (237 custom/247 reported checks)
pass; one front also matches repeated native output without extra CLI credit.
The affected 59/64 trace checks and joined strict433 pass at recorded cuts.
Receive/mapping and bailout paths remain partial.
[I99 review](coverage/semantics/generator-call-cancellation-review.json).

I100 extends hidden-copy cleanup to ordinary unknown/overwritten named arguments
and required named holes. Generated Error traces retain raw arguments until the
Error is released; prepared argv and original source owners still retire in order.
Three native/source originals, one affected successful call and strict433 pass.
Two joined reached fronts pass 243 custom/253 reported checks. Original baseline,
compile and fixture failures retain zero credit. Later receives, default throws
and bailout paths remain partial.
[I100 review](coverage/semantics/generator-call-mapping-review.json).

I101 replaces required-hole-specific retention with one authenticated restored
API cursor for admitted pre-Generator receive failures. Arity, type and default
throws preserve the copy while callee cells retire before API arguments/source.
Three native/source originals, strict433, new259 custom/269 reported checks and
the affected129/134 hole recipe pass. A matching adapter and joined default134/139
gate load current434, covering changed weak-free cleanup. Baseline and fixture
parser failures retain zero credit; wider producers, collection and bailout
contexts remain partial. [I101 review](coverage/semantics/generator-call-receive-review.json).

I102 admits exit during copied reference warnings and named default construction
before Generator creation. Handler restoration, failed-constructor suppression
and ordered prepared/API cleanup keep the hidden copy through shutdown. Two
native/CLI originals, strict434 and304 custom/314 reported reached checks pass.
The joined peer loads435 and covers shared destructor return and adapter changes.
Original semantic/fixture failures retain zero credit; wider cleanup, owning
retval, Fiber and bailout paths remain partial.
[I102 review](coverage/semantics/generator-call-exit-review.json).

I103 carries ordinary exit through an owning copied-warning retval destructor,
its Child and the real C cleanup before handler/API release. The hidden copy
survives through shutdown; fake and real originals agree at exit29/41. Strict435,
author151/156 and independent joined peer192/197 pass at their recorded cuts.
Earlier interpreter, compiler, descriptor, timeout and peer fixture
elaboration failures retain zero credit. At this cut, a cleanup throw replacing
the pending exit and wider bailout remained partial.
[I103 review](coverage/semantics/generator-call-cleanup-exit-review.json).

I104 validates the existing cleanup-throw path: a supplied plain Child exception
replaces the pending exit before Generator creation. Catch/finally run, cleanup
frees retval/Child and prepared owners, and a final string exit retains status41.
The pinned native and unchanged-model source agree; joined reached153/158 checks
cover the pending transfer, owner counts and shutdown. At that cut, aliased
throws, repeated cleanup exit and wider lifecycle remained open.
[I104 review](coverage/semantics/generator-call-cleanup-throw-review.json).

I105 carries a second exit through the owning warning retval's Child and
remaining fields before copied-call CLEAN and API release. A literal string
exit keeps status29; an independent integer exit changes41 to53. Native/source
pairs, strict435 and two reached fronts (349 custom/359 reported) pass at their
recorded cuts. The unchanged-model mismatch and first author fixture failure
retain zero credit; wider nested exit, pending-Throwable, Fiber and GC paths
remain partial. [I105 review](coverage/semantics/generator-call-repeated-exit-review.json).

I106 was automatically stopped for possible cybersecurity risk; private work remains preserved, with zero integration or validation credit.

I107 validates the existing normal return after an owning copied-warning
retval and its Child/After fields retire. The handler resumes the second fresh
reference; fake and captured real copies then create and use a Generator even
after the source CV clears. Two native/model source comparisons, fake full
reached116/121 and independent real joined handoff82/87 pass. The first
fixture error and timed-out full peer retain zero credit; wider Fiber, GC and
warning cleanup remain partial.
[I107 review](coverage/semantics/generator-call-cleanup-return-review.json).

I108 admits ARRAY-packed real and fake Generator `Closure::call` through the
existing collector. Retired source arrays leave nonowning authenticated history;
canonical RAW selects named entry and freezes values through reference warnings.
The saved value gets a fresh cell despite caller-alias replacement, and deferred
inner duplicate-name errors retain warning priority and raw API traces. Five
original source agreements and independent 84/89 ownership/reference-resumption
checks pass with the full 435-module SL manifest at their recorded cuts. Computed
method names, Traversable packs and wider lifecycles remain partial.
[I108 review](coverage/semantics/generator-call-array-pack-review.json).

I109 routes native Generator named/ARRAY-packed arguments through one shared
collector, then transfers its exact receiver/value roots into the ordinary
Generator argument cursor. Case-sensitive names, pack-local ordering and early
unknown/duplicate errors preserve initialization and trace priority. Array COW,
copied reference values and a sole receiver survive source-variable retirement.
Five unique source agreements (including the positional control), one explicit
Unsupported control with zero agreement, and the final 83/88 reached gate pass
at recorded cuts with the full 436-module SL manifest. Earlier runtime, diagnostic
and fixture failures retain zero credit. Dynamic selection, Traversable inputs,
specialized delegated histories and wider lifetimes remain partial.
[I109 review](coverage/semantics/generator-method-arguments-review.json).

I110 admits literal nullsafe native Generator API calls through the existing
receiver/argument protocol. NULL skips named-CV reception and spread producers;
nonnull calls preserve their selected receiver, copied values and method-result
handoff. Ignored owning zero-argument getter copies release before the receiver,
while used copies survive. Source checks distinguish cache-destructor weak
liveness, supplied cache-destructor throws and actual empty-pack normalization.
Seven unique originals agree, one
Unsupported assertion earns zero agreement, and the 83/88 ownership gate passes
with the full 436-module SL manifest. Earlier mismatches retain zero credit.
Native API callable creation, Traversable inputs, wider delegation and lifetimes
remain partial.
[I110 review](coverage/semantics/generator-nullsafe-method-review.json).

I111 freezes computed native Generator method selection before arguments in a
nonowning receipt. Receiver/name CV rebinding cannot change the target or named
parameter mapping; exact CONFIG-to-operation transfer preserves all owners.
NULL skips both producers; invalid method-name types avoid Stringable conversion
and unknown methods fail before arguments/initialization. The prior computed
named-send Unsupported original is promoted to normal. Shared binding/__invoke
site classification keeps its truth table with disjoint clauses. Three unique
originals agree; the 97/102 ownership/authority gate, including eight pure site
views, passes with the full 437-module SL manifest. Earlier runtime and fixture
failures retain zero credit. Wider callable, Traversable, delegation and lifecycle
combinations remain partial.
[I111 review](coverage/semantics/generator-computed-method-review.json).

I83 gives implicit invokable-object factories and direct Generator-bodied
`__invoke` calls one compiled-source/runtime-effective-method proof. Direct entry
requires the live receiver; a bounded lookup view authenticates retired factory
history without another owner. Finite forwarding and actual lexical/called
scope retain the ordinary receiver/cache/SEND owners. Five new originals agree
at their recorded cuts; five reached fronts pass 374 custom/399 reported checks,
including live-entry refusal, close/forwarding, parked BYREF input/cache owners
and budget continuation. Private strict432 retains its original cut; actual-tail
joined strict433 passes at the integration cut. The original SL-overlap and fixture-syntax failures
retain zero credit after narrow corrections. Wider implicit/callback/API,
delegation, collection and lifecycle combinations remain partial.
[I83 review](coverage/semantics/generator-invokable-factory-review.json).
[I82](coverage/semantics/generator-bound-factory-review.json),
[I81](coverage/semantics/generator-array-string-factory-review.json) and
[I80](coverage/semantics/generator-captured-factory-review.json) retain their
original scope and tested cuts.

GC06 carries an authenticated claimed count source through canonical materialized
ordinary destructor callbacks and PASS1, including retired original tables.
Ordered nested buffer removal preserves proxy-table count roles and free slots:
one first pass contributes 1 after debit 2, then retrace contributes 3.
Source-authenticated immediate `===`/`!==` temporary release and borrowed
matching `BASE` caches avoid false potential roots. Four native-first sources
agree at their recorded cuts; 11 reached SL groups pass 330 checks. Private
strict430 and actual-tail joined strict431 pass. WeakMap callbacks, skipped
prior histories, worker/residual/reentry paths, hooks, active contexts and wider
cache lifetimes remain partial.
[GC06 review](coverage/semantics/gc-materialized-claimed-callback-review.json).

GC07 carries canonical materialized destructor collection through ordinary
named-function and method callers. Current locals, saved caller locals and real
receivers keep their existing roots; GC sites must belong to the authenticated
caller body. Successful `WeakReference::create()` argument retirement and unused
local result-cache transfer preserve native potential-root order. Four new
native-first originals agree exactly, including resurrection count -1 followed
by later count 3. Nine reached SL groups pass 392 checks at their recorded
cuts. Private strict431 and compact AL/SL metadata controls pass; joined
actual-tail strict432 compilation passes at the integration cut. Fiber, worker,
residual, reentry, hooks and wider cache/table lifetimes remain partial.
[GC07 review](coverage/semantics/gc-caller-materialized-review.json).

GC08 skips potential-root buffering for enum cases, following Zend's
`GC_NOT_COLLECTABLE` flag. Cached cases retain their class-constant owner and
WeakReference identity; ordinary collectable objects still enter the physical
buffer in real order. One native-first source agrees exactly and a native status
witness plus two strict reached groups (47 checks) distinguish the buffer slots.
Joined actual-tail strict432 compilation passes; graph traversal and owner
counting are unchanged. Other builtin eligibility and wider collection contexts
remain partial.
[GC08 review](coverage/semantics/gc-enum-collectability-review.json).

GC09 records Zend's allocation-time `GC_NOT_COLLECTABLE` flag for receiverless
fake Closures created by the modeled named, intrinsic, method, constant,
fromCallable and Fiber capture routes. Clones and bind copies allocate without
that flag; bound fake and real Closures remain collectable. Two native status
batches distinguish these cases, three new sources agree exactly, and three
strict reached groups pass 153 checks. Actual-tail strict433 compilation passes;
GC graph traversal and owners are unchanged. Wider collection contexts remain
partial.
[GC09 review](coverage/semantics/gc-fake-closure-collectability-review.json).

GC10 admits direct calls through a plain childless real Closure as canonical
materialized collector callers. The active GC receipt binds the caller and its
real machine root; the Closure stays outside the white set while unrelated
Closures remain refused. One native-first original agrees exactly, a strict
pre-begin diagnostic passes 23 checks, and the affected reached group passes
87 checks. Private strict432 and actual-tail joined433 compilation pass.
Explicit `->__invoke`, pipe, captured and wider active collector contexts
remain partial.
[GC10 review](coverage/semantics/gc-closure-caller-review.json).

GC11 admits a normal literal, zero-argument `->__invoke()` call through a live
global variable holding a plain static real Closure without captures,
attributes, a by-reference return or a declared return type. Its wrapper owns
two current Closure roots and the global cell supplies a third owner; the existing
active caller and count rules still protect the held sibling. The native-first
original agrees exactly, a pre-edit reached diagnostic passes 24 checks, and
the private strict reached group passes 95 checks; the current-tail group passes
96 after the global receiver guard. The independent computed-receiver refusal
passes 18 strict checks; joined OB05 strict96 and the unchanged native/model
original also pass.
Calls with arguments, computed receivers,
attributes, return declarations, nullsafe selection and wider active contexts
remain partial.
[GC11 review](coverage/semantics/gc-closure-invoke-caller-review.json).

GC12 admits a complete childless by-value capture in a live direct real-Closure
collector caller. A scalar `use ($seed)` source agrees with PHP; a pre-edit
reached diagnostic passes 28 checks and the affected strict reached group
passes 95. The active caller, machine root and empty child set still guard the
ordinary count walk; object/reference captures and static cells remain outside
this cut. [GC12 review](coverage/semantics/gc-captured-caller-review.json).

GC13 admits one unbuffered, childless ordinary `stdClass` capture under an
authenticated live direct real-Closure collector caller. The captured object
stays outside the white set through the Closure's real root. One native-first
original agrees exactly, a pre-edit diagnostic passes 35 checks, and the
affected strict reached group passes 103. This cut left buffered leaves,
captured object graphs and reference/array captures fenced.
[GC13 review](coverage/semantics/gc-object-leaf-caller-review.json).

GC15 admits the same childless capture after a real post-`P|0` copy release
buffers it again. The live Closure keeps the token black; the second pass
removes its physical slot before the D/held count plan. A native status witness
shows roots 0→1 after that release. One new source agrees exactly; the new
strict reached group passes 103 checks and the affected GC13 group passes 101.
The old constructed buffered-token refusal is superseded; object graphs,
reference/array captures and wider collector contexts remain fenced.
[GC15 review](coverage/semantics/gc-rebuffered-leaf-caller-review.json).

GC16 admits one runtime-written, childless array capture in the active direct
real-Closure caller. The model binds the same nonimmutable array in the global
cell, Closure capture and entered local; both ordinary and physical GC tracing
find no child edge. A native status control observes roots 0→1 after an owning
copy release, and the original source agrees exactly. Pre-edit reached checks
pass 43; the affected strict group passes 106. At that cut, buffered active
array captures remained fenced; COW after capture, nonempty persistent
provenance and wider collector contexts are untested.
[GC16 review](coverage/semantics/gc-array-leaf-caller-review.json).

GC17 admits that same childless array after an owning copy release following
`P|0` buffers it for the D pass. The rooted capture keeps the real array black,
and its slot leaves the count plan before held/drop destruction. A native status
control observes roots 0→1; one source agrees exactly. Pre-edit reached checks
pass 45, the new strict group passes 106, and the affected GC16 group passes
104 after removing its superseded constructed buffered-array refusal. COW and
nonempty persistent provenance remain untested; graph/count/owners are unchanged.
[GC17 review](coverage/semantics/gc-rebuffered-array-caller-review.json).

GC18 admits one runtime-written array capture with exactly one direct childless
`stdClass` entry. The active direct Closure caller remains machine-rooted; the
array and leaf are unbuffered, with matching ordinary and physical GC edges.
One native-first source agrees exactly, a pre-edit reached group passes 54,
and the strict affected group passes 115. The final source read proves child
liveness only. At that cut, buffered array or leaf candidates and wider entry
shapes remained fenced; COW and nonempty persistent provenance were untested.
[GC18 review](coverage/semantics/gc-array-object-child-caller-review.json).

GC19 admits that same array after a post-`P|0` owning copy release buffers it
for the D pass. The globally held childless `stdClass` remains unbuffered, and
the live Closure keeps the array black. Native status observes roots 0→1; one
original agrees exactly. Pre-edit reached checks pass 57 and the strict D
group passes 118, including removal of the real array slot before held/drop
counting. Leaf candidates and wider entries remain fenced; COW and nonempty
persistent provenance are untested. Graph/count/owners are unchanged.
[GC19 review](coverage/semantics/gc-rebuffered-array-child-caller-review.json).

GC20 admits that childless `stdClass` when releasing one owning local copy
buffers it after the array. Native status observes roots 0→1→2; the exact
original agrees, and 122 strict reached assertions bind both ordered slots,
their removal from the D plan, and the rooted Closure/array/leaf owners.
Pre-edit model refusal remains zero credit. At that cut, wider entries,
backedges, COW and nonempty persistent provenance remained open.
[GC20 review](coverage/semantics/gc-buffered-array-child-leaf-caller-review.json).

GC21 admits two distinct childless `stdClass` entries at array keys 0 and 1
under the same direct Closure caller. The array and key-0 leaf are buffered;
key-1 stays outside the buffer. One pinned original agrees, and 136 strict
reached assertions check both slots, black removal, owners and a duplicate
child refusal at that cut, superseded by GC25. The pre-edit Unsupported
retains zero credit. At the GC21 cut, wider arrays, backedges and
post-capture COW remained open.
[GC21 review](coverage/semantics/gc-two-array-children-caller-review.json).

GC22 admits the same two-entry array after a third owning copy release
buffers the key-1 leaf. Pinned status sees roots 0→1→2→3; one original
agrees, and 139 strict reached assertions prove three ordered slots,
black D-plan removal and owners 2/3/2/2. A corrected fixture selects D
by collection nonce 2. Pre-edit refusal remains zero credit. At the GC22
cut, broader entries, backedges and post-capture COW remained open.
[GC22 review](coverage/semantics/gc-buffered-second-array-child-caller-review.json).

GC23 admits an ordered node-free scalar capture before one childless
runtime-written array capture in the same direct Closure. A pinned
Reflection control observes `seed,token` order; one original agrees and
110 strict reached assertions bind the capture layout, shared array owners
and source/caller bounds. Pre-edit Unsupported retains zero credit.
[GC23 review](coverage/semantics/gc-scalar-array-caller-review.json).

GC24 admits finite ordered node-free scalar captures around one mutable
one-level array in the same authenticated direct Closure. Its entries may
be direct scalars or childless stdClass leaves in physical order;
compiled-pool descendants and materialized property tables are fenced.
Reversed capture order, three mixed-key leaves and post-capture COW give
three exact source pairs. Strict reached checks pass 113+146 assertions,
and the corrected GC23 group passes 110. Its original duplicate-identity
refusal is superseded by GC25; shared separate captures, aliases, nested
arrays and user-destructor children remained refused at the GC24 cut; GC26
admits the bounded shared-capture case. Earlier Unsupported,
overlap and fixture failures retain
zero credit. [GC24 review](coverage/semantics/gc-finite-capture-review.json).

GC25 admits repeated direct edges to the same childless stdClass inside
that finite captured array. With global strong owners removed, two array
edges keep one leaf alive until Closure release; pinned status sees roots
0→1→2 and then 0. One full source agrees exactly. Strict reached checks
pass 127 new and affected GC21/22/24 groups 137+140+147, proving two
physical edges, one leaf buffer slot, owners 2/2, black D protection and
nested-array refusal. The source-only Unsupported and first fixture error
retain zero credit. [GC25 review](coverage/semantics/gc-duplicate-edge-review.json).

GC26 admits one finite captured array together with direct captures of
childless stdClass leaves already present in that array. Forward and reversed
capture orders match pinned PHP exactly, including weak liveness after the
call and death after Closure release. Two strict D-state groups pass 146
assertions each, proving separate Closure and array edges to the leaf, one
buffer slot, owners 2/2/3 and black protection. Pre-edit Unsupported and a
corrected P4 helper compile failure retain zero credit. Other captured
object layouts and nested or destructor-bearing graphs remain partial.
[GC26 review](coverage/semantics/gc-shared-capture-review.json).

GC27 admits finite direct capture graphs with at least two mutable array
occurrences under the same authenticated active Closure root. Distinct arrays
may share childless stdClass leaves; repeated array captures retain each owner
with at most one candidate slot per identity. Three originals agree exactly,
including a reordered three-array graph with an unrelated direct leaf and final weak death.
Three strict D-state groups pass 204+146+193 assertions, independent review
passes 73, and both affected GC26 groups pass 148. Nested, reference, proxy and finalizer graphs
remain partial; the hidden Closure capture table remains black under the real
caller root. [GC27 review](coverage/semantics/gc-multi-array-review.json).

GC28 admits finite nested DIRECT-array capture DAGs under the same real Closure
root. Unique traversal preserves repeated owner/trace edges; per-array self-reach
rejects forged DIRECT cycles, and the nested-edge guard is component-local.
Shared depth-three nesting, local parent/child COW and an independent self-copy
snapshot give three exact source pairs through final weak death. Strict reached fronts pass 246+191 assertions and the
changed GC27 group passes 207. Independent graph/self-copy fronts pass 63+85.
Reference, proxy, pooled and finalizer graphs remain partial.
[GC28 review](coverage/semantics/gc-nested-array-review.json).

GC29 admits mixed value/reference captures through ordinary untyped HCELLs.
Capture/local aliases own wrappers separately while each wrapper owns its payload
once; surviving reference decrements buffer only a collectable payload. Three
originals preserve shared/separate wrapper lifetime and request-string rebinding,
and one combined A95 original preserves old-cell 22/global 44 through Generator
retirement and actual GC. All four agree; strict reached fronts pass 177+197+154.
Independent mixed COW gives a fifth exact source and 214 further assertions.
Constrained/backed cells, ALIAS array entries
and arbitrary reference/Closure cycles remain partial.
[GC29 review](coverage/semantics/gc-reference-capture-review.json).

GC30 adds quiet inactive WeakReference unregister and standard notification in
terminal cleanup. The association view preserves owning edges while ordinary
field releases/C guards update the local heap; real handle order preserves fast
field shielding and inactive-destructor failure. Eight exact source/request
contexts include all three unchanged OB10 originals on their actual canonical
composition. Author206 and independent341 strict conditions pass. Map/custom
notification remained partial at that cut. [GC30 review](coverage/semantics/gc-inactive-weak-free-review.json).

GC31 adds inactive WeakMap free with all-key unregister before ordered value
release. Later value leases and shared ALIAS payload ownership survive correctly;
retired Maps no longer force unrelated key-field cleanup. Seven exact source/request
contexts cover empty/singleton/multi-entry Maps, AB/BA fatal order, fast/slow alias
cells and an independent all-unregister-before-value discriminator. Author292,
peer172 and affected GC30 HIGHER135 pass (599 total); two key-notification
Unsupported controls retain zero agreement at their original cuts. Key/incoming-Map
notification and active free pins remained partial at that cut. [GC31 review](coverage/semantics/gc-inactive-weakmap-free-review.json).

GC32 adds inactive standard-Key notification before fields. Per-Key registration
rank and surviving value-slot position preserve selective entry removal, duplicate
owners and later Map order; nested notifications retain pending entry/field owners.
Nine exact contexts (eight programs) include the two promoted GC31 originals,
fast/nonfast reference cells and an independent nonadjacent-duplicate discriminator.
Author359, independent208 and affected384 conditions pass (951 reported), with
strict434 at recorded cuts. Original Unsupported, binding/elaboration failures and
the wrong-W first draft retain zero credit. Internal/custom key hooks and active
free pins remained partial at that cut. [GC32 review](coverage/semantics/gc-key-notify-review.json).

GC33 composes inactive internal-Key hooks: WeakReference unregisters its referent
before incoming Map values; WeakMap unregisters outgoing keys and releases own
values before incoming notification. Shared values, self-keys and two incoming
Maps preserve separate owners and registration order. Nine exact positive
contexts/eight programs include nonfast table retirement; at that cut, three
ordinary unset controls stopped before generic retirement with zero agreement.
Author495, independent51 and affected320 conditions pass (866 reported), with
strict435 at recorded cuts. Original source/fixture failures remain zero credit.
Later producer policies, ordinary callback continuations, weak Closure keys and
active free pins remain partial. [GC33 review](coverage/semantics/gc-compound-key-review.json).

GC34 adds ordinary internal-Key callback continuations. Quiet registrations
activate cleanup; per-entry leases and parent/Key pins survive nested throws.
Wrapper unregister precedes incoming callbacks, while Map own values run first;
authenticated callbacks preserve or replace their weak observer. Fourteen exact
normal programs and 464 reported conditions (author233, independent86, affected145)
pass at recorded cuts. The three GC33 ordinary controls are promoted; earlier
mismatch/timeout/fixture stops retain zero credit. Wider producers, freeing-object
escape/mutation and active-pin collection remain partial.
[GC34 review](coverage/semantics/gc-ordinary-key-review.json).

GC36 admits one direct destructor-child property on an ordinary `stdClass`
WeakMap Key, attached before or after first insertion. The physical Key pin keeps
the field owner through Map value cleanup; wrapper registration order changes
Value callback visibility, and Key child release follows weak notification.
Six fresh normal source programs agree (author2, independent4), including a
throwing Value caught after Child cleanup. Author102 and independent70 reached
conditions plus an affected GC32 exact source and 71 reached conditions pass at
their recorded cuts. A two-field producer remains Unsupported with zero agreement;
the original baseline and fixture failures retain zero credit. Wider layouts,
multiple Maps, freeing-object mutation and active-pin collection remain partial.
[GC36 review](coverage/semantics/gc-standard-key-field-review.json).

GC37 admits a methodless user WeakMap Value with one public untyped declared
property owning a child before first insertion into an empty Map. The leaf
`stdClass` Key's retirement removes the Map edge, makes the Value observer's get
null, then releases its sole child through the ordinary storage pin.
Three new exact programs include a caught Child destructor throw; three affected
post-insertion/GC36 sources and 90 source-reached conditions (author46,
independent44) pass at recorded cuts. Occupied replacement remains explicitly
Unsupported with zero agreement. Wider Value layouts, extra child owners,
Map-first teardown and active-pin collection remain partial.
[GC37 review](coverage/semantics/gc-declared-value-child-review.json).

GC38 admits ordinary Map-first retirement of the GC37 one-declared-Child
Value while its leaf `stdClass` Key remains live. The Map unregisters its Key
and transfers its Value owner before the Value releases Child. During Child's
destructor, the Value observer's get is null while the Map observer's get is
still live under the Map storage pin. The new free arm requires no incoming
Map-key registrations; the existing leaf-Value free path remains available.
Three new exact sources (including caught Child throw), two affected exact
sources and 97 reached conditions (author57, independent40) pass at recorded
cuts. Retained Child owners and incoming Map-key registration stop explicitly
with zero agreement. Wider Value layouts and active-pin collection remain
partial; earlier fixture/source drafts retain zero credit.
[GC38 review](coverage/semantics/gc-map-first-value-child-review.json).

GC39 admits ordinary Map-first retirement of a one-declared-Child Value whose
Child has two physical owners: the Value property and one other strong owner.
The Map is the Value's sole owner and has no incoming Map-key registration.
In the tested outside-CV source, Map and Value weak gets become null after
teardown while Child stays live; unsetting that owner later runs its destructor.
The new arm leaves GC37 insertion, GC38 sole-owned Child cleanup and
replacement/foreach unchanged.
Two fresh exact sources (one caught Child throw), two affected exact sources,
and 96 reached conditions (author62, independent34) pass at recorded cuts. At
the GC39 cut, an owner-three Child was Unsupported with zero agreement. Wider
ownership graphs and active-pin collection remain partial; the baseline and
early fixture elaboration failures retain zero credit.
[GC39 review](coverage/semantics/gc-map-first-retained-child-review.json).

GC40 admits Map-first retirement of exactly two entries containing one
sole-owned declared-Child Value and one sole-owned methodless leaf Value.
Both Keys remain live and registered only in that Map; no incoming Map-key
registration or active cursor is admitted. Ordered release keeps the leaf
weakly live during Child's destructor only when its entry follows Value.
Nested Map/Value pins preserve weak visibility through a caught Child throw.
Three fresh originals agree, including Child throws in both positions, and
112 reached conditions (author72, independent40) pass at their recorded cuts.
Map dimension access during the nested callback and two declared-child Values
were explicit Unsupported with zero agreement at that cut. Original-source, ownership
transfer and budget evidence is recorded in the
[GC40 review](coverage/semantics/gc-two-entry-map-first-review.json).

GC41 replaces the two-entry Map-free pairing with a finite fold over direct
methodless leaves and exact one-declared-Child Values. Physical Value and Child
ownership may be shared or retained outside the Map; each slot keeps its own
ordered release job. Repeated Values, shared Children and pending later Child
cleanup compose with the existing physical pins and caught-throw protocol.
Held leaf Keys registered only in this Map, no incoming Map-key registration
and no active cursor remain required. The old two-Child control receives fresh
agreement in this milestone; its GC40 refusal keeps zero historical credit.
Four exact sources (three newly authored, one promoted) and one 85-condition
reached multiplicity/budget group pass at their recorded cuts.
Extra declared fields were Unsupported at the GC41 cut; freeing-Map dimension
access remains Unsupported.
Wider layouts, mutation, active-pin collection and caller contexts remain partial.
[GC41 review](coverage/semantics/gc-finite-map-first-review.json).

GC42 introduced a finite declared-slot layout for direct methodless Map Values:
initially public untyped nonstatic/nonreadonly fields without hooks, holding primitive
leaves or fieldless public-destructor Children. Descriptor identities and keys
authenticate physical declaration order; existing jobs preserve repeated Child
edges and borrowed snapshots add no owners. Reverse writes of `[X,Y,X,Z]` drop
one X owner, then run Y, X and Z while a Y throw preserves pending cleanup.
The previous extra-null-field refusal receives a fresh comparison here.
Three exact sources (two new, one promoted), two Unsupported controls with zero
agreement and one 96-condition reached ownership/budget group pass at their cuts.
Typed and deeper layouts, property aliases/hooks, freeing-Map dimension access/mutation,
active-pin collection and wider contexts remain partial; singleton and ordinary
consumer/type-source rules are unchanged.
[GC42 review](coverage/semantics/gc-finite-declared-properties-review.json).

GC43 shares that finite payload validation with ordinary singleton Map free,
removing the separate one-property and Child-owner1/2 arms. Each release keeps
its actual physical owners: a retained Value survives Map retirement and its
shared Children run only after the outside Value CV later releases. Singleton
multi-field Child throws preserve later field cleanup under the Map pin.
The old leaf/reference fallback and incoming notification behavior remain.
Backed property storage now uses the common nonvirtual-slot check; teardown
never calls getters/setters. An already accepted singleton backed getter and
the old leaf/incoming order are preserved; the old owner3 refusal is freshly
promoted. Virtual/typed/deeper layouts and incoming-Child notification remain
explicit limits; property executors/type-source rules and paused work are unchanged.
Six exact originals (three newly supported, one promoted, two affected), two
Unsupported controls with zero agreement and one 95-condition reached
transfer/budget group pass at their cuts.
[GC43 review](coverage/semantics/gc-singleton-finite-values-review.json).

GC44 admits prebuilt finite methodless Values at first insertion and private-Key
append through the same payload validation. The append arm authenticates the
actual RHS/selected operand and adds one Value edge without copying its Child
edges. Existing entry metadata and the used-result/temporary protocol remain.
An already built Value can enter an empty Map, appear under a second Key, and
coexist with a used-result temporary leaf. Clone producers retain their copied
Child edges; key-first throws preserve the earlier evaluation/cleanup behavior.
Occupied replacement and shared-Key finite payloads remain Unsupported. Other
mutation, quiet/shared-Key/GC admission and ordinary leaf/callback policies are
unchanged; paused work remains untouched. Two newly supported sources and one
affected key-order source agree exactly; two Unsupported controls keep zero
agreement. The append ownership/budget group passes 88 and the focused
first-write guard group passes 24 at separate cuts; earlier fixture failures
keep zero credit.
[GC44 review](coverage/semantics/gc-finite-value-insertion-review.json).

The cumulative GC12–19 join passes seven exact original source pairs and seven
strict SL reached groups (742 assertions) at its frozen cut. One representative
GC12 source pair passes after the A80 and enum-pipe joins; A81's named Generator
factory path is disjoint. Separate native status controls and original failures
retain their own evidence. [Joined review](coverage/semantics/gc-caller-cumulative-review.json).

Immediate identity cleanup now validates a sole produced right object/array
temporary with a borrowed or scalar left operand in both AL and SL. Fourteen
focused conditions pass in each mode, including strict compilation of the actual
431-module tail; the affected cached-enum Stringable original matches PHP again.
Existing owners and collection policy are unchanged.
[Identity receipt review](coverage/semantics/identity-produced-right-review.json).

Earlier [I75](coverage/semantics/generator-keyword-creation-review.json),
[I76](coverage/semantics/generator-keyword-chain-review.json),
[I77](coverage/semantics/generator-keyword-receiver-review.json),
[I78](coverage/semantics/generator-closure-factory-review.json) and
[I79](coverage/semantics/generator-closure-method-review.json) reviews retain
their distinct scope, counts and raw failures.

Scalar Generator unpack reaches fixed untyped reference parameters in argument
positions 1 or 2 of direct named functions returning by value, within the first
two sends. By-value caches keep their Warning snapshot; ordinary reference
caches reread a nonowning source-cell designation after the handler. Alias writes
change delivery, while actual global-name rebinding preserves the old cell.
Distinct private cells retain earlier sends across the second Warning.
A96 extends delivery from the selected live reference cell through cache
replacement, changed keys/index, normal closure and a running Generator in a
suspended Fiber. The next iterator advance retains its ordinary phase behavior.
Closed Generators keep their cache until storage retirement; CELL adds no owner.
By-value delivery retains its existing restrictions. Ineligible reference
carriers and pending warning exceptions remain partial. Eight new and two legacy
source agreements, strict433 and source-derived ownership/continuation gates pass
at their recorded cuts; two Unsupported controls retain zero agreement credit.
Original fixture failures remain preserved separately.
[Snapshot review](coverage/semantics/generator-byref-sink-review.json),
[reference-cell review](coverage/semantics/generator-reference-sink-review.json),
[captured-cell review](coverage/semantics/generator-captured-cell-sink-review.json).

CONFIG Iterator sends preserve scalar snapshots and finite CFG-admitted ARRAY or
ordinary non-Stringable INSTANCE arguments. Existing by-value Generator routes
also copy flat scalars before later resumes; INI_SET conversion, strict errors and
NULL handlers follow traversal and DATA/INPUT cleanup. COW protects array tables,
while embedded aliases, object identity and API TraceArgs retain ordinary owners.
Owning Iterator aborts release CURRENT, DATA/INPUT, then the copied prefix. Admitted
last-owner temporary Iterator INPUT finalizers keep live copied arguments protected.
Typed-source reads and existing producer/key/finite-graph policies stay intact;
named direct-CV Generator reference yields now copy scalars from authenticated
ordinary cells before later writes. One local scalar-cell route retires a CLOSED
Generator from sole DATA through the normal storage pin or quiet terminal cleanup.
Outside aliases can now retain an ordinary scalar cell after that Generator dies;
copied sends and retired source history survive later writes to the cell.
A direct temporary zero-argument BYREF Generator call keeps separate INPUT and DATA
owners; DATA drops first, then final INPUT/storage cleanup precedes API or catch.
A distinct BYVAL factory can return that BYREF Generator while publishing only a
weak observer; its source, owner transitions and weak death have private validation.
An outside-retained named BYVAL Generator now copies finite quiet owning ARRAY
or ordinary INSTANCE sends. The copied prefix survives cache replacement until
INI_SET TypeError trace reception, or retires before a terminal saved catch;
four new sources agree and 296 reached conditions pass at private cuts.
A named BYVAL factory temporary now copies a quiet owning first option and
finishes with an integer cached value; four sources and 372 reached conditions
pass at private cuts, including normal TypeError trace and terminal cleanup.
The joined strict433 and fresh normal source/state gate pass at `04d38dc55`,
which received independent review before guarded integration.
With a scalar first option, the same temporary source admits a finite quiet
owning final cache when its copied last argument protects the cache child.
Four more sources and 405 reached conditions pass at private cuts, including
real storage release and terminal saved-throw cleanup. Typed Generator cells,
effectful finalizers/casts and wider last-DATA reference graphs and lifecycles
remain partial.
The joined strict433 and fresh terminal-throw source/state gate pass at
`c7eb56942`; disjoint I84/ATTR07 changes were independently reviewed before
guarded integration.
Two quiet owning Generator sends now preserve distinct or repeated copied roots
through cleanup. Four frozen object sources, a separate array COW regression,
and 421 reached conditions pass; joined strict433 and terminal source/state
gates passed at `4c6d75817` and `6daa1de90`.
A retained named BYREF Generator now copies a finite quiet owning value from
an ordinary cell before later writes and a scalar send. Four originals and 406
reached conditions pass; joined strict433 and terminal source/state pass at
`186d8c368`.
A final owning BYREF cell value now copies after a scalar send and survives
later cell writes. Four originals and 408 reached conditions pass; joined
strict433 and terminal source/state pass at `86082901b`.
A retained BYREF Generator can keep that final ordinary owning cell through
closed storage while the copied send remains stable. Four originals and 448
reached conditions pass; joined strict433 and terminal source/state pass at
`c5086c205`.
Outside aliases can keep the ordinary owning cell after Generator retirement;
the copied final argument remains stable across later cell writes and COW.
Four originals, 527 reached conditions and an affected 266-condition control
pass; joined strict433 and fresh terminal source/state pass at `a00e229f9`.
A direct temporary BYREF Generator now copies an owning final value from its
ordinary local cell after a scalar send. Four sources and 472 reached conditions
pass; DATA then INPUT cleanup releases the temporary before API or catch.
Joined strict433 and fresh terminal source/state pass at `3699279a5`.
Outside aliases now keep that temporary Generator's ordinary final cell and its
current value after real storage release; copied arguments remain independent.
Four sources and 565 reached conditions pass; joined strict433 and fresh terminal
source/state pass at `9cde7e64d`.
A named BYVAL factory can return a distinct BYREF Generator with a final owning
ordinary cell. Four sources and 512 reached conditions pass; copied arguments
survive DATA/INPUT release and real Generator storage cleanup. Joined strict433
and fresh terminal source/state pass at `1a7c38d0b`.
The cumulative A88-A93 rule shares authenticated copied ITEM and live ordinary
cell sends across retained, direct temporary and BYVAL-factory BYREF Generators.
Six selected originals and four crossed/effectful sources agree exactly; strict433
and 827 reached conditions/11 raw steps pass. Stringable conversion and a
factory-retained Generator stop at exact send frontiers with zero credit.
[Bounded ownership review](coverage/semantics/config-generator-bounded-ownership-review.json).
[Owning arguments](coverage/semantics/config-iterator-argument-review.json),
[INPUT cleanup](coverage/semantics/config-iterator-input-finalizer-review.json),
[Generator scalars](coverage/semantics/config-generator-scalar-review.json),
[Generator reference scalars](coverage/semantics/config-generator-reference-scalar-review.json),
[Sole-DATA reference cleanup](coverage/semantics/config-generator-reference-sole-data-review.json),
[Surviving-alias cleanup](coverage/semantics/config-generator-reference-outside-alias-review.json),
[Temporary reference cleanup](coverage/semantics/config-generator-temporary-reference-review.json),
[Factory reference cleanup](coverage/semantics/config-generator-factory-reference-review.json),
[Owning Generator sends](coverage/semantics/config-generator-owning-value-review.json),
[Temporary owning sends](coverage/semantics/config-generator-owning-temporary-review.json),
[Owning final caches](coverage/semantics/config-generator-owning-cache-review.json),
[Two owning sends](coverage/semantics/config-generator-two-owning-review.json),
[Owning reference snapshots](coverage/semantics/config-generator-reference-owning-review.json),
[Final owning reference snapshots](coverage/semantics/config-generator-reference-owning-cache-review.json),
[Retained owning reference cells](coverage/semantics/config-generator-reference-owning-live-review.json),
[Outside owning-cell aliases](coverage/semantics/config-generator-reference-owning-alias-review.json),
[Temporary owning reference cells](coverage/semantics/config-generator-temporary-owning-reference-review.json),
[Temporary owning-cell aliases](coverage/semantics/config-generator-temporary-owning-alias-review.json),
[Factory owning reference cells](coverage/semantics/config-generator-factory-owning-reference-review.json),
[CONFIG contract](docs/semantics/INCLUDE-SOURCES.md).

ATTR01 adds builtin NoDiscard declarations with literal/NULL messages and
ordinary source-call warnings after sends/named defaults, before reception/body.
Selected references, real argument/receiver owners and caller-only traces survive
handlers and supplied throws; used results and callback APIs remain distinct.
Twenty-six originals agree, and four reached fronts pass 297 checks including 24
derived guards. Joined strict430 and the new FINAL callback control pass;
accepted private cuts are unchanged. Wider messages, targets, hooks and wrappers
remain partial.
[Attribute contract](docs/semantics/BUILTIN-ATTRIBUTES.md),
[review](coverage/semantics/builtin-nodiscard-review.json).

ATTR02 adds literal/NULL-message and since Deprecated declarations for named
functions and ordinary methods. Prepared VM calls warn after sends and named-hole
completion, before NoDiscard and reception, for used and discarded results.
Selected arguments, references and receivers survive handlers and abrupt cleanup.
Thirteen originals agree exactly (nine authored, four independent);
at the ATTR02 cut, two internal API cases were explicit Unsupported with zero
agreement credit.
Four reached fronts pass 314 conditions: 278 source-reached checks, 24 derived
guards and 12 raw API projections. Private and actual-tail joined strict430
pass; earlier failed fixtures retain zero credit. Wider messages, targets,
wrappers and other internal API consumers remain partial.
[Attribute contract](docs/semantics/BUILTIN-ATTRIBUTES.md),
[ATTR02 review](coverage/semantics/builtin-deprecated-review.json).

ATTR03 stages selected error-handler and `assert` callbacks at the internal API
phase: Deprecated precedes copies, by-reference warnings and reception. Error
handlers run with their registry disabled; `assert` warnings retain the active
handler, saved target and live failure policy. Captured Closure targets stay
borrowed until one call owner starts at entry. Ten new native-first originals
agree exactly, including one unmarked control; four reached fronts pass 179
conditions (172 reached, seven derived guards), and private and actual-tail
joined strict431 pass.
The maintained ATTR02 `assert` boundary is promoted without replay or new
agreement credit. Explicit captured-Closure `__invoke()` was still excluded
at that cut; wider API consumers remain partial. [ATTR03 review](coverage/semantics/builtin-deprecated-api-review.json).

ATTR04 extends that selected API cursor to exception handlers, including
unmarked callbacks. Deprecated precedes copies and by-reference warnings;
the moved registry owns the selected callback and the cursor holds the original
Throwable. Warning-handler replacement and nested exception reentry preserve
the original target; Closure call ownership begins at entry and can end before
readonly result validation. Nine new native-first originals agree, including
two terminal fatals. Four reached fronts pass 189 checks (184 reached, five
derived), and private and actual-tail joined strict431 pass. One measured old
API refusal remains zero credit. Effectful special callables remain partial.
[ATTR04 review](coverage/semantics/builtin-deprecated-exception-api-review.json).

ATTR05 stages explicit captured-Closure `__invoke()` wrapper (8192) then callee
(16384) warnings before inner copies, named holes and reception. Raw arguments and live
references survive both handlers; inner Closure ownership begins after fake
named preflight, while trace redaction keeps raw and coerced snapshots distinct.
Nine normal originals agree; a tenth native original was an explicit
unused-owning-result boundary with zero agreement credit at that cut. Six full reached
groups pass 337 checks (328 reached, nine derived), plus a separate bounded
53-check inner-throw diagnostic. Private and actual-tail joined strict432 pass
at separate cuts.
Wider special callables/messages remain partial.
[Wrapper review](coverage/semantics/builtin-deprecated-closure-invoke-review.json).

ATTR06 removes that owning-result fence: existing release jobs retire raw outer
arguments, then the unused by-value return, then the outer Closure receiver.
Each pending owner stays distinct through aliases; destructor callbacks use the
real caller and preserve supplied throws through remaining outer retirement.
Four originals agree: one former boundary uses retained native bytes, and three
new native-first controls cover used results, returned-argument aliases and a
throwing value destructor with caller traces. Three full reached groups pass
186 checks (no derived guards); private and actual-tail joined strict432 pass
at separate cuts. Wider callback, reference-return and reentry histories remain partial.
[Return review](coverage/semantics/builtin-deprecated-closure-return-review.json).

ATTR07 admits builtin literal/NULL NoDiscard and Deprecated on real Closure/arrow
expressions. Checked keyword receipts preserve multiline names/lines; shared and
snapshot captures survive handlers, warnings use selected/rebound scopes, and
Closure calls borrow their bound receiver. Nine eligible originals agree (six
normal, three static rejections); five reached groups pass 428 checks (422 reached,
six derived), focused syntax11 and private strict432 pass. One unsafe `assert`
reentrancy source has an unresolved native lifetime observation, preserved at zero
credit with exact expired-before-copy refusal; the safe control keeps an external
owner. General messages and wider consumers remain partial. The current-tail
join passed strict433 and three retained-native source comparisons at separate
cuts; later disjoint GC, enum, CONFIG and magic Generator changes have a reviewed
compatibility bridge. [Producer review](coverage/semantics/builtin-deprecated-closure-expression-review.json).

ATTR08 gives shutdown/tick FCC caches separate object and Closure owners,
including duplicate object IDs. Raw invokable and array-form tick identities
stay distinct; methods borrow This and inline unregister retires arguments,
cache.object, then cache.closure. Readonly selected metadata validates cleanup
after scope retirement. Quiet shutdown retention continues through FINAL.
Five normal originals agree; four reached groups pass 296 checks (292 reached,
four derived), private strict 432 passes, and one Closure-array control remains
an exact Unsupported boundary/zero credit at that cut; ATTR09 below extends its
tick consumer. The OB05 join passes strict433,
the retained captured-FINAL original, and two new exact raw-invokable originals.
Buffered post-output release reaches two equal FCC owners before retirement;
the affected bound-Closure executor case also passes. Other late-free and wider
callback/compiler forms remain partial. The current-parent bridge retains the accepted
strict and focused source/reached gates across disjoint enum pipe, Generator and
explicit-GC additions.
[Cache review](coverage/semantics/callback-fcc-cache-review.json).

ATTR09 stages cached tick `[Closure,"__invoke"]` calls: 8192 before outer copies,
reference warning 2 with a fresh private cell, then 16384 before inner reception.
The FCC owns the outer Closure; the user call adds one instance and borrows This.
Raw/received sensitive traces stay distinct, and unused results retire after raw
arguments while the cache remains live. Five normal originals agree (four new
native originals plus one retained-native former boundary); four reached groups
pass 302 checks (300 reached, two derived); private strict 432 and joined
strict 433 pass. A retained-native reference-warning/unregister source agrees
again on the corrected cache owners. The first normal deadline and two fixture
failures retain zero credit. Other API wrappers, late free and the older
source-wrapper inner-warning trace-head location remained partial at that cut.
[Tick wrapper review](coverage/semantics/callback-closure-invoke-review.json).

ATTR10 gives that source-wrapper inner warning's handler trace head the real
explicit `Closure->__invoke` call file/line, matching its existing wrapper frame.
One native-first original now agrees exactly; a reached warning state passes 24
assertions and full strict433 passes. The old model's two missing location
predicates remain a zero-credit counterexample. Wider wrapper/reentry and late
callback cleanup remain partial. [Trace-head review](coverage/semantics/builtin-deprecated-closure-trace-head-review.json).

ATTR27 preserves pending C owners when an ignored body-value integer exit replaces
a saved main exit 263. Actual 9/515/519 remains separate from saved phase 263 and
CLI status. A genuine NORMAL/BUDGET canonical unwind and its current singleton
null-C Tick-source frame authenticate a status-only history view. Frame validation
retains that witness before ordinary caller-scope drop; readiness, actual status,
phase facts and148 delivery are unchanged. Five new originals and two affected26
controls agree; strict435 and five independent groups/775 conditions (765 genuine,
ten derived) pass. Original Unsupported and narrow owner-loss diagnostic keep0.
[Replacement review](coverage/semantics/callback-late-tick-body-reexit-review.json).
Earlier [body-value exit](coverage/semantics/callback-late-tick-body-exit-review.json)
retains its normal/stable-main integer/string and 739-condition cuts.
Earlier [handler-value throw](coverage/semantics/callback-late-tick-handler-throw-review.json)
retains its separate disabled-handler/old-Throwable cut.
Earlier [normal handler-value](coverage/semantics/callback-late-tick-handler-value-review.json),
[body-value bailout](coverage/semantics/callback-late-tick-body-throw-review.json),
[body-return](coverage/semantics/callback-late-tick-body-return-review.json),
[handler](coverage/semantics/callback-late-tick-handler-review.json),
[exit/throw](coverage/semantics/callback-late-tick-exit-throw-review.json),
[bailout](coverage/semantics/callback-late-tick-throw-review.json),
[stable-exit](coverage/semantics/callback-late-tick-exit-review.json),
[cache-shape](coverage/semantics/callback-late-tick-callables-review.json) and
[copied-value](coverage/semantics/callback-late-tick-values-review.json) evidence
keeps its original cuts. Unshared owning channels, uncovered selected completion
owners, wider handler/callable/previous-chain/frame contexts and reentry remain
partial.

Tick plans follow Zend compiler order across Switch conditions/bodies, Match
conditions/results, Yield key/value and YieldFrom operands. Compiled unselected
callables contribute lexical declarables. Constant/CV versus temporary cleanup,
assignment/discard lines and ordinary Generator suspension preserve canonical
statement markers and the shared request counter.

Conditional and coalescing plans use published operands, redirects and retained
effects. Bodies erased during compilation and their static errors stay absent;
bodies skipped at runtime still compile. Retained effects run once and real conversions,
jumps and writes break adjacency. Quiet coalesce reads retain lazy RHS execution;
handlerless assignment target children compile once before RHS and memoized
writable refetch. The coalesce slice has seven original agreements, strict
compilation of 437 modules and three runtime fronts/144 reported conditions,
including bindings and one malformed-marker guard, at scoped cuts.
Exact source, strict and reached-state cuts remain in the
[Switch](coverage/semantics/tick-switch-review.json),
[Generator](coverage/semantics/tick-generator-review.json),
[Match](coverage/semantics/tick-match-review.json),
[conditional](coverage/semantics/tick-elision-review.json) and
[coalesce](coverage/semantics/tick-coalesce-review.json) reviews.

Compiler-special builtin/fallback result fences, empty multiline control-body
lines and wider child/result/lifetime contexts remain partial. Multi-operand echo
still lacks between-operand ticks. Registered-handler callable-key coalesce
assignment has an open quiet-reader composition/performance obligation: compilation
and 100-step progress complete, but full execution times out; those runs have zero
agreement credit. Return to that narrow dependency after the priority echo fix.

The earlier GC05 cut admitted public destructors on quiet, canonical
materialized ordinary cycles when the legacy callback walk and claimed walk
agree on ordered visits and counted nodes in the actual collector plan. The
collector rechecks after callback
mutation and before fresh collection of already-called survivors, refusing an
order mismatch. Two native-first sources agree, including resurrection followed
by later count 3; four strict SL reached groups pass 151 checks. Private strict429
and actual-tail joined strict430 compilation pass; source and reached cuts retain
their original inputs. At that cut, count-ambiguous callbacks, WeakMap callbacks,
residual tags, workers, hooks, reentry and active contexts remained partial.
[GC05 review](coverage/semantics/gc-materialized-callback-review.json).

CLASS157 admits public zero-argument anonymous `__toString` through ordinary
implicit Stringable linking and conversion. Raw-header names/counters remain
stable through deferred publication; saved conversion owners release before
emission, destroying the receiver when no other owner remains. Nine originals agree (seven normal, two static rejections), and
285 conditions pass (278 reached, seven controls). Return, never-kind and compile
diagnostics retain their distinct formats. Three changed private and joined strict433 cuts,
native6+2+1, old2 and source/state cuts stay separate; the never-kind mismatch
and fixture elaboration failure retain zero credit. Wider magic, reference,
attribute, callable and lifecycle contexts remain partial.
[Stringable review](coverage/semantics/anonymous-stringable-review.json).

CLASS156 admits public zero-argument anonymous destructors through the ordinary
method compiler and lifecycle. Alias and temporary release, eval callbacks,
reverse global cleanup, escaped failed constructors and pending-exception
replacement have five exact source agreements. Two reached groups pass 240
conditions (228 reached, 12 derived across six controls); private and joined strict433 passes.
Native5/old2, source and state cuts stay distinct. Nonpublic/reference-return/
attributed destructors, other magic methods and wider lifecycle contexts remain
partial. [Destructor review](coverage/semantics/anonymous-destructors-review.json).

CLASS155 admits anonymous array argument unpack through the ordinary
source classifier, array prescan/COW and binder. Embedded aliases stay shared;
direct slots promote only in the live table. Direct elements of value inputs use
fresh cells when reference demand requires them; embedded aliases remain shared.
Expanded names preserve holes/default reception and error priority;
constructorless arrays use the existing dummy send frame. Seven originals agree,
and 242 conditions pass (235 reached, seven derived guards), with private strict432
and actual-tail joined strict433 at separate cuts.
The original native5/old2 and separate literal/no-ctor natives retain their cuts;
projection has no agreement credit.
Traversable constructors, promotion/nonpublic modes and other anonymous magic
methods remain required class work.
[Array-unpack review](coverage/semantics/anonymous-constructor-unpack-review.json).
The prior [variadic review](coverage/semantics/anonymous-constructor-variadic-review.json)
retains CLASS154 source6/state270, its excluded COUNT observer and failed fixture.
The prior [reference review](coverage/semantics/anonymous-constructor-reference-review.json)
retains CLASS153 source6/state217 and its own native, strict and fixture cuts.
The prior [finite-arity review](coverage/semantics/anonymous-constructor-arity-review.json)
retains CLASS152 source6/state212 and its argument-TypeError/missing-arity display distinctions.
The [rejected-source review](coverage/semantics/anonymous-rejected-sources-review.json)
retains CLASS151 source5/state261 and zero-cost parser-rejection history at its own cuts.

GC03's quiet WeakMap registration/proxy-count behavior and its separate tested
cuts remain in the [GC03 review](coverage/semantics/gc-registration-order-review.json).
Typed-current capture and scalar argument snapshots remain in the
[CONFIG contract](docs/semantics/INCLUDE-SOURCES.md).

Current combined behavior is summarized below. Family docs and linked reviews
retain exact admission limits, original failures and tested cuts; this file does
not repeat historical receipt counts or renew their execution credit.

## Integrated behavior and entrypoints

| Family | Current behavior and scope |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered declaration publication, lexical/called scope and emitted-task authority. Include/eval, anonymous classes, traits and linked headers use source-authenticated routes; remaining acquisition and linker contexts stay explicit. [Source context](docs/semantics/SOURCE-CONTEXT.md), [linking](docs/semantics/LINKING-HANDOFF.md), [classes](docs/semantics/SOURCE-CLASSES.md). |
| Values, operators and warning decisions | Arithmetic and conversions are pure executable SpecTec. Supported warning callbacks preserve saved operands, live delayed reads, source sites, handler changes and pending-Throwable order. Operators, casts, dimensions and undefined-variable routes remain partial across their producers. [Numerics](docs/semantics/NUMERICS.md), [dimensions](docs/semantics/DIMENSIONS.md), [comparisons](docs/semantics/COMPARISONS.md). |
| Arrays and references | Physical owner edges distinguish DIRECT copies from ALIAS cells, COW table copies, selected lvalues and shared descendants. Iterator spreads retain raw current references through key before copying the value; invalid-key cleanup retires current before DATA while protecting the partial builder. Ordinary initialized declared fields share the reviewed fold across legal return modes. Materialized/special/cyclic graphs and wider callback lifetimes retain their documented limits. [Array unpack](docs/semantics/ARRAY-UNPACK.md), [reference wrappers](docs/semantics/REFERENCE-WRAPPERS.md), [cleanup review](coverage/semantics/array-iterator-invalid-key-cleanup-review.json), [field review](coverage/semantics/array-iterator-byval-fields-review.json). |
| Comparisons | Reached physical slots, count/key/value order, live reference contents and COW snapshots decide comparisons. Visited captured-graph traversal has no fixed depth limit and reports an authentic active-left recursion Error; earlier identity/class/leaf decisions skip later unsupported payloads. Canonical root admission and acyclic Previous-path validation have no numeric context/length ceiling. Canonical same-kind roots of the admitted builtin kinds share the visited physical-slot fold after older admissions once both finite Previous paths authenticate, preserving cache/trace/previous/severity order and reached table effects. Invalid/cyclic/materialized/freeing Previous nodes, pending states and actually reached callback contexts retain family limits. Captured canonical builtin Throwables share this fold; every distinct equal-kind entry checks active-left recursion before slots, including Previous descent. Supported ordinary images of any visibility admit uncalled methods, locally authenticated interfaces including implicit Stringable, and finite source-parent paths validated by actual names, links and publication order. Seen origins reject parent cycles before layout expansion; builtin parents/hook/readonly and wider layout fences remain. Whole-path authentication stays eager. Empty inline same-class images return zero before the object recursion guard; actual empty caches retain table order, COW and ordinary owners. Empty foreach produces a real table, and empty cached clones share without a callback or start uncached with one. Private/protected fields retain mangled KEY/DECL authority through actual caches and final typed-alias source retirement. Declared INITIAL/UNSET holes retain inline position and physical cached INDIRECT count/key order. Deleted dynamic mirrors leave current live count/order intact; deleted-only clone histories preserve sharing and callback copy routes. [Dynamic-deletion review](coverage/semantics/throwable-trace-dynamic-unset-comparison-review.json). [Declared-hole review](coverage/semantics/throwable-trace-uninitialized-comparison-review.json). [Nonpublic-image review](coverage/semantics/throwable-trace-nonpublic-comparison-review.json). [Empty-image review](coverage/semantics/throwable-trace-empty-layout-comparison-review.json). [Current comparison contract](docs/semantics/COMPARISONS.md), [finite captured graphs](coverage/semantics/throwable-trace-unbounded-comparison-review.json), [finite Previous paths](coverage/semantics/throwable-previous-finite-comparison-review.json), [standalone traces](coverage/semantics/throwable-null-trace-comparison-review.json), [base fallback](coverage/semantics/throwable-base-null-comparison-review.json), [linked base](coverage/semantics/throwable-base-previous-comparison-review.json), [captured Throwables](coverage/semantics/throwable-captured-comparison-review.json), [ordinary methods](coverage/semantics/throwable-trace-methods-comparison-review.json), [local interfaces](coverage/semantics/throwable-trace-interfaces-comparison-review.json), [inherited images](coverage/semantics/throwable-trace-inheritance-comparison-review.json). |
| Calls and callable values | Ordinary, scoped, captured and magic-call routes retain the selected callee/receiver, lexical/called scope, argument origin, positional/named ordering and reference mode across later effects. Closure and pipe consumers preserve their real owners, send diagnostics and abrupt cleanup. Callable producers, signatures and reentry remain partial. Bounded NoDiscard declarations preserve pre-body warning and pending-owner behavior. [Attributes](docs/semantics/BUILTIN-ATTRIBUTES.md), [Calls](docs/semantics/SOURCE-CALLS.md), [Closure::call](docs/semantics/CLOSURE-CALL.md), [first-class callables](docs/semantics/SOURCE-FIRST-CLASS-CALLABLES.md). |
| Configuration and constants | Supported INI_SET/DEFINE/CONSTANT/DEFINED routes retain their selected callee, option/name and API timing. Iterator and named Generator inputs preserve real DATA/INPUT and Aggregate producer history, copied sends, named-key Error priority and pre-API cleanup. CONFIG typed-current reads reuse property-source validation; structural receipts remain valid after physical cache retirement. Iterator sends retain raw scalar snapshots or real finite ARRAY/ordinary-instance slot roots, then defer INI_SET binding/conversion until after DATA/INPUT cleanup. Strict callers reject copied Stringable INI_SET options before casting, including retained setters after source-variable rebinding. An exact converted `zend.assertions` option reaches array/object value TypeError before lookup or accepts copied nonnegative integers, null, Boolean false/true, valid warning-free nonnegative quantity strings and finite floats whose post-option precision produces a warning-free nonnegative quantity. A saved receipt certificate keeps entry precision through assertion state/restore; false and null retain present empty raw INI bytes while their parsed quantity is 0, and strings retain exact raw bytes. Other accepted values remain outside this receipt. COW, shared embedded aliases and API TraceArgs keep their ordinary owners. Generator/other consumers, effectful casts and wider lifetimes retain their documented limits. [Include/configuration](docs/semantics/INCLUDE-SOURCES.md), [constants](docs/semantics/SOURCE-USER-CONSTANTS.md). |
| Classes, properties and enums | Linked declarations preserve receiver identity, slot declaration, visibility, typed-reference sources, readonly/hook policy and diagnostic order. Supported magic getters and reference-get chains preserve alias/copy and rebind timing. Enum declarations lower to cached singleton cases with lazy backing checks, readonly slots, ordered interfaces and generated/user methods. Registered-loader first use for static calls and class-constant fetches preserves selected class/member order and source-authenticated resume; reached dynamic/named/folded/enum cases and forged-target rejection retain separate raw cuts under `.tools/enum-acquisition-review-state-*`. Captured enum `cases(...)` preserves its selected target and singleton cache after closure retirement. Captured scalar `from(...)`/`tryFrom(...)` preserve cold backing tables, ordinary/inherited constant aliases, caller strictness and cached case identity after closure retirement. Captured Stringable arguments preserve their real callback child and line, selected closure lifetime and temporary retirement before lookup. For published enums, class-string array callables select generated `cases()`/`from()`/`tryFrom()` before argument evaluation; a case-object receiver also invokes `from()`. Array Stringable conversion preserves the selected enum and temporary retirement. Computed, literal and folded class-method strings also fix generated targets before arguments, preserving full original bytes and real named Stringable children across rebinding and temporary retirement; packed Stringable origins remain Unsupported. First-class string and array captures use internal Closures held through argument clears and released after invocation. Source-certified direct or negated enum-case conditions in class constants retain selected case identity or scalar results, including a condition from another enum; wider object-valued conditional transfers, other callable routes, the default loader, case attributes, link/type contexts and object lifetimes remain partial. [Classes](docs/semantics/SOURCE-CLASSES.md), [properties](docs/semantics/SOURCE-PROPERTIES.md), [property references](docs/semantics/SOURCE-PROPERTY-REFERENCES.md), [enum evidence](docs/ARTIFACTS.md). |
| Generators and Fibers | Supported named/method/Closure producers retain actual resumer and callee owners, by-value or reference caches, supplied Throwables and catch/finally continuations across Fiber suspension. Receiver-free static and same-`$this` nonstatic Generator bodies called through finite scoped chains retain real scope after return; supported real Closure, captured/bound user-method, implicit invokable and admitted magic-handler factories also authenticate scoped method-created bodies when the original source scope differs. Direct Generator-bodied __invoke uses its runtime-selected method; admitted direct magic handlers retain their actual target/owner receipt through close and Fiber transfer. Delegation and SEND preserve their selected chains and copied/delivered owners. Wider producers, binding/delegation combinations and teardown remain partial. [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [reference yields](docs/semantics/GENERATOR-REFERENCE-YIELDS.md). |
| Lifetime, weak references and collection | Eager release tracks real ownership, pending results/Throwables, destructor frames and protected storage. WeakMap protocols preserve weak-Key visibility, ordinary Value owners, aliases, selective notification and conditional collection. Physical tracing handles admitted ordinary/materialized graphs; quiet same-Key entries and no-Map ordinary siblings use claimed first-visit counts. Canonical materialized destructor callbacks retain claimed count and nested-buffer authority across retrace, including ordinary caller locals and receivers. Source-authenticated temporary cleanup, borrowed result caches and unused WeakReference result transfer preserve potential-root order. Enum cases and original receiverless fake Closures skip GC candidate buffering while retaining their owners and graph edges; clone and bind copies remain collectable. WeakMap callbacks, skipped prior histories, residual and other active collector contexts remain open. Stable retired cell metadata owns nothing; pooled literal arrays remain rooted by compiled constants. [Eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [reference returns](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [weak references](docs/semantics/WEAK-REFERENCES.md), [cycle collection](docs/semantics/CYCLE-COLLECTION.md). |
| Diagnostics, output and environment | Supported handlers retain registration, callback and emitting-frame identity through warnings, throws and cleanup. Echo/print preserve left-to-right effects and flat-array diagnostics; bounded default output buffers retain native callback/output order. Request, clock, stream and startup profiles have explicit contracts rather than ambient host answers. Wider buffering/shutdown/tick behavior remains open. [Handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [output buffers](docs/semantics/OUTPUT-BUFFERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

Copied positional Iterator `ini_get` now waits for a sole Stringable `precision`
option to retire before reading the live value; selected first-class getters
keep their original Closure through key-time rebinding. Held/named inputs stop
outside this receipt. [A107 review](coverage/semantics/config-iterator-get-stringable-review.json).

Copied positional Iterator `ini_restore` now waits for the same sole Stringable
`precision` option to retire before restoring startup precision. A selected
first-class restorer keeps its original Closure through key-time rebinding;
held/named options stop before the unvalidated restore.
[A108 review](coverage/semantics/config-iterator-restore-stringable-review.json).

A borrowed direct-CV `IteratorAggregate` may now return a fresh initialized
user Iterator for positional `ini_get` or `ini_restore` with the copied
Stringable `precision` option. The existing unary receipt runs after Iterator
and option cleanup; selected restore retains its original callee. Generator
returns remain SET-only. [A109 review](coverage/semantics/config-aggregate-unary-stringable-review.json).

## Decisions that constrain further work

- Implement PHP behavior in authored semantics, including pure arithmetic; the
  pinned project-local PHP binary is the differential oracle, never a runtime
  fallback. Core intrinsics/internal protocols are included where the language
  needs them; ordinary external libraries and services are separate.
- Authenticate execution from actual source, selected declarations and genuine
  frames. Historical/nonowning receipts preserve provenance; they neither own a
  dead value nor establish a current live alias.
- Keep acquisition, key evaluation, send snapshots, API reception and cleanup
  distinct. Type-source metadata constrains writes without adding owner edges;
  reading an authenticated typed cell does not perform coercion.
- Preserve diagnostic priority, skipped later work, PHP Error/Throwable identity,
  pending completion and physical lifetime. Explicit Unsupported, failed
  derivations, runner failures and timeouts are different outcomes.
- A bounded passing family does not close its inventory obligation. Extend
  coherent producers/consumers and shared invariants without special-casing
  spelling or weakening refusal boundaries.

OB01 integrates normal EOF and integer/string EXIT draining for existing user
output handlers after real shutdown/global/store retirement. Nested lower writes,
weak diagnostics and callback-local destructors preserve saved completion and the
sole handler owner. Fifteen native-first normal originals agree, six reached
groups pass 238 assertions, private strict427 and joined actual-tail strict429
pass. Its original 90/40-second abnormal timeouts and then-unrun captured throw
retain their historical zero-credit status. OB02 now covers those sources at
new tested cuts. [OB01 review](coverage/semantics/output-request-end-review.json).

OB02 admits default fatal takeover from builtin FINAL throws with scalar messages
and NULL previous. Stored traces and cache mutation precede fatal reporting;
inactive buffers then release raw owners without lower writes. Four originals
match PHP and three reached groups pass 131 assertions. Actual-tail strict431
and both affected guard fronts (70+33) pass without native or differential source
reruns. Its original pending-Throwable decrement admission was nonfinal or
destructor-inactive; OB03 extends it below. Selected exception handlers, wider
rendering and reentrant/abrupt deactivation remain partial.
[OB02 review](coverage/semantics/output-final-throw-review.json).

OB03 releases the retained local FINAL Throwable after cache/reporting while
buffers remain active/running; child output stays buffered. A child destructor
throw preserves the first report, emits a fresh unchained fatal and retains the
existing abandoned C cleanup owners before raw-zoh deactivation. Four originals
agree exactly and four reached groups pass 169 checks. Private and actual-tail
joined strict431 and separate affected FINAL fronts 77+33 pass. The original sole Unsupported and later failed
attempts retain zero agreement credit. Wider selected-handler/rendering and
reentrant/abrupt raw-owner teardown remain partial.
[Pending-release review](coverage/semantics/output-pending-release-review.json).

OB04 selects existing exception handlers for FINAL throws through authenticated
API reception and ordinary ignored-return/original cleanup. Normal handling keeps
UNDEF failure forwarding and real lower callbacks; abrupt cleanup preserves only
actual C owners before fresh fatal/deactivation. Retained Closure fast-free effects
after executor inactivity preserve the pinned late diagnostic and CLI0. Eleven
originals agree and eight reached groups pass 465 checks. Private strict432 and
actual-tail joined strict433 pass.
The independent 303 checks include retired GC HANDLE authority; author 162 includes
first-duplicate allocator mode controls. Slow executor teardown was still open at
that cut; wider internal hooks/rendering and reentrant deactivation stay partial. Source/state cuts retain
their original identities; failed forecasts, fixtures and the repaired invariant
cut keep zero credit.
[Selected FINAL review](coverage/semantics/output-final-exception-handler-review.json).

OB05 adds allocator-selected executor table/storage effects after FINAL and active
retirement of late shutdown registrations. Ordered arguments, the independent FCC
receiver and Closure retain their real C counts through ordinary release and caught
destructor throws. Native symbol/function/class/handler order, shared inherited
method statics and standard-hook shields determine the first inactive callback.
Twelve source/request contexts agree exactly at their recorded cuts; nine reached
groups pass 573 checks (author 171, independent 402), with a separate affected OB04
allocator group passing 58. Private strict433 and current-master joined strict433
pass; one inherited-static original agrees again at the joined 95f5bebf7 cut.
Earlier owning module/autoload
cleanup, uncovered table owners, wider hooks/rendering and reentrant/abrupt cleanup
remain partial. Original failures retain zero credit; the retained slow native
control is promoted without native replay.
[Nonfast executor review](coverage/semantics/output-executor-nonfast-review.json).

OB06 models a no-argument buffer start attempted by a shutdown-argument
destructor after output deactivation. The Notice, false result and unchanged
buffer stack/sequence agree in six source/request contexts, including suppression,
selected handler and fallback paths, slow allocation and an early-shutdown
success control. Three argument/reentrant forms reach checked Unsupported; one
source-reached Notice state passes 30 checks with budget resume. Private and
joined strict433 pass; joined plain/slow and selected-handler sources plus the
three refusals pass on the parent with changed executor queue roots. A retained
handler-return object destructor has native fast/slow observations but fails
before its nested call at the OB06 cut and earns zero credit there.
[Post-deactivation review](coverage/semantics/output-executor-post-deactivate-review.json).

OB07 models the selected Notice handler's returned-object destructor during
normal post-deactivation queue release. Echo-only and nested no-argument
`ob_start()` destructors agree with pinned PHP in both allocator modes; the
nested call uses the built-in Notice while the selected handler is disabled,
returns false and leaves the buffer stack/sequence unchanged. One source-reached
state passes 40 conditions, and OB06's explicit-argument, callable and active
handler-body starts remain checked Unsupported. Private and joined strict433
pass; joined nested fast/slow sources and the three refusals pass with the
executor tick-owner branch present. The retained OB06 native original is now
promoted with exact model agreement.
[Returned-handler cleanup review](coverage/semantics/output-executor-retval-review.json).

OB08–09 use ordinary `ob_start` argument reception during normal post-output
executor queue release. Named/unpacked defaults, converted chunk/flag cases,
deprecations and type/count errors precede callback creation. NULL/default
callbacks then emit E_NOTICE and return false without pushing a buffer,
including in the authenticated destructor of a Notice handler's returned object.
Private and actual2257 composition strict433, author17 and independent4
source/request contexts and scoped reached checks pass at the recorded cuts.
OB10 adds pure callable creation after conversion, with no callback invocation
or buffer push. Its transient owner releases before the Notice, while ordinary
argument ownership preserves temporary invokable/array receivers, captured
Closure cells, bound method receivers and caught-throw cleanup. Selection survives
Notice-time reference mutation; earlier conversion-handler mutation affects lookup.
Consumed Closure metadata uses borrowed source certificates and owns nothing.
The VM argument's root decrement skips GC candidate buffering; array children
still use ordinary cleanup. The source and reached checks retain their separate
cuts in the [creation review](coverage/semantics/output-executor-creation-review.json).
OB11 freezes known invalid callback lookup after conversion, emits Warning then
the failed-start Notice, and keeps failure final even if the Warning callback
defines the missing function or repairs referenced selectors. Declaration-prefix
history and DIRECT snapshots are borrowed checking data. Retired Warning-handler
objects release before the current Notice handler runs. Warning-return destructor
throws preserve the pending operation and real builtin argument trace, retaining
the argument through catch and caller-local cleanup. Pending Notice selection
distinguishes eligible-handler skip from ordinary reporting/suppression.
[Failed-lookup review](coverage/semantics/output-executor-invalid-review.json).
OB12 shares one argument-discard certificate across admitted Warning and Notice
throws. A precreated Throwable exposes direct-cycle NOGC versus ordinary
array-child cleanup; a new Throwable retains the argument through its trace.
Consumed Closure checks borrow retired capture facts without adding owners.
Seven exact originals, 279 reported reached conditions and 90 affected Warning
conditions pass at the recorded private cuts.
[Notice-discard review](coverage/semantics/output-executor-notice-discard-review.json).
OB13 admits a live Throwable thrown by a selected Notice handler's returned-object
destructor before the saved cleanup resumes. The genuine `ob_start` trace keeps
its temporary callback through catch; precreated-Throwable controls separate
VM root NOGC from ordinary array-child cleanup. An `ob_end_clean` countercontrol
also exposes the shared output-intrinsic trace frame. Seven exact originals
agree, and three reached groups pass 165 reported conditions (author 54,
independent 76, off-kind 35). Private strict435 passes; earlier failed packets
retain zero credit. [Returned-Notice throw review](coverage/semantics/output-executor-notice-retval-throw-review.json).
OB14 admits the normal Warning handler's returned-object destructor to a nested
post-deactivation `ob_start`. Its saved Warning receipt and unreleased RESULT
cleanup authenticate the start while the handler is disabled. Three exact
originals agree with native PHP; the genuine reached state passes 42 reported
conditions, and private strict435 passes. The selected handler resumes for the
original failed-start Notice after nested default Notice reporting. Throwing
paths through this new Warning-retval bridge remain outside this milestone.
[Normal Warning retval review](coverage/semantics/output-executor-warning-retval-nested-review.json).
OB15 adds ordinary positive-chunk pre-entry reference-warning throws from echo,
print and inline output. Diagnostic cursors retain the exact running producer;
prepared scalar wrappers retire before undefined-result failure routes live bytes
through lower buffers. Reached lower user chunks skip entry while smaller chunks
retain their bytes. Warning output retains PRODUCED without deprecation, and
owned print operands retire before catch without assigning the print result.
Seven targeted originals and one promoted original agree. Cached parameter
metadata survives a warning retiring its borrowed method receiver; actual entry
after retirement stays explicitly Unsupported. Prepared-prefix and producer fronts pass 108
reported conditions at their separate cuts. Eleven independent originals and one
SL435 front with seven reached groups/475 conditions pass at the repaired cut.
[Independent review](coverage/semantics/output-vm-reference-warning-review.json)
retains the receiver-retirement finding and original failures; the
[author evidence](coverage/semantics/output-vm-reference-warning-author.json)
keeps its separate source and reached cuts.
Explicit lower-cascade/FINAL pre-entry warnings and wider diagnostic cleanup
remain partial.
OB16 preserves scalar output-handler returns through produced-output deprecation
throws in source VM output and all six direct buffer APIs. Normal headers and
result bytes commit before pending lower routing; FALSE and suppressing results
retain their distinct dispositions. Ignored diagnostic-return destructors retain
the disabled running layer, real VM source sites and authentic API trace frames.
Owned producer reentry, current precision and frozen getter copies stay ordered.
Sixteen authored originals, two repaired fresh-trace witnesses and three reached
fronts/160 conditions pass at their recorded cuts. Seven independent originals
and one SL436 front with two reached groups/110 conditions pass at the repaired
cut. [Independent review](coverage/semantics/output-deprecation-warning-review.json)
records the trace findings, real owners and exact evidence. FINAL/lower API
cascades and wider return/control dependencies remain partial.
OB17 retains actual returned reference cells through warnings and callee cleanup,
then converts their live scalar payload without changing aliases. Referenced
FALSE suppresses, referenced TRUE emits1, and unused print/for output still
requests the callback result. Defined Notice/cleanup throws keep the return;
normal FINAL uses the existing drain, while pending FINAL and nonscalar payloads
remain Unsupported. Eight exact independent originals and one SL438 front with
two groups/183 conditions pass. The real HCELL release authenticates its COMMIT
continuation even after cell retirement. [Independent review](coverage/semantics/output-reference-return-review.json)
records the return-demand regression, release guard and affected checks;
[author evidence](coverage/semantics/output-reference-return-author.json) retains its separate cuts.
Unresolved/effectful creation, active handler-body reentry, other Warning/deprecation-handler returned-object
starts, other output Notice returned-object cases, allocation failure/memory limits
and wider executor completion remain partial.
[Explicit-null review](coverage/semantics/output-executor-explicit-null-review.json),
[general reception review](coverage/semantics/output-executor-reception-review.json).

CLASS156–163 are integrated at `0d756bb0e` after independent cumulative review and a joined 433-module SL gate. Their scoped evidence and remaining limits are in [SOURCE-CLASSES](docs/semantics/SOURCE-CLASSES.md) and the linked reviews.
CLASS164 is integrated at `4f3d1a90a`: four exact copied trait `parent` source originals and three reached state groups validate existing rules. [Review](coverage/semantics/trait-captured-parent-view-review.json).
CLASS165 is integrated at `fde2099b3`: four exact copied-alias trace originals and two reached groups pass; three tick-wrapper probes remain zero credit. [Review](coverage/semantics/trait-captured-alias-parent-trace-review.json).
CLASS166–168 establish deferred parented/parentless anonymous trait captures,
parent receive checks and one alias; their original cuts remain linked from
[SOURCE-CLASSES](docs/semantics/SOURCE-CLASSES.md).
CLASS169 shares ordinary finite trait plans across parentless, parented and
explicit-interface contexts. Qualified/visibility/final aliases, precedence,
multiple uses and distinct static cells preserve first-`new` publication and
copied FCC scope. Sixteen exact originals, 190 author and 135 independent reached
conditions, 229 affected conditions and private strict433 pass. The repaired
private-final warning retains class-site authority until `new` resumes before
allocation. Original Unsupported/interpreter and fixture failures retain zero
agreement credit. [Review](coverage/semantics/anonymous-trait-adaptations-review.json).
CLASS170 authenticates inferred Stringable interfaces before restoring the raw
anonymous header view. Direct imports and aliases preserve original name prefixes,
interface spelling and copied parameter scope; return/private/static conflicts
fail at the trait method before publication or allocation. Eight exact originals,
277 independent and 121 author reached conditions and strict433 pass. The ordinary
parentless `parent` receive view requires published interface targets and full
history; old empty-interface and snapshot paths stay unchanged. Original source
failures and three fixture corrections retain zero agreement credit.
Wider source and explicit/unpublished/collision scope histories, illegal-modifier
diagnostics and other member/lifetime contexts remain partial.
[Review](coverage/semantics/anonymous-trait-stringable-review.json).
CLASS171 shares composed trait views with closed successful include/eval units,
retaining source-entry bindings, request counters, publication and full replay.
Ordinary cached scopes validate before extra trait parameter views, breaking the
dynamic replay/cache cycle while retaining interface forgery refusals. Nine exact
originals, strict433, 82 author, 263 independent and 79 retained saved-view
conditions pass. Argument type and object trace displays use native C strings;
fresh eval classes preserve copied constants' selected callable targets. Original
display/timeout failures and the own-constant author control retain zero credit.
Wider source/member/scope histories remain partial.
[Review](coverage/semantics/dynamic-anonymous-traits-review.json).
CLASS172 admits nonempty own constant groups through the ordinary class compiler,
including multiple declarators, types, visibility and final checks. Own FCCs keep
separate source/function scopes across eval compilations; trait compatibility and
parent-final failures retain first-new ordering. Eleven exact originals,
strict433, 75 author and 192 independent reached conditions pass. Full stored
names remain authoritative; diagnostic operands use native C strings. The author
sort-prefix elaboration failure retains zero credit. Attributes and wider
member/type/initializer contexts remain partial.
[Review](coverage/semantics/anonymous-own-constants-review.json).

CLASS173–175 share ordinary anonymous property compilation, final/asymmetric
modifiers and parameter promotion with the existing named-class rules. Deferred
defaults finish before allocation; private keys, lexical setter permission,
reference constraints, eval/self identities and native compile/link ordering are
preserved. The pinned engine's final/private promotion acceptance remains distinct
from ordinary property declarations. Original failures and qualified standalone
warning evidence retain their actual cuts in the
[property](coverage/semantics/anonymous-properties-review.json),
[modifier](coverage/semantics/anonymous-property-modifiers-review.json) and
[promotion](coverage/semantics/anonymous-promotion-review.json) reviews.

CLASS176 admits readonly anonymous headers through those same member/runtime
rules. Physical class-token metadata and compiler counters authenticate names
and readonly bits; implicit fields, clone reinitialization, private keys and
recompiled self scopes retain source authority. Fifteen exact originals,
strict435, 144 metadata checks, 157 author and 220 independent reached conditions
pass at scoped cuts. The original dynamic-property display mismatch and author
metadata-sequence elaboration failure remain zero credit. Attributes/hooks
and wider contexts remain partial.
[Review](coverage/semantics/anonymous-readonly-review.json).

CLASS177 shares concrete named-method modifiers with anonymous methods and
constructors. Final flags/callable scopes, nonpublic access before arguments,
failed-construction destructor suppression and related bound-Closure lexical
access retain source authority. Static-constructor rejection follows parameter
and body compilation. Fourteen exact originals, strict435, one affected named
source, 139 author and 151 independent reached conditions pass at scoped cuts.
Two author front corrections retain their failed batches; completed components
keep explicit credit. Anonymous abstract diagnostics and wider method-body factory
contexts remain partial; the next review admits named source owners.
[Review](coverage/semantics/anonymous-method-modifiers-review.json).

CLASS178 admits anonymous factories in ordinary named-class methods with actual
owner/method/GOTOROOT, namespace/import and current/folded class-context authority.
Complete-unit images and child-before-deferred-owner counter order preserve
static/instance/default/byref/inherited/namespace/readonly behavior. Twelve exact
originals, final435 plus five member-fence checks, 155 author reached +31 pure
context queries and 212 independent conditions pass at scoped cuts. Initial
elaboration stops and failed whole state batches retain separate zero-credit
identities, with completed components qualified. At that cut, trait/anonymous
source owners, method-owned Closures, generators/byref returns/attributes and
wider contexts remain partial. [Review](coverage/semantics/anonymous-method-factories-review.json).

CLASS179 admits anonymous child factories in named `__construct` bodies with
authenticated owner and compiler context. Child-before-deferred-owner keys,
repeated construction, inherited access, promotion, failure cleanup and compile
diagnostic priority match PHP 8.5.10. Reached lazy final-link errors retain their
constructor trace through eager cleanup. At that cut, anonymous-owner methods
still required provisional key reservation before body compilation.
[Review](coverage/semantics/anonymous-constructor-factories-review.json).

CLASS180 reserves an anonymous owner's compiler-local descriptor before its
method bodies and replaces it in place after successful compilation. This
preserves source-order owner/child/grandchild keys, including reverse and
repeated calls, named factories with forward parents and anonymous constructors.
The ordinary runtime handles inherited scope, protected constructors, failed
owner cleanup and lazy links. Abrupt unit compilation drains child diagnostics
and skips only authenticated child checkpoints without installed images.
Twenty-two exact PHP 8.5.10 sources, 106 reached plus 20 pure conditions and
35 source-boundary checks cover this slice. At that cut, method-owned deferred
scopes, owner traits/constants/implicit Stringable siblings and dynamic units
remained partial. [Review](coverage/semantics/anonymous-owner-factories-review.json).

CLASS181 admits an ordinary public `__toString` sibling in an anonymous owner
whose other method or constructor creates anonymous children. The provisional
owner remains compiler-local with empty interfaces; existing in-place finish
derives implicit `Stringable` and clears early status. Before/after member
order, parented and nested owners, constructor children and compile-error
priority match PHP 8.5.10. Fifteen exact source rows plus a separately bounded
recursive source, 79 reached plus 17 source-derived conditions and 35 current
source-boundary checks cover this slice. The earlier full-batch recursive
timeout retains zero credit. Child factories inside `__toString`, private/static
magic variants, traits/constants, deferred scopes and dynamic units remain
partial. [Review](coverage/semantics/anonymous-owner-stringable-review.json).

CLASS182 admits anonymous factories through method-owned Closures and arrows,
including nested deferred bodies, with source-derived lexical names and actual
named/anonymous method-owner authority. Ordinary capture, retained receivers,
failed construction and class-link ordering use the existing runtime. Rejected
constructors suppress deferred child checkpoints. Closure `__METHOD__` now keeps
its complete generated name; ordinary methods and copied/fake Generator Closures
have separate affected controls. The [review](coverage/semantics/anonymous-method-closure-factories-review.json)
retains scoped source/state cuts, the initial name mismatches, fixture correction,
short-path guard failure and timeouts. Attributed/generator/by-reference-return
factories, anonymous owner explicit-interface headers/traits/constants and
dynamic units remained partial at that cut.

CLASS183 shares ordinary explicit-interface headers and trait/constant members
with unit0 anonymous factory owners. Provisional raw interfaces and the compiler
early marker preserve parent/first-interface prefixes and source-order child
keys; member completion stays in place. Constant callables, trait-inferred
Stringable and deferred scopes reuse the existing runtime. Selected original
programs and distinct source/runtime state groups cover composition, owner scope,
forgery refusal and compile/link order. The
[mixed-owner review](coverage/semantics/anonymous-owner-declarations-review.json)
records actual cuts and native-only preparation separately. Trait-owned source
factories, attributes and wider dynamic/member/lifetime contexts remained partial
at that cut.

CLASS184 admits unit0 trait-source method/constructor and Closure/arrow anonymous
factories through the real Trait body and PTTRAIT compiler context. Ordinary
copying preserves consumer lexical/called scope while repeated consumers and
aliases reuse compiled child identity. Abrupt compilation replays earlier
diagnostics and skips only source-owned uninstalled trait children. The
[review](coverage/semantics/trait-source-factories-review.json) separates source,
consumer/cleanup state and source-derived refusal evidence, retaining the
original missing-checkpoint Unsupported and fixture correction. Attributes,
generator/by-reference-return factories and wider dynamic/lifetime contexts
remain partial.

COMP160–161 are integrated through `084768600`: declared INITIAL/UNSET cached
images and deleted dynamic histories retain comparison, cast and clone behavior.
Their exact source, reached-state and affected gates are in
[SOURCE-CLONE](docs/semantics/SOURCE-CLONE.md) and the linked reviews.

COMP162 copies ordinary mixed declared tables after dynamic reinsertion when
obsolete dead mirrors precede a later live row. Four exact source agreements,
39 reached conditions, two affected clone sources and joined strict433 pass.
Live/live duplicate names and nonordinary tables remain partial.
[Review](coverage/semantics/throwable-mixed-reinsert-clone-review.json).

COMP163 admits checked file-mode shebang `ENCODEDPROGRAM` tick plans for main and
included units. Seven exact native/model sources and 32 source-reached tick-plan
conditions pass at the committed cut, with joined strict433 on the composed
master. BOM files follow the existing `PROGRAM`/InlineHTML route; eval uses its
separate parser mode. Other preamble profiles and wider encodings remain partial.
[Review](coverage/semantics/source-preamble-tick-review.json).

COMP164 admits terminal HALT offsets in raw, BOM-free file shebang units. Six
exact native/model sources cover direct offsets, an included child, CV lookup
and filename-local registration; ten checked-AST premises cover source offsets
and nonraw/BOM refusal. Joined strict433 passes. Plain and BOM files retain
their `PROGRAM` behavior; other encoded HALT profiles remain partial.
[Review](coverage/semantics/halt-preamble-review.json).

COMP165 admits the disabled-multibyte parser warning followed by a static
first-statement fatal for late or nested sole-string encoding declarations.
Five pinned-native source cases cover root, namespace and block fatals plus
included and eval first-declaration controls. Forty-four checked-AST premises
authenticate declaration and item paths, warning location, and malformed
occurrence refusal. Other declaration shapes and multibyte source conversion
remain partial. [Review](coverage/semantics/encoding-placement-review.json).

COMP166 admits arbitrary mixed/repeated encoding items with parser-literal values
and ordinary bodies in checked single-line declarations. Source token positions
order the complete recursive parser-warning prefix before compiler diagnostics;
literal concatenation passes the matching parser-form check. Ten original
sources agree, including strict/tick interactions and include/eval body returns.
Authored 256, independent dynamic 93 and affected legacy 179 strict-SL premises
pass, alongside six CLI guards and two explicit multiline Unsupported controls.
Actual cuts and preserved failures are in the
[review](coverage/semantics/encoding-list-review.json). COMP167/168 below extend its multiline and rejected-source boundaries;
multibyte conversion remains partial.

COMP167 retains checked declaration header-close line/token facts. Multiline
headers use their closing line for parser warnings while compiler diagnostics
keep the first item's line. Nested header reductions precede enclosing headers;
comment-only Nops retain their genuine empty token spans. Twenty-one new original
comparisons, independent compiler/state gates and affected regressions pass;
strict compilation covers 433 modules. Fresh classified syntax covers 30,980
profiles and independent metadata checks cover 17 profiles. Original failures
and exact cuts remain in the [review](coverage/semantics/encoding-header-review.json).
COMP168 below extends rejected dynamic sources; multibyte conversion remains partial.

COMP168 preserves encoding warnings from completed foreign header reductions
when eval/include parsing later fails, without compiling a partial AST. Literal
items warn in reduction order until the first nonliteral encoding item raises
CompileError. Rejected-source Throwable handles are installed before publishing
zero-budget continuations. Twenty-two exact sources plus one explicit lexical
refusal, 214 authored and 375 independent reached conditions pass; accepted
eval/file service controls also pass. Actual cuts, prior failures and the remaining
lexer/multibyte limits are in the [review](coverage/semantics/encoding-rejection-review.json).

COMP169 preserves completed headers before the first foreign lexer error by
validating its token boundary and parsing the preceding token prefix. Earlier
grammar errors still stop parsing; harmless control bytes inside strings/comments
do not truncate it. All 32 new eval/file originals agree, with 30 independent
boundary controls, 40 affected service checks, three selected legacy originals
and 220 reached conditions. Accepted syntax and authored P4 rules are unchanged;
unreported prefix differences and multibyte conversion remain partial.
COMP170 extends main-file failures below.
[Review](coverage/semantics/encoding-lexical-review.json).

COMP170 delivers completed-header warnings before rejected main-file parser
errors through existing checked file receipts. Warning 128, Parse 4 and Compile 64
report independently, including separate stdout newlines and exit 255 at zero
VM steps. The terminal result installs no program/history or Throwable and
explicitly refuses VM reentry. Thirty-seven exact profiles from 15 originals,
28 independent service controls, 240 terminal-state conditions and two accepted
include/eval controls pass; strict compilation covers 435 modules. The original
fixture's misplaced VM-history check remains a failed gate with zero credit.
Parser/schema contracts are unchanged; wider source profiles remain partial.
[Review](coverage/semantics/main-source-rejection-review.json).

COMP171 supplies rejected file/eval units with parser-mode lexical token tapes,
without calling the Zend grammar. Trivia and original positions survive; malformed
Unicode/heredoc segments stop later headers while retaining earlier interpolation
declarations. Accepted lexers, schema, adapter and authored P4 rules are unchanged.
Private native build, 53 independent scanner/service controls, 30 affected controls,
35 exact source cases, 200 reached conditions and four main-file regressions pass.
The initial null-scanner eval/file heredoc failures remain zero-credit packets.
Multibyte conversion and wider core remain partial.
[Review](coverage/semantics/rejected-scanner-tape-review.json).

COMP172 preserves completed encoding headers after nested namespace reductions
when a later parser error rejects the unit. Namespace nesting remains a compiler
check; genuine grammar errors and other parser validation still stop collection.
Sixteen eval/include and four rejected-main comparisons, 24 independent service
controls, 100 reached conditions with SL435 and two affected main regressions pass.
The original service fixture's extra namespace diagnostic remains zero credit;
accepted parsing and the receipt/runtime contracts are unchanged.
[Review](coverage/semantics/rejected-namespace-review.json).

COMP173 defers rejected-only class/interface/enum, static magic-method and try
validation to its native compiler phase, retaining later completed parser headers.
Readonly and duplicate-modifier parser stops remain active. Readonly body-prefix
differences were explicit refusals at that cut; COMP174 below extends them.
Thirty-eight dynamic and four rejected-main
comparisons, 49 service controls, 24 affected controls and 110 reached conditions
with SL435 pass at their recorded cuts. The original history fixture failure
remains zero credit; its correction requires exactly the rejection-exit record
and no partial declaration installation.
[Review](coverage/semantics/rejected-static-validation-review.json).

COMP174 validates rejected method-target modifiers at the foreign grammar's
actual function lookahead, before parameters/body. Earlier attribute headers
survive; forbidden readonly/asymmetric-set bodies supply none. Valid readonly
properties and ordinary method flags keep their headers. All 22 dynamic and four
main comparisons, 37 service controls, 108 reached conditions/SL435 and affected
49/24 controls pass at one cut. Constant-target prefix differences were explicit
refusals at that cut; COMP175 below extends them.
[Review](coverage/semantics/rejected-method-modifier-review.json).

COMP175 extends the checked foreign lookahead rule to constant modifiers before
initializers. Earlier attribute headers remain; forbidden static/abstract/readonly
and asymmetric-set initializers supply none. Visibility/final typed constants and
method/property contexts retain their behavior. All 22 dynamic and four main
comparisons, 42 service controls, 108 reached conditions/SL435 and 37 affected
controls pass at one cut. The mistaken native control missing `const` remains
separate; accepted parsing and native/schema/adapter/P4 contracts are unchanged.
[Review](coverage/semantics/rejected-constant-modifier-review.json).

COMP176 checks rejected trait-use alias modifiers at the named and unnamed
foreign reductions, retaining earlier encoding headers but cutting off later
ones for readonly and asymmetric-set flags. Six method-target flags still allow
later parsing; a missing semicolon stops in the foreign grammar with the same
empty later prefix. Native diagnostics retain their own message and alias-end
line. Thirty-eight dynamic and four main originals, 73 service controls, 108
reached conditions/SL435 and affected constant42/method37 controls pass at
their recorded cuts. The preliminary relative-path and multiline-line fixture
failures and an interrupted unwatchable-`cases.json` run have zero credit;
corrected authoritative campaigns hash their expectations. Accepted parser,
native helper, schema, adapter and P4 interfaces are unchanged. Broader
rejected-source prefixes remain partial.
[Review](coverage/semantics/rejected-trait-alias-modifier-review.json).

COMP177 defers rejected-only property-hook name, `get(...)` parameter-list and
empty-list checks until compilation, retaining completed encoding headers before
later parser failure. Property, promoted and ordinary parameter, and interface
contexts agree; parser-time invalid modifiers keep their earlier cutoff and can
preempt deferred checks. Thirty-six dynamic and four main originals, 62 service
controls, 110 reached conditions/SL435 and affected method37/constant42/trait
alias73 controls pass at their recorded cuts. Two multi-property grammar controls
are explicit Unsupported refusals with zero agreement, and the initial service
fixture failures have zero credit. Accepted parsing, native helper, schema,
adapter and P4 interfaces are unchanged; wider rejected-source prefixes remain
partial. [Review](coverage/semantics/rejected-property-hook-static-review.json).

COMP178 stops rejected comma-separated property declarations at their opening
hook brace, matching Zend's grammar before any hook body. Earlier attribute,
initializer and completed-hook headers survive; parameter and ordinary property
lists retain their behavior. Twelve dynamic and four main originals agree,
76 maintained service controls and 40 independent challenges pass at their
recorded cuts. The two COMP177 multi-property refusals are now supported.
Accepted parsing, native helper, schema, adapter and P4 rules are unchanged;
wider rejected-source prefixes remain partial.
[Review](coverage/semantics/rejected-multiproperty-hook-review.json).

COMP179 defers rejected-only attributed global constant-list validation to
compilation, preserving later headers across namespaces and initializer closures.
Later parser-time modifiers and nonliteral encoding declarations keep their
priority; class, single and unattributed constants retain their behavior.
Sixteen dynamic and four main originals agree; 25 service controls, 76 affected
hook controls and 32 independent challenges pass at their recorded cuts.
Accepted parsing, native helper, schema, adapter and P4 rules are unchanged;
wider compiler and attribute behavior remains partial.
[Review](coverage/semantics/rejected-constant-attribute-review.json).

COMP180 stops rejected abstract/final anonymous classes before constructor
arguments and bodies, preserving earlier attributes and encoding headers.
The actual NEW terminal's value and span distinguish named classes whose
preceding statement list begins with NEW; the empty-list sentinel is excluded.
Sixteen dynamic and four main originals agree; 27 service controls, 101 affected
controls and 52 independent challenges pass at their recorded cuts. The initial
direct-parser negative-index warnings remain preserved with zero gate credit.
Accepted parsing, native helper, schema, adapter and P4 rules are unchanged;
wider rejected-source/compiler behavior remains partial.
[Review](coverage/semantics/rejected-anonymous-class-modifier-review.json).

COMP181 admits parsed attributed global multi-constant declarations to authored
compilation. Ordered initializers, reached closure bodies, qualified class checks
and retained compiler lines precede the final attribute fatal; ignored attribute
arguments retain parser warnings. Eval/file compilation terminates before
catch/finally. Single attributed constants and wider attribute behavior remain
partial. Across preserved cuts and reviewed guard bridges,93 distinct original
source comparisons agree; one single-attribute control remains Unsupported.
Strict412 conditions/435 modules and the final pipe controls pass. The full
classified syntax/inventory gate passes30,981 profiles with zero unresolved
failures at its frozen syntax cut; the [review](coverage/semantics/attributed-constant-compile-review.json)
records the pointwise bridge to final semantic bytes.

## Active and unintegrated work

| Track | Owner-confirmed current work |
| --- | --- |
| CLASS185 | Class and Trait factories with Generator bodies; private implementation/review. |
| I112 | Owning native Generator API captures and invocation; private implementation/review. |
| GC45 | Notification when ordinary WeakMap keys die, with finite payloads; private implementation/review. |
| COMP182 | Single attributed global constants; trace compiler attribute ordering and source/runtime receipt boundary after COMP181 acceptance. |
| OB18 | Array output return reception and conversion; private implementation/review. |
| ATTR33 | Echo tick placement between operands, with late reads and aborts; private implementation/review. |
| Enum callable arrays | Namespace fallback preserving a saved builtin through local publication; private implementation/review. |
| V110 | Temporarily held/unintegrated after repeated generic cybersecurity-risk flag; CPU3 released, exact rejected action unknown. Accepted source3 retained. |
| GC35 | Held after an automatic possible-cybersecurity-risk stop; private work preserved with zero integration and validation credit. |
| COMP123 | Held unrun; no actor. |

The active table is an owner-confirmed handoff snapshot, not validation credit
for private changes. Integrated work is indexed by the current family docs,
[feature inventory](coverage/semantics/features.json) and linked reviews above;
[ARTIFACTS](docs/ARTIFACTS.md) locates original evidence and private cuts.

## Remaining core work

- Finish the partial inventory obligations across every source constructor and
  runtime dependency. Unsupported cases remain explicit; a passing bounded slice
  does not close its family.
- Extend warning/read/cast and argument consumers, callable/Closure forms,
  reference parameters/returns and constrained coercions without erasing delayed
  reads, diagnostic priority, saved targets or abrupt cleanup.
- Complete wider array/object/reference ownership, nested access and key forms,
  ArrayAccess/Iterator interactions, COW, released targets and callback lifetimes.
- Complete remaining class/static/trait/enum/attribute/hook/readonly contexts and
  wider magic/property/callable producers, including reentry and typed aliases.
  Beyond public destructors and Stringable, anonymous magic methods and wider forms
  remain substantive class work; Traversable constructor producers,
  promotion/nonpublic modes and wider factories also remain required.
- Complete wider Generator/Fiber suspension, delegation, destructor reentry,
  physical collection, weak-reference/WeakMap, output/shutdown/tick and other
  required lifecycle behavior.
- Extend remaining Traversable CONFIG producers, consumers and lifetimes beyond
  initialized user Iterators, fresh named Generators, their bounded Aggregate producers and the empty/singleton WeakMap slice.
- Extend dynamic compilation, startup/configuration profiles, environment and
  provider consumers within the agreed core/intrinsic boundary. Ordinary external
  libraries/services are separate; builtin presence alone supplies no semantics.
- Run final combined current-source validation and a fresh copied-path,
  network-isolated offline rebuild. Current local tool reuse is not that rebuild.

Interaction-tree semantics in Rocq and the selected BOLA/CRIS proofs follow
completed PHP core and renewed differential validation; they are not established
by these tests.

## Paused boundaries

Do not resume or broaden these lanes through neighboring work:

- OP12 increment/decrement dimension warnings.
- Source47 low-precision DEFINE-name NaN conversion.
- Owned-NUL source-release behavior.
- Undefined by-reference LIST key handling.
- COMP88 Stringable supplied-throw crash.

## Validation and evidence

Use the pinned project-local PHP oracle and matching profile. Preserve original
bytes/path/cwd, raw streams/status, semantic completion, tested revision,
compiler/runtime identity, commands and relevant environment. Ordinary, explicit
request and callable profiles retain separate contracts.

Independent review covers semantic correctness, counterexamples and test
reliability. Fix discrepancies narrowly; rerun affected checks only. Metadata
edits and pointwise disjoint composition do not renew accepted execution credit.
Interrupted, timed-out, Unsupported, malformed and budget-control outcomes remain
separate from native agreements. State fixtures complement source comparisons.

Large originals and raw failures stay outside Git; [ARTIFACTS](docs/ARTIFACTS.md)
provides recovery. Detailed prior checkpoints remain in their existing ledgers,
[MILESTONE-HISTORY](MILESTONE-HISTORY.md), and Git history through `25b63539e`.
The [post-arrow baseline](coverage/semantics/post-arrow-integration-review.json)
retains its historical profile/count identities, not current full-core coverage.
Keep this file focused on current behavior, remaining work and active boundaries;
replace superseded status prose instead of accumulating receipt history.
