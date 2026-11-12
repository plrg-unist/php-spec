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
Integer-valued full/shorthand ternaries retain their selected-long rule.
Their truth projection accepts admitted long trees, resolved bare Boolean/null
leaves and finite `!`, `&&`/`and`, `||`/`or` and eager `xor` trees.
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
