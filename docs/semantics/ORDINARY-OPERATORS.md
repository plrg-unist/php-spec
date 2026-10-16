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
registry; a thrown handler prevents later conversion notices and the result.
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
Plain CVs, unlike physical slot classes, copied operands, right-only warning
ingress, owning/expired replacements, failed LEFT conversion and wider
arithmetic/exit paths remain required; existing integer-operator evidence is unchanged.

Failed RIGHT conversion on this selected-cell route now raises TypeError using
both live raw scalar types, rather than earlier numeric holders. The unfinished
marker is removed before ordinary caller Throwable search; the assignment stays
unchanged. Conversely, a completed RIGHT warning still delivers its cached number
even when the live pair would now fail conversion. Two exact originals and 82
author plus 77 independent genuine SL premises check these distinct routes,
source/phase/expiry guards, sole Error ownership and budget resumption in the
[ADD failure ledger](../../coverage/semantics/arithmetic-failure-review.json).


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
they do not establish typed-source or owning-target execution. Newly warning or
invalid RHS values, constrained/owning/expired targets, wider operands/callbacks
and lifecycle paths remain explicit boundaries.
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
queries, not authenticated typed/lifetime behavior. The selected RHS must remain
plain, defined and quietly numeric; wider operands, owning/constrained targets,
callbacks and lifecycle paths remain required.

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
[unary ledger](../../coverage/semantics/unary-warning-review.json). Other producers,
references/owning operands, callbacks and lifecycle forms remain required.

Bitwise NOT now retains a finite in-range fractional float's converted long before its
precision-loss deprecation. The bounded producer accepts a defined non-reference
CV and named handler. Fresh capture/dispatch equals the CV; saved callback frames
and resumed integer holders stay historical, without adding roots. Complement
follows callback return; a supplied throw discards the marker and preserves the
unchanged destination. Three exact originals and 227 author plus 97 independent
SL premises check live 99, negative truncation, false fallback on the operand line,
public snapshot/diagnostic rejection and budget resumption in the
[BITNOT ledger](../../coverage/semantics/bitnot-warning-review.json).
Range/NaN, other operands, callbacks and lifecycle forms remain required.

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
Numeric-string conversion warnings, references/copies, wider `**=` forms and callbacks
or lifecycle forms remain partial.

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
pruned/missing/wrong-slot/owning projections establish refusals only. Initial
references/copies, wider operands/targets, callbacks and lifecycle remain partial.

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
Initial references/copies, warning or noninteger RHS values, unsafe targets,
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
and budgets are covered. Pure ready projections establish refusals only. Initial
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
pure projections establish refusals only. Initial references/copies, warning or
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
