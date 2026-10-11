# Current Closure and fake binding

Module253 implements `Closure::getCurrent()` through literal, imported,
computed, object and nullsafe API entries. Argument evaluation and argument
errors precede the observation. The API returns the exact immediate executing
ordinary Closure, including arrows, clones, rebound copies and created source
Closures. Named functions, methods and fake captures raise `Error` with
`Current function is not a closure`. Calling the static API on another Closure
uses that object's type as historical selection evidence; its receiver adds no
owner during argument effects.

Literal named-static `Closure::getCurrent(...)` also creates an API Closure.
Calling it observes the immediate ordinary body; a named helper still raises
`Error` even under an ordinary outer Closure. Dynamic calls pin the selected API
in CONFIG through argument evaluation. Its OWNER/SELECTION tag carries the
resolved object identity, outside selected-name nonce scans; the handler consumes
that owner before returning or propagating an error. Clearing the picked cell
then retires the API independently of the returned body; clearing the returned
cell retires the body. The named error's three scalar-only trace frames retain
neither object, and the actual caught-null write prunes the error graph. The
earlier three native originals, one direct and two repaired captured sources,
body (206) and named (241) cuts, four failed full fixtures and localization cut
retain their original evidence. Recorded zero-argument bridges (54/57) validate the new
CONFIG tag/owner and the same successful current identity and named rejection.

An ordinary positional helper may clear the sole API cell after a call has been
selected. Native static calls observe that API gone; captured calls observe it
held by the saved CONFIG. Both produce the exact one-argument ArgumentCountError.
The real api-null write before the weak producer verifies this distinction;
consuming the arity-error CONFIG retires the API while the ordinary body is still
current. Its two scalar-argument trace frames retain neither API nor body, and
caught-null prunes the error graph. Both original native observations are retained;
the unchanged direct and affected captured sources each agree with their own oracle.
The 527 state premises pass (488 genuine/derived plus 39 controls). Three syntax
failures remain zero-credit.

Direct first-class conversion of `$closure->__invoke(...)` returns that existing
Closure, matching the factory's `__invoke` identity rule. Invocation then uses
its ordinary selected body and frame rather than an extra invoke wrapper.

Binding a fake function, method, finite throwable getter or admitted intrinsic
allocates a distinct Closure and preserves the frozen selection. Nonstatic
bindings own their new receiver; old sources and receivers may retire. User
function and method statics remain shared with the selected source, including
through clone and repeated binding. Getter bindings invoke the selected getter
on the new compatible receiver. Free intrinsic bindings clear lexical scope and
receiver while retaining their changed called class for equality.

Scope resolution precedes receiver and fake-scope validation. Only exact lowercase
`static` denotes the previous lexical scope; weak scalar scope operands convert
to strings. Selected warnings suspend for error handlers. Handler class declarations
cannot undo a held missing-class warning, and throws run `finally` and retain
callback writes before the binding unwinds.

A free user-function fake bound to an object acquires internal `Closure` lexical
scope. A returned ordinary source Closure copies that scope, called class and
receiver as durable evidence; cloning copies its ordinary static storage.
Ordinary REAL bindings that need an internal lexical/called scope use the same
copied scope carrier. With a receiver and null lexical scope, Zend supplies the
dummy `Closure` scope. These objects retain their captures, static cells and bound
receiver without retaining the prior Closure. Created children authenticate their
immediate parent function and copied scope; bound copies authenticate their
binding site and identical source template. User-class permission still follows
its real lexical origin. `self`/`static` names, parent errors and anonymous
`new self` defaults preserve the internal scope.

Literal named-static `Closure::bind(...)` creates an API Closure and dynamic
invocation uses the existing binding handler. Explicit null scope with a
`stdClass` receiver produces the copied internal scope described above. The
creating CONFIG authenticates the selected live BIND API. Dynamic calls now pin
that API with the same owned selection tag as CURRENT; direct static-API
authority remains borrowed. Historical receipt
source forms admit dynamic and literal `__invoke` calls while preserving the
copied source/function/scope/receiver checks. Actual null writes retire the API
and original body, then the bound Closure, then the returned receiver separately.
Two native originals, one direct and one repaired captured comparison, and 289
state premises (269 genuine/derived plus 20 controls) retain their original tested
cut, where the main API cell stays live across arguments. Original Unsupported
and the first interpreter failure retain zero credit.

A third-argument null-scope helper can clear the selected BIND API cell. The
captured call keeps it live through the saved CONFIG_SEND; the direct static
control releases it before the helper's weak read. Consuming the binding CONFIG
then releases the API and creates the same copied receipt. Two native originals,
one direct and one repaired captured comparison, and 413 state premises
(375 genuine/derived plus 38 controls) pass. The state cut includes a narrow
recorded bridge for the old CONFIG tag/roots; the original 289 cut is unchanged.
The initial global-table fixture failure retains zero credit.

Simple class-CV `$class::bind(...)` capture resolves `Closure` before minting the
API. Changing that class cell to `stdClass` afterward preserves the selected BIND
call and its existing copied receipt. Two native originals, one literal control,
one repaired computed source and 161 state premises (148 genuine/derived plus
13 controls) pass. The state test distinguishes the raw class operand, prepared
class string and genuine mint with registered handles. The initial elaboration
and raw-mint fixture failures retain zero credit; wider class expressions remain
required.

Literal-class `Closure::$method(...)` capture resolves a simple method CV to bind
bytes, including the authentic interned string carrier. A later write of
`getCurrent` to that cell preserves the selected BIND API and its existing owned
CONFIG and copied binding receipt. Native2/literal1 at 836b and computed source1
and 169 state premises at 48fee/375 pass (150 genuine/derived plus 19 controls).
The state test separates raw VARIABLE, resolved carrier and genuine handle-normalized
mint; a byte-equivalent plain string also passes. Original Unsupported, first
repair Unsupported and the diagnostic retain zero credit.

Combined simple class/member-CV `$class::$method(...)` BIND capture authenticates
the internal Closure call task without a user-class descriptor. The real class
evaluation precedes member resolution and minting; later writes to `stdClass` and
`getCurrent` preserve the selected API. Two native originals, one literal control,
one repaired computed source and 237 state premises (209 genuine/derived plus
28 controls) pass. Certificate checks remain separate from method-byte admission;
existing mint/tag/handler/receipt rules are unchanged. Original Unsupported and
the initial EVAL-tail fixture elaboration failure retain zero credit. Wider class
and member expressions remain required.

Named-class computed-member BIND capture now accepts the existing evaluated
member source/task authority. The concat witness `Closure::{$left . $right}(...)`
reaches authentic interned operands and a request string before minting; later
separate writes to `get` and `Current` preserve the selected API and receipt.
Native2/literal1 at 64be and computed source1/state233 at 4ec/375 pass
(214 genuine/derived plus 19 controls). The state cut distinguishes the derived
string helper from the genuine normalized concat step and shares admission
controls once. Original Unsupported and the source-name fixture-origin failure
retain zero credit; checked packets are reused without old lifetime renewal.
Wider evaluation contexts remain required.

Evaluated nonnamed class BIND capture with a literal member now uses existing
class evaluation/canonicalization and source/task/line/FCC authority. The witness
`($prefix . $suffix)::bind(...)` produces a genuine request string, then prepares
canonical Closure and mints in one wrapped source step; later separate writes
to `std` and `Class` preserve the API. Native2/literal1 at a303 and computed
source1/state236 at 43fd/375 pass (216 genuine/derived plus 20 controls). Raw class
carrier and derived preparation remain distinct; CONFIG/receipt/ownership are
unchanged. Wider evaluation evidence remains open.

Nonnamed evaluated class and computed member BIND captures now use the same
internal Closure task certificate, preserving canonical saved class and compiled
member-child authority without a user-class descriptor. The both-concat witness
`($prefix . $suffix)::{$left . $right}(...)` produces two request strings at
distinct actual indexes, prepares Closure before member evaluation, then mints
before four separate writes to `std`/`Class` and `get`/`Current`. Native2/literal1
at e360 and computed source1/state347 at 53a19b/375 pass (322 genuine/derived
plus 25 controls). Named arms and existing mint/tag/handler/receipt/ownership
remain unchanged; shared certificate and member-byte controls, zero-budget and
identical full continuation pass. General admission is distinct from this
concatenation evidence; wider evaluation and argument-retirement routes stay open.

Module264 adds the admitted REAL static/internal warnings and `$this`-sensitive
unbinding through the same genuine handler continuation; the
[ordinary binding contract](CLOSURE-BINDING.md) records validation order, compiled
flag authority and copied storage. Wider binding API captures and argument
retirement beyond the BIND scopes above, object/computed current
captures, wider argument-retirement routes, temporary REAL `Closure::call` current-object
escape and further internally scoped keyword consumers remain required.
Temporary-call behavior stays separate.

The temporary-current issue is independent of paused return verification. At the
8.5.10 pin, non-generator `Closure::call` zeroes a temporary object's standard
header and gives it `GC_NULL` (`zend_closures.c:176–179`); `getCurrent` checks only
the copied function flags and returns that header with an added reference
(`421–435`). `call` frees it unconditionally (`214`), so the added reference does
not make an escaping value a valid Closure. This is a source-only finding; no
temporary-engine probe or patch was run. The proposed safe domain is a borrowed
identity for repeated current reads and strict identity comparisons inside the
active call, discarded before exit. Object operations and escaping values need
an explicit lifetime or intentional-divergence decision before core completion;
the current spec keeps this lane `Unsupported`.

Rules follow vendored `zend_closures.c` (`Closure::getCurrent`, `do_closure_bind`,
`zend_valid_closure_binding`, `zend_create_closure_ex`, `zend_closure_from_frame`,
`zend_closure_compare`) and static-method receiver ownership in
`zend_vm_def.h`. Source and paused fixtures retain distinct tested cutoffs in the
[current-binding ledger](../../coverage/semantics/closure-current-binding-review.json).
