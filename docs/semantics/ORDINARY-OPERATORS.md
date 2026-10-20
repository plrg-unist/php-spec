# Ordinary operators and casts

The source compiler and runtime now pair the ordinary `%`, `**`, `<<`, `>>`,
`&`, `|`, `^` and `.` operators, bitwise `~`, casts to bool/int/float/string/array,
and `(void)` with their checked source occurrences. This extends the existing
arithmetic, comparison and logical paths for current scalar and array values.
Object casts, resources, object protocols and request-environment access still
require their own value and execution models.

## Evaluation and diagnostics

Operands evaluate left to right. Direct compiled variable operands may retain a
delayed read until the final operator; computed names, dimensions and expression
results retain their own value-copy timing. The operator uses the compiler's
ending context for conversions and delayed reads. Parser-folded literal
concatenations used as variable names remain distinguishable from unary or
ternary expressions that merely produce the same bytes.

For two defined direct CV operands, implicit integer conversion in `%`, `<<`,
`>>` and mixed scalar `&`, `|`, `^` suspends through warning/deprecation handlers.
Conversions capture the number and original float-string before diagnostics.
`%` and shifts dereference the RHS after left conversion; bitwise operations
dereference both before conversion and retain their original numeric dispatch.
Borrowed reference pointers add no owner. Each notice reads the current handler
registry. A thrown handler cancels the result; the NaN modulo case below first
finishes safe conversion's remaining notice.
The [review ledger](../../coverage/semantics/integer-operator-warning-review.json)
keeps source and genuine production-SL state checks at their tested revisions.
Evaluated literal/unary/ternary copies and reference-assignment/named byref-call
results now keep their original operands as real owners; selected pointers and
conversion snapshots add no owner. Rebinding the sole global owner preserves
an owning reference result, and two operands may own the same cell twice.
Bitwise conversion follows Zend's physical opcode order: CONST1, TMP2, VAR4,
CV8, with lower-ranked left slots swapped before conversion. Source evaluation
remains left to right. This determines callback order, saved integers and the
TypeError operand order; `%` and shifts retain left-first conversion.
The [COPY ledger](../../coverage/semantics/integer-operator-copy-review.json)
binds 37 source cases and 714 reached conditions, preserving the original swap mismatch.
Wider bitwise producer classes and object conversion remain open. Expired
pointers stay Unsupported; six earlier callback-unset native originals crashed with
signal11, with no diagnosed engine cause or agreement claim.

Plain-CV NaN `%` now preserves the remaining precision Deprecated after its
range Warning handler throws. With mask `2`, the default Deprecated on line 25
precedes the same supplied Exception from line 20; mask `8194` runs neither a
second handler body nor default. The callback's writes `x=99`, `y=0` survive,
outer `100` remains unchanged, and the pending conversion never reads that zero
divisor. Normal return instead finishes both notices before reading current RHS:
the control keeps divisor `0` through H1, changes it to `5` in H2 and yields saved
`0 % 5 = 0` despite live LEFT `88`. Three originals and 165+175 focused premises
cover real callbacks, pending Throwable ownership, raw default/restoration and
normal RIGHT capture/result, EOF and budgets in the
[pending modulo ledger](../../coverage/semantics/mod-nan-pending-review.json).
The eligible-pending control is source-only. Only a specialized discard bridge
and pending task are added; old normal/numeric/formatting/unwind bodies remain
unchanged. Other operators, phases, producers and broader lifetimes remain partial.

Module404 stages `+` when the left operand is a leading-numeric string and both
direct CVs already select live, initially untyped reference cells. Zend's
`add_function_slow` dereferences both operands before conversion; each scalar
numeric holder is filled before its warning. A handler's write to the converted
operand does not replace that holder, while the next conversion reads its already
selected referent. A second warning likewise retains its captured number even if
the handler returns false and changes the cell again. Selected pointers and scalar
holders add no owners. A supplied handler throw discards the addition without
delivering a result. Initial selection and pre-callback input snapshots are checked;
post-callback holders remain historical. Three exact originals and 321 genuine SL
premises retain their cuts in the [ADD ledger](../../coverage/semantics/arithmetic-warning-review.json).
Other mixed/copied operands, owning/expired replacements, failed LEFT conversion and
wider arithmetic/exit paths remain required; existing integer-operator evidence is unchanged.

Failed RIGHT conversion on this selected-cell route now raises TypeError using
both live raw scalar types, rather than earlier numeric holders. The unfinished
marker is removed before ordinary caller Throwable search; the assignment stays
unchanged. Conversely, a completed RIGHT warning still delivers its cached number
even when the live pair would now fail conversion. Two exact originals and 82
author plus 77 independent genuine SL premises check these distinct routes,
source/phase/expiry guards, sole Error ownership and budget resumption in the
[ADD failure ledger](../../coverage/semantics/arithmetic-failure-review.json).


That selected-reference ADD failure route now also handles allocated flat arrays
after the first LEFT Warning. Both live arrays produce `array + array` TypeError;
the earlier array-union fast path is not retried. A live bool and selected old RHS
array produce `bool + array` even after the current RHS name binds replacement7.
The old cell remains live through its alias, with owners falling from two to one;
the replacement has two. The literal array retains pool1+cell1 owners through the
error, then pool1 after its old alias is overwritten. No source cell or outer
destination is replaced by failure. Two originals and 296 focused premises cover
raw THROWN, fresh indexed TypeError and this topology in the
[ADD array-failure ledger](../../coverage/semantics/add-array-failure-review.json).
The old scalar helper and entry remain exact. Other producers, constrained or
expired cells, nested/reference/owning array leaves and wider lifetimes stay partial.

Selected-reference ADD now admits valid nonnumeric RHS text before the LEFT
Warning. A separate entry keeps the old plan exact and enters its existing phases;
both selected cells must be live, untyped and nonowning. The LEFT number is captured
before its handler repairs the selected old RHS. Fractional holders `12.5` and `5.5`
yield strict float `18.0` despite later writes. Repair to complete text `5.5` gives
`17.5` with one Warning after the current RHS name is rebound to `2tail`: the
replacement neither converts nor warns. Unrepaired text uses the unchanged live
bool + string TypeError route, without storing the outer result. A first supplied
throw suppresses later conversion and is source-only. Four originals and 428
focused premises check these routes in the
[ADD repair ledger](../../coverage/semantics/add-repair-review.json).
Other producers, owning/constrained/expired cells, failed LEFT conversion,
indirect handlers and wider lifetimes remain partial.

Binary `-` and `*` now have a separate named-handler continuation for the same
bounded preexisting reference-cell class. Both cells are selected before LEFT
conversion, but RHS conversion waits until LEFT's handler returns, so initially bad
text can be repaired. Each numeric holder survives its own Warning; later RHS
name rebinding leaves the selected old referent in use while a real alias keeps
it live. Cached `12` and `5` give `7`/`60`; fractional `12.5` and `5.5` give float `68.75` after live
values become invalid. Failed RHS conversion instead reports the live selected
types, and supplied throws cancel result delivery while preserving callback writes.
Seven exact originals and 834 focused premises check real dispatch/entered phases,
default Warning bytes, selected-cell owners and budget resumption in the
[SUB/MUL ledger](../../coverage/semantics/submul-warning-review.json). Other mixed,
owning/constrained/expired and wider arithmetic/lifecycle forms remain partial;
earlier ADD/DIV evidence retains its original cuts.

Direct plain-CV `$x += $x` now starts its numeric conversion before the generic
self snapshot. Zend emits the same CV for both operands without a temporary copy.
LEFT captures `12.5` from initial `12.5tail`; its handler writes `5.5tail`, which
the same live CV then supplies to RIGHT. After RIGHT captures `5.5`, its handler's
write of `88` cannot change the strict float `18.0` stored in that CV and delivered
to the outer destination. A second supplied Exception from line 20 instead keeps
`88` and outer `100`, with no compound store. Two originals and 193+166 focused
premises cover actual callback entry, both captures, equal pointers, historical
validation, raw versus driven store, EOF and budgets in the
[self-addition ledger](../../coverage/semantics/addassign-self-warning-review.json).
No alias or extra cell owner is introduced. Old numeric, store and unwind bodies
stay unchanged; other operand producers, compound operators and wider histories
remain partial. Dimension self-copy and paused inc/dec paths are untouched.

Numeric compound `+=` now stages the same leading-left warning for direct CVs
with preexisting untyped reference cells and a quiet numeric RHS. The saved left
number and both selected addresses survive a named handler. On return, the live
selected RHS is converted quietly and the result replaces the selected old left
cell, even if the current variable name was rebound. A supplied throw cancels the
store and preserves callback mutations. The descriptor adds no owners; the
rebind original retains the old cell through its surviving alias, with owners
falling from two to one. Fresh input/selection authority is checked before entry;
entered and returned holders remain historical. Three exact originals and
273 author plus 87 independent focused SL premises are recorded in the
[compound ADD ledger](../../coverage/semantics/addassign-warning-review.json).
Lookup-only negative projections check PROPREF presence, ownership and expiry;
they do not establish typed-source or owning-target execution. Other invalid RHS
values, constrained/expired targets, owning targets for these numeric stores, wider operands/callbacks
and lifecycle paths remain explicit boundaries.

Selected-reference `+=` now captures a leading RHS produced by that first
Warning, before issuing a second Warning. The old RHS stays selected despite
current-name rebinding; after capture its last alias may disappear, leaving owner0
and no allocation without invalidating the historical holder. Cached `12.5`/`5.5`
then store strict float `18.0` through the old target alias, while the current
target name keeps replacement77. This updates the existing selected cell and
LOCATION, with no new cell, detachment or name redirect. A supplied second throw
instead preserves callback88/7 and outer100, with no store. Two originals and
330 focused premises retain real phases, raw/driven stores and aliases in the
[selected-RHS Warning ledger](../../coverage/semantics/addassign-selected-rhs-warning-review.json).
The old entry and quiet completion remain exact. Fresh selected RHS and final
selected target require live unconstrained scalar cells at their respective phases;
other producers, unsafe targets and wider lifetimes remain partial.

A separate selected-reference `+=` entry now admits valid initially nonquiet
text RHS while preserving the old quiet entry. Distinct bad text `bad5` can be
repaired to `5.5tail` by the first Warning; a second supplied Exception cancels
the selected and outer stores, preserving old `88`/`7` and outer `100`.
Two variable names may also select the same CELL: LEFT captures `12.5`, the first
callback changes that shared cell to `5.5tail` and rebinds current RIGHT to `7`.
RIGHT captures old `5.5` before the second callback writes shared `88` and rebinds
current LEFT to `77`. Cached float `18.0` then replaces `88` in the old cell through its surviving alias,
with its owners falling from three to two to one; neither replacement is changed.
The store creates no CELL, detachment or name redirect. Two originals and 175+177
focused premises check real handlers, raw/driven transitions, aliases and budgets
in the [staged RHS ledger](../../coverage/semantics/addassign-repair-review.json).
Fresh scalar selected cells, valid text RHS and the surviving safe old target
bound this slice; other producers, constraints/owning payloads and lifetimes stay partial.

Failed delayed RHS conversion on selected-reference `+=` now reports the
live old referents and preserves both cells. Changing them to flat arrays `[1]`
and `[2]` raises `array + array` TypeError without retrying the earlier union
fast path. Rebinding both current names to 77/7 cannot replace the old false/bad
text labels: failure reports `bool + string`, while old aliases keep owner1 and
current replacements owner2. No compound/outer store, detachment or name redirect
occurs; later old-alias73/4 versus current8/9 writes preserve that topology.
Two originals and 304 focused premises check real Warning phases, raw THROWN
versus driven fresh TypeError25, array identity/item/count preservation and budgets
in the [selected failure ledger](../../coverage/semantics/addassign-selected-failure-review.json).
Both old cells must remain allocated/live/unconstrained; the existing scalar/flat
DIRECT-array bound is reused. Missing/expired/constrained cells, objects,
nested/reference/owning array leaves, other producers and wider lifetimes remain partial.

Initially plain CV `+=` destinations now keep their original CV-slot selection
across the leading-left warning. A reference created by the named handler can
retain the callback's replacement through an alias. Successful arithmetic detaches
that wrapper from the destination and writes a new non-reference cell, with
LOCATION naming the actual returned CELL. A supplied throw performs neither
detachment nor store, so subsequent writes still reach both aliases. The old
initially referenced destination route keeps its selected-cell behavior.
Three exact originals and 272 author plus 115 independent focused SL premises
are recorded in the [plain-CV ledger](../../coverage/semantics/addassign-cv-warning-review.json).
Fresh selection/snapshot authority, real saved TARGET frames, historical values,
old-alias owners two to one, default Warning and budget continuation are checked.
Missing-name, PROPREF, owning and newly referenced RHS projections are pure refusal
queries, not authenticated typed/lifetime behavior. That quiet-RHS completion needs
a plain, defined numeric RHS; wider operands, owning/constrained targets,
callbacks and lifecycle paths remain required.

The existing plain-CV `+=` entry now also handles a newly leading RHS after
the first LEFT Warning. It captures that RHS number before issuing the second
Warning and preserves both holders as history. Late RHS reference creation or
unset cannot replace cached `12.5`/`5.5`, which yield strict float `18.0`. Storage
uses the existing CV replacement helper: a late target alias and RHS retain `88`
with owners falling from three to two, while LEFT gets a new cell and LOCATION.
A supplied second throw instead preserves target alias write-through and outer
destination `100`, with no detach/store. Four originals and 465 focused premises
retain real phases and raw-versus-driven writes in the
[second-Warning ledger](../../coverage/semantics/addassign-rhs-warning-review.json).
The unchanged entry requires an initially quiet RHS; the new snapshot still
requires that RHS plain and defined. Selected-reference destinations, pre-snapshot
RHS references, owning/constrained/expired targets and wider lifetimes remain partial.

A failed delayed RHS conversion after that first plain-CV `+=` Warning now
raises TypeError from the live dereferenced pair. Changing both values to flat
arrays yields `array + array`: the earlier array-union fast path is not retried.
Creating a late LEFT alias, then changing LEFT to false and RHS to bad text yields
`bool + string`. Failure preserves the target/alias, outer destination `100`,
array identities/items/counts and callback writes, with no detach or store.
Two originals and 273 focused premises distinguish raw THROWN from the fresh
indexed TypeError in the
[delayed-RHS failure ledger](../../coverage/semantics/addassign-rhs-failure-review.json).
The inherited entry stays unchanged. Current RHS must still be plain; the live
pair is bounded to valid nonowning scalars or allocated flat DIRECT arrays.
Missing/constrained cells, nested/reference/owning leaves, objects/resources and
wider producers/lifetimes remain partial.

The same bounded CV/reference-cell route now stages leading-numeric-string `/`.
Zend's `div_function` dereferences both operands before conversion; each numeric
holder is filled before its warning. The divisor is tested after conversion, so a
handler-written zero raises DivisionByZeroError, while a second warning retains
captured zero even if its handler writes live7 and returns false. The DIV marker is
removed before ordinary numeric/error delivery: the real caller tail receives a
fresh Error at the operator line and the assignment remains unchanged. Two exact
originals and 130 author plus 94 independent genuine SL premises retain their cuts
in the [DIV ledger](../../coverage/semantics/division-warning-review.json). Initial
selection, fresh input snapshots, historical resume holders, sole Error ownership,
default Warning and budget resumption are checked. Wider operands, callbacks and
lifecycle paths remain required; the ADD bodies and evidence are unchanged.

Selected-reference DIV now also admits valid nonnumeric RHS text before the
LEFT Warning. A separate entry preserves the old plan while the existing phases
capture the left number `12`, run its handler, then convert the selected old RHS. Repair to
`5tail` yields strict float `2.4` despite later writes. Repair to `0tail` still
raises DivisionByZeroError after the current RHS name is rebound to `2tail` and
the old alias becomes `7`. Failed RHS conversion instead uses the live selected
scalar types, including bool / string, and removes its marker before ordinary
TypeError allocation; this also covers the same late failure from old DIV entry.
A first supplied throw cancels later conversion and assignment. Four originals
and 468 focused premises check these routes in the
[DIV repair ledger](../../coverage/semantics/div-repair-review.json).
Selected cells must remain live, untyped and nonowning; other producers,
owning/constrained payloads, failed LEFT conversion and wider lifetimes remain partial.

Selected-reference `-=` now stages both conversions through named Warning
handlers. Cached `12.5 - 5.5` writes strict float `7.0` through the old target alias,
while current names retain replacements `77`/`7`. The RHS may lose its last alias after
capture; returned history keeps its number without a live lookup. A supplied second
Exception from line 20 cancels compound and outer stores, preserving callback value `88`
and outer result `100`.
The scalar store consumes the marker and updates the old cell, result and location
without allocation, detachment or name redirect. Two originals and 183+199 focused
premises cover real fresh/entered phases, raw/driven effects, owners and budgets in
the [compound subtraction ledger](../../coverage/semantics/subassign-warning-review.json).
Initial leading LEFT/quiet RHS in untyped scalar reference cells and a surviving
old-target alias bound the slice. Failed conversions, other producers/targets and
wider lifetimes remain partial.

Selected-reference `/=` now stages LEFT conversion and the delayed old RHS
through named Warning handlers. Both numeric holders survive callbacks. Cached
`12.5`/`5` yields strict float `2.5` in the old target alias even after both current
names rebind to 77/7. A second supplied Exception20 cancels compound/outer stores
and preserves callback88/7. A captured zero instead raises fresh
DivisionByZeroError25 despite RHS repair7 and last-alias retirement; the old target
stays 88 and outer100. Successful storage updates the existing selected cell,
RESULT and LOCATION without detachment or name redirect. Three originals and
554 focused premises retain real fresh/entered phases, raw/driven effects,
owners and budgets in the [compound DIV ledger](../../coverage/semantics/divassign-warning-review.json).
Entry requires leading LEFT/quiet RHS in live untyped scalar reference cells; a
surviving alias keeps the old target live. Fresh inputs and successful targets
have separate guards, while returned holders stay historical after RHS expiry.
Failed conversions, other producers/targets and wider lifetimes remain partial.

Unary `+`/`-` now suspend leading-numeric warnings from defined non-reference
CVs through named handlers. Zend's `zend_compile_unary_pm` lowers to multiplication
by fixed `+1`/`-1`; the operand instruction line governs the warning. The converted
number is captured before dispatch, so handler writes cannot replace it.
Fresh capture/dispatch snapshots are authenticated; entered caller frames and
resumed holders stay historical and add no roots. A supplied throw discards the
unfinished marker. Its Throwable keeps its identity and null Previous; no result
reaches the destination.
Three exact originals and 227 author plus 96 independent genuine SL premises
check negative boundary float delivery, false fallback, public snapshot/message
rejection, ownership and budget resumption in the
[unary ledger](../../coverage/semantics/unary-warning-review.json). Other reference/owning producers, callbacks and lifecycle forms remain required.

Evaluated nonowning copies now enter the same unary `+`/`-` Warning protocol.
The named by-value-return case emits its producer output once before unary plus;
its handler writes source `99`, unsets that source and throws the same Exception
from line 20, leaving outer `100`. The selected-ternary unary-minus case removes
its source, flips the condition and returns false. The unselected assignment
sentinel stays `7`, while native echo `-0` and focused negative-zero bits establish
the copied result's sign. Source retirement leaves the immutable `KNOWN` snapshot
valid; a supplied throw discards the continuation. Unary completion writes no
source cell. Two originals and
118+135 focused premises cover source/carrier authority, real callbacks, raw
versus driven transitions, cancellation, owners, EOF and budget cuts in the
[unary-copy ledger](../../coverage/semantics/unary-copy-warning-review.json).
Old CV/reference entry, function/ternary, numeric and unwind bodies stay unchanged.
Other producers, owning reference results and wider lifecycles remain partial.

Selected scalar-reference unary `+`/`-` now reuses this captured-number protocol.
Fresh snapshots authenticate the selected live unconstrained CELL and actual raw
text. The handler writes old value `99`, rebinds the current name to replacement
`77` and removes its last old alias; that CELL reaches owner zero and retires.
Returned history remains valid without a source lookup or operand-retention root.
A supplied Exception from line 20 cancels outer delivery (`100`). Normal unary minus
instead delivers float zero: native echo `-0` and exact negative-zero bits establish
its sign, while strict equality checks its float type/value. Unary completion writes
no source or replacement cell. Two originals and 134+130 focused premises cover
real fresh/entered callbacks, raw versus driven results, owners, EOF and budgets in
the [unary-reference ledger](../../coverage/semantics/unary-reference-warning-review.json).
Fresh untyped scalar references and primitive handler writes bound these traces;
other producers/constraints/owning payloads and wider lifetimes remain partial.

Plain-CV bitwise NOT now also handles float conversion with only a range
Warning. The original double is saved before that callback; finite signed wrapping
follows its return. At `2^63`, writing source `99` and then unsetting it still gives
`PHP_INT_MAX` after complement, with one default Warning on line 25. Infinity's
supplied Exception from line 20 instead preserves its identity, callback write `99`
and outer `100`, canceling complement and delivery. Neither case emits Deprecated.
Two originals and 116+124 focused premises cover source/bits/line authority,
fresh versus returned snapshots, real callbacks, raw no-store result versus driven
metadata, retirement/fresh EOF and budgets in the
[range BITNOT ledger](../../coverage/semantics/bitnot-range-warning-review.json).
Existing conversion/complement, precision-only/NaN, formatting and unwind bodies
stay unchanged. Initial references/copies, owning values and broader lifecycles
remain partial; paused low-initial-precision name paths are untouched.

Plain-CV NaN bitwise NOT now preserves the two-notice conversion order. Range
Warning precedes precision Deprecated, and the engine checks a pending exception
only afterward. With a first-handler supplied throw, mask `2` still defaults the
second notice; mask `8194` runs neither a second body nor its default. Both cancel
complement and outer storage while keeping the same Exception and the callback’s write of `99`.
The independent normal case handles both notices, unsets the source during the
second handler and returns false: default Deprecated occurs once, then cached zero
produces strict integer `-1` despite source owner zero. Three originals and
158+139 focused premises cover reached handler frames, pending ownership, raw
transitions, default events, EOF and zero/one-step cuts in the
[NaN BITNOT ledger](../../coverage/semantics/bitnot-nan-warning-review.json).
The eligible-pending control has source coverage only. Named handlers and a plain
NaN CV bound this slice; numeric/formatting/CONFIG/module400 and paused low-initial-
precision NaN-name callbacks stay unchanged. Other producers/lifetimes remain partial.

Bitwise NOT now retains a finite in-range fractional float's converted long before its
precision-loss deprecation. The bounded producer accepts a defined non-reference
CV and named handler. Fresh capture/dispatch equals the CV; saved callback frames
and resumed integer holders stay historical, without adding roots. Complement
follows callback return; a supplied throw discards the marker and preserves the
unchanged destination. Three exact originals and 227 author plus 97 independent
SL premises check live 99, negative truncation, false fallback on the operand line,
public snapshot/diagnostic rejection and budget resumption in the
[BITNOT ledger](../../coverage/semantics/bitnot-warning-review.json).
Other operand producers, callbacks and lifecycle forms remain required.

Explicit `(int)` of a range-warning float in a plain nonreference CV now
resumes a named handler using the original double. Finite `2^63` wraps to
`PHP_INT_MIN` even after the callback replaces it with same-spelling text whose
quiet cast saturates to `PHP_INT_MAX`. C saves the double before Warning and
wraps afterward; the model's earlier pure long calculation adds no observable effect.
The explicit false conversion flag gives NaN one range Warning, without the
implicit-safe precision notice. A supplied Exception cancels delivery after source
removal, preserving identity and outer `100`. Two source cases and 145+122 focused
premises cover real
callbacks, fresh versus historical validation, EPS roots, raw typed result/BASE,
retirement, diagnostics and budgets in the
[integer-cast range ledger](../../coverage/semantics/int-cast-range-warning-review.json).
The original rule-label parser failure stays zero; numeric/string/formatting and
generic unwind bodies remain unchanged. Normal NaN, throwing finite conversions
and wider producers/lifetimes remain partial; paused DEFINE precision is untouched.

Explicit `(int)`/`(float)` casts of an empty `stdClass` in a plain CV now stage
one named-handler Warning. The VM borrows that CV and formats the class message
before calling the handler; no conversion owner keeps the object alive. Replacing
or unsetting its sole source makes the existing WeakReference observer return null
inside the callback. Float conversion then delivers strict `1.0` without rereading
the missing source. An integer-cast supplied Exception from line 20 instead preserves
identity, null Previous, callback write `99` and outer `100`, canceling delivery.
Two originals and 134+138 focused premises cover fresh versus historical validation,
real callbacks, object retirement/nonowning weak history, EPS task roots, raw versus
driven effects, EOF and budgets in the
[object numeric-cast ledger](../../coverage/semantics/object-numeric-cast-warning-review.json).
WeakReference, GC, numeric and unwind bodies stay unchanged. Normal int completion,
throwing float conversion, other classes/producers and wider lifetimes remain partial.

Explicit `(string)` casts now stage an array warning for a defined non-reference
CV holding a nonempty mutable flat array of direct, defined nonowning scalars.
Source and compiled operand-line authority accompany the CV identity. Fresh
capture/dispatch checks the array; saved handler frames and resumed stages keep
history when the CV is replaced or removed. No PARRAY is saved and no task owner
keeps that borrowed array alive. Normal return delivers fixed interned `Array`
without changing storage; a supplied throw discards the marker before assignment.
Three exact originals and 213 author plus 113 independent SL premises check
owner one to zero, real saved TARGET/caller-throw fronts, default Warning at the
operand line, public guard rejection and budget continuation in the
[array-cast ledger](../../coverage/semantics/array-string-cast-warning-review.json).
Empty/immutable/nested/reference-element/owning arrays, copied/reference operands,
wider callbacks and lifecycle forms remain partial. Pure refusal projections
are not executed typed or owning array cases.

Ordinary `.` also stages array warnings for two distinct defined plain CVs,
with one nonempty mutable flat DIRECT scalar array and one quiet string. Both
branches start at authentic `CONCAT_PREP`: a left-array warning yields fixed
interned `Array` before reading the same live RHS CV cell, while a right-array
warning keeps the first converted string in the existing legacy continuation.
Fresh capture/dispatch verifies source, RHS line, snapshots and adjacent consumer;
historical return permits removal of the borrowed array without retaining it.
A supplied throw cancels the assignment and removes both warning/legacy markers.
Three exact originals and 270 author plus 135 independent SL premises pass in the
[concat-array ledger](../../coverage/semantics/concat-array-warning-review.json).
Pruned/missing-name and RHS projections are pure refusals, never driven.
After a left-array warning, missing/rebound/new-reference/non-string later RHS
remain partial, along with wider arrays/operands, callbacks and lifecycle forms.

Plain-CV `.=` now handles a quiet first string and a supported array RHS.
Its source-authenticated warning marker caches the exact first string carrier;
fresh capture/dispatch proves initial plain selections, while historical return
allows the RHS to disappear and a late destination reference to appear. No array
owner is saved. Normal commit joins cached string with fixed `Array`, detaches a
late wrapper and records the actual written CELL/LOCATION. A supplied throw cancels
the store and preserves callback mutations and aliases. Three exact originals and
285 author plus 110 independent SL premises pass in the
[concat-assignment ledger](../../coverage/semantics/concatassign-array-warning-review.json).
Pure missing/allocation/PROPREF/owning projections are refusal checks only.
Left-array warnings, wider operands/targets/callbacks and lifecycle forms remain partial.

Concatenation has an additional compile/runtime distinction. The compiler visits
both operands before converting known scalar operands and queuing conversion
warnings. At execution, known array operands produce their conversion warnings
before delayed variable reads at the final operator. Captured operand roots stay
live throughout conversion and evaluation. This preserves warning order under
rebinding, singleton references, COW and cycles.

Ordinary `**` now suspends zero-base/negative-exponent deprecation for two
bounded primitive numbers in distinct plain CVs. Source, selection, current values
and RHS instruction line authenticate fresh dispatch; entered and returned stages
retain both historical numbers. The zero-root marker resumes through existing pure
power rules without repeating the diagnostic. Signed negative zero to an odd
negative exponent still yields `-INF` after live operand writes. A supplied throw
cancels delivery and preserves the destination. Three exact originals plus
265 author and 101 independent SL premises pass in the
[power-warning ledger](../../coverage/semantics/power-warning-review.json).
Counterfeit source/cache/range/metadata states are validator negatives only.
Other copied and wider operand/callback/lifecycle forms remain partial.

Binary `**` also admits leading numeric LEFT strings on two preexisting untyped
reference cells. Both referents are selected first; the LEFT Warning may repair initially
nonnumeric RHS text before its conversion. Each number is captured before its
Warning. A final power Deprecated uses both historical holders even at fresh
dispatch, after callbacks changed the cells or rebound the RHS name. A surviving
alias retains the selected old RHS; its one owner stays distinct from the current
replacement's two owners. Cached numbers yield integer `8`, strict float `2.0` or
signed infinities despite live writes. Failed conversion reports live selected
types; supplied throws cancel outer result assignment while callback writes survive.
Seven exact originals and 951 focused premises cover real phases, default Warning/
Deprecated bytes, atomic results/errors, owners and budgets in the
[power-conversion ledger](../../coverage/semantics/power-conversion-review.json).
Other mixed/copied/owning/constrained or expired operands and wider
callbacks/lifecycles remain partial. Old numeric-CV power and other arithmetic
bodies and evidence are unchanged.

Quiet LEFT/right-only leading-number Warnings now use the same selected-reference
`+`, `-`, `*`, `/`, `**` paths. A shared pure ingress check adds four plan arms;
the unchanged CONVERT LEFT then RIGHT steps capture both numbers without a LEFT
callback. The sole RHS Warning cannot replace those holders: cached results include
`17`, `7`, `60`, float `2.4` and `248832`, while cached zero still raises DivisionByZeroError.
Final power Deprecated retains both numbers after the current RHS name is rebound;
a surviving alias keeps the old selected cell live. Nine originals and 576 focused
premises cover all four plan arms, strict float `68.75`, signed infinity, default
diagnostics and result/error ownership in the
[right-warning ledger](../../coverage/semantics/right-arithmetic-warning-review.json).
Other mixed/copied/owning/constrained or expired operands, other conversion orders
and wider callbacks/lifecycles remain partial. Earlier evidence receives no renewed credit.

Ordinary arithmetic now also stages these diagnostics for two initially plain CVs.
Their selected pointers name the original CV slots, rather than reference referents.
Only the pending input must remain defined, untyped, nonowning and nonreference
when converted: LEFT may already be historical when RHS warns. A first Warning
can repair bad RHS text. Once RHS is captured, its new alias or missing binding
does not invalidate the number; final power Deprecated likewise uses both holders.
The dedicated path leaves old pointer readers and reference continuations exact.
Ten originals and 1,055 focused premises check quiet/leading LEFT, cached results,
live bool/string TypeError, supplied Warning/Deprecated throws, and one cell owner
versus two after aliasing or none after unset in the
[plain-arithmetic ledger](../../coverage/semantics/plain-arithmetic-warning-review.json).
Other mixed/copied/reference-result and owning/constrained operands, pre-conversion
reference creation and wider lifecycles remain partial.

The same arithmetic holders now accept exactly one initially plain CV and one
pre-existing reference. Both selections precede numeric conversion: the reference
keeps its original cell when its name is rebound, while the plain input names its
CV until capture. Until converted, the selected cell must remain allocated, untyped,
live and nonowning; a surviving alias keeps it alive in these witnesses. A fresh RHS Warning
reads that old referent even when the current name selects a replacement. Returned
holders and final power Deprecated use history, while failed conversion reports
the live types at the selected pointers. Separate mixed entry preserves old plain
and reference plan controls and reuses all conversion/result bodies.
Nine originals and 858 focused premises check both orientations, quiet/leading
entry, cached float `68.75` after old-RHS rebinding, old bool-string TypeError,
cached-zero division after RHS-name unset and final supplied-throw cancellation.
Old and replacement cell owners, exact atomic effects and budgets are recorded in
the [mixed-arithmetic ledger](../../coverage/semantics/mixed-arithmetic-warning-review.json).
Other copied/reference-result/owning operands, unheld referent lifetimes, wrapping a
pending plain input and wider callbacks remain partial; OP12 remains paused.

Staged arithmetic Warnings also admit evaluated nonowning scalar copies from
literals, unary/selected-ternary expressions and by-value named returns, paired
with another copy, a plain CV or a selected live reference. Copies keep raw values
independently of their originating variables: repairing a source cannot repair a
copied bad RHS, and unsetting sources does not invalidate captured numbers.
Descriptors retain lexical operands; MUL alone follows the pinned opcode slot-rank
swap when choosing conversion and raw-error pointers. Thus literal-left/CV-right
`12tail * 5tail` yields `60` with two Warnings, while by-value-VAR/TMP multiplication
stays unswapped. Fresh COPY checks use saved values; returned/final holders remain
historical. Old entry controls/readers stay exact and old unswapped pointer choices
are equivalent through the phase adapter. Ten originals and 767 focused premises
check real phases, physical bool-string errors, copied raw-type labels, strict
`68.75` after both origin names disappear and final power supplied-throw cancellation
in the [copied-arithmetic ledger](../../coverage/semantics/copied-arithmetic-warning-review.json).
Other quiet/no-Warning MUL orders, owning payloads and other reference-result producers,
pending-CV wrapping and wider lifetimes remain partial; OP12 stays paused.

Staged arithmetic Warnings now also retain evaluated reference results from an
untyped byref named return or direct-CV reference assignment. Each operand adds
its real cell owner, even when both refer to the same cell; selected pointers and
number holders add none. The owner survives source-name removal through both
conversion Warnings and final power Deprecated, then retires on result, error or
supplied throw. Reference selection and physical MUL order reuse existing rules.
Nine originals and 853 focused premises check shared-cell `17` with owners3→2→0,
swapped repair-before-conversion, strict division after both origins disappear,
live bool-string TypeError, cached-zero Error and same supplied Exception20.
Raw numeric PhpStep equality is checked separately from actual driver pruning in
the [owned-arithmetic ledger](../../coverage/semantics/owned-arithmetic-warning-review.json).
All selected reference cells must remain defined, live, scalar and unconstrained
throughout this trace domain. Late owning/constrained replacements can invalidate
an entered continuation; an explicit completion/lifecycle boundary remains open.
Wider producers, typed returns and other quiet/no-Warning orders remain partial; OP12 paused.

Quiet nonowning scalar MUL failures now use authenticated opcode slot order for
TypeError labels. CONST1/TMP2/VAR4 before CV8, and TMP2 before VAR4, swap the two
raw operands; equal/reverse ranks keep lexical order. A by-value RHS producer can
repair the originating LEFT variable to 12 after its TMP copy was captured, yet
the error remains float * string. Both selected reads must be defined, both
conversions quiet, and at least one value nonnumeric. Numeric products and staged
conversion Warnings use their unchanged rules. Seven originals and 217 focused
premises separate raw `THROWN` from a fresh TypeError at line 25 with no previous
exception. The destination stays unchanged and no Warning callback runs; see the
[quiet-MUL ledger](../../coverage/semantics/quiet-multiply-order-review.json).
Undefined/owning inputs, wider producers and other diagnostic orders remain partial.

Quiet POWER now also admits an authenticated ternary LEFT scalar copy and a
plain RHS CV. Both numeric conversions are quiet, so a single step captures the
holders and enters the existing final Deprecated continuation; the named handler
needs only `E_DEPRECATED`, with no conversion Warning. Final dispatch and finish
retain historical numbers after source writes or unsets: captured holders
`0.0`/`-2` yield `+INF`, and `-0.0`/`-3` yield `-INF`. A supplied Exception cancels
outer result delivery while preserving callback writes and destination100. Three originals and 266
focused premises cover direct ingress, real handler frames, default Deprecated,
same-Exception cancellation and missing-source history in the
[quiet-power-copy ledger](../../coverage/semantics/quiet-power-copy-review.json).
Other quiet-power producers, reference/owning operands and wider lifetimes remain partial.

Primitive plain-CV `**=` now retains both numbers and the original target binding
through zero-base/negative-exponent deprecation. Normal return stores the captured
signed result. A throwing handler also commits and detaches a late target alias
before the same pending Exception resumes; the enclosing assignment stays unchanged.
The pending marker replaces exactly one Throwable owner. Commit records the actual
written CELL/LOCATION, while the old alias retains its callback value and sole owner.
Three exact originals plus 296 author and 111 independent SL premises check these
paths, default operand-line Deprecated, fresh guards and budgets in the
[power-assignment ledger](../../coverage/semantics/powerassign-warning-review.json).
Ready requires the same live, allocated, nonowning, unconstrained target; pure
pruned/missing/wrong-slot/owning projections establish refusals only. Other initial
reference/copy forms, wider operands/targets, callbacks and lifecycle remain partial.

Quiet selected-reference `**=` now captures both primitive numbers before final
Deprecated. A supplied handler Exception still permits the compound store:
cached `+INF` replaces the callback's `88` in the selected old target alias before
the same Exception resumes; the outer assignment retains `100`.
A false handler with captured negative-zero/-3 yields strict `-INF` in old target
and result even after both current names rebind to 77/7 and the old RHS loses its
last alias. Fresh dispatch authenticates both selected live unconstrained cells;
returned history avoids RHS lookup, and the final target has its own safety guard.
The scalar store consumes the marker and changes only old STORE/RESULT/LOCATION
(or restores THROW_SEARCH and clears delivery); no cell, detachment or ENV redirect.
Two originals and 181+153 focused premises check raw/driven effects, pending owner2,
retired RHS owner0, alias topology and budgets in the
[selected power-assignment ledger](../../coverage/semantics/powerassign-selected-warning-review.json).
Initial quiet PINT/PFLOAT references and a surviving old-target alias bound the slice.
Other text conversions, producers/targets and wider lifetimes remain partial.

Selected-reference `**=` now also stages leading-text conversions before final
Deprecated. Each number is captured before its own Warning. A supplied second
conversion Exception leaves callback value `88` and outer result `100` unchanged;
a final Deprecated Exception instead permits cached `+INF` to replace callback
value `66` in the old target before that same Exception resumes. Outer delivery stops.
The final marker owns the pending Throwable until the mandatory store restores
`THROW_SEARCH`; old quiet-power snapshot and commit rules remain exact.
An independent signed-zero/default case delivers strict `-INF` through the old target
after both current names rebind to `77`/`7` and the captured RHS retires. Three originals
and 186+241+261 focused premises cover real fresh/entered callbacks, historical holders,
raw/driven marker/store effects, owners and budgets in the
[converted power ledger](../../coverage/semantics/powerassign-conversion-warning-review.json).
Initial leading LEFT/quiet RHS untyped scalar refs and a surviving old-target alias
bound the slice. Before final dispatch and store the old target must be PINT/PFLOAT,
avoiding refcounted-target destruction. Wider values/producers/lifetimes remain partial.

Selected-reference `%=` now converts a freshly rebound fractional RHS after the
first LEFT Deprecated callback. The current RHS CV selects that reference live;
its long is then captured before the second Deprecated. Captured `0.5` becomes
zero even when the second handler repairs current RHS to `5` and the original RHS
alias also holds `5`: fresh `DivisionByZeroError` at line 25 preserves callback
old target `88`, current target name `77` and outer `100`. Conversely, captured
`5.5` becomes `5` even when its fresh reference is changed to `7` and both owning
names are unset. Cached `12 % 5` stores integer `2` through the surviving old
target alias; current name `77` and original RHS alias `0` remain independent.
Two originals and 190+174 focused premises cover both reached fresh/entered
handlers, current selection versus returned history, RHS owners two to zero,
raw capture/store or THROWN versus driven fresh Error, EOF and budget cuts in the
[RHS conversion ledger](../../coverage/semantics/modassign-selected-rhs-warning-review.json).
Initial selected scalar references with fractional LEFT and quiet PINT RHS stay
unchanged. Later fitting fractional RHS references, named Deprecated handlers and a safe
surviving old target bound the slice; other values, owning/typed producers and
wider lifetimes remain partial. Generic throw/unwind and numeric bodies are unchanged.

Selected-reference `%=` now fixes its old LEFT cell before converting a fitting
fractional float. Captured `12` survives the named Deprecated callback; RIGHT stays
a delayed CV wrapper and is dereferenced afterward. Rebinding current RHS from
old `0` to replacement `5` therefore stores integer `2` through the surviving old
target alias, despite callback value `99` and current target name `77`. Rebinding
old RHS `5` to current `0` instead raises Modulo-by-zero DivisionByZeroError at
RHS line 25 without replacing callback `88` or outer `100`. Both original aliases
stay live with one owner, while rebound names and replacements share two.
Two originals and 151+170 focused premises cover actual fresh/entered callbacks,
source/selection controls, raw store or THROWN versus driven fresh Error, owners,
EOF and zero/one-step cuts in the
[selected modulo ledger](../../coverage/semantics/modassign-selected-warning-review.json).
Initial scalar refs, finite in-range fractional LEFT, quiet PINT RHS before and
after the callback, and a safe surviving old target bound the slice. Other
conversions, producers/constraints/owning payloads and lifetimes remain partial.

Plain-CV `%=` now captures a fractional-float left conversion before its
deprecation, then reads the live quiet integer RHS after a named handler returns.
Captured `12` and live `5` produce `2` despite the callback's target write.
A supplied throw cancels storage and preserves its Exception identity; a live
zero creates the ordinary caller `DivisionByZeroError` without writing or
detaching a late target alias. False return emits one default Deprecated on the
compiled RHS line. Three exact originals and 242 author plus 120 independent SL
premises pass in the
[modulo-assignment ledger](../../coverage/semantics/modassign-warning-review.json).
Fresh source/selection/cache/line guards, actual CELL/LOCATION, alias/error owners
and budget resumption are covered. Pure ready projections establish refusals only.
Other initial references/copies, warning or noninteger RHS values, unsafe targets,
wider callbacks and lifecycle paths remain partial.

For a quiet integer LEFT and fractional-float RIGHT, `%=` keeps both converted
longs through the RHS deprecation. Captured `12 % 5` stores `2` despite callback
writes of `99` and `7`; a late target alias detaches and retains `99`. Supplied
throw cancels storage and preserves the alias. Captured `0.5` becomes a zero
divisor even after a callback writes `5`, producing the ordinary RHS-line
`DivisionByZeroError` without storage or detachment. Ready checks only the original
safe target; it never rereads the RHS. Three exact originals and 267 author plus
137 independent SL premises pass in the
[RHS modulo ledger](../../coverage/semantics/modassign-right-warning-review.json).
Fresh cache/source/line/range guards, actual cells/owners, default Deprecated and
budgets are covered; pure refusals establish no wider execution. Wider operand
combinations, initial references/copies, unsafe targets and wider lifecycle remain partial.

For two initially fractional-float plain CVs, `%=` captures LEFT before its first
deprecation, then reads the RHS after that callback. Captured `12` with the new
`5.5` captures divisor `5` before the second deprecation; later writes `88`/`7`
still store `2`, leaving late alias `88` detached. A quiet integer `5` after the
first callback instead reaches the existing modulo commit with one diagnostic.
Either supplied handler throw cancels storage and preserves its Exception, callback
writes and alias. Captured `0.5` remains zero despite a second callback writing `7`:
one default Deprecated precedes the original-line `DivisionByZeroError`, without
storage or detachment. Five exact originals and 746 author plus 183 independent SL
premises pass in the
[ordered modulo ledger](../../coverage/semantics/modassign-both-warning-review.json).
Fresh first-LEFT and second-RHS guards, actual entered frames, quiet handoff,
cells/owners and budgets are covered; LEFT remains historical at the second
capture. Initial references/copies, other RHS conversions, unsafe or rebound
bindings and wider callbacks/lifecycle remain partial; pure projections are refusals only.

After the first modulo callback, a fitting integral float RHS also converts
without a second diagnostic. Historical LEFT `12` and live `5.0` store `2` through
a fresh result cell, detaching late alias `99`; the RHS remains a float. A supplied
first-handler throw preserves its Exception, destination and alias write-through.
Independent default-first `-0.0` instead raises `DivisionByZeroError` at RHS line 25
without storing or detaching. Three exact originals and author 135/99 plus
independent 130 SL premises pass in the
[quiet float modulo ledger](../../coverage/semantics/modassign-quiet-float-review.json),
covering the actual atomic commit/error, original bindings, owners and budgets.
Initial references/copies, unsafe targets and wider RHS/callback/lifecycle forms
remain partial; refusal projections do not establish wider execution.

Selected-reference `>>=` fixes the old target before converting LEFT, but resolves
the RHS CV after its Deprecated callback. Captured `-12` with rebound count `64`
stores strict integer `-1` through the surviving old alias despite callback target
`99` and current LEFT `77`; old count `2` would give `-3`, and a positive LEFT
would give `0`. A rebound count of `-1` instead raises `ArithmeticError` with
`Bit shift by negative number` at RHS line 25, preserving callback target `88`,
outer `100` and alias topology. EOF writes still reach old aliases separately
from replacement cells. Two originals and 195+163 focused premises cover real
fresh/entered callbacks, source and reference controls, returned LEFT history,
raw no-store THROWN or old-cell store, driven fresh indexed Error, owners and
zero/one-step cuts in the
[selected shift ledger](../../coverage/semantics/shiftassign-selected-warning-review.json).
Initial untyped primitive references, fitting fractional LEFT, quiet PINT count
and a safe surviving old target bound this slice. SHIFTLEFT, additional count
conversions, typed/owning operands and wider producers/lifecycles remain partial;
numeric and generic-unwind bodies keep their earlier cuts.

For distinct initially plain CVs, `<<=` and `>>=` keep a fractional-float left
conversion before their deprecation and read the live quiet integer count afterward.
Captured `-12` with live count `2` stores `-48` or `-3` despite callback target `99`;
successful replacement detaches a late alias, which retains `99`. Supplied throw
cancels storage. A negative live count raises the ordinary RHS-line `ArithmeticError`
before storage or detachment. Four exact originals and 406 author plus 120 independent
SL premises pass in the
[shift-assignment ledger](../../coverage/semantics/shiftassign-warning-review.json).
Both AST directions have their own source authority; old modulo validators stay
unchanged. Fresh cache/source/op/line guards, actual cells/owners, default Deprecated
and budgets are covered. Pure ready projections establish refusals only. Other initial
references/copies, warning or noninteger counts, unsafe targets and wider lifecycle
remain partial.

With a quiet signed-64-bit integer LEFT, distinct initially plain CV `<<=`/`>>=`
cache both longs before a fractional-RHS deprecation. Captured `-12`/`2` from `2.5`
stores `-48`/`-3` despite callback `99`/`1`, detaching a late alias. Supplied throw
cancels storage. A cached negative count still raises RHS-line `ArithmeticError`
after the live count becomes positive; a captured `64` uses the original LEFT
sign for right shift. Resumption checks the safe original target without rereading
either numeric operand. Five exact originals and 438 author plus 236 independent
SL premises pass in the
[RHS shift ledger](../../coverage/semantics/shiftassign-right-warning-review.json).
Both source directions, fresh cache/source/op/line guards, actual cells/owners,
default Deprecated and budgets are covered. Pure projections establish refusals
only. Wider operand combinations, initial references/copies, unsafe targets and
wider lifecycle remain partial; earlier modulo/LEFT-shift contracts stay unchanged.

For two initially fractional-float plain CVs, `<<=`/`>>=` retain LEFT before its
first deprecation, then read the live count after that callback. Captured `-12`
with the new `2.5` captures count `2` before the second deprecation; later writes
`88`/`1` still store `-48` or `-3` and detach late alias `88`. A quiet integer
count `2` after the first callback instead reaches the existing shift commit with
one diagnostic, leaving alias `99`. Either supplied handler throw cancels storage,
preserving the same Exception, callback writes, destination and alias write-through.
Cached `-1` from `-1.5` still raises the original-line `ArithmeticError` after its
default Deprecated even if the second callback writes positive `2`, without
storage or detachment. Six exact originals and 989 author plus 183 independent SL
premises pass in the
[ordered shift ledger](../../coverage/semantics/shiftassign-both-warning-review.json).
Both AST/OP pairs, fresh first-LEFT/second-count guards, actual entered frames,
quiet handoff, cells/owners and budgets are covered. LEFT stays historical at
second capture; pure projections are refusals only. Initial references/copies,
other count conversions, unsafe bindings/targets and wider callbacks/lifecycle remain partial.

After the first callback in that both-fractional shift route, a fitting integral
float count also converts quietly. Historical LEFT `-12` and live `2.0` store
`-48`/`-3` directly through fresh result cells, detaching alias `99`; the RHS stays
a float and calls stay one. A supplied first-handler throw preserves its Exception,
destination and alias write-through. Independent default-first `-1.0` raises
`ArithmeticError` at RHS line 25 without storage or detachment; `64.0` still gives
right-shift `-1` from the cached negative sign despite live LEFT `99`, detaching
its alias. Five exact originals and author 135/135/99 plus independent 130/130 SL
premises pass in the [quiet float shift ledger](../../coverage/semantics/shiftassign-quiet-float-review.json),
covering actual atomic commit/error, original bindings, cells/owners and budgets.
Wider initial forms, conversions, unsafe targets and lifecycle remain partial;
pure projections establish refusals only, and older threshold cuts are not renewed.

Selected-reference `^=` also protects a leading fractional RHS string before its
Warning. After LEFT Deprecated, old `5.5tail` is selected despite current RHS `7`.
A supplied Warning throw returns the same Exception at line 20 and skips the
later precision diagnostic and compound store, leaving callback write `88` and outer
`100`. Normal return instead retains the original quoted `"5.5tail"` message and
long `5` after the old RHS is rewritten to `7` and loses its last owner. The third
callback writes old target `66`; cached `12 XOR 5` then stores integer `9` through
its surviving alias while current LEFT `77` remains separate. Two originals and
200+250 focused premises cover real callbacks, fresh selection versus returned
history, raw TODO-only capture/store, cancellation, owners, EOF and budget cuts
in the [protected XOR text ledger](../../coverage/semantics/xorassign-selected-rhs-warning-review.json).
Initial untyped scalar references, fractional LEFT/quiet PINT initial RHS,
exactly leading Warning plus string-precision Deprecated and a safe surviving
target bound the slice. Single-notice text, other conversion forms/producers,
typed or owning cells and wider lifecycles remain partial. Existing generic
unwind, numeric conversion and diagnostic-formatting bodies stay unchanged.

Selected-reference `^=` now dereferences both operands and chooses numeric
specialization before converting fractional LEFT. Captured `12` survives the
Deprecated callback; selected old RHS `5`, rather than rebound current name `7`,
produces integer `9` through the surviving old target alias. Current LEFT `77`
and replacement bindings remain separate. If the handler instead changes both
old values to nonnumeric strings, `TypeError` reports `string ^ string` at line 25
without retrying bytewise XOR, replacing the old string or changing outer `100`.
Two originals and 199+163 focused premises cover real fresh/entered callbacks,
source/selection controls, returned LEFT history, raw store or THROWN versus fresh
indexed Error, owners, EOF and zero/one-step cuts in the
[selected XOR ledger](../../coverage/semantics/xorassign-selected-warning-review.json).
Initial untyped scalar references, fitting fractional LEFT and quiet PINT RHS,
later quiet PINT or failed nonowning scalar RHS conversion and surviving aliases
bound the slice. Other conversions, operators, producers and owning lifetimes
remain partial; generic unwind and numeric algorithms keep their earlier cuts.

For distinct initially plain CVs, numeric `&=`, `|=` and `^=` keep a fractional
LEFT conversion before deprecation and read the live quiet integer RHS afterward.
Captured12/live5 stores4/13/9 despite callback target99 and initial RHS3, detaching
a late alias. A supplied handler Exception cancels storage, preserving callback
writes, the same Throwable and alias write-through. Independent signed XOR keeps
captured(-12)/live5 and stores(-15), with exactly one RHS-line16 default Deprecated.
Five exact originals and 575 author plus 117 independent SL premises pass in the
[bitwise-assignment ledger](../../coverage/semantics/bitassign-warning-review.json).
All three AST/operation pairs have separate source authority from modulo/shifts.
Fresh cache/source/op/line guards, actual cells/owners and budgets are covered;
pure projections establish refusals only. Other initial references/copies, warning or
noninteger RHS, unsafe targets and wider lifecycle remain partial. Initial float
LEFT/quiet integer RHS bypasses Zend's separate two-string specialization.

With a quiet signed-64-bit integer LEFT, distinct initially plain CV numeric
`&=`, `|=` and `^=` keep both converted longs through fractional-RHS deprecation.
Captured12/5 from5.5 stores4/13/9 despite callback99/10 and detaches a late alias;
a supplied handler Exception cancels storage and preserves callback writes, the
same Throwable and alias write-through. A negative converted RHS remains an
ordinary bit mask: captured12/(-1) stores XOR(-13), with default Deprecated at
RHSline16. Only the safe original target is rechecked; the numeric RHS is not reread.
Five exact originals and 605 author plus 119 independent SL premises pass in the
[RHS bitwise ledger](../../coverage/semantics/bitassign-right-warning-review.json).
All three source/OP pairs, fresh both-cache/source/line/range guards, actual cells/
owners and budgets are covered; pure projections establish refusals only.
Wider operand combinations, initial references/copies, unsafe targets and wider
lifecycle remain partial. Earlier modulo/shift/LEFT-bitwise contracts stay unchanged.

For two initially fractional-float plain CVs, numeric `&=`/`|=`/`^=` retain LEFT
before its first deprecation, then read the live RHS after that callback. Captured
`12` with the new `5.5` captures mask `5` before the second deprecation; later
writes `88`/`10` still store `4`/`13`/`9` and detach late alias `88`. A quiet integer
RHS `5` after the first callback instead reaches the existing OR commit with one
diagnostic, leaving alias `99`. Either supplied handler throw cancels storage,
preserving the same Exception, callback writes, destination and alias write-through.
Cached `-1` from `-1.5` remains a valid mask: XOR still stores `-13` after the second
default Deprecated despite live `88`/`10`, leaving alias `88` detached. Seven exact
originals and 1240 author plus 181 independent SL premises pass in the
[ordered bitwise ledger](../../coverage/semantics/bitassign-both-warning-review.json).
All three AST/OP pairs, fresh first-LEFT/second-RHS guards, actual entered frames,
quiet handoff, cells/owners and budgets are covered. LEFT stays historical at
second capture; pure projections are refusals only. Initial references/copies,
other RHS conversions, unsafe bindings/targets and wider callbacks/lifecycle remain partial.

After the first callback in that both-fractional bitwise route, a fitting integral
float RHS also converts quietly. Historical LEFT `12` and live `5.0` directly store
`4`/`13`/`9` through fresh result cells, detaching alias `99`; the RHS remains a
float and calls stay one. A supplied first-handler throw preserves its Exception,
destination and alias write-through. If the first handler returns false with RHS
`-1.0`, XOR still stores `-13` despite live LEFT `99`, with one default LEFT Deprecated
at RHS line 25 and no second diagnostic. Five exact originals and author
135/135/135/99 plus independent 130 SL premises pass in the
[quiet float bitwise ledger](../../coverage/semantics/bitassign-quiet-float-review.json),
covering actual first frames, original bindings, atomic storage, cells/owners and
budgets. Wider initial forms, conversions, unsafe targets and lifecycle remain
partial; pure projections establish refusals only.

The first callback in the both-fractional plain-CV `%=`/shift/numeric-bitwise routes
may also leave a quiet `bool` or `null` RHS in its original nonreference cell.
`true` converts to 1; `false` and `null` to 0, with no second warning. Historical
LEFT `12` with `true` stores `0`/`24`/`6`/`0`/`13`/`13` for `%=`/`<<=`/`>>=`/`&=`/`|=`/`^=`;
success detaches the handler's alias `99`. False/null modulo raises DivisionByZeroError
at RHS line 25 before store/detachment, preserving destination `100` and alias write-through.
Independent default-first null XOR stores `12` despite current `99`, while null modulo
preserves the alias; both have one LEFT Deprecated. A supplied first throw retains
its Exception and skips conversion. Ten exact originals and 688 focused SL premises
(one fixture per new rule plus the independent null cases) pass in the
[quiet scalar ledger](../../coverage/semantics/quiet-scalar-review.json).
Other initial forms, conversions, unsafe targets and wider lifecycles remain partial;
type/ref/binding/ownership projections are refusals only.

The first callback may also leave a complete quiet numeric string in the original
RHS cell of those both-fractional routes. Existing `string_long` must return an
integer with no notices; plain strings or authenticated interned/request carriers
retain their bytes/type/identity. Initial floats already selected numeric bitwise
behavior. Cached LEFT `12` and numeric string `5` store `2`/`384`/`0`/`4`/`13`/`9`
for `%=`/`<<=`/`>>=`/`&=`/`|=`/`^=` and detach alias `99`. Dynamic nonempty concat
creates a genuine request carrier `"05"`; OR also covers `" +5e0 "`. Supplied first
throw preserves its Exception, destination and alias write-through. Independent
default-first `"-1"` yields XOR `-13` but ArithmeticError for right shift; `"0"`
modulo raises DivisionByZeroError. Both errors occur at RHS line 25 before store/detachment.
Ten exact originals and 807 focused SL premises pass in the
[quiet string ledger](../../coverage/semantics/quiet-string-review.json), covering
actual handlers, direct stores/errors, carrier metadata, cell/Throwable owners and
budgets. Other warning/invalid conversions, unsafe bindings/targets and wider forms stay
partial; pure guard controls are distinct from executed cases.

A leading numeric string in the original RHS cell now issues its own Warning after
that first callback when `string_long` returns only `LEADINGNUMBER`, with no further
precision-loss diagnostic. LEFT remains historical; the selected RHS parse is
saved before the Warning, including exponent text with an exact integer value.
A fresh second dispatch authenticates the current RHS, message, phase and original
RHS line. After its callback only target readiness is required: current RHS writes,
reference rebinding or unset cannot replace either saved number. Dynamic `"05tail"`
and literal/exponent text store `2`/`384`/`0`/`4`/`13`/`9` from cached LEFT `12` and
numeric `5`, detaching alias `88`; either supplied throw keeps the same Exception,
destination and alias write-through. Independent default-second `"-1tail"` XOR
stores `-13` even after RHS aliases target `88` (target owners 3 to 2 on detach);
negative shift with RHS unset and `"0tail"` modulo despite live RHS `7` instead raise
ArithmeticError/DivisionByZeroError at RHS line 25 before store/detachment.
Eleven originals and 1211 focused SL premises (four author plus three independent
fixtures) pass in the [leading string ledger](../../coverage/semantics/leading-string-review.json),
covering actual handlers, parse/carrier history, storage/owners and budgets.
The pre-application notice-list failure and over-strong cross-callback metadata
assertion retain zero credit. Only corrected checks and previously unrun peers
execute; accepted author states and source cuts remain unchanged. Other notice
shapes, unsafe pre-snapshot RHS/targets and wider lifecycle remain partial.

After the first LEFT callback in those initially both-fractional plain-CV routes,
an authenticated nonnumeric-string or allocated-array RHS now fails integer
conversion with TypeError before any compound store or alias detachment. Messages
use the live dereferenced operand types: callback bool/NULL/float/string changes
produce `bool % string`, `null << string`, `float >> string` and all three
`string &/|/^ string` labels. The earlier bitwise specialization decision remains
fixed; two live strings do not retry a bytewise operation. Default-first peers
cover `string ^ string`, `null % array` and `bool >> array` at RHS line 25, preserving
callback writes, destination 100, RHS identity/array ownership and later alias
write-through. Ten originals and four focused state fixtures (566 premises) pass
in the [delayed failure ledger](../../coverage/semantics/delayed-type-failure-review.json).
The shared live-pair predicate and three error rules add no task/schema/protocol;
pre-snapshot RHS references, unsafe targets, other initial forms and wider
conversions/lifetimes remain partial.

Fractional numeric-string RHS values now capture the existing conversion when its
notices are exactly precision Deprecated, or leading Warning followed by precision
Deprecated. One cursor preserves the original string and number: its first RHS
dispatch authenticates the live original CV, while later precision dispatch uses
history even after RHS reference rebinding or unset. LEFT remains historical after
its own callback. Dynamic `"05.5tail"`, complete text and exponent text use cached
LEFT `12`, not callback `101`; all six operators and three new throw fronts agree.
Independent complete `"-1.5"` XOR stores `-13` after RHS aliases target `88`, detaching
owners 3 to 2; leading negative shift after RHS unset and cached-zero modulo despite
live `7` instead raise ArithmeticError/DivisionByZeroError at RHS line 25 without storing. Default
Warning and protected precision Deprecated retain their exact order and messages.
Twelve originals and six focused fixtures (1089 SL premises) pass in the
[precision string ledger](../../coverage/semantics/precision-string-review.json),
including real callback frames, carrier identity, storage/owners, supplied Exception
identity and resumed budgets. The original pre-evaluation declaration-order failure
retains zero credit. Other notice shapes, initial forms, unsafe pre-snapshot RHS or
targets and wider callback/lifecycle behavior remain partial.

The existing fractional-LEFT/initial quiet-integer RHS routes now continue through
that same post-LEFT conversion pipeline when the first callback changes RHS.
Three returned single-marker boundaries become TODO-only handoffs to matching
BOTH_LEFT1 tasks; all initial snapshots, source/cache validators, quiet commits
and conversion bodies stay exact. Initial PINT `3` still refuses BOTH stage0;
the actual first callback then supplies leading request text, quiet strings,
fractional/integral floats, bool/NULL or an explicit rejected array. LEFT `12`
remains cached rather than callback `99`/`88`, with all six normal results checked.
Independent NULL modulo errors without detachment, negative-float XOR detaches
owners 3 to 2 after RHS aliases target, and live `bool >> array` TypeError preserves
the literal array's pool-plus-cell owners 2. Defaults retain their actual phase and
RHS line 25. Ten originals and six focused fixtures (857 SL premises) pass in the
[single-LEFT ledger](../../coverage/semantics/single-left-bridge-review.json),
including exact whole-state handoff equality except TODO, real RHS callbacks,
fresh CELL/LOCATION, storage/owners and full/resumed budgets. A newly reached
Warning throw is source-tested with same Exception20 and destination100; unchanged
cancellation and prior malformed-state matrices are not replayed. Other initial
forms, unsafe targets/pre-snapshot RHS and wider lifecycle remain partial.

In the existing named-handler routes, initial RHS admission for fractional-LEFT
modulo, shifts and numeric bitwise assignments now includes NULL/bool, finite
signed64-fitting floats and valid plain or carrier strings. Text is not parsed at
entry: the first LEFT handler can repair invalid text or replace leading text
before any RHS notice. One shared snapshot
predicate reuses the existing plans and continuations; PINT keeps its earlier
single-warning route. Nine originals and four focused fixtures (593 SL premises)
pass in the [initial-scalar ledger](../../coverage/semantics/initial-scalar-review.json).
They check actual first/RHS callback frames, repaired cached results, live
`string ^ string` TypeError without a string-specialization retry, fresh storage
and alias owners, supplied-throw priority, immutable carrier data and resumed
budgets. Initial owning/undefined/reference RHS, nonfinite/range floats, unsafe
targets and wider lifecycle remain partial.

Arithmetic and bitwise conversion use the existing pure SpecTec numeric and byte
helpers, including signed 64-bit boundaries, binary64 values, string operands,
pinned power behavior and conversion diagnostics. Explicit casts keep their
separate rules: casts to int do not reuse implicit arithmetic notices; array casts
preserve array values with COW, turn null into an empty array, and wrap other
current scalar values at key zero. `(void)` evaluates and discards its operand,
retaining reads, warnings and side effects.

## Evidence and remaining work

`tests/semantics/ordinary.py` embeds 1,506 exact source inputs and checks 25 source
states with 2,875 assertions, including dense budgets 0–100. The source additions
retain 805 initial operator/cast originals, 28 concat timing originals, and 673
admitted expansion originals. Independent review adds 62 source controls for
operand timing, conversion order, array ownership and parser name provenance.
The [combined source report](../../coverage/semantics/source.json) records 4,407
exact comparisons and 25 outcome negatives. It and the
[state report](../../coverage/semantics/ordinary.json) bind the unchanged
`a8f6aa0cac996578befe8fa49621af2fdc214a44e4d9612a4cb8ce5dcee05691` identity
(799 inputs). The [independent audit](../../coverage/semantics/ordinary-campaign-audit.json)
checks complete ordered source bytes, observations and archive membership.

The expansion archive preserves all 680 originals. Its seven request-environment
boundaries remain explicit Unsupported results, excluded from admitted source
comparisons and recorded in the
[boundary archive](../../coverage/semantics/ordinary-request-environment-boundaries.json).
They remain implementation work. Unpack, destructuring, foreach, remaining
coalesce and quiet-write forms,
frames, objects and the other obligations in PLAN remain unfinished; these
operator checks do not close a constructor family or the complete PHP core.
