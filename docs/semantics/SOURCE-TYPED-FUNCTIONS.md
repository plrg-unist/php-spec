# Typed positional parameters and value returns

Accepted in code **0ed17419**, compiler evidence **2ea12015**, author evidence
**dabc28d9** and [independent review e097f95e](../../coverage/semantics/typed-function-review.json).
Canonical926/599f3963 differs from tested926/baa85f57 only by one standalone
protocol output helper; all925 other bytes and all926 modes are unchanged.

Target: pinned PHP 8.5.10 CLI NTS64. This increment connects normalized source
signatures to the existing positional call, default and ownership machinery.
It admits builtin scalar/container singleton types and legal unions of `null`,
`true`, `false`, `bool`, `int`, `float`, `string`, `array` and `mixed`; return types
also admit `void` and `never`. Existing 16/17 phase ordering and default
normalization remain authoritative. This is partial core coverage, not callable
or type-family closure.

## Receive and return behavior

Arguments are evaluated and bound before typed receives. A function with typed
parameters then receives slots in order: an earlier provided type failure wins
before a later missing required parameter. Functions with only untyped parameters
keep their existing schedule. Caller strictness governs parameter verification;
callee strictness governs return verification. Strict mode admits the prescribed
int-to-float conversion. Weak mode follows exact-type preference and PHP scalar
conversion order, including numeric-string classification, overflow rejection and
precision diagnostics.

A by-reference parameter conversion writes its bound reference cell. Parameter
types impose no continuing constraint after entry: later writes, or conversion of
another parameter sharing the same cell, may change its type. By-value return
conversion produces a detached result and does not overwrite a referenced local,
global or parameter. Type failures use the existing frame cleanup and ownership
rules, retaining externally rooted values.

Stored float defaults materialize as floats even when the original literal pool
contains an integer. Successful deferred evaluation installs the uncoerced cache
value and class before parameter verification; a later type failure retains that
cache. Evaluation failure does not install it. Fresh omitted parameter cells and
array/reference ownership follow the existing default contract.

Value returns are checked before unwind. `void` may fall through; `never`
fallthrough raises its distinct TypeError. Other declared return types, including
`mixed` and nullable types, reject falling through without a return. Explicit
return diagnostics use the compiled return instruction's emission line;
fallthrough diagnostics use the function's source end line.

## Effectful callable returns

Ordinary named, nongenerator, by-value USER functions now verify fresh two-entry
callable arrays through the existing API resolution stages. The receiver is a
direct published USER class string or live ordinary instance; qualified method
bytes may come from a reference cell. Public concrete methods and known absence
are distinguished without invoking the target. Other exact union alternatives,
including array/object and nullable acceptance, bypass callable diagnostics.

The resolved return temporary has one owner across the API, return unwind and
caller continuation. Successful verification is not repeated after finally, so
an aliased method member can change while the same array returns. A handler
exception after valid lookup survives finally and callee-CV cleanup before the
returned temporary drains. Invalid lookup instead releases that temporary before
finally and creates the return TypeError, retaining any pending handler exception
as Previous. Existing throwing-frame cleanup also preserves a replacement exception
from a local destructor.

The [scoped review](../../coverage/semantics/callable-return-review.json) binds
the four originals and owner/budget checks. ALIAS object receivers, keyword
contexts and wider entries remain outside that increment. Pending successful
lookup with an explicit replacement transfer
inside a protected finally stops as Unsupported: two native timeout controls
remain zero credit, and the stopped state keeps its existing owners. This does
not change generic finally, destructor, collection or invocation rules.

Plain compiled CV returns now have a separate borrowed continuation. Native
unref happens before the second exact-union test: a unique reference unwraps in
place, while a shared reference copies into a new ordinary local cell and leaves
global/other aliases intact. Lookup adds no value or cell owner. A used RETURN
moves the local value and clears its slot; an ignored return leaves it for that
slot's ordinary frame cleanup. A protected CV instead has a real compiler-copy
temporary and keeps the original alias mapping, so finally may see a changed CV
while the saved array returns.

A valid lookup-handler throw continues through RETURN, bypassing local catches;
used and ignored values retain their distinct lifetimes. An ignored protected
temporary drains after finally and before local cleanup. Invalid lookup raises
TypeError with any pending handler Exception as Previous, leaving the detached CV
available to a local catch/retry. The [CV review](../../coverage/semantics/callable-return-cv-review.json)
keeps these source/ownership cuts separate from the earlier temporary family.
Admission requires a defined plain untyped local in an ordinary named USER frame
and the existing direct-receiver callable-array domain. Property/coercion/backing/
container/debt/released-cell authority and return sites inside an active finalizer
are outside this cut; the pending replacement-finally refusal remains unchanged.

The same carriers now cover public ordinary instance methods and receiver-free
public static methods selected by a fixed, nonkeyword literal class call. The
published method descriptor remains immutable; a separate active proof checks
the real target, source call site, declaring/called classes and receiver. Thus
Base remains the declaring scope while Child is the called scope. A handler can
remove the creator's global without removing its real method-frame This owner.

The creator and returned array have independent owners. Pending valid cleanup
can retire the creator before the caller drops the returned target; descriptor
validation then uses published class/method metadata, without requiring a live
creator or permitting lookup through a dead receiver. Invalid lookup retains
lexical method TypeError names and any pending handler Exception as Previous.
Used/ignored, protected-copy and borrowed-CV transfers reuse the prior laws.
The [method review](../../coverage/semantics/callable-return-method-review.json)
binds two new originals and 548 independent source/owner/budget conditions.
Static calls through objects, scoped implicit This, keywords/dynamic selectors,
magic/nonpublic/API/Closure/Generator entry and all existing value, cell and
finalizer bounds remain outside this increment. No returned callable body is invoked and
no schema, task or owner is added.

Raw self/parent/static strings and DIRECT keyword/bare-method arrays now use the
same return carriers. Verification uses the real method scope, called class and
This, and consumes the actual API phase 0 or 1. Successful returns preserve raw
spelling and member references; no This is captured and the value is not checked
again in the caller's scope. Protected copies, local unref and exact union
acceptance retain their existing order.

A keyword-class deprecation handler throw rejects callable checking before leaf
lookup, even when the method is valid or the handler repairs an aliased member.
The return TypeError retains that handler Exception as Previous and follows the
ordinary local catch, finally and frame cleanup. The earlier compound-member
notice has a different continuation and remains separate. Known invalid scope
rejects before a class cursor is minted. Resumed NUL or compound method bytes
keep structural callback cleanup valid, then stop as Unsupported before lookup;
this does not implement owned-NUL release or a second compound notice.
The [keyword review](../../coverage/semantics/callable-return-keyword-review.json)
binds three originals and the affected pending/union checks. No keyword string
has a pending-success CANCEL path; the prior ARRAY-only guard stays unchanged.
Existing producer, public metadata, entry, cell and finalizer bounds remain.

Unprotected by-reference returns in ordinary named nongenerator USER functions
now verify qualified callable arrays from defined plain CVs. Verification keeps
an existing reference wrapper intact and borrows the local cell. Its original
array stamp adds no owner: active lookup still needs the real array and receiver
to remain live. A callback may replace the current cell and remove/rebind its
global name while another genuine holder keeps that query array alive. Successful
verification returns the captured cell's current contents and reference identity;
it does not repeat lookup or reselect the global binding.

A used result creates the real returned reference; a value consumer copies from
it later, while an ignored return adds no wrapper owner. A valid compound lookup
after a handler throw retains that reference through callee cleanup, separately
from the real pending Exception. Invalid lookup instead raises TypeError,
retaining a pending handler Exception as Previous, and leaves the CV for local
catch/slot cleanup.
If the original query graph is lost, borrowed metadata permits entered-handler
cleanup only, then explicit Unsupported before lookup. These loss controls are
model-only. The [reference callable review](../../coverage/semantics/callable-reference-return-review.json)
binds three new originals, exact cells/owners and the affected budget/refusal cut.

Protected named-function CV returns now retain one real MAKE_REF cell through
quiet finally and the actual second callable check. A new recheck marker owns no
cell; the captured reference, rather than a rebound CV name, supplies the second
query and its current method bytes. Used results preserve that reference, while
normal and pending ignored calls release the temporary before callee locals.

A first-warning Exception remains pending across finally. The proven live-object,
canonical declared-prefix cache path performs a silent second check without
entering the handler; a failed prior-exception recheck remains Unsupported.
A fresh second-warning throw instead resumes real lookup: success propagates the
original Exception, while failure creates TypeError with Previous, releases the
temporary before local catch and replays the completed try/finally context.
The real Exception stays immediately behind release; nonowning origin/replay
tasks restore catch context afterward. No returned callable body is invoked.

Quiet scalar/CV syntax and values are checked at capture and after the first
handler. First-pending completion additionally excludes active output/tick
callbacks. Structural source/error cleanup stays valid on refusal, without
historical active lookup or a new owner. The [protected reference review](../../coverage/semantics/callable-reference-protected-review.json)
binds two effectful source agreements, one retained pure control and the affected
270 state/budget checks at the private 473-module cut. The full pending-original mismatch and all
failed/interrupted/diagnostic cuts remain zero; no unfinished assertions are reused.
Current source/entry/place/typed-reference, replacement/active-finalizer,
visibility, magic, autoload and held bounds remain explicit.

Pure protected plain-CV returns now use a nonowning recheck witness after one
quiet finalizer. The existing MAKE_REF temporary remains the sole task owner;
the witness authenticates the compiled return, finalizer and captured cell,
without rereading a rebound CV name. Current unchanged TYPEVALUE acceptance,
including a noncallable array accepted by another union arm, needs no callable
query. Structural validity is separate from current conversion eligibility.
Used returns transfer the same reference. Ignored returns use the ordinary
single-cell release before local cleanup; a surviving ENV owner preserves the
value until its own slot is released.

The [pure protected reference review](../../coverage/semantics/pure-protected-reference-review.json)
binds one new three-mode source and the first 178 owner/refusal/budget checks at
the private 481-module cut. The original duplicate-root and ignored-schedule
projections remain diagnostic-only. Existing effectful verification is unchanged;
its tested cuts and ledger are retained.

Exact `int` protected reference returns now permit one quiet scalar-literal
write before the optional unset/rebind. Successful initial verification proves
that the retained payload was primitive before this write. Quiet integer-number
conversion uses the existing type-check kernel and writes through the captured
reference, even when its CV name now selects another cell.

A rejected second check creates one genuine TypeError and transfers the one
MAKE_REF temporary to an ordinary cell-release job before local catch. The real
THROW_SEARCH follows that job immediately; source-derived nonowning origin/replay
tasks restore the completed try/finally context afterward. A detached cell retires
before catch, while an ENV-held cell survives with its current payload. Replay
retains no retired reference cell.

The [scalar protected reference review](../../coverage/semantics/pure-protected-reference-scalar-review.json)
binds one four-mode source and the first 224 actual owner/transfer/refusal/budget
checks at the private 483-module cut. Integer-string writeback and detached/kept
TypeError catch/finally order agree with the pinned native. Fractional conversion
controls are model-only refusals; wider conversions, pending callbacks,
computed/property operands, replacement/cursor and wider-finalizer paths remain
required. No generic root, debt, collector, type-check or destructor rule changes.

Two quiet nonreplacing finalizers now share the same captured reference and one
MAKE_REF temporary. Protected source paths are outer-to-inner; execution/replay
owners are inner-to-outer. The witness retains the actual first inner owner,
while active outer FINALLY_REF_RETURN/PHASE tasks and the final function-origin
tail authenticate progress. Tail-only completion preserves the same witness
without inventing another producer or cell root. The repeated check runs after both
bodies, so an outer literal repair can make an intermediate invalid value
acceptable.

Structural validation recognizes the real future function-origin restoration;
live outer entry separately checks its actual origin. The new multi-body route
requires empty output/tick callback state, keeping that marker lifetime within
the quiet source proof. Single-finalizer routes retain their existing behavior.
Final writeback and rejection release/replay reuse the scalar continuations.
The [two-finalizer review](../../coverage/semantics/pure-protected-reference-multi-review.json)
binds one new four-mode source and the first 343 phase/owner/refusal/budget checks
at the private 484-module cut; all finite baseline/projection observations stay
zero. Callback bodies, computed/property sources and overriding transfers remain
required; no schema, generic root or collector rule changes.

The pure exact-int route now derives a finite inner-to-outer owner sequence from
the actual protected source paths. One nonowning witness keeps the first owner
and captured reference while completed or active-finalizer views match the
remaining source suffix. Exact queued origin restorations authorize structural
validation; every live next entry separately requires its actual owner and empty
output/tick callback state. At a source-authenticated next entry, reordered,
incomplete nonsuffix or wrong-restore tails refuse explicitly. A coherent genuine later suffix is not distinguished
by a new nonce or history certificate.

The repeated type check runs once the pending suffix is empty, so earlier
invalid scalar writes may be repaired by the last body. Existing checked
writeback and single-cell release before local catch/replay remain the final
consumers. Unchanged TYPEVALUE, quiet integer conversion and known-rejection
bounds remain; fractional/lossy scalar diagnostics are not admitted. The [finite-chain review](../../coverage/semantics/pure-protected-reference-chain-review.json)
binds one new three-body/four-mode source and the reduced 271 completed
phase/owner/refusal/budget checks at the private 487-module cut. The separate
actual 489-module load adds zero source renewal. The full 514-condition timeout
and finite checkpoint
remain zero; no unfinished prefix is reused. The 360-second source timeout stays
zero, separately from the
600-second-budget retry agreement. Single/two-finalizer and effectful paths
retain their previous cuts without replay. Wider callback, replacing, active
finalizer, computed/property and constrained-cell contexts remain required.

An exact-int protected plain-CV return now stages a finite fractional float
literal from its single quiet finalizer. The existing numeric conversion plan
snapshots the integer and one precision deprecation before the callback. One
owning LOSSY_REF_RETURN task carries the real MAKE_REF cell; the notice, entered
handler and normal continuation transfer that owner once. The old general
quiet-value and scalar predicates remain unchanged.

Normal completion checks the current cell, then writes the saved integer through
the existing checked reference operation and resumes the genuine verified
return pair. It does not convert the handler-written payload again. A handler
throw instead creates return TypeError using the current payload tag, even if
that tag is already int. The actual handler Exception becomes Previous; one
cell-release job precedes local catch and nonowning source-derived replay.
There is no successful pending-return or new CANCEL carrier. In the selected
normal program, ignored cleanup has no destructor-operational context and
synchronously drops local/temp owners from three to the real GLOBAL owner.

Callback transport validates immutable source/snapshot metadata and the live
reference identity independently of current ENV, value or typed-source flags.
Finish/rejection separately requires a plain cell with NULL/Boolean/int/float
payload and empty output/tick callback state; other late values or constraints
reach explicit refusal while preserving the cell and any real pending Exception.
No string/owned-NUL, typed-cell, active/replacing-finalizer or new entry scope is
admitted. The [lossy reference review](../../coverage/semantics/pure-protected-reference-lossy-review.json)
binds two selected source agreements and the reduced 185 completed owner,
Previous, refusal and budget checks at private 489. Full 207 failure and all
finite/preparation observations remain zero; actual 492 is load-only.

Unprotected weak exact-int BYREF CV verification now uses a separate borrowed
LOSSY_REF_CV_RETURN. The actual restored ENV name/cell and compiled return site
authenticate it; stale LOCATION grants no capture authority. The task owns no
cell or value and requires no existing reference marker or extra cell/value
owner for structural transport. Plain-cell, current primitive payload and output/tick
conditions are checked separately at admission/finish. Source validation also
keeps the exact return-site origin through the callback.

Normal saved-integer writeback first selects the real current local location,
then reuses reference_return_store and reference_return_unwind. Only the actual
used return creates/addrefs a wrapper; RESULT moves into unwind and is cleared.
Both nonreference CVs and genuine GLOBAL aliases preserve this distinction.
A handler throw creates TypeError from the current tag, links the real Previous
once, and preserves the original catch tail. The ENV retains its current cell;
there is no protected temporary release, MAKE_REF continuation or synthetic
finally replay. Protecting/active-finalizer sites remain outside this cut.

The [unprotected precision review](../../coverage/semantics/unprotected-reference-lossy-review.json)
binds two new sources (five normal and two pending calls) and the first 251
owner/tail/refusal/budget checks at private 492. The declaration-binding failure
and all finite observations remain zero; actual 494 is a separate load-only
check with zero source renewal.
Owning/string/constrained/released cells and wider producers remain partial,
with no new user-destructor or owning-payload claim. Protected170 remains unchanged.

Unprotected named weak exact-int by-value CV precision warnings now use
LOSSY_VALUE_CV_RETURN. Actual wrapper count is read before resolve: a plain CV
stays, a unique reference loses its marker, and a shared reference separates only
this local ENV binding. The old GLOBAL and saved tables remain intact. The
zero-root task stamps the prepared local cell and authenticates exact source,
origin and ENV independently of late primitive/plain/nonREF/output-tick checks.

Normal checked saved-integer writeback enters the ordinary known-PINT return
unwind while retaining the local scalar; neither used nor ignored adds a cell
owner or wrapper. Handler failure allocates TypeError with the real pending
Exception as Previous and preserves the actual catch tail and current local
value. It adds no protected temporary release or synthetic replay. The
[by-value review](../../coverage/semantics/by-value-lossy-return-review.json)
binds two originals (six normal and three pending calls), the first 304 checks
at the private cut with 494 modules,
and the separate actual joined load. Fixture-only failures and finite observations
remain0. CONST/temporary, protected/active-finalizer, string/constrained/owning
and wider producer domains remain partial; earlier reference-return bodies stay
literal.

A mismatching FLOAT CONST in an ordinary named weak-int by-value return now
uses LOSSY_VALUE_TEMP_RETURN. VERIFY copies that literal into a genuine TMP;
immutable literal bits, compiled line and exact return site authenticate the
zero-root continuation. ENV, GLOBALTABLE, stale LOCATION and their payloads
grant no authority. Structural callback transport stays independent of the
separate output/tick readiness check.

Normal saved-integer success directly enters the ordinary known-PINT unwind
over the original tail, without CV preparation or storage writeback. Handler
throw formats TypeError from the actual saved FLOAT temporary, keeps the live
pending Exception during allocation, links Previous once and preserves ordinary
finally/catch execution. It adds no reference cell, release or synthetic replay.
The [literal precision review](../../coverage/semantics/by-value-literal-lossy-return-review.json)
binds two new programs (used/ignored plus a real union bypass), the first 205
checks at the private cut with 494 modules, and a separate actual joined load. Finite/strict/native
preparations remain0. BYREF literals, protected CV copies, generalized TMPs,
active-finalizer returns and wider types/entries remain required.

Weak exact-int BYREF FLOAT literals now use the zero-root LOSSY_REF_TEMP_RETURN
for initial precision verification. Its immutable literal bits, compiled line
and exact site/origin carry no cell, exception or result-demand field. Ambient
output/tick readiness remains separate from structural callback validity.
Saved-integer success requeues the original RETURN_REF_VALUE over the unchanged
tail. Its new candidate is false; existing99 performs a pure exact-int check,
and existing379 controls finally, AST-based Notice designation and RV handling.

Precision-handler throw creates TypeError from the actual saved FLOAT tag,
links Previous once and preserves the genuine finally/catch tail before any
Notice marker exists. Fresh Notice-handler throw occurs after successful
verification and escapes as its original Exception. Actual used frame VALUE
owns one returned HCELL and ignored VALUE none; pending E is held once in
FRAME.PENDING during the local marker destructor. The
[reference literal review](../../coverage/semantics/reference-literal-lossy-return-review.json)
binds two originals and the first 191 checks at the private cut with 495
modules. Finite/strict/native/recovery preparations remain0; the actual joined
load is separate. New precision code leaves379,
pure recheck and generic owner/release rules literal. Generalized TMP/CV,
active-finalizer and wider types/entries remain partial.

Supplied weak exact-int reception now stages a finite fractional float in one
required by-value formal of an ordinary named nongenerator USER function. The
formal ENV binding supplies its sole cell owner; `LOSSY_PARAMETER_RECEIVE` adds
none. The integer and precision diagnostic are captured before the handler.
Normal completion stores the saved integer, restores the function origin and
enters the ordinary body. A handler-written caller GLOBAL remains independent.

A handler throw follows the existing error-handler discard and call unwinding:
the original Exception survives, with the unconverted formal left for ordinary
frame cleanup. It creates no replacement TypeError or Previous. Structural
parameter-site/cell/snapshot authentication remains separate from late plain-cell,
original-float and output/tick/held readiness. Direct continuation validation
requires its actual singleton queue; entered handler wrappers retain their own
shape. Caller strictness comes from the saved caller context, including a distinct
eval unit. The [reception review](../../coverage/semantics/supplied-integer-reception-review.json)
records three original-source agreements and their scope bridge separately from
the earlier 194-condition state gate and final 33-condition singleton gate.
Failed and diagnostic cuts retain zero credit.
BYREF functions/formals, defaults, variadics, named/unpacked arguments, resumable
entries and wider type/value or lifetime contexts remain outside this increment.

Supplied weak exact-int reception now also admits one required BYREF formal
passed an ordinary source CV. SEND and binding supply the real marked cell;
`LOSSY_REFERENCE_PARAMETER_RECEIVE` adds no owner. Normal completion writes
the saved integer through that same cell after a handler changes its current
primitive payload, then enters the ordinary body. Caller and formal observe the
same converted value. Parameter typing adds no continuing property constraint.

A handler throw uses ordinary error-handler discard and call unwinding. Its
current cell write survives with the original Exception and no replacement
TypeError or Previous. Structural source/cell/snapshot validation stays separate
from normal readiness, which requires a marked plain cell, a current
null/bool/int/float payload and quiet output/tick/held state. Direct continuation
validation requires the actual singleton queue. The snapshot never reconstructs
a historical caller alias; the current formal ENV remains authoritative.

The [reference reception review](../../coverage/semantics/supplied-reference-integer-reception-review.json)
binds three original-source agreements and 133 independent ownership, refusal
and budget conditions at their private cuts with 498 modules. Initial binding
failure, unchanged Unsupported controls and finite preparation retain zero
source credit. Reference-returning functions, defaults, variadics, named/unpacked
sends, special/dynamic variable arguments and resumable entries remain outside
this increment. Owning late payload cleanup has no new validation claim.

Ordered precision reception now covers a finite list of at least two required
by-value exact-int formals supplied by ordinary positional CV arguments. At
admission, supplied values have already been copied into separate formal cells.
A handler may change later caller globals while their formal snapshots remain
fixed. `LOSSY_POSITIONAL_PARAMETER_RECEIVE` records the function, receive index,
cell, float bits, saved integer and line, with no task-owned root.

The index authenticates the actual formal ENV binding, parameter source origin
and diagnostic line. Earlier slots need their current defined bindings; their
past values and types are not reconstructed. Normal completion uses the existing
indexed store to advance the genuine next receive or enter the body. A remaining
formal at or beyond the supplied count stays on the existing missing-argument path, after
earlier reception completes. Handler throw instead preserves its original
Exception, skips the remaining receives/body and leaves ordinary frame cleanup
to release the formal cells. Structural callback validation remains separate
from the existing original-float, plain-cell and quiet-state readiness checks.

The [ordered reception review](../../coverage/semantics/supplied-positional-integer-reception-review.json)
binds three source agreements and 150 independent index, ownership, refusal and
budget conditions at their private cuts with 500 modules. Unchanged Unsupported
controls and finite preparation keep zero source credit; actual joined loading
is separate. BYREF formals/returns, defaults, variadics, named/unpacked sends,
special/dynamic variable arguments and wider types/entries remain partial.

Ordered weak exact-int reception now also covers a finite list of at least two
required BYREF formals supplied by ordinary positional CVs. Each precision receive captures
its selected cell's current float. Passing one CV twice lets the first saved
integer satisfy the later receive without another warning. With distinct cells,
an earlier handler can instead change the later float before its snapshot.

`LOSSY_POSITIONAL_REFERENCE_PARAMETER_RECEIVE` records the function, index,
cell, current float bits, saved integer and line without adding an owner. A new
indexed readiness check uses the genuine current formal CVS/ENV name and retains
the marked, primitive, unconstrained-cell and quiet-state fences. Earlier slots
need their current defined bindings. A later handler may change an earlier
verified int slot to float before body entry; no type history is reconstructed
or continuing parameter type source attached.

Saved-integer success writes through the selected reference and advances the
actual receive/body schedule. Handler throw leaves its current cell writes and
original Exception for ordinary discard/unwind, without TypeError or Previous
replacement. A completed first conversion writes back before a later required
argument is missing; a throwing handler interrupts that schedule before writeback.

The [ordered reference review](../../coverage/semantics/supplied-positional-reference-integer-reception-review.json)
binds three source agreements and 157 independent alias, index, ownership,
refusal and budget conditions at their private cuts with 502 modules. The initial
SpecTec declaration failure, unchanged Unsupported controls and finite preparation keep zero
source credit. Actual joined loading stays separate. Mixed BYVAL/BYREF modes,
reference returns, defaults, variadics, named/unpacked sends, wider producers and
owning late payload cleanup remain partial.

Weak exact-int reception now covers finite required signatures containing both
by-value and BYREF formals, supplied by ordinary positional CVs. Mixedness is
checked against the full immutable formal list, including missing slots. A
copied formal keeps its SEND value; a reference formal reads its current cell
when its receive arrives. The same caller CV therefore behaves differently when
value-first/reference-second is reversed.

`LOSSY_MIXED_PARAMETER_RECEIVE` keeps the existing six indexed snapshot fields
and adds no root or mode bit. Its mode comes from `PARAMETERS[n].BYREF`, with
readiness delegated to the unchanged value and indexed-reference helpers. The
current REF marker and callsite argument flag do not select the mode. Structural
source/cell/snapshot validation remains separate from those physical checks;
earlier slots require defined bindings without type/value history reconstruction.

The existing indexed store writes the saved integer and advances reception or
body entry. Handler throw preserves current writes and its original Exception.
On that pre-body path, ordinary cleanup retires private formal cells while
genuine caller roots keep shared cells alive. With only one supplied argument,
its mode-specific reception still precedes the later missing required slot. Existing return, discard,
ownership and collector rules remain unchanged.

The [mixed reception review](../../coverage/semantics/supplied-mixed-integer-reception-review.json)
binds three source agreements and separate bounded independent AL selections of
93 mode, 48 pending-exception and 32 missing-priority conditions at their private
cuts with 505 modules. Each is a genuine first pass under unchanged caps.
Unsupported controls and finite preparation keep zero source credit; actual
joined loading stays separate. Wider types, reference returns, defaults,
variadics, named/unpacked sends and wider producers/entries remain partial.

Module518 admits positive-arity required exact-int signatures with ordinary CV
actuals in a positional prefix followed by a nonempty named tail, including
all-named calls, whose fixed slots form a supplied prefix. SEND order stays separate
from formal receive order. The existing named-call validity check precedes shape
construction; that shape authenticates slot extent, absence of holes and absence
of extra names. Fixed parameter names do not populate `CURRENT.NAMED`.

`LOSSY_NAMED_PARAMETER_RECEIVE` borrows the selected formal cell through the same
six snapshot fields. Immutable `PARAMETERS[n].BYREF` selects the existing copied
value or current reference readiness; source argument flags and mutable markers
add no mode authority. Saved-integer completion advances ordinary reception;
handler throw retains current writes and its original Exception through existing
cleanup. Earlier received values and types are not reconstructed.

Required interior holes fail during named preflight before any precision
callback. A hole-free supplied prefix instead receives before a trailing missing
argument, preserving mode-specific writeback and earlier callback-throw priority.
The original [named mixed review](../../coverage/semantics/supplied-named-mixed-integer-reception-review.json)
keeps three source agreements and five independent AL selections totaling 264
executed conditions at their private 506-module cuts separate from actual joined
loading. Repeated prefixes are not unique coverage; original fixture failures,
Unsupported baselines and finite preparation retain zero source credit.

The [homogeneous required review](../../coverage/semantics/homogeneous-named-required-integer-reception-review.json)
adds value-only and BYREF-only headers, including one formal, by removing only
mixedness and the redundant two-formal lower bound. Positive `ARGC` still proves
a nonempty header. Every other source, shape, strictness and readiness guard,
the indexed task and all completion/cleanup rules remain unchanged. Seven exact
source comparisons pass with 508 modules: six precision programs and one quiet
control. Author AL166 and independent derived AL211 execute 377 conditions across
eight fixtures (329 body, 48 setup); their cuts and the earlier pre-receive90
remain separate. Prior mixed inputs are unchanged and are not replayed.
Defaults on this required-only path, variadics,
unpacking, wider producers/types/entries and late owning payloads remain partial.

Module519 admits a possibly empty required exact-int prefix followed by a nonempty
tail of integer defaults from finite operator and selection trees: unary signs
and integer NOT; binary `+`, `-`, `*`, exact `/`, integer-result `**`, `%`, shifts
and integer AND/OR/XOR. Powers require a nonnegative exponent and the existing
pure power kernel's completed integer result.
Quiet `(int)` defaults admit bounded integer trees, resolved Boolean/null leaves,
decoded literal strings and finite signed float-literal chains whose final value
is compiler-eligible. Boolean-producing NOT, AND/OR, XOR, explicit `(bool)`
and eight long predicates also cast to integer 0/1; ordinary integer and spaceship casts retain
their actual integer. Below `(int)`, full/shorthand ternary and coalesce trees can
select those primitive leaves while keeping their original values. Their truth
conditions admit Boolean/null/long values, raw strings, non-NaN signed float
literals, full/shorthand ternaries and coalesce selections over that bounded truth
domain. Only resolved null selects a coalesce RHS; wider condition producers
remain partial. String overflow uses the existing saturating cast; direct
out-of-range and nonfinite float literals remain partial.
Integer `<=>` compares two admitted long trees and returns normalized -1, 0 or 1.
Integer-valued full/shorthand ternaries retain their selected-long rule.
Their truth projection accepts admitted long trees, resolved bare Boolean/null
leaves, finite `!`, `&&`/`and`, `||`/`or` and eager `xor` trees, and all eight
equality/identity/order predicates over two admitted long trees.
Coalescing retains a long or selects its RHS after resolved bare null.
Special names use the actual declaration environment and existing constant resolver.
Every admitted integer operator child and result must fit a target long.
Division/modulo require a nonzero divisor, and shifts require a nonnegative count.
Left shift preserves target-word wrapping. Uniform value-only,
uniform BYREF and mixed headers use the same immutable per-formal mode.
Each optional default retains its complete source AST and signature expression;
the classifier's integer must match the compiled `PINT` at the authenticated
`PDSTORED` descriptor's origin. Ordinary positional CVs and positional CV
prefixes with nonempty named CV tails, including all-named calls, are admitted.
Named validity precedes shape construction; exact slot extent,
holes and selected `NAMED_SENT` distinguish a supplied operand from a default.

The added metadata arm reuses the existing indexed snapshot and immutable formal
mode. Omitted trailing defaults remain absent until their ordinary receives;
named optional holes are filled before any receive. An omitted BYREF default
creates no reference marker solely from its signature. Existing default insertion,
required-hole priority, saved-integer writeback, original handler exceptions and
cleanup remain authoritative; no task, root, return or discard rule changes.

The [optional-tail review](../../coverage/semantics/optional-integer-tail-reception-review.json)
records the initial mixed-header cut: six exact source comparisons with 508
modules, reusing the six original native observations: five precision agreements
and one existing quiet-default comparison. Author AL118 and independent derived AL84 retain
separate cuts; the original peer timeout retains zero credit.

The [homogeneous-tail review](../../coverage/semantics/homogeneous-optional-integer-reception-review.json)
adds value-only and BYREF-only headers by removing the mixedness guard. Those
three cases exhaust valid nonempty Boolean mode vectors; every other metadata,
source and readiness guard stays unchanged. Six fresh source comparisons agree
at their private 508-module cut. Author AL126 and independent derived AL176
execute 302 conditions across six fixtures, with repeated setup and source0 state
checks distinguished. Historical mixed-header evidence is not replayed.
The [all-optional review](../../coverage/semantics/all-optional-integer-reception-review.json)
removes only the required-prefix lower bound. Positive supplied extent and the
nonempty optional tail remain required; empty supplied calls keep ordinary default
insertion. Seven exact source comparisons pass at the private 508-module cut,
reusing seven fresh native originals once. Author AL125 and independent AL252
execute 377 conditions across eight fixtures (329 body, 48 setup); the separate
pre-receive70 and all state checks have source credit0. Default-hole cells never
gain supplied authority, even when forged physical readiness succeeds. Original
throws preserve current caller writes and retire private cells without committing
the saved integer. Earlier required-prefix cuts are unchanged and not replayed.
Computed defaults, wider types/producers/entries and owning late payloads remain
partial.

The [mixed-CV review](../../coverage/semantics/mixed-cv-integer-reception-review.json)
adds positional prefixes before nonempty named tails through one shared source
predicate. It retains the literal CV predicates, rejects empty/pure-positional
vectors on module518 and preserves the separate positional continuations.
Required-only and genuine optional-tail headers stay disjoint; named validity,
slot/HOLES/SENT authority, immutable-mode readiness and every receive body remain
unchanged. Seven exact SL508 source comparisons reuse seven fresh native originals
once. Accepted author127 and independent194 execute 321 conditions across seven
fixtures (279 body, 42 setup), with source0 state/derived checks. The first two
author fixtures had constructor-list parse errors; only their two corrected
lines and affected92 checks were rerun, retaining the original trailing35 cut.
All failures and tested cuts remain explicit. Wider argument producers, unpacking,
variadics, defaults and lifetime contexts remain partial.

The [signed-default review](../../coverage/semantics/signed-integer-default-reception-review.json)
admits only unary-sign chains classified as `PSINTEGER` by module17. Module519
still authenticates the exact default AST, parameter index/origin, `PDSTORED`
descriptor and matching compiled integer. Equivalent values with different ASTs
grant no authority; every receive, mode, source-shape, root and cleanup body stays
unchanged. Six exact SL508 comparisons reuse six fresh native originals once:
five precision programs and one quiet control. Accepted author150 retains
original81 and corrected69 at separate cuts; independent115 gives 265 physical
conditions across five fixtures (235 body, 30 setup), with no unique-count claim
and source0 state/derived checks. Three pre-runtime first-fixture failures remain0;
only that fixture's pool syntax and binding order were corrected. Actual joined
loading remains separate. Floats, overflow, arithmetic beyond unary signs,
constant/object defaults and wider producers or lifetimes remain partial.

The [binary-default review](../../coverage/semantics/binary-integer-default-reception-review.json)
adds only one root `+` or `-` whose two operands independently yield `PSINTEGER`
under module17, with a long result. A small integer projection retains the exact
old classifier as its fallback; it never recurses on binary operands. Its result
must still match the compiled `PINT` at the exact default AST and authenticated
descriptor origin. Source, mode, readiness and every execution body remain
unchanged. Three exact SL508 originals include two precision programs and one
quiet control, with fitting MIN/MAX defaults observed in every precision body.
Author132 and independent130 pass on first execution:262 physical conditions
(238 body, 24 setup, four fixtures), all state/derived checks source0 and no unique
aggregate. The separate genuine pre-receive47 is also source0; there are no new
failures or old-source replays. That original cut excludes nested arithmetic and
unary signs over arithmetic; its accepted evidence is not replayed below.

The [additive-default review](../../coverage/semantics/additive-integer-default-reception-review.json)
extends the projection recursively through binary `+`/`-` and unary signs over
arithmetic. Each new node checks long children and results, so overflow cannot be
canceled by later arithmetic or a second negation. The exact old module17
fallback remains unchanged; new unary arms require its full-node result to be
`PSNONNUMERIC`, keeping successful alternatives disjoint. Exact AST, default index,
origin, `PDSTORED` and compiled-`PINT` equality still grant authority together;
every receive, mode, source-shape, root and cleanup body is unchanged.
Three exact SL508 originals cover quiet defaults, opposite shared-CV modes and
required-prefix handler throws. Author104 and independent80 pass on first execution:
184 physical conditions (172 body, 12 setup, two fixtures), all state/derived
checks source0 with no unique-count claim. The separate genuine pre-receive34
also has source0. Two affected earlier pure expectations are covered in the new
fixture without renewing their historical campaign. Other operators and
float/overflow/constant/object defaults remain outside that cut.

The [product-default review](../../coverage/semantics/product-integer-default-reception-review.json)
adds one multiplication arm to the same recursive projection, checking both long
children and the long product. Nested products and additive/sign parents retain
the exact full AST and stored integer proof. An overflowing child cannot be
rescued by multiplication by zero, cancellation or another sign; unsupported
children are still checked when the other operand is zero. Existing execution,
source, mode, hole/SENT, readiness, root and cleanup rules remain unchanged.
Three exact SL508 originals cover quiet defaults, copied/current mixed modes and
required-prefix handler throws. Accepted author103 and independent95 give 198
physical conditions (186 body, 12 setup, two fixtures), all state/derived checks
source0; pre-receive38 is separate. The first author fixture stopped before
execution on an unbound metadata variable and retains zero credit; only that
fixture was corrected and rerun. Two affected historical multiplication controls
are covered by the new fixture without replaying their campaigns. Division and
other operators remain outside that cut.

The [exact-division review](../../coverage/semantics/division-integer-default-reception-review.json)
adds one division arm with long children, a nonzero divisor, zero remainder and
a long quotient. The divisor guard precedes partial mathematical remainder and
division; zero numerators remain valid. Nonexact results and `MIN / -1` cannot be
rescued by later multiplication or division, and a fitting final quotient cannot
erase an overflowing child. Exact source AST/default/index/origin/stored-integer
authority and every existing receive, mode, hole/SENT, readiness and cleanup body
remain unchanged. Three exact SL508 originals cover quiet defaults, copied/current
modes and required-prefix handler throws. Author108 and independent96 pass on first
execution: 204 physical conditions (192 body, 12 setup, two fixtures), all state
checks source0; pre-receive38 is separate. The one affected historical division
control is checked as `4` in the new fixture without replaying its campaign. No new
failures or replays occur. Modulo, shifts and bitwise operators remain outside that
cut.

The [integer-operator review](../../coverage/semantics/integer-operator-default-reception-review.json)
adds the seven integer-only constructors through the existing pure module01
kernels. `IRESULT` selects valid modulo/shift results, rejecting zero modulus and
negative counts. Signed remainder, `MIN % -1`, negative odd right shift and counts
at or above64 retain PHP results. Left-shift word wrapping remains valid; the
older arithmetic overflow/nonexact guards still reject invalid children even
when a parent masks them with zero. Integer bitwise NOT/AND/OR/XOR preserve the
same exact AST/default/index/origin/stored-integer proof and all receive, mode,
hole/SENT, readiness, root and cleanup bodies.
Three exact SL508 originals cover all seven nodes, overlapping mask operands,
word MIN/MAX defaults and unchanged warning/throw observers. Author117 and
independent108 pass on first execution:225 physical conditions (213 body,12 setup,
two fixtures), all state checks source0; the genuine full-five-default pre74 is
separate. The affected historical modulo control is checked as `0` in the new
fixture without replaying its campaign. No new failures or replays occur.
Power, wider scalar/constant/object defaults, variadics/unpacking and wider
types/producers/lifetimes remain partial; actual joined loading stays separate.

The [integer-power review](../../coverage/semantics/power-integer-default-reception-review.json)
adds one Pow projection through the existing pure module06 kernel. Both children
and the result must fit a target long; the exponent is nonnegative and only
`POWERDONE (NINT i) false` grants admission. Zero powers still validate both
children, so unsupported or overflowing children cannot be rescued by `** 0`.
Exact source/default/index/origin/stored-integer authority and all receive,
mode, hole/SENT, readiness, root and cleanup bodies remain unchanged.
Three exact SL508 originals cover nested/zero/huge powers, `(-2) ** 63` as MIN,
NOT(MIN) as MAX and the unchanged warning/throw observers. Author 133 and
independent 95 pass on first execution: 228 physical conditions (216 body, 12 setup,
two fixtures), all state checks source0; the genuine pre67 is separate. The
affected old Pow(2,3) control is checked as 8 without replaying its campaign.
No new failures or replays occur. Negative/float/overflow powers, selection and
wider defaults/types/producers/lifetimes remain partial; actual loading is separate.

The [integer-selection review](../../coverage/semantics/integer-selection-default-reception-review.json)
adds full/shorthand ternary and coalescing projections. Conditions are admitted
long trees or resolved bare Boolean/null constants; coalesce left operands are
admitted longs or resolved bare null. Only selected branches are inspected and
the result must be a long, so shorthand true and non-null coalesce never coerce
Boolean values. Full source AST/index/origin/PDSTORED/PINT authority remains.
The projection threads immutable `pfunction.ENV` through every recursive arm and
uses the existing DEFAULT constant-name resolver, preserving import and namespace
meaning. The old one-argument helper is an empty-environment fixture wrapper;
production always uses the declaration environment. All old kernels/range guards,
receive/mode/hole/SENT/readiness/root/cleanup bodies remain unchanged.
Three exact SL508 originals cover `0 ?:` versus `0 ??`, skipped undefined names,
mixed-case special names, MIN/MAX and unchanged warning/throw observers. Author 175
and independent 160 pass on first execution: 335 physical conditions (323 body,
12 setup, two fixtures), all state checks source0; pre67 remains separate.
Alias/scope controls and both environments through all 14 old recursive operators
are state-derived; original sources are global with no imports. No failures or
replays occur. Comparison/logical predicates, wider Boolean/null/float/constant
selectors and wider defaults/types/producers/lifetimes remain partial; actual
loading stays separate.

The [Boolean-condition review](../../coverage/semantics/boolean-condition-default-reception-review.json)
adds four clauses in module519 over the existing constant-folder shapes, covering all
six logical constructors. NOT and reached operands recurse under the actual
declaration environment. A decisive AND/OR left truth skips its right projection;
XOR requires both truths. The constant compiler still visits both logical children
before selecting a result. Full source/default/index/origin/PDSTORED/PINT authority
and every receive, mode, readiness, root and cleanup body remain unchanged.
Logical results serve as conditions, never integer defaults or true shorthand
results. Three exact SL508 originals retain two precision agreements and one quiet
agreement, with native observations reused once. Corrected author 185 and first-pass
independent 138 execute 323 physical conditions (311 body, 12 setup). The 68
pre-change conditions are separate; all state/derived checks have source credit 0.
The original author fixture reused a variable for a ternary fallback and a
Boolean leaf; one binding was renamed and only that fixture rerun, preserving
the failure at 0.
Derived alias controls switch skipped/reached unknown operands and retain exact
source, pool and named-hole authority through default ownership and retirement.
Original sources remain global/no-import; actual loading is separate. Comparison,
cast/spaceship, general Boolean-valued ternary/coalesce leaves, wider scalars,
defaults, producers and lifetimes remain partial.

The [integer-comparison review](../../coverage/semantics/comparison-integer-default-reception-review.json)
adds four predicate clauses and one spaceship clause to module519. Both children
are projected in source order under the actual ENV and must fit a target long.
Equality and identity coincide on this integer-only domain. Greater predicates
reverse only the already projected values for the existing comparison kernel;
spaceship returns normalized -1/0/1 without subtraction overflow. Boolean results
remain conditions, never integer defaults. Full AST/default/index/origin/stored
integer authority and every receive, mode, readiness, root and cleanup body remain.
Three exact production-SL508 originals cover all eight predicates, all three
spaceship results, MIN/MAX ordering and unchanged precision/throw observers,
reusing native observations once. First-pass author 208 and independent 139 fixture
SL checks execute 347 physical conditions (335 body, 12 setup); pre 77 is separate.
The derived first-VAL and leading-REF fronts retain all five exact source defaults,
ENV, stored roots and ownership. They establish left/right ENV propagation,
reached unknown/out-of-range refusal, Boolean-versus-integer results, genuine named holes
and default-cell retirement, with source credit 0 and no AL claim. A trailing blank
line was removed from the tested peer script without changing its parsed code;
no semantic rerun or new failure occurs. Wider scalar comparison operands, casts,
general Boolean-valued selection leaves, defaults, producers and lifetimes remain
partial; actual composition/loading retains its own cut.

The [scalar integer-cast review](../../coverage/semantics/scalar-integer-cast-default-reception-review.json)
adds five disjoint `(int)` projections without changing reception or source authority.
Float eligibility follows the complete sign chain: negative MIN is admitted even
when its positive literal is not. Literal strings retain numeric-prefix and
saturating conversion, including nonfinite parsed strings producing zero;
concatenation and general float/string producers remain partial. Actual declaration
ENV resolves Boolean/null leaves. Three exact production-SL508 originals reuse
native observations once. Separate first-pass author131 and independent peer142
fixture-SL checks execute273 physical conditions (261 body,12 setup), with pre77
separate and all state/derived checks at source0, without AL or unique-count credit.
Exact source/default roots, aliases, named holes, default ownership and retirement
remain checked. Actual99485d599/508 loading passes16.086345817 s/source0 at its own
cut. No failures or replays occur; Boolean-producing operator casts, general
selection leaves, wider producers and signatures remain partial.

The [Boolean integer-cast review](../../coverage/semantics/boolean-integer-cast-default-reception-review.json)
adds one Boolean-producing shape guard and two integer 0/1 clauses to module519.
Only NOT, AND/OR, XOR and the eight long predicates borrow the existing actual-ENV
truth projection. Ordinary integers and spaceship keep their prior integer casts;
selected unknown operands refuse while decisive AND/OR skips the unused truth
projection. All source/default authority and receive/owner bodies remain unchanged.
Three exact production-SL508 originals reuse native observations once. First-pass
author 174 and independent 153 fixture-SL conditions execute 327 physical checks
(315 body, 12 setup), with pre 77 separate and all state/derived checks at source 0,
without AL or unique-count credit. The affected196 `Equal(1,1)` cast expectation
changes from refusal to 1 and is checked by ENUM197 without replaying ENUM196. Real ENV,
long bounds, wrong source/pool/default authority, named holes, saved integer
writeback, default owners and retirement remain checked. Actual `d92dd08e`/508
loading passes in 15.629225030 s/source 0 at its own cut. General Boolean-valued
selection leaves, other casts/producers, signatures and lifetimes remain partial.

The [selected integer-cast review](../../coverage/semantics/selection-integer-cast-default-reception-review.json)
adds a shape-gated leaf selector below `(int)` without replacing existing casts or
conditions. It follows selected full/shorthand ternary arms and coalesce inputs;
shorthand keeps integer 7, while false, zero and empty strings remain nonnull and
skip the RHS. Unknown left values refuse, and an ineligible selected float cannot
be rescued by the RHS. Only resolved null selects that RHS. Original selected
leaves use the existing scalar/Boolean cast rules, preserving signed-float final
eligibility, string prefixes and saturation, actual ENV and full outer source/pool
authority. Three exact production-SL508 originals reuse native observations once.
First-pass author 155 and independent 151 fixture-SL conditions execute 306
physical checks (294 body, 12 setup); pre 77 remains separate. All state/derived
checks have source 0, without AL or unique-count credit. Four affected ENUM197
refusal expectations become 1 and are checked freshly without replaying old
actors. Actual `c90b74ae3`/508 production-SL loading passes in 15.510795725 s
at its own source-0 cut. String/float truth conditions, selection beneath other
operators, wider producers and signatures remain partial.

The [scalar-truth review](../../coverage/semantics/scalar-truth-default-reception-review.json)
adds raw string and warning-free signed float literal truth in those bounded trees.
Only an empty string or the single ASCII byte `0` is false; both float zero signs
are false,
while non-NaN nonzero floats, including infinity, are true. Truth does not grant
integer-cast eligibility. The pinned compiler still defers every float NOT;
original stored-integer roots remain mandatory. Three production-SL508 originals
match on their first semantic executions, reusing native observations once.
Separate author157 and peer169 fixture-SL conditions execute326 physical checks
(314 body,12 setup), with pre77 separate and every derived check at source0;
there is no AL or unique-count claim. Seven old expectations are checked freshly
without replaying old actors. A catalogue recorder failure before selected-source parsing or semantic/oracle
execution retains0.
Explicit Boolean casts, general condition selections and wider producers,
signatures and lifetimes remain partial. Actual `9182b7aeb`/508 production-SL
loading passes in 15.447642532 s at its separate source-0 cut.

The [Boolean-cast review](../../coverage/semantics/boolean-cast-default-reception-review.json)
adds explicit `(bool)` to that finite truth domain and Boolean-producing shape.
It preserves fractional and infinite truth without granting direct float-to-int
eligibility or treating a Boolean-valued default as an integer. A genuine unused
float-NOT default remains signature-tagged deferred, with `PDDEFERRED` and no
stored integer; its pure projection alone cannot admit the header. Three exact
production-SL508 originals reuse native observations once. Separate author187
and peer171 fixture-SL conditions execute358 physical checks (346 body,12 setup),
with pre91 separate and every derived check at source0, without AL or a unique
count. One affected199 expectation is checked freshly without replay. No200
failure occurs. General value-producing ternary and Boolean-coalesce conditions,
wider producers, signatures and lifetimes remain partial. Actual `79b95118f`/508
production-SL loading passes in 15.494809378 s at its separate source-0 cut.

The [ternary-truth review](../../coverage/semantics/ternary-truth-default-reception-review.json)
adds full/shorthand ternary conditions over the existing bounded truth domain.
One computed condition selects only the needed truth branch. The separate
cast-leaf projection keeps the selected AST, so the shorthand string witness
casts to `13`.
The ternary-only guard leaves integer-coalesce truth unchanged; Boolean-valued
coalesce remains partial. Three corrected production-SL508 comparisons reuse
natives once: quiet ABC is an existing control, precision ABCDE and pending BC
are new agreements. First-pass author 183 and peer 184 fixture-SL conditions execute
367 physical checks (355 body, 12 setup), with pre 91 separate and derived checks
at source0, without AL or unique-count credit. Original optional-Boolean dispatch
and minimal-probe failures retain zero credit; explicit equality guards fix the dispatch.
Four old200 outcomes are checked freshly without replaying old actors. Actual
`3905effdf`/508 loading passes in 15.334248181 s at its separate source-0 cut.
Wider condition producers, signatures and lifetimes remain partial.

The [coalesce-truth review](../../coverage/semantics/coalesce-truth-default-reception-review.json)
shares an original selected AST and cached truth across ternary/coalesce choices.
Only a resolved null leaf uses the coalesce RHS; false-like nonnull values retain
the left certificate. Infinity supplies quiet truth without integer eligibility,
and shorthand string `13tail` still casts to `13`. Original cast and stored-PINT
source authority remain. Three first-pass production-SL508 comparisons reuse
natives once: quiet ABC is an existing control, precision ABCDE and pending BC
are new agreements. Separate author 212 and peer 238 fixture-SL conditions execute
450 physical checks (438 body, 12 setup), with pre 91 separate and derived checks
at source0, without AL or unique-count credit. Five old truth outcomes are checked
freshly; four helper-shape references are maintained without replay. Removing an
unused fixture helper preserves identical generated source/stage/checks. No202
failure occurs. Actual `b9a3ac1eb`/508 loading passes in 15.731924920 s at its
separate source-0 cut. Wider producers, signatures and lifetimes remain partial.

The [float-cast-truth review](../../coverage/semantics/float-cast-truth-default-reception-review.json)
adds explicit float-cast truth over the same selected-AST certificate. Raw or
selected strings use decimal-prefix conversion, distinguishing `0.0` from its
raw truth and `0.5tail` from integer truncation. Numeric, Boolean and null leaves
retain their cached truth; unknown/reached NaN refuses. Integer-cast eligibility,
original source/default/pool authority and reception owners stay unchanged.
Three first-pass production-SL508 originals reuse native observations once: one
existing quiet control and two new precision agreements. Separate author249 and
peer283 fixture-SL conditions execute532 physical checks (520 body,12 setup),
with pre91 separate and derived checks at source0, without AL or a unique count.
Removing unused peer construction preserves identical generated CASES without
rerun. No203 failure occurs. Actual `994493f99`/508 loading passes in
16.131328344 s at its separate source-0 cut. CONCAT and wider string/float
producers, signatures and lifetimes remain partial.

The [CONCAT-string review](../../coverage/semantics/concat-string-default-reception-review.json)
adds finite literal-string CONCAT trees to one decoded-byte projection shared by
raw truth and explicit integer/float conversion. Empty bytes remain a known value;
NUL/non-ASCII and left/right byte order survive. Assembled `0.0` has true raw
truth, false float truth and integer0; selected syntax retains its original AST.
The source/default/pool/header and receive/owner bodies remain unchanged.
Three first-pass production-SL508 originals reuse native3 once: one existing
quiet control and two new precision agreements. Corrected author310 and first-pass
peer314 fixture-SL conditions execute624 physical checks (612 body,12 setup),
with corrected pre91 separate and all derived checks at source0, without AL or
unique-count credit. The prefixture boundary-digit typo and author expectation
of MAX for infinite text retain their original failures at source0; the pinned
cap returns0 for infinity and saturates finite overflow. Four affected old203
refusals use mixed string/integer0 operands and are checked freshly without replay.
Actual `484d489ce`/508 loading passes33.197897111s at its separate source-0 cut.
Mixed/selected CONCAT operands, other string/float producers, signatures and
lifetimes remain partial.

The [string-NOT review](../../coverage/semantics/bitnot-string-default-reception-review.json)
adds bitwise NOT to that finite byte domain through the existing complement
kernel. String `~"0"` yields byte207; integer `~(int)"0"` remains -1.
Empty bytes stay known, double NOT restores bytes, and selected syntax keeps its
original AST for integer/float conversion. Source/default/pool/header and
receive/owner bodies remain unchanged. Three first-pass private production-SL508
originals reuse native3 once: one existing quiet control and two new precision
agreements. Separate first-pass author350 and peer275 fixture-SL checks execute
625 physical conditions (613 body,12 setup), with pre91 separate and every derived
check at source0, without AL or unique-count credit. No205 fixture/source failure
or old expectation change occurs. Equivalent Get guard factoring recovers joined
loading; the current `0599ebd55`/508 load passes15.936661636s/source0. Both earlier
fixed60-second failures retain zero credit; private accepted cuts stay separate.
Scalar/selected producer children, wider signatures and lifetimes remain partial.

The [binary-string review](../../coverage/semantics/bitwise-string-default-reception-review.json)
adds string AND/OR/XOR through nine byte-projection lines and existing kernels.
Both operands must certify even beside an empty string. AND/XOR truncate to the
shorter length; OR preserves the longer suffix. Raw truth, integer/float casts,
selected AST and all source/default/pool/header and receive/owner rules remain.
Three first-pass private production-SL508 originals reuse native3 once in
492.846682899s, within unchanged360/600s limits. First-pass author294/peer375
fixture-SL checks execute669 physical conditions (657 body,12 setup), with pre91
separate and derived checks at source0, without AL or unique-count credit.
No206 failure, witness reduction, old expectation change or replay occurs.
The source/test package is integrated. Its original `ab60fab36`/508 joined load
passes17.792991204s/source0; the later index addition below retains its own cut.
Scalar/selected producer children, wider signatures and lifetimes remain partial.

The [string-index review](../../coverage/semantics/index-string-default-reception-review.json)
adds one-byte reads from certified byte expressions at nonnegative, in-bounds
integer literal/unary indices. NUL and individual UTF-8 bytes stay distinct from
empty bytes; raw `"0"` truth and integer/float conversion remain separate.
Negative indices stay compiler-deferred, without stored PINT authority. The
source/default/pool/header and receive/owner rules remain unchanged. Three
first-pass private production-SL508 originals reuse native3 once in154.009043956s:
one existing quiet control and two new precision agreements. Corrected author294
and peer260 fixture-SL checks execute554 physical conditions (542 body,12 setup),
with pre107 separate and derived checks at source0. The original fixture syntax
and binding failures retain zero credit; no semantic failure or old expectation
change occurs. Actual `0599ebd55`/508 loading passes15.936661636s at its separate
source-0 cut. String/computed/coerced indices, scalar/selected producer children,
wider signatures and lifetimes remain partial.

The [numeric-string-selector review](../../coverage/semantics/string-selector-default-reception-review.json)
adds certified byte-string selectors whose numeric classification is an integer.
Leading zeros/signs, ASCII whitespace, trailing text and NUL follow the pinned
compiler's quiet folding; `"0x1"` supplies decimal prefix0. Float-form, overflowing,
negative and out-of-bounds selectors remain outside this fold. Runtime offset
Warnings use their separate protocol. Four projection lines reuse the existing
numeric-string/index helper without changing source/default/PINT or owner rules.
Three first-pass private production-SL508 originals reuse native3 once in309.556213943s.
Author336 and peer355 fixture-SL checks execute691 physical conditions (679 body,
12 setup), with pre123 separate and all derived checks at source0. Nine affected
old207 refusal checks use nonnumeric/float strings and are checked freshly inside
these208 fixtures; their old campaigns are not renewed. The unchanged16-level
chain passes within the original300-second limit. Actual `b1e8a2876`/508 loading
passes34.611321754s at its separate source-0 cut. Scalar/selected byte producers,
computed/coerced integer indices, wider signatures and lifetimes remain partial.

The [integer/byte CASTSTRING review](../../coverage/semantics/integer-string-cast-default-reception-review.json)
adds signed integer-literal formatting and identity over certified byte strings
as one cast group. Five projection lines reuse the decimal formatter and byte
certificate; raw `"0"`/`"0.0"` truth stays distinct from integer/float conversion.
Boolean/null names require declaration ENV and float-to-string casts remain precision-deferred.
All four genuine unused deferred contrasts retain no stored PINT authority.
Three first-pass private production-SL508 originals reuse native3 once in164.128623923s.
Author329 and peer345 fixture-SL checks execute674 physical conditions (662 body,
12 setup), with pre139 separate and derived checks at source0. Fifty affected
old condition entries across seven fixtures are covered by11 author and31 peer
fresh helper formulas, sharing the identical eight-formula CONCAT block. Their
old campaigns are not renewed. The unchanged24-level cast chain passes; no
failure, cap increase or witness reduction occurs. Actual `aac5dc4fc`/508 loading
passes15.087097541s at its separate source-0 cut. Contextual Boolean/null and
computed scalar casts, float precision, wider signatures and lifetimes remain partial.

The [contextual scalar CASTSTRING review](../../coverage/semantics/contextual-string-cast-default-reception-review.json)
threads the actual declaration ENV through byte projection and float truth.
Certified computed integers, typed Boolean predicates and resolved Boolean/null
names now cast to bytes; recursive byte identity and strict AST descent remain.
Three real global constant imports supply the source witnesses; general namespace,
producer and signature coverage remains open. The existing header still requires
the exact source default and stored PINT. Four genuine deferred contrasts retain
no stored PINT, including precision-dependent float-to-string conversion.
Three first-pass private production-SL508 originals reuse native3 once: one
existing quiet agreement and two new precision agreements. Author382 and peer360
fixture-SL checks total742 physical conditions (730 body,12 setup); pre144 and
all derived checks retain source0. The33 affected old209 right-side expectations
are covered freshly without replaying those campaigns. All original limits hold;
source/tests are integrated at `44c9cec63`. The separate actual `2c2c8f051`/508
production-SL load passes15.891098138s with source0; private cuts are unchanged.

The [computed integer selector review](../../coverage/semantics/computed-index-string-default-reception-review.json)
admits certified integer expressions as string indices in the receive certificate.
One projection premise reuses the declaration-aware integer certificate; existing
numeric-string keys, nonnegative byte bounds and exact stored-PINT authority remain.
Five real defaults exercise integer casts, arithmetic, selected/coalesced aliases,
exact division and remainder. Five genuine unused deferred contrasts retain no
stored PINT, including a computed negative index. Raw Boolean/null/float keys and
runtime float formatting remain outside this extension.
Three first-pass private production-SL508 originals reuse native3 once in257.361783628s:
one existing quiet agreement and two new precision agreements. Author378 and
peer457 fixture-SL checks total835 physical conditions (823 body,12 setup); pre161
and derived checks retain source0. Twelve old right-side expectations across
three fixtures preserve their inputs and are covered freshly without old replay.
The16-level computed-index chain passes at the original limits. Source/tests are
integrated at `ce8ea3b16`; the separate actual `477816a67`/508 production-SL
load passes16.394898964s with source0. Wider defaults and lifetimes remain partial.

The [selected scalar CASTSTRING review](../../coverage/semantics/selection-string-cast-default-reception-review.json)
admits selected byte, Boolean and null children through the existing full/shorthand
ternary and coalesce selector. Five projection lines require a child without an
existing integer certificate, then cast its proper selected descendant. Integer formatting stays separate;
raw selected-byte producers and float formatting gain no authority. False remains
non-null under coalescing, empty bytes remain present, and `"01"` retains its bytes.
Five real stored-PINT defaults and six genuine unused deferred contrasts preserve
the existing source/default/pool and ownership requirements.
Three first-pass private production-SL508 originals reuse native3 once in243.627074868s:
one existing quiet agreement and two new precision agreements. Author368 and
peer503 fixture-SL checks total871 physical conditions (859 body,12 setup); pre181
and all derived checks retain source0. Six old right-side expectations preserve
their exact inputs and are covered freshly without old replay. The16-level selected
cast chain passes at the original limits. Source/tests are integrated at `a4ab11dcc`;
the separate actual `89a828eec`/508 production-SL load passes16.081071375s with
source0. Wider defaults, float precision and lifetimes remain partial.

The [computed FLOAT integer-cast review](../../coverage/semantics/computed-float-integer-cast-default-reception-review.json)
admits explicit integer casts of typed arithmetic through the existing pure
ADD/SUB/MUL/DIV kernels. Existing integer certificates and signed FLOAT literals
feed the projection; only its FLOAT result enters the unchanged NaN, fit and quiet
integer-cast guards. Direct computed unary/selected FLOAT operands, raw scalar
coercion, bare computed-FLOAT truth and string formatting remain outside this
extension; inherited outer CASTINT selection still casts an admitted selected leaf.
Five stored-PINT roots exercise all four operations under their actual declaration
ENV; nine genuine unused deferred contrasts preserve nonfit, zero-divisor and NaN
boundaries. Source/default/pool authority and receive ownership remain unchanged.
Three private production-SL508 originals reuse native3 once in153.706436005s:
one existing quiet agreement and two new precision agreements. Author366 and
corrected peer405 fixture-SL checks total771 physical conditions (759 body,12 setup);
pre228 stays separate. A copied root-binding fixture failure retains zero credit;
only its two bindings change before the same405-condition case passes. One old196
right-side expectation changes with its exact input freshly covered. No source,
native, current or author campaign is replayed. Source/tests are integrated at
`01d02e899`; the separate actual `455190ea0`/508 production-SL load passes
15.680603100s with source0.

The [computed unary FLOAT review](../../coverage/semantics/unary-computed-float-integer-cast-default-reception-review.json)
adds typed unary signs through the existing multiplication kernel and integer
factors +1/-1, matching the pinned compiler. Eight projection lines require no
existing whole integer or signed-literal certificate; those earlier arms retain
precedence. Explicit integer-cast guards, source/default/pool authority and receive
ownership remain unchanged. Five real stored-PINT defaults and ten genuine unused
deferred contrasts distinguish signs, signed zero and MIN promotion/refitting.
Three private production-SL508 originals reuse native3 once in155.999185517s:
one existing quiet agreement and two new precision agreements. Corrected author371
and peer447 fixture-SL checks total818 physical conditions (806 body,12 setup);
pre245 stays separate. One blanket-refusal fixture expectation overlooked the old
whole-expression INTMIN certificate; its one RHS changes before the same371 case
passes, with the original failure at zero. One old213 unary-helper RHS promotion
keeps its exact input and is covered freshly. No source/native/current/pre campaign
is replayed. Source/tests are integrated at `3301b52db`; its separate actual508
production-SL load passes16.588960099s with source0. Direct selected FLOAT operands,
raw coercion, bare computed-FLOAT truth and formatting remain partial.

[Computed FLOAT truth defaults](../../coverage/semantics/computed-float-truth-default-reception-review.json)
use the existing typed numeric projection and unchanged quiet `number_bool` guard.
The numeric truth arm excludes selection roots, preserving their existing route.
Signed zeros are false; finite nonzero/subnormal values and infinity are true;
NaN remains refused. Five actual stored-PINT roots use three real global constant
imports. Twelve genuine deferred/no-PINT contrasts retain compiler FLOAT-NOT
conservatism even where the finite helper projects0. Three originals agree,
reusing native3 once; author405 and independent567 fixture-SL checks retain their
private508 cuts (972 physical=960body+12setup), with pre285 separate. Exactly31
old condition RHS promotions preserve source/stage/count/inputs and are covered
freshly. One nonexecuting inspection import failure retains source0; all six
campaigns pass first attempt. Direct selected FLOAT Numeric operands, raw
coercion, wider defaults/lifetimes and formatting remain partial. The separate
actual `c739a2b8f`/508 production-SL load passes15.838359269s with source0.

[Selected FLOAT numeric defaults](../../coverage/semantics/selected-float-numeric-default-reception-review.json)
retain the selected FLOAT tag below existing arithmetic/sign parents. The new
Numeric arm requires an absent whole integer certificate and a proper selected
NFLOAT leaf; explicit CASTINT selections retain their existing route. The inherited
coalesce fit proof applies only to a nonnull LEFT leaf: `INF ?? unknown` refuses,
while `null ?? INF` can project infinity before final CASTINT refusal. Raw selected
byte/bool/null arithmetic and FLOAT formatting remain outside this widening.
Five actual stored-PINT roots produce -7/-11/13/MIN/MAX; fifteen genuine deferred
contrasts keep their source and no-PINT authority. Three originals agree with
native3 reused once. Author447 and corrected independent552 fixture-SL checks
retain private508 cuts (999 physical=987body+12setup), with pre372 separate.
One unbound copied fixture metadata name caused the retained failed552/source0;
only its five references change before that peer case passes. Sixteen old RHS
promotions preserve original source/stage/count/inputs and are covered freshly.
Actual MAIN `646663d66`/508 loads in16.138222003s with source0; wider numeric
producers/defaults/lifetimes and formatting remain partial.

[Typed numeric FLOAT-cast defaults](../../coverage/semantics/numeric-float-cast-default-reception-review.json)
reuse `num_float` for INT rounding and FLOAT identity. Typed CASTDOUBLE truth uses
the existing quiet numeric arm; a guard requiring Numeric=eps keeps the prior
byte, Boolean and null truth route disjoint. Static/default casts reject NaN as Zend's
compiler does; runtime FLOAT identity remains unchanged. Five actual stored-PINT
roots include exact INTMIN and MAX-rounding cancellation before final CASTINT.
Seventeen genuine deferred/no-PINT controls retain their source authority.
Three originals agree with native3 reused once. Author490 and independent593
fixture-SL checks retain private508 cuts (1083 physical=1071body+12setup), with
pre389 separate. Both old RHS promotions preserve source/stage/count/inputs and
are covered freshly. All six campaigns pass first attempt; one draft-only Python
preparation failure retains source0. Actual MAIN `6b8f94943`/508 loads in
15.279918018s with source0. FLOAT-value projection for raw bytes/Boolean/null,
wider numeric/default/lifetime scope and formatting remain partial.

[Explicit scalar FLOAT-cast defaults](../../coverage/semantics/scalar-float-cast-default-reception-review.json)
reuse byte parsing and FLOAT0/1 for special null/Booleans and quiet Boolean-shaped
children. Typed numeric casts and the prior truth fallback retain their separate
routes. String `NAN` parses as zero; direct FLOAT NaN remains refused by the static
cast certificate. Five actual stored-PINT roots include CONCAT/CASTSTRING, byte
bitwise NOT and actual false/null/true conversions. Eighteen genuine deferred
contrasts keep their source and no-PINT authority. Three originals agree with
native3 reused once. Author563 and independent647 fixture-SL checks retain
private508 cuts (1210 physical=1198body+12setup), with pre409 separate. All six
campaigns pass first attempt, including the unchanged eight-level interleaved
FLOAT/Boolean author witness within its original300cap. All36 old RHS inputs
preserve source/stage/count and are covered freshly. Actual MAIN `20b196ef1`/508
loads in15.631246611s with source0. FLOAT-value projection for selected byte/Boolean/
null casts, raw arithmetic coercion, wider defaults/lifetimes and formatting remain partial.

[Selected scalar FLOAT-cast defaults](../../coverage/semantics/selected-scalar-float-cast-default-reception-review.json)
recurse through an actual selected leaf when the CASTDOUBLE child lacks an existing
Numeric certificate. Typed casts, including static NaN refusal, retain priority;
raw selected byte/Boolean/null arithmetic remains outside this cast-only widening.
Known null stays distinct from absence, and the inherited nonnull-left coalesce
fit proof remains required. Five actual stored-PINT roots produce -7/-11/13/MIN/MAX;
nineteen genuine deferred contrasts retain exact source and no-PINT authority.
Three originals agree with native3 reused once. Author524 and independent696
fixture-SL checks retain private508 cuts (1220 physical=1208body+12setup), with
pre441 separate. All six campaigns pass first attempt under their original caps.
Eleven old RHS promotions preserve source/stage/count/inputs and are covered freshly.
Actual MAIN `722479554`/508 loads in16.084281732s with source0. Wider numeric
producers, implicit arithmetic coercion, defaults/lifetimes and formatting remain partial.

[Typed numeric comparison defaults](../../coverage/semantics/numeric-comparison-default-reception-review.json)
use existing NINT/NFLOAT comparison and identity kernels for all eight predicates
and integer spaceship results. Tags distinguish strict identity; greater-than and
greater-or-equal reverse operands, and quiet NaN comparisons retain the truth/cast refusals.
Actual declaration ENV and five stored-PINT roots remain required, alongside
nineteen genuine deferred/no-PINT contrasts. The two affected originals now agree
in174.330/44.073s under the original360cap. Native3 ran once; the earlier quiet
agreement stays at its original failed-campaign cut, without campaign PASS or
stability credit. Author614 and independent718 fixture-SL checks retain their
cuts (1332 physical=1320body+12setup); pre420 and earlier603 stay separate.
Four precision timeouts remain zero credit. Diagnostic profiling identified
compiler tuple-tail unpack/repack work; a separately reviewed
[lookup refinement](../../coverage/semantics/compiler-lookup-tail-review.json)
preserves opaque payloads, first matches and conflicts without a cache.
The one old RHS promotion is covered freshly. Actual MAIN `d3e72bce9`/508 loads
in16.184982364s with source0. Wider producers, namespaces, formatting and lifetimes
remain partial.

[Numeric integer bitwise defaults](../../coverage/semantics/numeric-bitwise-default-reception-review.json)
retain signed64 `NINT` results through AND/OR/XOR and unary NOT using the existing
pure integer kernels. An absent whole integer certificate and proper typed numeric
children keep the older integer path disjoint. Exact source, declaration ENV,
resolved names, complete no-DIM bindings, Shared caches and ordinary receive/owner
guards remain required. Cold/warm BYREF defaults, named holes and warning reentry
preserve masks, MIN/MAX and nonnull zero. FLOAT/string coercion, effectful
`E_STRICT`, wider operators, entries and lifetimes remain partial.

[Numeric modulo and shift defaults](../../coverage/semantics/numeric-integer-operator-default-reception-review.json)
also use the existing integer dispatch with proper signed64 `NINT` children.
Only `IRESULT` grants a quiet value: zero divisors and negative counts remain
outside this certificate. Wrapping left shifts, signed right shifts, counts at
or above64, `MIN % -1` and nonnull zero retain the same source/ENV/no-DIM/name,
Shared-cache and receive/owner authority. FLOAT/string coercion, effectful
`E_STRICT`, POWER and wider producers, entries and lifetimes remain partial.

[Numeric integer power defaults](../../coverage/semantics/numeric-power-default-reception-review.json)
retain proper signed64 `NINT` children, a nonnegative exponent and a fitting
`POWERDONE (NINT i) false` result from the existing pure power preparation.
Absent whole integer authority keeps the old path disjoint. Exact MIN/MAX,
exponent-zero, odd negative bases, nested powers and nonnull zero preserve
source/ENV/no-DIM/name, Shared-cache and receive/owner guards through cold/warm
BYREF defaults and named warning reentry. FLOAT results and negative exponents
extend below; coercion, effectful `E_STRICT` and wider scope remain partial.

[Completed Numeric FLOAT power defaults](../../coverage/semantics/numeric-float-power-default-reception-review.json)
also retain proper signed64/binary64 Numeric children and quiet
`POWERDONE (NFLOAT n) false` preparation. Raw FLOAT tags and signed-zero bits
remain in Shared caches before private integer reception; nonfitting and NaN
results reach the ordinary TypeError. Source/ENV/no-DIM/name and owner guards
remain through cold/warm BYREF defaults and named warning reentry. The affected
earlier overflow source reuses its saved native observation. Quiet GENERAL
completion extends below; power diagnostics, implicit coercion, effectful
`E_STRICT` and wider scope remain partial.

[Quiet GENERAL Numeric FLOAT power defaults](../../coverage/semantics/numeric-general-power-default-reception-review.json)
use `(NFLOAT n, false) = $num_pow(left, right)` after the same proper Numeric
child and word bounds. The existing pure kernel preserves completed results
and finishes GENERAL plans, including nonunit overflow factors. Raw fractional
FLOAT caches precede their own precision callbacks, throwing callbacks, retry
and private integer reception. Source/declaration ENV/name/no-DIM/selected-child,
Shared-cache and receive/owner authority remain unchanged. Cold/warm BYREF and
named reentry source agreements, two saved-original promotions, author184 and
independent229 fixture conditions retain separate cuts. Quiet scalar operands
extend below; power diagnostics, effectful `E_STRICT` and wider scope remain partial.

[Quiet scalar power-default operands](../../coverage/semantics/numeric-coercive-power-default-reception-review.json)
use a dedicated POWER projection for existing Numeric values, Boolean/null and
decoded FULLNUM strings whose conversion is quiet. The added arm requires a
proper child without Numeric identity, exact operand bounds before pure power,
a quiet power result and exact result bounds. Generic raw Numeric identity remains; quiet binary arithmetic extends below.
Raw PINT/PFLOAT cache tags precede private integer reception, including a
fractional default's own throwing precision callback and retry.
Source/ENV/no-DIM/cache/owner guards remain. LEADNUM, nonnumeric strings and
zero-negative power diagnostics remain outside this certificate.

[Quiet scalar arithmetic default operands](../../coverage/semantics/numeric-coercive-arithmetic-default-reception-review.json)
share that unchanged three-route projection through `quiet_operand`, retaining
the POWER wrapper. A disjoint ADD/SUB/MUL/DIV arm requires a proper child without
Numeric identity, exact input bounds before the existing pure kernel, a NUM
result and exact output bounds. Raw int/float cache types precede private
receives and own precision callbacks through BYREF resume, throw/retry and
named reentry. Source/ENV/no-DIM/cache/owner guards remain. LEADNUM, BADNUMBER,
DIVZERO, effectful constants and wider scope remain partial.

[Computed Boolean default operands](../../coverage/semantics/computed-boolean-operand-default-reception-review.json)
also pass through `quiet_operand` when their AST has a genuine Boolean shape,
Numeric identity is absent and the existing condition proof is quiet. NOT,
BOOL casts, short AND/OR, XOR and numeric predicates retain PBOOL meaning before
conversion to NINT0/1 for arithmetic or POWER. Source/ENV/no-DIM/cache/owner
guards remain; decisive skipped effects stay skipped. Raw caches still precede
private integer reception, BYREF resume and own precision throw/retry. Noisy
NaN truth, selected effects and raw scalar selections remain outside this arm.

[Falsey full-ternary defaults](../../coverage/semantics/deferred-falsey-full-ternary-redirect-wrapper-default-reception-review.json)
retain exact FIELD2 scalar values while checking only condition and selected
bindings. Skipped unresolved names retain genuine source occurrences without
becoming compiled reads. Five scalar falseys and bare empty/`'0'` predicates
require their exact source/pool/redirect and literal-header certificates.
Quiet emitted integer casts carry selected null to integer zero. Two original
agreements reuse native observations once; prelaw144, author227/62/261 and
independent396/34 retain separate cuts and original failures0. Truthy/NaN
conditions, wider strings, owning results and wider contexts remain partial;
quiet-shape/no-DIM, declaration, cache, recipient and owner bounds remain.

[Literal-TRUE full-ternary defaults](../../coverage/semantics/deferred-true-full-ternary-redirect-wrapper-default-reception-review.json)
carry selected FIELD1 scalar tags through an exact source/pool/redirect certificate.
The selected value keeps its BOOLfalse, NULL, long or binary64 type; the condition
must resolve to TRUE with a matching plain Boolean pool and no executable leaf.
Existing binding pruning skips unresolved FIELD2 names, while every source
occurrence remains authenticated. Two originals reuse native observations once;
prelaw162, author244/206/62 and independent280/76/32/28 pass at separate cuts.
Wider truthy predicates, owning results and wider contexts remain partial;
declaration, quiet-shape/no-DIM, cache, recipient and owner bounds remain.

[Computed-Boolean-TRUE full-ternary defaults](../../coverage/semantics/deferred-computed-true-full-ternary-redirect-wrapper-default-reception-review.json)
extend the selected FIELD1 certificate through one recursive exact-Boolean
condition premise. Matching pools and absent condition CODE/read/redirect remain
required; selected tags, skipped names and all other guards are unchanged.
Eight primitive conditions retain raw integer, Boolean, NULL and binary64 results.
Two originals reuse native observations once; prelaw214/165, author252/206/62 and
independent300/76/32/28 retain separate first-pass cuts. Only three old assertions
are promoted, with separate affected27/13 checks per author and reviewer; forged
SOURCE versus SIGNATURE still refuses the whole default. Actual49e4a8839 and its
sole saved production-SL509 load pass in16.239776302s with source0, independently
cleared through one immutable tuple. Generic truthy/NaN conditions, owning results
and wider contexts remain partial.

[Literal-infinity full-ternary defaults](../../coverage/semantics/deferred-infinite-float-full-ternary-redirect-wrapper-default-reception-review.json)
retain exact FIELD1 scalar tags when a raw FLOAT literal or unary sign chain
has infinity bits. The same literal/INFINITE/typed-pool/full-source receipt
serves binding pruning and value transport; the condition has no executable
read or redirect, and the root has one proper noncopy FIELD1 redirect.
Skipped FIELD2 names keep their source occurrences without demanded bindings.
Shared raw caches and private integer recipients survive cold/warm calls and
named coercion-handler reentry. Two originals and separate author/independent
state cuts pass; the actual SL509 load remains a distinct zero-source-credit cut.
Named infinity, wider computed predicates, NaN conditions, owning results and
wider contexts remain partial. Prior finite FLOAT and literal STRING certificates
retain their existing scope and evidence.

[Computed-infinity full-ternary defaults](../../coverage/semantics/deferred-computed-infinite-float-full-ternary-redirect-wrapper-default-reception-review.json)
admit one ADD/SUBTRACT/MULTIPLY/DIVIDE over raw FLOAT literals or unary sign
chains when the pure binary result and actual condition VALUE have identical
INFINITE bits. Both exact operand SOURCE trees and FLOAT pools remain required,
with no executable CODE, read or redirect at operand/condition roots. The receipt
shares the existing unique proper FIELD1 redirect with binding pruning and
scalar VALUE transport; literal-infinity and finite-FLOAT helpers are unchanged.
Skipped names, raw selected tags, Shared caches and private integer reception
retain their existing bounds through cold/warm calls and named handler reentry.
INT-left, named or wider computed operands, NaN predicates, owning results and
wider contexts remain partial; prior accepted cuts retain their original identities.

[FLOAT-left/INT-right infinite defaults](../../coverage/semantics/deferred-float-integer-infinite-full-ternary-redirect-wrapper-default-reception-review.json)
admit one ADD/SUBTRACT/MULTIPLY/DIVIDE with a raw FLOAT/sign left operand and
raw signed64 INT/sign right operand. The integer recognizer checks every sign
step; unary overflow receives no INT receipt. Exact FLOAT/PINT pools, matching
pure and actual INFINITE result bits, full SOURCE/bindings and operand/condition
root CODE/read/redirect absence share the unchanged proper FIELD1 redirect proof.
Selected NULL/BOOL/INT/FLOAT tags, Shared caches and private integer reception
retain their existing bounds through cold/warm calls and named handler reentry.
INT-left, names, STRING or computed operands, NaN predicates, owning results and
wider contexts remain partial. Earlier FLOAT-only receipts and accepted cuts
retain their original identities.

## Source metadata and resumed states

Compiler 94 restores the surrounding return context after nested declarations,
records function `ENDLINE`, and records return-root `CODEEXPR` entries after
compiling each return expression. Runtime 95 consumes these source projections.
Typed receive tasks bind the current function, receive index, previous defined
slots and sole work queue. They do not reconstruct previously received values or
types. Fallthrough tasks bind a current function with a declared return type.
Return tasks bind the owning function's source unit, actual return root and
compiled line. Saved tasks are checked under their saved caller context.
Unit return-root metadata is compared with the source compiler projection,
including units without function declarations.

Uncaught CLI rendering follows pinned `zend_exceptions.c`: exact TypeError and
ArgumentCountError messages containing `, called in ` receive the temporary
` and defined` display suffix. The semantic diagnostic message remains unchanged.

The review binds15 native profiles plus3 ticks dependencies,5 dense states/1357,
19 retained protocol controls/217 and2 complete untyped917 state bridges. Author
38 source profiles plus3 cache projections/12,4 states/1096 and compiler56+8/38
pass onbaa. Corrected fresh protocol19/218 and canonical CLI8 pass on599. Source
sets overlap; these counts are not added.

## Required continuation

Mixed caller/callee strictness is an interface requirement. The retained native
same-file witnesses use a `ticks` declaration block that remains outside current
source execution. They are dependency controls, not admitted runtime agreements.
Cross-unit/dynamic/callback integration must exercise that distinction through
its own checked source route.

Class/object/callable/iterable types, reference returns, variadics, named and
unpacked sends, methods and other callable forms remain required. So do other
declare directives, builtin body execution, ordinary exception control, dynamic
sources, generators/fibers and the rest of the core checklist. The full callable
integration campaign and final current-source/full-syntax/fresh offline gates
remain mandatory. Unsupported outcomes and tool failures never count as agreement.

The [runtime successor handoff](RUNTIME-REFERENCE-RETURNS-HANDOFF.md) supplies
the exact926 starting point and reference-return/call-acquisition preparation.

The later [call-reference increment](SOURCE-CALL-REFERENCE-ASSIGNMENT.md) on933
corrects shared post-argument emission locations: a retained typed return around
a multiline call now reports native line5 instead of926 line4. Historical typed
gates and the926/baa-to599 test-only bridge above retain their original scope.
