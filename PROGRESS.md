# Core PHP semantics progress

This project targets PHP 8.5.10 CLI, NTS, 64-bit. Executable core semantics and
source-driven differential validation are active; complete PHP core, the later
Rocq interaction-tree model and BOLA/CRIS verification remain unfinished.
[PLAN](PLAN.md) records settled scope; the [feature inventory](coverage/semantics/features.json)
and current family documents identify implemented routes and remaining obligations.

## Current checkpoint

Named and positional reference-send Notice arrays now admit DIRECT quiet
`stdClass` leaves. Copying a DIRECT object entry adds a physical object edge
while preserving object identity and shared property writes. Source replacement cannot redirect
the pending old table. Supplied throw cancellation retires the last private
cell, table and object before catch, including WeakReference notification.

Every array ancestor, including the root, must be allocated, mutable, nonpool
and free of literal retained/debt records or native units on this new route.
Objects retain the root-stdClass bound: a complete canonical record of DIRECT
scalar/non-NUL interned fields with non-NUL startup names, no cached table,
owning children, freeing/called state, native unit or WeakMap key, and inactive
GC ACTIVE/PLAN/WORKER. ALIAS-object entries, USER instances, wider fields and
callback lifetimes remain partial. Earlier scalar/array arms, root history and
generic ownership/GC receipts remain literal.

Three source originals agree at their recorded 490-module SL cuts. Completed
AL cuts 83/36/105 execute 224 premises: 138 unique source-reached premises
(including six heap bindings), 85 derived and one repeated initial binding.
The old Unsupported baseline, original 196 timeout, first header-fixture failure
and finite 64-step diagnostic retain zero credit. The
[DIRECT-object review](coverage/semantics/direct-object-leaf-reference-notice-review.json)
keeps actual COW, last-owner cleanup, header refusals and budgets separate.
Actual joined main `0291c2407` with 492 modules passes independently with zero
source credit.

Root quiet stdClass values/references retain their
[earlier cuts](coverage/semantics/stdclass-reference-notice-review.json).
Finite DIRECT/ALIAS array graphs retain singleton unwrapping, shared-cell payload
identity, nested COW and last-owner cleanup. Their original cuts remain in the
[array-cell review](coverage/semantics/alias-child-reference-notice-review.json),
[DIRECT-graph](coverage/semantics/direct-child-reference-notice-review.json),
[flat-array](coverage/semantics/array-reference-notice-review.json) and
[scalar-reference](coverage/semantics/alias-array-reference-notice-review.json)
ledgers. New object-leaf ancestry checks do not narrow the old root-array routes.

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
Malformed live arrays return false before syntax-only lookup. Admitted name
output accepts admitted literal/string-variable inputs and initialized scalar
CVs, preserving spelling and the captured reference cell. An input-SEND receipt
keeps a variable input fixed through later callbacks, output aliases and nested
queries; argument throws skip the query's assignments.
[Saved-input review](coverage/semantics/enum-is-callable-saved-input-review.json).
Named nonunpack output separates source SEND order from signature slots,
including early `callable_name` and omitted `syntax_only`. A nonowning acquisition
certificate preserves the sent cell through CV unset/rebinding. Real SENT/output
owners, genuine input history and clear/destructor/name commitment remain intact;
nested queries, argument/output throws and named errors keep their order. Separate
rebound-array source/value proofs, packs and wider output places remain partial.
[Named-output](coverage/semantics/enum-is-callable-named-output-review.json) and
[reference-history](coverage/semantics/enum-is-callable-named-output-reference-history-review.json)
reviews retain the two cuts.
`syntax_only` now receives weak scalars or enforces caller strictness before
query/output work. Weak null deprecation retains actual operands and the acquired
cell through handler reentry/throw; missing value keeps priority and name commit
waits for successful reception. Separate input/output and nonunpack bounds stay
explicit. Three source agreements, 454 independent checks and joined SL452 pass
at their recorded cuts. [Boolean reception](coverage/semantics/enum-is-callable-bool-reception-review.json).
Ordinary function-string queries now distinguish actual USER/builtin availability
from body support and known absence. Lookup follows flag reception; captured
bytes and the real output cell survive null-handler rebinding. A nonowning output
publication prefix freezes the result through destructor publication. Wider
domains remain partial. One source agreement, 313 independent checks and joined
SL453 pass at their recorded cuts. [Function strings](coverage/semantics/is-callable-function-string-review.json).
Quiet primitives and existing known Closure objects now share the query/output
path, preserving exact scalar/function names without invoking bodies. Actual
SENT retains Closure/receiver ownership across source removal and same-CV writes;
saved query-time precision preserves float names through output callbacks.
Three source agreements and 161 independent ownership/budget checks pass at their
recorded cuts; current joined SL454 passes. Producer and wider Closure/output
domains remain partial. [Review](coverage/semantics/is-callable-primitive-closure-review.json).
Existing ordinary USER instances and `stdClass` now classify without entering
`__invoke` or `__toString`. Published public method presence and proved table
absence stay separate from unresolved metadata; inherited names use the runtime
class. Real SENT and acquired-cell owners retain same-CV/removal history through
normal and throwing output effects. Two source agreements and 179 independent
ownership/budget checks pass at their recorded cuts. [Review](coverage/semantics/is-callable-instance-review.json).
Ordinary USER method strings and class/object arrays now share public concrete
method/known-absence queries without body entry. Structural syntax-only admission
stays separate from lookup; exact names and selected booleans survive member-cell
mutation, receiver retirement and normal/throwing cleanup using borrowed history
and the existing result carrier. Three source agreements and 227 independent
history/ownership/budget checks pass at recorded cuts. [Review](coverage/semantics/is-callable-user-method-review.json).
Qualified USER array queries now use staged effectful API resolution, retaining
the resolved boolean independently of the later name snapshot. Lookup-handler
throw still commits NAME and cancels result assignment; reception-handler throw
keeps the old NAME. Real SOURCE/cell/exception owners preserve reentry, direct
receiver drain and namespaced nested queries. Seven source agreements and 259
independent history/ownership/budget checks pass at recorded cuts. [Review](coverage/semantics/is-callable-api-resolution-review.json).
Untyped receiver references now keep qualified public method resolution tied to
the original live USER object while a warning changes the current member. A
completed receipt survives later holder removal/receiver retirement during output
cleanup. Receiver loss during the warning reaches explicit Unsupported through
coherent callback/exception transport; no historical lookup or new owner is granted.
One three-mode source agreement and 98 independent loss/ownership/budget checks
pass at recorded private 461-module cuts. [Review](coverage/semantics/is-callable-alias-api-review.json).
Raw keyword callable strings and bare-method arrays now resolve self/parent/static
from the actual ordinary USER caller frame. Lexical versus called class and real
This ownership preserve public availability; known invalid scope is false without
a lookup deprecation. Existing phase-aware receipts retain exact names and lookup-throw
commitment through reentry and output cleanup. Five source agreements and 166
independent owner/phase/budget checks pass at recorded private 456-module cuts.
[Review](coverage/semantics/is-callable-keyword-context-review.json).
Last-owner ordinary Closure name outputs now use the existing NULL-clear, ordered
capture/static/This drain and NAME/result continuation. The real captured OLD
identity remains valid after retirement without rechecking drained cells or
adding a root; fresh Closure queries still require liveness. Normal, rebind,
throw, retained/same-CV and shared-edge controls use existing producers/entries.
Opaque/internal graphs and unproved cycles stay explicit. Three source agreements
and 247 independent owner/history/budget checks pass at their private 457-module
cuts. [Review](coverage/semantics/is-callable-closure-output-review.json).
Ordinary USER/stdClass name outputs now admit live acyclic owning property graphs
with plain untyped slots, through unique and retained/same-CV recipients. Existing
post-destructor storage handles actual unset/replacement, dynamic-before-declared
order, resurrection and pending throw without frozen child lists or new owners.
Historical std identity remains borrowed after retirement; source/cell/NAME/BOOL
continuations stay unchanged. Four source agreements and 426 independent
owner/history/budget checks pass at recorded private 458-module cuts.
[Review](coverage/semantics/is-callable-property-output-review.json).
Ordinary array name outputs now record the actual pre-clear heap identity through
ordered child cleanup and saved-name commitment, including rebinding/throw,
retained copies and same-CV SENT. The legacy rebound witness stays distinct;
new array history adds no owner and never rereads retired buckets. Current graph,
producer/nonunpack and opaque/cycle bounds remain. Three source agreements and
95 independent history/budget checks pass at their recorded private 459-module
cuts. [Review](coverage/semantics/is-callable-array-output-review.json).

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
records its bounded source/state cuts.
Fixed namespace fallback now records the actual selected builtin before
arguments. Callback publication cannot replace its target/signature; root and
ordinary named-function cache owners reuse that choice on later invocations,
including after an argument throw. Fresh sites select the newly published local
function. The [fixed-fallback review](coverage/semantics/enum-is-callable-fixed-fallback-review.json)
records source/authority/timing checks; unproved cache
owners remain explicit Unsupported.
The first real-Closure cache slice now records literal births and clone policy
without adding owners. Authenticated unscoped root/named-function factories and
their normal clones share the template cache, including after original retirement.
Unknown first births remain unknown; live stamps must match the actual function
and scope. The [Closure cache review](coverage/semantics/enum-is-callable-closure-cache-review.json)
records the shared slice. Real bind copies and Generator `Closure::call` copies
now preserve known cache policy: shared same-scope copies share, while changed
scope and every private copy receive a fresh private key. Retired source stamps
add no owners. The [private-cache review](coverage/semantics/enum-is-callable-private-cache-review.json)
records the copy hooks. Ordinary user `Closure::call` now records a separate
nonowning temporary-function cache identity. Each scope-changing/private call
gets a fresh key; warmth inside that invocation survives throws and nested calls.
Ordinary function entry clears inherited keys and frame restoration retains the
caller key. The [invocation-cache review](coverage/semantics/enum-is-callable-ordinary-call-cache-review.json)
records the bounded source/context checks. Named/inherited method factories
now authenticate first literal cache births from the exact ordinary creator,
compiled lexical owner and actual post-created scope. An inherited Child receiver
keeps Base lexical cache policy; clone and same-Base bind/call share it, while
Child scope changes are fresh. Unknown first births still block later inference.
The [scoped-birth review](coverage/semantics/enum-is-callable-scoped-cache-review.json)
records the source/lifetime and unknown-first control cuts. Raw ordinary named
and inherited nongenerator methods now authenticate their shared function cache
from the exact descriptor, actual target/function and lexical owner. `is_callable` selection
stays before arguments and survives argument/output throws and receiver retirement;
a fresh method can choose the newly published local function. The
[method-cache review](coverage/semantics/enum-is-callable-method-cache-review.json)
records this slice. Runtime named-function and direct method FCC and plain-function
`Closure::fromCallable` now stamp actual INIT/lookup-proven shared cache policy.
Clones preserve that policy after original retirement; existing-Closure FCC/API
conversions retain the same object and add no birth. The
[shared-capture review](coverage/semantics/enum-is-callable-shared-capture-cache-review.json)
records ownership, aliases and the promoted runtime-method control. Method
`fromCallable` now distinguishes known cold/private births from initialized/shared
source caches. Own-method registration, before-argument INIT, runtime FCC and
authenticated raw CAPI entry supply nonowning facts; missing or uncertain views
stay unknown. Birth-relative history preserves old private captures and fresh
private clones after later source initialization and retirement. The
[method-API cache review](coverage/semantics/enum-is-callable-method-api-cache-review.json)
records the source/owner/budget cuts. Runtime array/string method captures and
clones now authenticate shared cache ownership from actual INIT, immutable raw
function identity and canonical scope. Saved selectors remain coherent after
selected-array/source/receiver retirement, and argument/output throws preserve
namespace fallback warmth. The
[runtime-capture review](coverage/semantics/enum-is-callable-runtime-capture-cache-review.json)
records this bounded slice. Known user fake `bind`/`bindTo` copies and bound clones
now retain actual source cache policy and completed scope. Shared same-scope
copies share; Private and dummy-scope copies receive fresh keys. Immutable source
history survives original source/receiver retirement without new owners, and
copied calls leave raw method initialization facts unchanged. The
[fake-bind cache review](coverage/semantics/enum-is-callable-fake-bind-cache-review.json)
records two exact source agreements and 123 reached conditions with strict446.
Known unbound nongenerator user-method `Closure::call` now authenticates fresh
Private invocation keys from immutable method/source and exact completed scope,
while Shared same-scope calls retain their cache. Source removal during arguments
keeps real API owners until cleanup; history adds no pins or raw initialization.
The [fake-call cache review](coverage/semantics/enum-is-callable-fake-call-cache-review.json)
records one exact source agreement and 77 reached conditions with strict446.
Bound nongenerator user-method temporary calls now follow immutable SOURCE after
ancestor capture/receiver retirement. Completed Base SCOPE, distinct from Child
CALLED, and actual call authority preserve Private freshness or Shared reuse with
exact Base replacements. The
[bound-call cache review](coverage/semantics/enum-is-callable-bound-method-call-cache-review.json)
records one public-method source agreement and 107 reached conditions with
strict446. Known early top-level named user functions bound to the dummy
`Closure` scope now retain their warmed Private source cache while every temporary
call on a plain real nongenerator user Closure receives a fresh key. Argument-time
source removal preserves actual API owners and separate captured-leaf cleanup;
pure history survives retirement without pins. The
[dummy-scope review](coverage/semantics/enum-is-callable-dummy-user-call-cache-review.json)
records one exact source agreement, 120 independent reached conditions and
strict446. Direct top-level `if`-body named functions now authenticate actual
callable publication, a root runtime-declaration receipt and completed main-unit
history before the same dummy-bound temporary calls. The
[conditional-source review](coverage/semantics/enum-is-callable-conditional-user-call-cache-review.json)
records one exact source agreement, 136 independent conditions and strict447.
A named function published by an ordinary early named factory now retains
cache authority after creator-frame retirement. The saved call/source selection
and earlier publication prefix authenticate its real declaration cause without
live-frame inference. The [factory-source review](coverage/semantics/enum-is-callable-factory-user-call-cache-review.json)
records one exact source agreement, 165 independent conditions and strict447.
Public static nongenerator user-method captures from named class constants now
record cold Private versus pre-birth initialized Shared policy at the real
constant-creation hook. Actual initializer/PREFIX/scope and object birth ordinal
preserve old Private births after later raw initialization; Shared history and
clone policy recognize the new producer without metadata roots or raw INIT.
The [constant-method cache review](coverage/semantics/enum-is-callable-constant-method-cache-review.json)
records one distinct source agreement, 140 independent conditions and strict448.
Root globals authenticate that policy from declaration/SITE/PREFIX receipts;
unscoped entered include/eval globals additionally require real source bindings.
Entered units require an available unscoped caller before their first recorded
entry and completed compilation within the birth PREFIX; eval additionally retains
the exact generated filename and excludes constant/default receive contexts.
Pending, nonentered and forged receipts add no authority. Real constant roots
remain separate from nonowning cache history. The
[root](coverage/semantics/enum-is-callable-global-constant-method-cache-review.json),
[include](coverage/semantics/enum-is-callable-included-constant-method-cache-review.json) and
[eval](coverage/semantics/enum-is-callable-eval-constant-method-cache-review.json)
reviews retain their separate original-source, entry/owner/budget and strict
cuts, with include recorder controls counted separately.
Class-scoped include/eval producers authenticate named public nongenerator
methods and their class publication before entry. An inherited
Producer scope stays distinct from Child CALLED and captured Host scope;
producer retirement adds no metadata pin. Completed class/method publication
establishes caller availability even during surrounding compilation, while
the target unit must finish compilation before its constant birth. Eval retains
exact generated filename and empty LOCATION/RECEIVES. The
[scoped-include](coverage/semantics/enum-is-callable-scoped-included-constant-method-cache-review.json) and
[scoped-eval](coverage/semantics/enum-is-callable-scoped-eval-constant-method-cache-review.json)
reviews retain their separate source, entry/history/retirement and strict cuts.
Public static producers now share that exact declaring-scope/publication proof
across both routes with no This or Producer allocation. One mixed source and
shared route-specific entry/history/root-budget evidence are retained in the
[static-producer review](coverage/semantics/enum-is-callable-static-producer-constant-method-cache-review.json).
Other constant/default captures, wider conditional/factory sources, unproved
transformed copies and Generator/Fiber query owners remain partial.
Cleanup exit with an ordinary Throwable already pending, switched Fiber
completion/force-close, other owning rebound arrays, late attached type sources,
wider variable arrays, typed/backed/debt valid-pair cells, unpacked output,
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

I112 owns native Generator API first-class captures through the existing internal
Closure child edge. Literal/computed capture and `fromCallable` preserve a Gen
after its CV retires. Invocation roots the capture and borrows its receiver,
retaining the exact argument/Throwable roots through ordinary reception. Unused
owning returns clear before capture retirement; last-capture forced close runs
Generator finally after capture weak notification. Active call authority requires a real live marker;
saved source history remains nonowning. Its earlier binding and explicit
`__invoke` boundaries are promoted by I114 and I113; the call boundary is
promoted by I115. Six unique originals agree;
the 89/94 ownership/history gate passes with the private 438-module SL manifest.
Earlier compile/fixture failures retain zero credit; wider lifecycle combinations
remain partial.
[I112 review](coverage/semantics/generator-api-capture-review.json).

I113 gives captured native Generator API `__invoke` calls their real outer
signature, argv and capture owner. Pre-handler mapping errors keep no API frame;
inner count/type errors and body traces retain both Generator and Closure frames.
The inner return stays owned through outer argv cleanup. Unused results release
before capture retirement; used uncommitted results survive it when an argument
destructor throws. Five unique originals and one affected I111 computed-call
control agree exactly. The 98/103 bounded ownership/authority gate passes with
the private 440-module SL manifest.
Earlier compile, native-fixture and abrupt mismatches keep zero credit; no core
obligation closes. [I113 review](coverage/semantics/generator-explicit-invoke-review.json).

I114 retargets captured native Generator methods through existing binding-copy
storage. The original keeps its old Generator; each new copy owns only its
replacement, with historical SOURCE metadata preserving permission after the
original retires. Binding warning/type and supplied-throw cleanup reuse the
existing native machinery. Ignored instance `bindTo` copies release before the
original receiver through a dedicated owner continuation, including nullsafe
supplied-finally throws. Six unique originals agree; the sole 132/137 unused-copy
owner/resumption front passes with the private 441-module SL manifest. A generic
fresh/started request predicate
overlap has a separate truth-preserving guard already integrated. Its captured
call boundary is promoted by I115; no core obligation closes.
[I114 review](coverage/semantics/generator-api-binding-review.json).


I115 invokes captured native Generator APIs through `Closure::call` on the frozen
replacement receiver. The original capture and replacement argument retain their
actual owners; the temporary internal function adds no heap Closure or cache
owner. Raw outer argv and copied inner arguments preserve native mapping/trace
phases. The always-used inner return survives replacement/argv cleanup; source
demand controls its release before original capture or through supplied argv
throws. Compiled SEND locations also govern callback/default undefined-CV
warnings independently of API frame lines. Seven unique originals agree; the
sole 123/128 bounded owner/forward/budget front passes full 444 SL. It does not
drive terminal cleanup. Original failures retain zero credit;
Traversable and wider lifecycle combinations remain partial.
[I115 review](coverage/semantics/generator-api-call-review.json).


I116 receives one initialized user-Iterator CV pack at ordinary literal native
Generator APIs. Selected receiver and current snapshots survive callback CV and
property replacement; finite DATA retires before API reception. Mapping errors
precede body entry, and count errors retain native frames. Cancellation preserves
the selected owner even with scalar current/no copied slots. Lookup-only history
survives receiver retirement while active cursors require real membership.
Normal genuine direct SEND pins its receiver through argv cleanup and saves
returned values separately from the retained cache through reentry and
demand-sensitive supplied throws. Six unique originals agree across their recorded cuts; the sole 99/104
owner/budget front passes full 445 SL with raw-versus-public decrement staging.
Captured/temp/borrowed/loop/startpack/from/pending-advance protocols remain
separate. Original failures and the expensive diagnostic timeout retain zero
credit; wider Traversable/lifecycle scope remains partial.
[I116 review](coverage/semantics/generator-method-iterator-pack-review.json).

I117–I120 keep an ordinary named Generator's selected SEND receiver through
body-Throwable argv cleanup. By-reference bodies require their actual328 producer
and live cached HCELL; cell/cache owners stay separate from API argv, and the
storage pin keeps Gen weak-live during cache destruction. Ordinary and nonnull
nullsafe calls retain the frozen method/receiver through argument CV rebinding;
NULL skips both producers. Pending search/Previous chaining preserve original
traces and the unassigned result, with a nonowning nullsafe tail. Five unique
originals and four separate reached owner/cache/receipt/budget fronts pass full446
SL at their recorded cuts. Shared Throwable search rules are unchanged. Active
delegation, pending initialization, reference snapshots without a live cache cell
and wider API/lifecycle modes remain partial.
[Literal review](coverage/semantics/generator-send-body-throw-review.json),
[computed review](coverage/semantics/generator-computed-send-body-throw-review.json),
[nullsafe review](coverage/semantics/generator-nullsafe-send-body-throw-review.json),
[reference-cache review](coverage/semantics/generator-reference-send-body-throw-review.json).

I121 admits an owning VALUE snapshot after the genuine by-reference yield/Notice
path and proves its separate cache, reference and API-argument owners. The actual
handler API SEND/REF carriers now preserve Notice identity and borrowed scope
before invocation. The normal R source component retains its original cut through
that API-only repair; the corrected throwing C source has its own exact cut.
Independent R107/C117 fronts pass 224 reported conditions (214 custom) over446
runtime modules plus the fixture at SL447. The original false packet and failed
diagnostics retain zero credit; wider producers/lifecycle contexts remain partial.
[Snapshot review](coverage/semantics/generator-reference-snapshot-send-body-throw-review.json).

I122 extends direct post-init SEND body-throw cleanup to registered ordinary
public instance-method by-value Generators. The actual factory This retires
during Generator close with the native SEND trace before caller-only argv
destruction; lexical/called classes, receiver/cache/argv owners, supplied Previous
and untouched result remain distinct. An authenticated descriptor view preserves
the physical pending cleanup wrapper and all owners. Static/reference/magic
producers and wider lifecycle modes remain partial.
One frozen original agrees with PHP; the 274-condition NORMAL/closed frontier
and separate 50-condition factory-budget check pass at their recorded cuts over
448 runtime modules plus fixture449. Earlier failures retain zero credit.
The joined main SL449/inventory load also passes with COMP189, ENUM143 and
CLASS200; its shared record adds no source-agreement credit.
[Instance-method review](coverage/semantics/generator-instance-send-body-throw-review.json).

I123 admits ordinary public static by-value Generator methods through exact
descriptor/source static-flag equality in the same physical-method certificate.
An object-CV selector retires before initialization; the actual frame keeps its
distinct lexical/called classes without This or receiver owners. Pending frame,
cache and argv retain the existing direct SEND body-throw cleanup and budget law.
Reference/magic/captured/delegated producers, incoming throw, pending initialization
and held I106 remain separate.
One frozen original agrees with PHP; the actual static-frame/cleanup/budget
front passes 223 conditions across 449 runtime modules plus fixture450. Source
flags, absent receiver ownership and malformed-state refusals are independently
reviewed; the instance case retains its original evidence without replay.
[Static-method review](coverage/semantics/generator-static-send-body-throw-review.json).

I124 admits ordinary public instance/static reference-Generator SEND body throws
through source/signature BYREF agreement and their actual live ordinary Module 328
REFCELL, before storage consumption. CELL/cache/argv and instance This retain
separate owners; the static selector can retire before initialization. Existing
static/source authority remains exact. VALUE/Notice, typed/backed/borrowed cells,
capture/delegation, incoming throw, pending initialization, Closure::call and
held I106 remain separate.
Two frozen originals agree with PHP; paired instance/static fronts pass
393 custom/403 reported conditions across 449 runtime modules plus fixture450,
with actual CELL/cache/argv/This owners, source guards and budget continuation.
[Method-reference review](coverage/semantics/generator-method-reference-send-body-throw-review.json).

I125 connects borrowed Aggregate getIterator/return authority to post-init,
nondelegated literal Generator SEND and zero-argument APIs. An initialized
ordinary user Iterator supplies DATA; selected Gen and copied argv survive
source-CV rebinding, while INPUT/producer history adds no Aggregate owner.
DATA retires before reception, mapping errors precede the API, and count or
ordinary USER-call body TypeErrors keep their actual trace frames. One shared
return-admission hook defaults to true for old consumers and leaves effective
BYREF current explicit Unsupported before promotion on this route.
Generator-returning Aggregates, typed/borrowed current, incoming throw, pending
initialization, capture, delegation, Closure::call, held I106 and wider packs
remain separate.
Four frozen originals agree with PHP; the actual getter/return/copy/cleanup and
public-budget frontier passes 271 conditions across 449 runtime modules plus
fixture450. The constructed BYREF refusal has no native agreement credit.
All selections pass on their first attempt; existing cleanup law is reused.
[Aggregate reception review](coverage/semantics/generator-aggregate-arguments-review.json).

I126 connects existing direct named by-value Generator-CV traversal to literal
native Generator SEND and zero-argument reception, with distinct initialized
nondelegated source/selected Generators. The actual CONFIG marker supplies the
receiver root; borrowed source rewind/next keeps real DATA/cache ownership.
Quiet source retirement and retained owning caches keep their existing limits,
including the unchanged pending-destructor value guard.
Pending mapping cleanup transfers selected Gen/copied argv into CONFIG_INVOKE
before releasing DATA; ordinary throw cleanup then retires that real cursor.
Old INI/numeric owner checks and source/value/storage policy remain unchanged.
BYREF/typed/borrowed cells, temporary/Aggregate sources, incoming throw, pending
initialization, capture/delegation, Closure::call and I106 remain held.
Frozen native selections cover scalar normal, quiet retained cache/body TypeError,
mapping and count. Four maintained source agreements retain separate scalar and
affected/unrun cuts; the destructor-bearing payload refusal and failed selection
have zero credit. Separate scalar/quiet-cache/mapping fronts pass 430 conditions
(208/134/88) across 450 runtime modules plus fixture451 per case. Real borrowed
source, cache/argv roots, direct quiet transfers and public budgets are checked;
initial front/diagnostic fixture failures retain zero credit. The actual current
451-module joined load/inventory also pass without renewing source cuts.
[Generator-source review](coverage/semantics/generator-source-arguments-review.json).

I127 connects existing computed/nullsafe selected-method authority to admitted
single-CV Iterator, Aggregate-to-Iterator and initialized named by-value
Generator packs. Shared source/selection proof keeps method/receiver identity
fixed through callback rebinding while actual CONFIG roots own selected Gen
and argv; NULL skips method and pack reads. New paths stay post-init,
nondelegated/by-value and exclude captured/temporary selectors and held modes.
Callback reentry and wider destructor histories stay outside this join.
Producer/value/owner policies and old ordinary literal admission remain intact;
new direct Iterator current is by-value. Module 447 reuses existing argument domains
and 280/450 receipt minting/liveness. A defaulted 420 cancellation dispatch keeps
the actual native receiver/prefix in CONFIG_INVOKE while key/current/DATA retire,
including the equivalent admitted literal root shape; old INI/value policy stays.
Native nullsafe CONFIG descriptors advance tail validation to the outer callsite
while physical origins/tasks/owners remain unchanged. Six maintained source
contrasts agree at separate first-four and affected/unrun cuts. Independent
623 conditions pass as retained Iterator169 plus affected/unrun
Aggregate190/Generator160/mapping104 at separate cuts. Public descriptors,
physical selected/cursor/argv roots and 0/1 budgets pass. The actual current
453-module joined load/inventory also pass. Pre-semantic failures, the genuine
mapping cleanup-order mismatch, failed frontier selections and the bounded
descriptor diagnostic retain zero credit.
[Selected Traversable review](coverage/semantics/generator-computed-traversable-arguments-review.json).

I128 removes the artificial two-item prefix limit for the existing named
by-value Generator CV source at authenticated native Generator consumers.
The shared consumer policy leaves old INI bounds exact; item/source/value,
real DATA/receiver/copied-prefix owners and borrowed-resume laws remain intact.
One-CV syntax and held producer/value/lifecycle modes do not widen. Four frozen
native contrasts pass: scalar fourth-item count, source throw after owning
prefix3, fourth-key mapping failure and distinct owning prefix3/cache/trace
retirement. Four exact source comparisons and 363 independent conditions also
pass first attempt, covering actual third/fourth appends, INI controls,
borrowed/pending/count/cache roots and public 0/1 budgets. The actual current
453-module joined load/inventory also pass. Wider core remains partial.
[Finite-prefix review](coverage/semantics/generator-finite-prefix-arguments-review.json).

I129 composes ordinary positional arguments with one terminal simple-CV
Traversable at admitted native Generator consumers. Real argument-index and
ordinary-SENT replay preserve frozen earlier values through callbacks; terminal
DATA/finish/pending paths use their actual source position. Generator roots
count normalized earlier/new argv once and preserve old root order. INI,
prefix-free and producer/value/lifetime bounds remain intact; ARRAY prefixes,
multiple Traversables and held modes do not widen. Native4 plus one focused
scalar witness pass. The first owning-prefix/empty Iterator SEND source agrees
at its authentic cut; remaining Aggregate/Gen/count/scalar comparisons also pass.
Five source agreements retain first/remainder cuts without replay. Independent
566 owner/index/budget conditions pass as retained401 plus corrected/unrun165;
the raw-count fixture phase error and failed containing selection retain zero credit.
The actual current 454-module joined load/inventory also pass, without source/state replay.
[Positional-prefix review](coverage/semantics/generator-prefixed-traversable-arguments-review.json).

I130 joins Fiber transfer to the existing named by-value Generator-CV argument
source during authentic borrowed NEXT. One local saved-frame proof reuses
CONFIG/source authority and existing VM ownership/unique-resumer checks, without
new roots or PARKED mutation. DATA/selected/prior+copied argv roots stay distinct
from the source VALUE cache. Unfinished copied native calls now release argv
before receiver in actual pre-API throw context. Three native-first sources
agree at separate retained/corrected cuts; independent N169 plus focused T138
compose307 conditions without a full307 rerun. The original ordering mismatch,
superseded T prototypes and diagnostic timeouts retain zero credit. Current456
joined load/inventory pass with a scoped195/196/GC65 compatibility bridge.
Source/value/CV/last-DATA and held-mode bounds remain. Existing helper,
Fiber-Throwable and guarded-close paths have common-law review, without new
direct source credit. Early noncopied cursor retirement has its separate I131
scope below.
[Borrowed-source Fiber review](coverage/semantics/generator-borrowed-fiber-arguments-review.json).

I131 extends argv-before-receiver retirement to actual early CONFIG_SEND/PREP
at admitted native Generator ordinary-prefix/terminal-CV calls. Exact partial
source replay preserves frozen SENT without reading a future pack. A throwing
operational producer now retains its real cursor until Search transfers prior
argv then receiver into the existing eager queue. No DATA is acquired and no
source/value/root/schema or held mode changes. Two native-first originals and
two source comparisons agree: scalar pack TypeError precedes zero-arg API count;
a later no-arg argument throw skips an undefined local pack. Both preserve
original trace/Previous/sentinel and release prior argv before Gen finally.
Independent PREP97+SEND80=177 actual source/retention/owner/queue/budget checks
pass first attempt. Original pre-retention mismatch and diagnostics retain zero
credit. Actual current457 joined load/inventory pass without source/front replay.
Other task/array-ledger/producer/default policies stay unchanged.
[Early-cursor review](coverage/semantics/generator-early-cursor-cleanup-review.json).

I132 replaces the outside-callee-owner assumption during native Generator
Aggregate acquisition with proof of the actual PREP/CONFIG_AGGREGATE marker.
The borrowed Aggregate retains its real owner; ordinary Iterator return still
transfers RESULT into DATA once. Native cancellation transfers prior SENT before
receiver in both operational and ordinary contexts, through the existing real
Search queue. INI-only Generator returns and producer/value/frame policies stay
unchanged. Native3 and source3 pass first attempt: normal getter rebinding/return,
supplied getter exception in a named Fiber, and return-type failure outside one.
Independent N99/E81/T78=258 owner/promotion/cancellation/public-budget checks
pass. Existing pending-cleanup activation validates queued jobs after ordinary
entry; one fixture type-check stop retains zero credit. Actual current459 joined
interface load/inventory pass; no source/front replay.
[Aggregate acquisition review](coverage/semantics/generator-aggregate-acquisition-review.json).

I133 authenticates saved direct-Iterator cursor history while its callback runs
the already selected initialized Gen via `next`/`send`. One real resumer proof
and a finite ordinary named-helper fold authorize only the saved callback/cursor
phase view; runtime state, complete graph and global owner checks stay real.
Entry PAUSED/CLOSED and existing selection/source/value/held policies are exact.
Two source agreements pass at separate retained-N/corrected-E cuts; independent
N120/E121=241 ownership/phase/graph/budget checks pass. The elaboration stop and count-only observer
Unsupported retain zero credit. Actual current461 shared-interface load/inventory
pass without source/front or older replay.
[Iterator reentry review](coverage/semantics/generator-iterator-reentry-review.json).

I134 connects two actual running Generators during native argument collection:
borrowed source NEXT invokes selected next/send. A default-old423 operation-frame
scope and local447 dual-pair/source proof authorize only saved target phase
history; both physical IDs/roots and global pair checks remain real. Source
CV/cache/DATA, ordinary-prefix/value and final cleanup bounds are unchanged.
Native2/source2 and independent N135/E139=274 phase/pair/ownership/budget checks
pass first attempt. The current load of 461 modules and inventory pass at the
accepted main cut; private source/front cuts remain separate.
No I133 or older campaign is replayed; Fiber transfer rules and all holds remain.
[Source reentry review](coverage/semantics/generator-source-reentry-review.json).

I135 adds the remaining borrowed Aggregate-getter reentry endpoint: selected
next/send may run before normal Iterator DATA or getter failure. The existing
real singleton/frame proof and phase-only view are reused; the Aggregate's real
allocation/positive owner remains mandatory. Literal-prefix0 and computed/prefix
calls share this law. Native2/source2 and independent N138/E93=231
phase/ownership/return/budget checks pass first attempt. The current integration
uses a narrow absence/default bridge without a new load or semantic replay. No older replay, new root, source/value/INI-Gen
return or Fiber/held-mode expansion is introduced.
[Aggregate reentry review](coverage/semantics/generator-aggregate-reentry-review.json).

I136 adds source-authenticated public USER method helper links to the existing
singleton Fiber and Iterator/Aggregate/source-Generator reentry walks. Helpers
return by value; ordinary parameter/source/storage policies are unchanged.
Immutable simple-CV instance or receiver-free scoped-static callsites preserve
real method receiver roots across rebinding and VM movement. A real validation
cycle is cut by checking the cursor head before the body proof; necessary saved-ID
checks run before deeper helper proofs without changing accepted endpoints.
Two maintained native/model agreements compose authentic N909 and lean-Ef9 cuts.
One complete focused packet passes 161 conditions (parked VM 86, dual reentry 75)
at private462 plus fixture463. Accepted source cuts retain later return/catch and
retirement observations; repeated validators and later seeks are omitted.
Original timeouts, fixture stops and diagnostics retain zero credit, including
the earlier whole237 timeout. The named-function fallback and all source/value/
held domains remain. Other This/object-static/receiver-bearing scoped helper
sources gain no new proof here; no older campaign is replayed. One actual current
466-module shared-interface load passes at `7715a03b0` with inventory 169/306;
that load adds no source-agreement credit.
[Method-helper review](coverage/semantics/generator-method-helper-reentry-review.json).

I137 closes receiver-free object-form static USER helper links in the existing
Generator reentry and Fiber walks. One disjoint late447 classifier arm reuses
physical public/static/by-value-return method and immutable simple-CV source
proofs; no selector is reread or retained. Native2 distinguishes preargument
selector death, inherited lexical/called-class identity through normal parking,
and static helper links before/inside borrowed-source reentry with a Given throw.
Both exact source comparisons and the independent180 focused conditions pass
first attempt at private467 plus fixture468. Actual preclear selector1→parked/
dual0, cached classes, source/pairs/phase graph and public0/1 cuts are checked.
The three executable/test commits are accepted at `37e293f57` without another
load or semantic replay. All old helper guards, real roots, source/value and
parked-operation bounds remain.
[Object-static helper review](coverage/semantics/generator-object-static-helper-review.json).

I138 admits raw uncaptured static Closure helper contexts in the existing four
Generator reentry/Fiber walks. Matching TARGET/FUNCTION/INSTANCE and physical
empty, unbound template source preserve the real call-instance owner after CV
clearing. Both allocated static cells and latent function-static code are
excluded; all current/saved/source/tail/ID/transfer guards stay unchanged.
Native2/source2 and complete independent164 actual INSTANCE/parked-VM/dual-source/
budget conditions pass first attempt at private468 plus fixture469. The exact
executable/test packet is accepted at `5ecf29066` with a narrow actual-current
absence/default bridge. An already-READY shared469-module load passes at that
cut separately, with zero source credit and no standalone I138 replay. No capture/
binding/arrow/fake/Closure::call or other held mode is reopened.
[Raw Closure helper review](coverage/semantics/generator-raw-closure-helper-review.json).

I139 authenticates a parked Iterator cursor while an external ordinary resumer
runs its selected Generator, including reactivation from an admitted actor Fiber.
Snapshot/full-cursor authority supplies a descriptor phase view; old physical
entry, real VM roots, transfer and global-ID checks remain intact. Actual consumed
cursor and eager-operation continuations retain existing cancellation rules.
Source agreement composes unchanged N at `b34665291` with actor-Fiber E at
`dbf6f3cdc`; original main-hosted E Unsupported and two elaboration stops retain
zero credit. Retained N76 at `e92fedae7` plus affected E97 at `cb6037386` compose
173 conditions at private469 plus fixture470, with no full current rerun. A
one-premise saved-ID fallback guard removes a duplicate singleton derivation,
retaining every previously defined result. Earlier failed selections retain zero credit.
The exact packet is accepted at `79ce60a0e`; its actual shared472-module load
passes separately with zero source credit. Private469/fixture470 cuts stay exact.
[Parked-cursor review](coverage/semantics/generator-parked-cursor-reentry-review.json).



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

GC61 corrects generic TEMP receipt progress: a replacement consumes the old
receipt only when its new queue is exactly the old head's tail. Storage cleanup
can retain the next queued TEMP without advancing either single or ordered-list
receipt metadata. Actual pop, storage and decrement behavior use existing rules;
no source/array whitelist, schema, phase or collector policy changes.
Two supported originals and the motivating ATTR63 expression agree with native;
one 137-condition (132 authored) strict450 front passes. The original failure
and diagnostic/control preparations remain external with zero new credit.
[TEMP-consumption review](coverage/semantics/gc-temp-release-consumption-review.json).

GC68 separates positive unmatched native-RC units from physical heap ownership.
A normal root function-string query can replace the exact sent NAME cell's
eligible callback-written object with its saved string while retaining
one native count and scheduling no decrement. Weak-reference recovery, genuine
temporary release, GC trial protection/snapshots, pruning and store shutdown use
the effective count; actual retirement removes the units. Empty excess preserves
old behavior, and wider raw overwrites remain explicit. The retained original
matches native weak-live/collection-zero/shutdown order; the focused independent
front passes 208 reported / 203 authored conditions at its private 461-module cut.
The authentic current 462-module load passes separately.
[Native-count review](coverage/semantics/gc-native-rc-excess-review.json).
Finite public untyped DIRECT scalar/fieldless-Child slots now share this query
admission. The Parent's unit protects its actual descendant closure without
crediting Children or copying their repeated edges. Store callbacks follow
allocation order while the Parent and its fields remain live, separating this
case from standard last-owner slot cleanup. Generic count, release, GC and
shutdown rules are unchanged.
Two allocation-order originals and the focused 213-condition front (208 authored)
pass at exact private462 cuts; current acceptance uses a separate static bridge.
[Property-graph review](coverage/semantics/gc-native-rc-property-graph-review.json).
Reference-copy decisions now keep those native-retained Parent edges in their
pruned ownership views. A property reference and array entry remain two real
HCELL owners, so COW and unpack preserve the alias and writes reach both original
storage places. Only the two read-only prune images change; physical cell counts,
singleton/source-self rules, COW thresholds and all producers remain unchanged.
Two exact originals and the focused 154-condition front (149 authored) pass at
their recorded 463-module cuts; the original wrong normal result stays zero.
[Reference-copy review](coverage/semantics/gc-hidden-reference-copy-review.json).
Raw NAME commitment also admits flat mutable DIRECT arrays with an actual
distinct retained root CV, existing quiet scalars and fieldless Children. Losing
the sent-cell edge reduces physical owners from two to one while the native count
stays two through an old-header unit. Separation creates a new header
with zero excess and real copied Child edges; the hidden original survives visible
replacement/removal and collection. An exact source/image receipt keeps the
old-header `GC_TRY_DELREF` out of candidate visits while ordinary item decrements
remain intact. Old object/abrupt paths and physical owner graphs remain unchanged.
Two originals retain their private 463-module cuts through the reviewed observation
bridge; the final 322-condition front (317 authored) and actual joined SL465 load pass.
[Array-COW review](coverage/semantics/gc-array-native-cow-review.json).
The existing retained DIRECT-array domain also supports ordinary item-reference
acquisition. Native-count separation leaves the old DIRECT row/unit unchanged;
the new ALIAS owns a fresh CELL once, with a NULL acquisition result. The exact
ACQUIRE_ARRAY receipt reuses old-header TEMP consumption without a GC visit.
Ordinary REF_NAME binding, later writes and visible-array cleanup stay unchanged.
Two originals retain their genuine pre-edit/patched console cuts through the
observation bridge. The 306-condition front (301 authored) and actual joined
SL466 load pass at their separate recorded revisions.
[Item-reference review](coverage/semantics/gc-item-reference-cow-review.json).
Quiet scalar ALIAS leaves now share the retained-array raw-NAME fold. Genuine
untyped reference metadata excludes backing, coercion, literal-debt and released
history; CELL excess remains zero. Existing duplication unwraps physical
singleton cells and preserves shared aliases. A disjoint clone/write image
accounts for scalar STORE-through without replacing the shared entry binding;
old DIRECT and generic count/reference rules remain unchanged.
Two exact originals and 321 independent conditions (311 authored) pass at their
recorded private 466-module cuts. The shared fixture syntax stop retains zero;
its corrected affected facet passes without replaying the unchanged singleton.
The separate current combined SL467 load passes with zero source credit.
[Scalar-reference review](coverage/semantics/gc-scalar-alias-cow-review.json).
GC74 accounts for the existing-domain DIRECT target copied then overwritten
during retained-array COW. Exact source/clone/STORE images supply its transient
nonlast decrement to existing GC buffering; the old-header TEMP receipt,
physical ownership and ordinary same-table release rules remain unchanged.
The focused 230-condition front (225 authored) passes at private SL467. Two
originals retain console/status matches with zero complete-behavior credit:
the author comparison precedes the fix, and the peer retains a separate raw
borrowed-root header-buffer mismatch at that recorded cut.
The separate current combined SL468 load passes with zero source credit.
[Copied-target review](coverage/semantics/gc-copied-target-decrement-review.json).
Current array/reference coverage distinguishes borrowed lookup from real
reference/header loss. Source-authenticated ROOT/CV lookup suppresses only its
borrowed visit, while variable self-assignment, ELEMENT writes and genuine Child
VALUE decrements remain. An unused AssignRef's modeled result protector uses TEMP
at every admitted positive owner count: one edge is consumed, leaving at least
the real array and destination CV. Existing-CV rebinding to the same array CELL
keeps its genuine binding-time visit, separate from unused-result disposal;
real reference-CV removal retains ordinary VALUE checks. The
[borrowed-root](coverage/semantics/gc-borrowed-array-writeback-review.json) and
[unused-result](coverage/semantics/gc-unused-reference-result-review.json) reviews
retain historical labels; the
[owner-count review](coverage/semantics/gc-unused-reference-owner-count-review.json)
records the current law and two superseded count-only control updates.

Retained unit1 arrays support singleton/shared owning ALIA, real nonlast payload
loss and last-Child callbacks with actual saved-root authority. Copied DIRECT
siblings that hide a payload drop contribute one inferred decrement. Header-first
TEMP remains separate from real item VALUE; positive remaining header owners use
native progress and exact one-pop suffixes. COW deletion checks only its copied
selected item and derives ROOT independently of scratch CELL. Generic counts,
physical owners and task types stay unchanged. Scope and separate validation cuts
remain in the [owning-alias](coverage/semantics/gc-owning-alias-cow-review.json),
[header-owner](coverage/semantics/gc-shared-header-owner-review.json) and
[deletion](coverage/semantics/gc-array-unset-copy-review.json) reviews.

Ordinary zero-unit DIRECT and quiet-scalar ALIA arrays use that nonvisiting
header law only with a distinct surviving compiled-CV old view and explicit
source/data/history/HELD/GC bounds. Singleton wrappers unwrap in the new table;
shared/repeated CELLs preserve real entry multiplicity and scalar write-through.
A separate zero-only image and pre-domain guard reject owning-to-quiet receipt
escape. Later genuine last-view ARRAY/CELL cleanup retires storage and can invoke
Child D before shutdown. Quiet-ALIA item-reference acquisition now separates
fresh versus reused CELL images: singleton copying unwraps before one new CELL
is allocated, while shared copying reuses its marked CELL without STORE append
or REFCELLS change. Acquisition borrows CELL with NULL; later reference-CV
binding/removal keeps its existing result and VALUE laws. Owning ALIA acquisition,
zero-unit owning callbacks and held contexts retain their separate bounds.
See [DIRECT COW](coverage/semantics/gc-ordinary-direct-cow-review.json),
[quiet-ALIA writes](coverage/semantics/gc-ordinary-quiet-alias-review.json) and
[quiet acquisition](coverage/semantics/gc-ordinary-alias-reference-review.json).
Without objects, references or active destructor machinery, finite DIRECT scalar
array graphs use the quiet observer. Replacing an outer item checks its copied
selected table; a scalar write through two integer dimensions separates both
headers without visiting either. Repeated sharing keeps real child-edge multiplicity;
ordinary later deletion and last-view retirement retain their decrements. The
[root-copy](coverage/semantics/gc-quiet-scalar-array-dag-review.json) and
[nested-copy](coverage/semantics/gc-nested-scalar-array-cow-review.json) reviews
retain separate cuts. The latest nested cut has two first complete originals and
whole 221/211 checks at private 484; accepted 71f/485 uses a static composition note.
The preceding 257f/485 load has source credit zero and predates that fix. Earlier
source/state, partial/failure and load labels remain in their linked ledgers;
historical GC76 198/193 is not rerun or promoted.

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
independent44) pass at recorded cuts. At the GC37 cut, occupied replacement was
Unsupported; that historical control retains zero agreement. Wider Value
layouts, extra child owners,
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

Safe scalars, finite methodless objects and finite direct-array graphs share
WeakMap payload validation across insertion,
ordinary leaf-Key append, occupied replacement, reads/explicit entry removal from
multiple-entry tables,
singleton/multiple-entry Map retirement and selective Key notification. Safe
null/bool/int/validated startup strings and binary64 floats add no heap edge.
Object payloads have
public untyped nonstatic/nonreadonly backed slots containing primitives,
fieldless destructor Children or one direct array of those leaves; matching
identities and keys fix declaration order. Ordered jobs preserve repeated Value
and Child edges, outside owners and later cleanup after a Child throw. Backed
storage clears without hook dispatch; used results, temporary producers and
clones retain their existing evaluation and owner transfers. Direct fetches
and used coalescing results add actual Value owners; terminal isset/empty borrow
storage. These many-table reads keep existing source/key authority, require a
nonfreeing input Key. Explicit offsetUnset now shares the same guard and
existing detach/release executor. Missing-Key bool/coalescing/Error behavior is unchanged.
Two new originals and one 73-condition spare-Key reached group pass at their
separate cuts; the native-checked variant adds no original agreement.
[Read review](coverage/semantics/gc-finite-value-reads-review.json).
The finite fallback now explicitly excludes the old storage selector, fixing
an overlapping-success regression on leaf-many access. A fresh comparison of
the exact legacy M141 separate-leaf original passes; its repair entry in that
review retains the separate tested cut and reports.

Explicit removal unlinks the entry before Child cleanup. A fetched Value owner
can delay all property cleanup; otherwise the removed Value job precedes the
consumed selected-Key job, keeping a returned Key live through callbacks even
after its outside CV was cleared. Supplied Child throws preserve later fields,
Throwable identity/creation trace and the skipped next-statement marker. Two
new originals and one 102-condition reached group pass at their recorded cuts;
the original overlap failure and old baseline keep zero credit.
[Explicit-removal review](coverage/semantics/gc-finite-value-unset-review.json).

Occupied singleton and multiple-entry writes publish the new slot before old
Value cleanup, preserving registration/order. A fetched old Value owner delays
its Children; immediate Child throws preserve supplied/fresh traces and skip
the outer result assignment after RHS rebinding. Same-identity replacement
records the native old-zval GC visit despite unchanged Value/Child owner counts.
The old writer domains remain disjoint and authoritative.
Three new originals agree exactly and one 71-condition source-reached group
passes. The supplemental native-only roots probe adds no source agreement;
the original baseline and initial independent timeout retain zero credit.
[Replacement review](coverage/semantics/gc-finite-value-replacement-review.json).

The shared payload policy permits scalar/object mixtures throughout those
consumers. Present-row predicates borrow the actual stored value: isset tests
NULL and empty tests truth, so false/zero differ from NULL. The initial GC49
object-only predicate and two state-fixture setup failures retain zero
credit. Mixed replacement, retained-owner, unset/append, Key notification and
Map retirement evidence are bound in the
[mixed-payload review](coverage/semantics/gc-mixed-scalar-finite-review.json).
Three new originals agree exactly and one 89-condition ownership/default group
passes at its recorded cut; constructed counterstates add no PHP agreement.

Validated float entries preserve negative zero, NaN and infinity through
ordinary storage/copies and cleanup. NaN empty warns before rereading the
selected row's numeric word, including a warning handler's same-row update and
reentry. The borrowed continuation preserves original operands and source/caller
authority, with no new Value or receiver owner; structural mutation/free is
fenced across old/new paths. Current float/long words use the pinned 64-bit
representation, while other post-warning tags stop explicitly. Property-float
validation delegates to the same bound without a duplicate success arm.
Two originals agree exactly and one 93-condition handler-write front passes;
[float-payload review](coverage/semantics/gc-float-payload-review.json) retains
the failed setup/dispatch cuts with zero credit.

Public typed float-property NaN warnings also retain their selected borrowed
receiver through authenticated API callback argument delivery. A handler can
write the captured slot and rebind the original CV; the result still reads that
slot. One unchanged original and one 82-condition cursor/ownership/resumption
front pass. The old interpreter failure keeps zero credit; WeakMap rules and
their evidence remain unchanged.
[Property cursor repair](coverage/semantics/gc-property-nan-cursor-review.json).

Root arrays form finite acyclic DIRECT graphs over the existing scalar/object
leaves. Branch-local ancestor paths reject cycles while admitting shared children;
property arrays keep their separate one-layer policy. Fetched arrays retain real
table owners across Key death, and COW creates separate physical edges. Ordered
retirement transfers each edge to a job without copying descendants. The earlier
[flat-array cut](coverage/semantics/gc-direct-array-payload-review.json) retains its
99-condition record; its constructed nested-root refusal is promoted and retired
from the current fixture without rerunning that campaign.
Two nested-array originals agree exactly and one 93-condition front passes:
outer retirement transfers two jobs for the same inner table, then an actual
inner owner2-to1 release leaves Value/Child edges unchanged. Cycle, ALIAS and
property-layer counterstates add no PHP agreement; the old baseline remains zero.
[Nested-array review](coverage/semantics/gc-nested-array-payload-review.json).

Ordinary leaf `stdClass` Keys can register across canonical Maps using the same
finite payload policy. A nonrecursive fold checks actual associated tables and
registration ranks; ordinary reads, occupied writes and explicit unset inherit
that validation. Selective Map retirement removes only its registrations and
Value/HARRAY owners. Key retirement transfers one slot at a time to ordered
release jobs under the exact retiring-Key pin. A later wrapper stays weak-live
through every preceding registration's cleanup; an already-delivered wrapper
stays weak-null through finite continuation. The other Keys and Maps remain
nonfreeing, with no active cursor or incoming Map-key association. Existing
leaf/reference, callback, singleton and cursor policies keep their prior domains.
Two originals agree exactly, and one front passes 144 conditions across real
pending/delivered-wrapper selections. The preserved early-wrapper source supplies
the second selection and adds no original differential credit.
[Shared-Key review](coverage/semantics/gc-shared-key-finite-review.json).

Direct by-value foreach now acquires finite scalar/object/nested DIRECT-array
payloads through one authenticated cursor and plain Map/Key/Value CVs. Pending
assignments copy Key and Value/HARRAY owners while the saved foreach continuation
owns Map; inner DAG edges stay unchanged. Map-CV unset, break and exhaustion
preserve fetched owners. Three originals agree exactly and the sole reached-state
front passes 131 conditions across 447 modules. Common storage cursor rejection,
by-reference iteration and factory/owned Iterator acquisition retain their earlier
domains. The occupied-current-row write exception below leaves other mutation,
retiring Keys, extra cursors and active lifecycle contexts Unsupported.
[Foreach review](coverage/semantics/gc-finite-byvalue-foreach-review.json).

An ordinary KEY_R read of the current multiple-entry row now copies its fetched
object/array owner during one authenticated direct by-value loop. Exact header
CVs, the current loop marker, body source and selection receipts preserve that
row. Its copied owner survives loop-Value/Map CV unset, break and later Key
cleanup without copying descendant edges. Two originals agree exactly and one
reached front passes 110 conditions (105 authored) across447 modules. Singleton
reads and common storage/quiet/reference/API/mutation/lifecycle fences keep their
earlier domains. [Current-read review](coverage/semantics/gc-foreach-current-read-review.json).

Occupied current-row replacement now uses that direct multiple-entry finite
cursor while the actual plain loop Value CV still owns the old payload. Original
Map/Key CVs, source and Key snapshot preserve selection and registration; existing
publication, copied-result and ordered release rules retain native timing. A
separate cursor operation proof covers only quiet old-value and later Map-pin
release, including the old payload's real nonlast GC visit. Two originals agree
exactly and the sole front passes 169 conditions (164 authored) across 448 modules.
Common storage, wider old callbacks, other mutations, Key retirement/freeing
and wider cursor/lifecycle forms retain their limits.
[Replacement review](coverage/semantics/gc-foreach-current-replacement-review.json).

Last-owner current-row replacement now authenticates a separate callback phase
after the loop Value CV is rebound to a nonowning scalar. Ordered old slots
select the real fieldless Child; its read through original Map/Key global cells
sees the published leaf. Normal return assigns the result, while a fresh Exception
preserves the outer target. A nonowning continuation claim retains old-row,
cursor and cell authority through Map-pin release without adding owners.
Root callers and ordinary leaf inputs are this cut; quiet GC58 remains separate,
and held GC35's freeing-Map write is unchanged. Wider mutation/callers, Key freeing,
by-reference/owned Iterator and active-GC/threshold cases remain partial.
Four exact originals and one 242-condition (237 authored) strict449 front pass;
failed fresh/descriptor/dispatch runs remain external with zero agreement.
[Last-owner review](coverage/semantics/gc-foreach-last-owner-read-review.json).

That same last-owner operation now accepts quiet NULL/boolean/integer/non-NaN
float and authenticated interned-string replacements. Incoming storage and KEY_R
results add no heap owner; present NULL assigns the outer result normally, while
a fresh Exception leaves its sentinel intact. The existing claim, source/cells,
cursor, old pin and Map-release phases are unchanged. Request/unknown string
identities, NaN and wider mutation/lifecycle forms remain outside this admission.
Seven exact originals and one 208-condition (203 authored) strict450 front pass;
the sole preimplementation baseline retains zero agreement.
[Quiet-scalar review](coverage/semantics/gc-foreach-quiet-scalar-review.json).

A separate current-row phase now admits a direct fieldless old Value's own
public destructor. Its actual last old-zval job selects the call; the old root
stays weakly live under call/result owners, with no storage pin during that
callback. Original Map/Key globals read the published leaf or quiet primitive.
Normal return assigns the outer result; a fresh Exception preserves its sentinel.
Only later cleanup creates the real standard-storage pin, then retires old and
releases the Map carrier through the existing nonowning claim.
Fresh unwind retains its genuine generic THROW_SEARCH inner operation; exact
phase and readonly future-prefix checks preserve its separate authority.
Root callers, the existing all-object construction domain and held Keys remain
bounded;
resurrection, callback writes, GC35 and active collection are unchanged.
Four originals and the maintained ownership front's normal/fresh facets pass
329 conditions (319 authored) at separate451 cuts; current joined453 also passes.
[Own-destructor review](coverage/semantics/gc-foreach-own-destructor-review.json).

Own-destructor Values now also admit finite public untyped declared scalar and
fieldless-Child slots. Source-bound construction/acquisition preserves the common
storage fences and ordinary leaf companion rows. The own callback sees old weak
live; actual standard teardown then makes it weak-null before declaration-ordered
Child release. Shared Child slots preserve physical multiplicity and invoke the
Child only at its real last release. Normal and fresh-own paths read the installed
replacement through the same original cells. Fresh Child calls remain attached to
the genuine generic inner operation, while the outer claim owns the pending
Exception. Exact saved-task certification restores borrowed registries with
identical heap; no pin/receipt/schema or executor change is needed. Four originals
and 506 independent conditions (496 authored) pass at their recorded453 cuts.
[Declared-own review](coverage/semantics/gc-own-declared-slots-review.json).

A fresh Child throw during fresh-own cleanup now transfers the protected old
Exception from the actual parent pending root into the new Exception's Previous
edge. The parent claim owns the new pending Exception; the genuine generic inner
operation keeps its source and zero roots. Later declared Children still run in
order and read the installed row before catch, with the outer result unassigned.
Separate source/slot/history and saved-prefix proofs cover this handoff without
changing the earlier read guards or held lifecycle domains. At that cut, a further
Child throw in that established Previous history stops explicitly before RESULT
consumption; its raw fence retains every pending and callback root. Two originals
and 375 independent conditions (365 authored) pass at their recorded454 cuts;
authentic joined455 also passes.
[Pending-handoff review](coverage/semantics/gc-child-pending-handoff-review.json).

Finite repeated fresh Child throws now preserve the original inner SOURCE while
extending the parent pending Exception's canonical Previous path. Every path
identity is fresh and decreases toward the original NULL Previous; the real
selected RESULT and Root slot history authorize each atomic transfer only while
every existing node and the new Throwable have one owner. Later normal Child
reads preserve the installed row and outer sentinel. Existing default pending
behavior, refusal outside the proved history and held domains remain unchanged.
Two exact originals and the focused 206-condition front (201 authored) pass at
their recorded455 cuts; authentic joined456 also passes.
[Finite-chain review](coverage/semantics/gc-finite-previous-handoff-review.json).

Retained plain DIRECT-array DAG incoming values now share the existing
current-row own/Child callback phases. Slot publication, KEY_R copy and explicit
callback-local release change only outer-array owners; shared subarrays and
ordinary leaf edges retain their physical multiplicity. The RHS remains held
and unimported, normal used assignment adds its outer result owner, and fresh
own throw preserves the sentinel before later Child reads. Dedicated finite
incoming validation leaves old payload/free policies and held domains unchanged.
Four originals and the focused 230-condition front (225 authored) pass at exact
private456 cuts; the review records current457 default-route compatibility.
[Retained-array review](coverage/semantics/gc-retained-array-callback-review.json).

Own-Value cleanup now separates declared array ownership from descendant Child
selection. Shared Root array slots first decrement without visiting elements;
last release retires the array ownership node and transfers ordered VALUE jobs.
The actual Root slot/NEXT, borrowed original row and remaining release suffix
authorize each last-owner Child read, preserving old weak-null and later direct
field order. Own normal/fresh paths keep the original claim/cells and deferred
outer result. Unproved Child throws stop before RESULT/root consumption.
Four originals and seven bounded facets pass 492 reported / 457 authored
conditions at their private 457-module cuts; full endings belong to the originals.
[Own-array review](coverage/semantics/gc-own-array-slots-review.json).

Property-array owners survive ordinary copies and COW. Removing the Value leaves
a fetched array owner intact; repeated array identities in declared slots defer
element cleanup until their last owner releases. Slots release in declaration
order; a final array release runs elements in table order, including cleanup
after a supplied Child throw between shared array slots.
Two originals agree exactly and one 91-condition front passes. The front checks
the actual slot-to-array job transfer and array owner2-to1 with Child edges
unchanged; later callback order comes from the original endings. The old
first-insertion baseline retains zero agreement.
[Property-array review](coverage/semantics/gc-property-array-payload-review.json).

Typed/alias/virtual/inherited/deeper, nested-array and recursive property layouts,
wider mutation/caller contexts,
freeing-Map dimension access and active-pin collection remain partial. Paused
work is untouched. The earlier [private-Key notification review](coverage/semantics/gc-finite-value-key-notice-review.json)
separates its source/owner/budget results from reconstructed helper inputs and
zero-credit baseline/structuring failures. Earlier cuts remain in the reviews for
[two entries](coverage/semantics/gc-two-entry-map-first-review.json),
[finite entries](coverage/semantics/gc-finite-map-first-review.json),
[declared slots](coverage/semantics/gc-finite-declared-properties-review.json),
[singleton/backed storage](coverage/semantics/gc-singleton-finite-values-review.json)
and [insertion/append](coverage/semantics/gc-finite-value-insertion-review.json).

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
statement markers and the shared request counter. Grouped Echo, unset, global
and static operations interleave canonical ticks with completed operations and
later item evaluation, preserving late targets, reads, initializers and compiler
lines/frequencies. Unset cleanup finishes before its Tick; abrupt callbacks leave
later owners intact. Cached static bindings still tick on later calls.
Foreach value/key targets compile before the body even for empty input. Shared
by-value list traversal visits RHS, keys and nested targets in compiler order.
Runtime target callbacks stay lazy per iteration, and later failure preserves
completed writes while skipping pending targets/body and releasing the iterator.
Plain global constant groups compile initializers in order and tick after all
bindings, preserving the final emitter line and installed values on callback abort.
Class-like plans consume completed early-binding facts to preserve or break prior
adjacency. Methods, ordinary block/expression-GET hooks, class-constant and plain
property initializers contribute lexical declarations even when uncalled. Constant groups
remain unticked; property-group Ticks preserve main adjacency, type/name lines
and callback abort before pending class activation. Short GET expressions retain
nested callable order and implicit return; callback removal of the global receiver
keeps it alive until unwind, with later fresh-object retry. Nested Closure scope
uses completed getter/property ownership. Escaped Trait-getter Closures match
shared physical code to actual consumer property/getter imports, retaining separate
lexical/called classes and receivers after getter frames retire.
Escaped block-SET Closures authenticate exact class/trait setter origins and
actual consumer imports while retaining captured values and receiver ownership
after hook return and removal of the original receiver variables
([review](coverage/semantics/tick-set-closure-review.json)).
Ordinary public typed class short SET hooks evaluate the real expression, write
backing storage and fall through as void while preserving the caller's input
result. Input errors skip the body; RHS throws skip the implicit assignment and
result type errors prevent its slot update. Retry and receiver cleanup retain
the existing owners
([review](coverage/semantics/short-set-expression-review.json)).
These short SET bodies also bind an actual typed, defaultless by-value Param,
preserving its name, contravariant signature and original string input separately
from integer storage. Body compilation precedes variance checks; the existing
receiver owners survive throw/retry and budget resumption
([review](coverage/semantics/short-set-explicit-review.json)).
Existing public typed class block GET and short SET hooks now share one authentic
backing descriptor and retain their distinct indexed functions/signatures. Crossed
own-backing access skips the other hook; assignment input, stored transformation
and getter result stay distinct through RHS throw, retry and receiver release.
Three originals agree and strict448 passes; 137 independent source/owner/budget checks
are in the [short-pair review](coverage/semantics/short-get-set-pair-review.json).
Initialized properties now also admit pure block GET plus an inherently backed
short SET through the actual source/property/initializer certificate. Neither body
needs syntactic backing use; persisted SET storage stays distinct from GET 700.
Four source agreements, strict448 and 148 independent source/slot/owner/budget checks
retain their recorded cuts in the [pure-pair review](coverage/semantics/pure-get-short-set-pair-review.json).
With no initializer, the same pair keeps genuine uninitialized backing until its
first successful write. GET 700 precedes that write; backing-read Error, parameter/implicit-write
TypeErrors, persistent 15/12 and first-write receiver abort/retry preserve storage.
Four originals, strict449 and 148 independent initial-slot/owner/budget checks retain
their cuts in the [uninitialized-pair review](coverage/semantics/uninitialized-pure-get-short-set-pair-review.json).
Trait, byref/attribute/default and wider headers stay partial.
Existing expression-bodied GET now pairs with short SET on the same initialized
or uninitialized property. Actual backing/source authority reuses implicit-return
compilation and runtime; getter throw/return TypeError preserves the caller target
and storage. One saved getter-context receiver owner survives global removal;
the result receipt adds none. Five originals, strict449 and 146 independent source/
return/owner/budget checks are in the [expression-pair review](coverage/semantics/expression-get-short-set-pair-review.json).
Short SET can also precede GET: actual source derives logical GET 1/SET 0 while
compilation visits physical 0 then 1, preserving checked SET body/builtin-variance error priority.
Existing descriptor, return, storage and Closure source-owner rules consume those
real roles, including source-covered absent initializers. Seven originals and
strict449 pass; main 148 and corrected Closure 37 checks retain separate cuts in the
[SET-first review](coverage/semantics/set-first-hook-pair-review.json).
Source-backed block SET now composes with admitted GET forms and actual physical
roles, including explicit typed/defaultless input and reversed statement pairs.
Actual SET syntax authenticates pure initialized GET backing; absent initialization,
original string input, transformed storage and checked compiler error order remain
distinct. Seven originals, strict449 and 156 independent statement/receiver/budget checks
are in the [block-SET pair review](coverage/semantics/block-set-hook-pair-review.json).
Backed GET syntax now establishes whole-property storage even when block SET has
no own-backing access/write. Actual pair/role/default authority preserves initialized
values or a real uninitialized slot through no-write success, throw and retry;
implicit parameter coercion stays distinct from the caller's original input result.
Five originals, strict449 and 147 independent source/slot/receipt-owner/budget checks are
in the [GET-backed no-write review](coverage/semantics/get-backed-no-write-set-review.json).
True virtual class GET/block-SET pairs now retain source roles and typed metadata
without any object slot. Existing GET forms and implicit/explicit typed SET preserve
input/return checks, no-write effects and receiver throw/retry. Explicit defaults
fail after physical hooks at the last hook's end line; earlier default-type and
checked body/builtin-variance errors keep their priority. Seven originals and
150 independent no-slot/source/receipt-owner/budget conditions use the current
450-module manifest in the [virtual-pair review](coverage/semantics/virtual-get-block-set-pair-review.json).
The original temporary-cast comparison cleanup failure stays unresolved/zero;
accepted empty-cast observations use a CV. Pair overrides, Trait and wider headers
remain separate.
Direct flat Trait GET/block-SET pairs also compose admitted backed bodies, actual
roles and typed/defaultless builtin parameters. Raw partners and source/type facts
authenticate both Consumer clones atomically; two Consumers retain separate slots
and lexical/called classes while sharing Trait code/magic. Original string input,
weak reception, no-write initialization state, callback throw/retry and imported
GET1 return/Closure source owners reuse existing execution rules. Six originals and
212 independent source/clone/slot/receipt-owner/budget conditions are in the
[Trait pair-family review](coverage/semantics/trait-backed-get-block-set-pair-review.json).
The initial source timeout and first peer fixture typing failure retain zero credit.
GET/block-SET and GET/short-SET pairs also export through acyclic unadapted Trait
wrappers and multiple Traits with disjoint properties. Each property's real immediate
exporter and installed path authenticate flattened raw hooks/Params; wrapper rows
remain noncallable. Unique callable selection is separate from admission of a
specific incoming edge, preserving diamond and first local-property conflict
priority. Virtual Consumer pairs keep both authentic hooks without a value slot,
while adjacent backed properties retain real storage. Original input, weak/union
reception, GET return typing, callback throw/retry and raw Trait versus Consumer
scope use existing execution. Imported virtual pairs stay outside the admitted
virtual override/inheritance paths. Short SET is inherently backed, even with
pure GET and no own-property syntax. Its real raw RHS evaluates before the implicit
write at the Consumer hook origin; input, stored transformation and GET700 remain
distinct through initialization, implicit-write TypeError, abort/retry and two
pending receiver owners. The [nested](coverage/semantics/nested-trait-backed-pairs-review.json),
[branching](coverage/semantics/branching-trait-exporters-review.json),
[virtual](coverage/semantics/virtual-trait-pairs-review.json) and
[short Trait reviews](coverage/semantics/trait-short-set-pairs-review.json) retain
separate source/path/clone/slot/receipt-owner/budget cuts and zero-credit failures.
Consumers may also extend ordinary source Parents with disjoint stored fields and
no declared or effective hooks. Pre-link import checks the actual installed
declared Parent; runtime hook authority requires the final SOURCE_PARENT link and
publication. Existing inherited layout, raw Trait/Consumer/descendant scope and
receiver owners remain distinct through
throw/retry. Trait conflict precedes a final-Parent linking error, while a raw body
error precedes main.
[Parented pair review](coverage/semantics/parented-trait-pairs-review.json).
Backed Trait pairs also preserve public reads with protected/private SET access.
Exact source flags authenticate setter visibility and private(set) implicit finality.
Consumer lexical permission stays distinct from Grand called-scope diagnostics;
RHS effects precede denial and allowed input then reaches reception. Initialized
and genuine uninitialized storage, original assignment input and writer/SET owners
survive the tested store/throw/retry paths. Virtual-asymmetric, arbitrary explicit
final and wider override forms remain excluded.
[Asymmetric pair review](coverage/semantics/asymmetric-trait-pairs-review.json).
Symmetric protected/private READ backed Trait pairs now authenticate canonical
keys through real raw Trait, wrapper and Consumer rows. Dispatch checks the actual
permitted descriptor, preserving private-first lookup and original caller access
while a plain helper runs. Short SET retains the source name before storage-key
resolution. Consumer readers, unrelated Consumers, Grand private fallback and
protected uninitialized storage keep their distinct outcomes; reader/getter owners
retain the receiver through throw and fresh retry.
[Nonpublic key review](coverage/semantics/nonpublic-trait-pair-keys-review.json).
Quiet and conditional planners now use that permitted descriptor and check their
result tails in the saved caller scope. Inaccessible `isset`/`empty` skips GET;
NULL and zero retain different `??=` paths. The real conditional write task
reacquires its receiver after the RHS and enters the existing SET call/result
rules, preserving original input, transformed storage and private denial after
rebinding. Getter and RHS aborts preserve the prior result and permit fresh retry.
[Quiet conditional review](coverage/semantics/nonpublic-quiet-trait-pairs-review.json).
Existing integer-RHS `+=` now invokes SET after GET/addition for symmetric
builtin-backed pairs. Permitted descriptor lookup and saved caller access retain
the selected receiver even if GET rebinds its CV. Real compound source and the
retained finish task authenticate the SET target; expression result and transformed
storage remain distinct. The outer operation pin survives the independent SET
receipt through normal return or unwind; GET-only storage/finish remains unchanged.
[Compound pair review](coverage/semantics/compound-get-set-pairs-review.json).
Direct named CV/This `unset` now recognizes nonpublic hooks through the resolved
canonical key. Visibility denial stays first; permitted caller and active own
GET/SET contexts still receive the hooked-property Error, with backing retained.
An unset-specific descriptor query keeps raw-name magic-property consumers and
ordinary storage rules unchanged; indirect hooked unset remains Unsupported.
[Canonical unset review](coverage/semantics/canonical-hook-unset-review.json).
Normal GET/SET on admitted backed pairs now accepts plain non-NUL string-CV
property names. The existing pending selector resolves a normal assignment name
after the RHS; the selected hook property stays fixed through later name changes.
Actual source/code/line and saved caller access authenticate the selected
Consumer descriptor independently of a helper's current name CV. Changed-name
GET abort, receiver cleanup and fresh retry retain ordinary ownership. Arbitrary
expressions and Stringable-name forms stay separate.
[String-CV name review](coverage/semantics/string-cv-hook-names-review.json).
Plain string-CV names also compose with existing quiet/coalesce-assignment and
symmetric builtin-backed integer-RHS compound consumers. Quiet task roles stay
distinct from normal GET. Conditional writes retain late receiver/name
reacquisition, including retirement of the original GET receiver before an RHS
abort. A retry can select SET again and preserve the original string input while
transforming storage;
zero skips the write. Compound dispatch instead uses the retained property's
source NAME through GET-time name changes, preserving its fixed target and
independent operation/SET holds. Existing literal, type and ownership laws remain.
[CV name consumer review](coverage/semantics/string-cv-hook-consumers-review.json).
Normal magic GET/private SET now authenticate plain string-CV names on direct CV
receivers. Entry checks the original emitted operand; selected NAME/DECL and
actual method arguments remain authoritative after handlers change the name CV.
A scalar-int/nonref completion gate preserves wider getter/coercion boundaries.
Existing getter receipt ownership, private setter body/signature/scope and
integer literal/direct-CV RHS delivery remain unchanged through throw and retry.
[Magic CV name review](coverage/semantics/string-cv-magic-properties-review.json).
Quiet magic CV-name consumers now reuse the selected NAME receipt for terminal
`isset`, `empty` and coalesce, including the `__isset` to GET handoff after name
mutation. New callback results stay boolean for `__isset` and scalar integer for
GET; false `__isset` supplies the existing no-GET null path. Conditional assignment
keeps its real VARIABLE selectors and reacquires receiver/name after the existing
no-argument integer RHS, preserving ordinary fallback versus actual SET dispatch,
throw and retry. Entry/source changes leave storage and receipt ownership intact.
[Quiet magic CV name review](coverage/semantics/string-cv-magic-quiet-review.json).
Private ordinary `__unset` now authenticates direct-CV/string-CV source and the
actual pending VARIABLE name through existing PPUNSET resolution. Initial name
equality is separate from entered receipt history, preserving selected NAME and
one receiver hold after handler mutation/removal. Void method/body/scope gates,
literal/public history, broad fallback, canonical hook exclusion and storage
rules stay unchanged.
[Magic unset CV name review](coverage/semantics/string-cv-magic-unset-review.json).
Public integer CV unset now distinguishes actual INITIAL/VALUE ordinary clearing
from PROP_UNSET magic dispatch using an authenticated source/name/PPUNSET/slot
certificate. Only that ordinary case partitions broad unknown-name pending;
callback entry requires UNSET, while entered public history survives repopulation.
Literal/private, void method/body, storage and one-receipt ownership laws remain
pointwise; bounded public CV recursion is described below.
[Public CV unset state review](coverage/semantics/public-cv-magic-unset-state-review.json).
Public integer CV unset now clears repopulated VALUE before consulting an active
same-object/name guard. PROP_UNSET with that guard uses the existing no-op without
another callback or receipt; the ordinary callback plan still excludes recursion.
Authentic CV/source/name/PPUNSET/public-int/no-hook/void/scope gates remain, with
existing context/receipt and local-CV ownership through helper throw and retry.
Reachable active VALUE and UNSET are witnessed; inactive INITIAL evidence stays
pointwise, without an active-INITIAL claim or storage/root/body change.
[Recursive CV unset review](coverage/semantics/public-cv-magic-unset-recursion-review.json).
Active private integer CV-name unset now authenticates actual PROPERTY_DENIED
and existing source/name/PPUNSET/capture/scope/no-hook/void gates before using the
ordinary visibility Error at the inner source line. The same-object/name guard
suppresses another callback; no public no-op, storage deletion or inner receipt
is introduced. Existing local-CV plus outer-receipt ownership survives Error
catch, helper throw and fresh retry; public/literal and normal callback paths stay
pointwise.
[Private recursive unset review](coverage/semantics/private-cv-magic-unset-recursion-review.json).
Indirect append now authenticates its actual main-scope CV/literal-property
assignment before calling an existing nonref getter on a private integer slot.
After return, the receiver hold transfers from guarded RESULT to guard-free BASE
through the indirect-modification Notice. Handler reentry sees IN_GET clear;
after the handler, scalar verification/copy precedes receiver release and the
ordinary append Error. Handler throw/destruction and retry preserve the outer
result. Existing tasks, source nodes, storage and root formulas are reused.
[Indirect magic getter review](coverage/semantics/indirect-magic-get-append-review.json).
Main-scope private integer magic `+=` now authenticates plain CV names after the
existing no-argument integer RHS, then retains the selected receiver/name through
GET and SET. Existing scalar-int/nonref getter, void setter, method/body and
range gates remain; computed result differs from transformed store. The operation
and current handler receipt retain independent receiver holds through abort and
retry, without a new source node, storage rule or root formula.
[Magic compound CV name review](coverage/semantics/string-cv-magic-addassign-review.json).
Main-scope private integer magic pre/post updates now authenticate actual OP/POST
and a plain CV name at UPDATE_PREP/PPRW selection. Retained GET/SET history keeps
that object/name through live-variable changes; immutable OLD/NEW distinguish the
prefix/postfix result from transformed storage. Existing scalar/range/method/body,
literal and independent operation/handler-hold laws remain.
[Magic update CV name review](coverage/semantics/string-cv-magic-incdec-review.json).
Terminal `isset` now admits the existing typed-bool method alongside a same-owner
admitted getter, authenticating both physical functions and canonical no-hook
private descriptor while dispatching only `__isset`. The literal terminal defer
and existing CV entry use the same bool/source/receipt law; old untyped/noGET and
empty paths remain pointwise, with no getter-result or body/type expansion.
[Terminal bool pair review](coverage/semantics/terminal-typed-isset-pair-review.json).
Sole short-SET Traits, same-name/hooked Parents, adaptation, nominal and wider
binding remain separate.
Conditional declarations activate before their header-line Tick, while top
declarations have no outer Tick.
Trait use and admitted alias/precedence metadata add no Tick or repeated method
compilation; callbacks retain physical source, alias trace name and receiver
through abort and retry.
Namespace markers use authenticated form/name/brace facts: semicolon headers
precede following work, braced markers follow it, and empty/EOF boundaries remain
in the flattened compiled stream. Header callback abort skips pending body activation.
Ordinary/group imports contribute one metadata Tick per statement at name/prefix
lines. Literal eval namespace/import events share the caller's request counter;
callback abort skips pending class activation and restores the eval continuation.
Global-file `__halt_compiler` adds no opcode but can emit a terminator-line Tick.
Its callback sees the existing halt offset and can abort while payload remains inert.
Ordinary function, method, Closure and arrow defaults contribute lexical declarables
left-to-right before body planning, with separate callee adjacency and the caller
plan preserved. Fresh received Closures retain declaring lexical/called scope,
while callbacks can read the actual receiver and abort before later body work.
Certified EnumCase markers run before the existing enum activation task, retaining
member order, prior-marker frequency, backed-value lines and abort/resume behavior.

Conditional and coalescing plans use published operands, redirects and retained
effects. Bodies erased during compilation and their static errors stay absent;
bodies skipped at runtime still compile. Retained effects run once and real conversions,
jumps and writes break adjacency. Quiet coalesce reads retain lazy RHS execution;
assignment target children compile once before RHS and memoized writable refetch.
Captured key consumers preserve string-carrier identities and classify their bytes
with the ordinary numeric-string rules. Registered-handler callable-key coalesce
writes and equal-byte runtime write/unset now consume their tasks and complete.
Exact source, strict and reached-state cuts remain in the
[Switch](coverage/semantics/tick-switch-review.json),
[Generator](coverage/semantics/tick-generator-review.json),
[Match](coverage/semantics/tick-match-review.json),
[conditional](coverage/semantics/tick-elision-review.json),
[coalesce](coverage/semantics/tick-coalesce-review.json),
[Echo](coverage/semantics/tick-echo-review.json),
[grouped emitters](coverage/semantics/tick-grouped-review.json),
[Foreach targets](coverage/semantics/tick-foreach-review.json),
[destructuring](coverage/semantics/tick-list-review.json),
[global constants](coverage/semantics/tick-constant-review.json),
[class-like declarations](coverage/semantics/tick-classlike-review.json),
[enum cases](coverage/semantics/tick-enum-case-review.json),
[member constants](coverage/semantics/tick-class-const-review.json),
[plain property defaults](coverage/semantics/tick-property-review.json),
[property hooks](coverage/semantics/tick-hook-review.json),
[plain trait use](coverage/semantics/tick-trait-use-review.json),
[trait adaptations](coverage/semantics/tick-trait-adaptation-review.json),
[namespace forms](coverage/semantics/tick-namespace-review.json),
[import emission](coverage/semantics/tick-import-review.json),
[halt emission](coverage/semantics/tick-halt-review.json),
[named defaults](coverage/semantics/tick-parameter-review.json),
[callable defaults](coverage/semantics/tick-callable-parameter-review.json),
[short getters](coverage/semantics/tick-short-get-review.json),
[Trait getter scopes](coverage/semantics/tick-trait-get-review.json) and
[carrier-key](coverage/semantics/tick-key-carrier-review.json) reviews.

Compiler-special builtin/fallback result fences, empty multiline control-body
lines and wider child/result/lifetime contexts remain partial. The earlier
registered-handler timeouts retain zero agreement credit; the carrier-key review
records their exact successful-conversion fixed point and the completed fix.

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

Effectful callable return checks now retain a fresh array temporary across
qualified public lookup, live member mutation and finally. Valid lookup carries
a handler exception through callee-CV cleanup; invalid lookup drops the temporary
before finally and creates a return TypeError, retaining any pending handler
exception as Previous. Exact union branches
bypass lookup. Four source agreements, private 463-module strict compilation and an independent
190-condition owner/budget packet pass. Accepted current464 source/interface
composition is recorded separately;
the scoped review keeps the unresolved pending/replacing-finally timeouts and
model-only refusal checks separate. [Callable returns](coverage/semantics/callable-return-review.json).

Plain compiled CV callable returns now distinguish protected compiler copies
from unique/shared local unref. Shared references separate only the local ENV
binding before even an exact union match; API lookup borrows its value without
adding a pin. Used RETURN moves and clears that slot, while ignored results keep
native compiled-variable cleanup order. Pending handler throws and invalid
TypeError/local catch-retry preserve the same value and real Exception carriers;
ignored protected temporaries drain after finally before locals. Plain-cell,
active-finalizer and existing callable/context bounds remain explicit. Four new
source agreements and 913 independent ownership/source/budget conditions pass at
the recorded private 465-module cut; the accepted current 467-module interface
load is recorded separately.
[CV return review](coverage/semantics/callable-return-cv-review.json).

Public ordinary instance and fixed literal class static method returns now share
callable verification through published method descriptors and separately
validated live target/scope/This context. Creator This and returned arrays keep
independent owners, including descriptor validation after creator retirement,
lexical method TypeError/Previous and used/ignored cleanup. Two new source
agreements and 548 independent conditions pass at the private 467-module cut;
no new task, root, entry or wider context is introduced.
[Method return review](coverage/semantics/callable-return-method-review.json).

Raw self/parent/static strings and bare keyword arrays now verify through the
actual API phase in the existing return context. Raw string bytes and
member-reference identity are preserved, without a captured This owner or
caller-scope recheck.
Keyword-class handler throws reject with TypeError/Previous; compound-member
throw resumption remains separate. Structural cleanup survives resumed leaf
mutation, with scoped NUL/compound refusals before lookup. Three new originals
agree; the affected 246-condition pending/union packet passes at private469.
Earlier failed aggregates and projections retain zero credit, and actual471's
joined interface load is separate.
[Keyword return review](coverage/semantics/callable-return-keyword-review.json).

Unprotected named USER by-reference CV returns now borrow their cells through
effectful callable verification without unref, detachment or payload restoration.
A live captured query can succeed while a handler replaces the cell or rebinds
its global name; RETURN still uses the captured cell's current contents. Used
results retain the real reference through pending cleanup, while ignored and
invalid calls preserve CV-slot retirement. TypeError retains a pending handler
Exception as Previous. Lost query graphs reach explicit refusal, without a pin
or historical lookup permission; the loss controls are model-only. Three new
originals agree; the affected 125-condition packet
passes at the private 471-module cut, with the failed 561-condition packet,
diagnostic cuts and the actual 473-module joined load
kept separate.
[Reference callable review](coverage/semantics/callable-reference-return-review.json).

Protected named USER reference returns now keep one real MAKE_REF temporary
through quiet finally and the actual second callable check, using the captured
cell after CV rebinding. Normal/pending ignored drain precedes locals; used
pending results and fresh TypeError/Previous retain separate cell/Exception
owners. First-pending callback suppression requires the proven canonical prefix
and quiet callback-free continuation; failing recheck remains Unsupported.
Two effectful source agreements and one retained pure control pass at their own
cuts; the affected 270-condition packet passes at the private 473-module cut. The original
pending mismatch, timeout, failed/interrupted packets and diagnostics stay zero.
Actual 481's joined load is separate.
[Protected reference review](coverage/semantics/callable-reference-protected-review.json).

Pure protected named-function CV returns now replace the duplicated recheck root
with a nonowning witness for a bounded single quiet finalizer and unchanged
TYPEVALUE conversion. Exact union acceptance is independent of callable shape.
The captured cell survives name rebinding with one real temporary; ignored
returns schedule one cell release before locals, preserving any surviving CV
owner. One new three-mode source agrees, and the first 178-condition packet
passes at the private 481-module cut. The separate current 483-module load
passes with zero source renewal. Earlier failures and finite projections remain
zero. Legacy computed, cursor, overriding and wider-finalizer paths stay open.
[Pure protected reference review](coverage/semantics/pure-protected-reference-review.json).

Exact-int protected reference returns now admit one quiet scalar-literal write
through the captured cell. Initial verification proves its earlier payload is
primitive. Existing integer conversion writes back through that same reference;
TypeError transfers the one temporary to a real release before local catch and
source-derived finally replay. Detached cells retire, while retained ENV owners
survive. One four-mode source and the first 224 conditions pass at the private
483-module cut; the separate current 484-module load adds zero source renewal.
Finite baseline/admission observations and the declaration-order failure remain
zero. Wider conversions, pending callbacks and legacy finalizer paths stay open.
[Scalar protected reference review](coverage/semantics/pure-protected-reference-scalar-review.json).

Protected plain-CV exact-int returns now carry one temporary through two quiet
nonreplacing finalizers. Source-derived inner/outer phases preserve one nonowning
witness and defer the repeated check until both bodies finish; the outer write
repairs the intermediate invalid value before that check. Final conversion/rejection uses the captured
cell after CV rebinding, including detached/ENV-held local catch and replay.
New multi-body entry requires empty output/tick callback state. One four-mode
source and the first 343 conditions pass at the private 484-module cut. The
separate current 487-module load adds zero source renewal. Finite root/projection
observations stay zero; wider finalizer/callback paths remain open.
[Two-finalizer reference review](coverage/semantics/pure-protected-reference-multi-review.json).

Protected plain-CV exact-int returns now follow a finite source-derived chain of
quiet nonreplacing finalizers, preserving the first inner owner and one temporary.
Each remaining owner/restore suffix authenticates progress; the repeated check
runs only when that suffix is exhausted. The three-body source agrees in four
modes at the private 487-module cut, including repair after two invalid writes
and detached/ENV-kept rejection with full replay. The reduced 271-condition
independent packet passes at that cut; the full 514-condition state timeout and
finite diagnostic remain zero. The separate actual 489-module load adds zero
source renewal. The original 360-second source timeout remains zero;
the separate retry passed in 358.147415 seconds under its declared 600-second
limit. Finite root observations add no agreement credit.
[Finite-chain reference review](coverage/semantics/pure-protected-reference-chain-review.json).

Protected plain-CV exact-int returns now stage a finite fractional-float
precision warning while one real MAKE_REF temporary owns the captured cell.
The saved integer survives handler writes; normal completion writes it back,
while handler throw creates TypeError/Previous without that writeback and
releases the temporary before local catch/finally replay. Genuine GLOBAL/ENV
aliases survive independently. Two selected sources and the reduced 185-condition
packet pass at the private 489-module cut. The failed 207-condition packet,
ignored-return projection and all preparation/finite observations remain zero.
Primitive-cell release is covered; no new owning-payload or user-destructor
behavior is claimed. The separate actual 492-module load adds zero source
renewal. [Lossy reference review](coverage/semantics/pure-protected-reference-lossy-review.json).

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
OB18 adds Array return conversion through the real Warning and child release,
then commits `Array` while preserving pending replacements, traces, frozen getters
and late PRODUCED flags. Reference unwrap transfers the actual Array before
warning-time alias changes; a narrow GC handoff hook leaves the later retval
decrement ordinary. Twenty author originals and two reached groups/234 conditions
pass at recorded cuts. Four independent originals and one SL439 front with three
groups/162 conditions pass at the final cut. [Independent review](coverage/semantics/output-array-return-review.json)
records real transfer/retirement owners, forged-source fallback and affected scalar
marker authority. That cut leaves FINAL Array and object/resource conversion Unsupported.
[Author evidence](coverage/semantics/output-array-return-author.json) retains the
failed dispatch diagnosis, scoped GC reviews and affected renewals.
OB19 adds ordinary standard-object/Stringable output returns, retaining the
original retval, cast receiver and actual method result through their ordered
cleanup. Returned string cells are read late; defined return-by-reference Notice
throws keep their cell and pending Throwable through genuine frame or unstaged
owners. Pending exceptions skip the method body while preserving the native cast
guard decrement and destructor-visible GC candidate. Conversion Errors, fresh
method throws and destructor replacements preserve normal buffer processing,
frozen getter copies and API/VM traces. Eighteen exact normal originals, two
refusal controls and four reached groups/420 conditions pass at their recorded
cuts. Checks and remaining FINAL/internal/custom/resource boundaries are recorded in
[author evidence](coverage/semantics/output-object-return-author.json). Five independent
originals agree at their recorded cuts; three reached groups/219 conditions pass
at the final scope-repaired cut. [Independent review](coverage/semantics/output-object-return-review.json)
records real C-frame authority, late-cell traces and collector dispatch. The two Notice originals retain public60 timeout cuts
with zero source agreement; their completed ownership fronts are state evidence.
That source-performance limitation remains unfinished.
OB20 extends normal FINAL returns to Arrays and ordinary Stringable objects.
Warnings retain `Unknown:0`; known methods enter at a null callsite/internal line
while the registration remains documentary metadata. Actual retval/cast owners,
frozen converted bytes and the normal drain retain their order. Two exact normal
originals, one pending refusal and a reached Array group/95 conditions pass at
their recorded cuts. [Author evidence](coverage/semantics/output-final-conversion-author.json)
records authority and limits. One independent normal original and one SL446
group/69 conditions validate the actual null caller, two Object owners, internal
trace and forged/nested frame refusals through full drain.
[Independent review](coverage/semantics/output-final-conversion-review.json) records
the exact cuts and observer/fixture corrections. Pending
conversion exceptions, FINAL non-Stringable Errors and abandoned cast/fatal
owners remain explicit dependencies. OB19's public Notice performance limitation
is unchanged.
OB21 adds direct fatal reporting for a top FINAL non-Stringable return. Real
null-C entry reports `Unknown:0`/255 before retval destruction; a source-only
abandoned-C receipt retains the actual object/FCI owners through existing
deactivation and inactive executor cleanup. No Throwable, method or cast guard
is fabricated. Two exact originals and one reached user-T packet/14 assertion
groups pass at their recorded cuts. The [independent review](coverage/semantics/output-final-error-review.json)
clears public validity, strict receipt/class-history guards, budgets and full
deactivation. A readonly view removes only the current authenticated receipt
from class-history checking to break recursive validation. [Author evidence](coverage/semantics/output-final-error-author.json)
preserves the initial failure and timed-out fronts with zero credit. Lower cascades,
pending cast exceptions and the earlier Notice performance limitation remain open.
OB22 handles a sole direct literal-new Exception throw from a no-local FINAL
`__toString` body with no selected exception handler. The actual null-C handoff
retains the RV and cast guard as two owners before ordinary receiver cleanup,
then reuses real Throwable reporting/release and deactivation. One exact
retained-destructor witness and 14 reached assertion groups pass at their recorded
cuts. The [independent review](coverage/semantics/output-final-cast-throw-review.json)
clears real owner/GC transfer, Throwable retirement, public guards, budgets and
full fatal completion; [author evidence](coverage/semantics/output-final-cast-throw-author.json)
keeps earlier failures at zero.
OB23 extends the direct literal-new builtin `Exception` route to ordinary compiled
CVs and in-method catch/finally. Real null-C restoration precedes ordered local
destruction; an actual frame-exit barrier retains retval/cast owners even when
no jobs or user destructor exist. Borrowed birth metadata clears on catch or
staged/unstaged normal return. A structural saved-consumer check removes repeated
immutable declaration replay during pending unwind; full capture/public/report
authority remains. One exact original now agrees within its unchanged 90-second
cap. [Author evidence](coverage/semantics/output-final-cast-locals-author.json) and
[independent review](coverage/semantics/output-final-cast-locals-review.json) retain
the source, owner, native-header, budget and normal-return cuts. Selected handlers,
supplied identities, replacement chains, wider constructor/result owners, ticks
and lower FINAL cascades remain partial; prior performance/paused boundaries stand.
OB24 adds a local destructor's fresh literal-new `Exception` at its own genuine
null-C return. Its fatal abort retains the saved outer exception, remaining outer CVs,
two destructor C protections and the outer retval/cast pair, with NULL previous
and ordinary reported-Throwable release before deactivation. One exact original
and independent primary11/caught2/finally2 groups pass, including public validity
after real normal owner consumption. Source/runtime and the current 451-module
joined load are integrated. [Review](coverage/semantics/output-final-cast-nested-review.json),
[author evidence](coverage/semantics/output-final-cast-nested-author.json).
OB25 replaces literal-message/latest-object freshness in the structural native
paths with a genuine completed `CTOR_NEW` record. Actual selected receiver/result,
NEW site and normalized fields survive arguments; only the matching own-code throw
becomes pending. Catch/normal consumption and retired-report validation preserve
the existing owners. Two original string-CV/helper-allocation sources agree exactly
with PHP under the unchanged 90-second cap.
[Author evidence](coverage/semantics/output-ctor-birth-author.json) and
[review](coverage/semantics/output-ctor-birth-review.json) retain the affected cuts;
independent 28 provenance, 5 local-endpoint and 8 catch/finally groups pass.
The current 452-module joined load passes. Current constructor, rendering and
held-path bounds remain.
OB26 transports a completed fresh builtin `Exception` from a direct no-argument
nongenerator helper into the existing native output consumer. Its producer origin
and native call site remain separate; only the same pending identity at real VM
restoration advances to native report authority. Helper cleanup keeps its producer
FUNCTION and restored native CURRENT/callsite, with ordinary staged/unstaged release.
Both frozen originals agree exactly under90; the reached helper-restore front passes
8+8 groups. [Author evidence](coverage/semantics/output-helper-unwind-author.json) and
[review](coverage/semantics/output-helper-unwind-review.json) retain the affected cuts.
Independent 71 transport/report/issuer/clearing/empty/byref groups pass, including
the current-continuation owner guard at birth and its checked source bridge.
The current joined 454-module interface load passes.
Constructor-argument aborts, owning saved continuations and held domains stay outside
this cut.
OB27 folds the actual finite saved helper contour, retaining immutable leaf birth
and native-consumer facts plus a nonowning position cursor. Each same-pending real
VM restoration consumes one frame tail, including recursive activations with
identical contexts. Departing cleanup FUNCTION/caller/callsite remain distinct;
only contour exhaustion at the original null-C boundary grants native authority.
Intermediate catch/normal overrides clear the contour, with current-at-birth and
every saved-continuation owner bounds preserved.
[Author evidence](coverage/semantics/output-call-contour-author.json) and
[review](coverage/semantics/output-call-contour-review.json) record the affected cuts.
Two exact per-source comparisons finish in73.295/57.220 seconds under90, with
original mixed-batch and layered/control timeouts retained0. Independent31 actual
edge/owner/report/receipt/intermediate-clearing groups pass; complete old26 fixture
adaptation is declaration-only. The current455-module joined load passes.
OB28 carries a completed fresh by-value factory result through its actual
RETURN_UNWIND/result/compiled-CV cleanup handoff before the native caller throws
it. Producer NEW/RETURN and native call/THROW are authenticated separately;
restored CURRENT alone grants no authority. The nonowning three-phase fact uses
existing return/value owners and constructor hook, with no80/161/257 change.
Two exact frozen originals agree in46.463/66.174 seconds under90; the affected
staged/unstaged owner/phase front passes7+7. Independent45 provenance, return-slot,
report/retirement, override/catch, two-site identity and native-destructor checks pass.
The actual current457-module joined load and169/306 inventory pass at the recorded cut.
[Author evidence](coverage/semantics/output-factory-return-author.json) and
[review](coverage/semantics/output-factory-return-review.json) retain the exact cuts.
OB29 folds finite by-value factory-return contours with immutable leaf NEW/RETURN
and final native THROW facts. Selected intermediate RETURN(call) sites and each
actual same-object frame pop consume one cursor position, including identical
recursive contexts. Cleanup VALUE belongs to the actual departing function;
final capture requires an exhausted contour and no remaining contour VALUE owner.
Intermediate normal override clears partial RETURNED provenance before retirement.
Two exact originals agree in 50.700/59.611 seconds under 90; 55 affected assertions
and baseline 45 on the unchanged runtime remain separate. Independent 48 provenance,
report/retirement, cleanup/override, catch and native-destructor relay groups pass.
The actual 458-module joined load and 169/306 inventory pass at the recorded cut.
[Author evidence](coverage/semantics/output-factory-contour-author.json) and
[review](coverage/semantics/output-factory-contour-review.json) retain the exact cuts.

OB30 follows completed fresh factory results through real private compiled-CV
publication and a later matching variable throw. Nonowning cell associations
preserve siblings, selective rebinding/catch and the selected historical report
fact while existing CV/pending owners supply the transfer. The single-CV source
matches native in 64.972 seconds under 90; multiple-CV public comparisons still
time out and retain zero credit. The baseline passes 16 owner checks and the
affected front passes 7. Independent 49 protocol, refusal, selective clearing,
cleanup, native-consumer and retired-receipt groups pass. The measured early commit
rejection is filtered before full validation without removing admission authority.
The actual current462 joined load and 169/306 inventory pass at their recorded cut.
[Author evidence](coverage/semantics/output-factory-cv-author.json) and
[review](coverage/semantics/output-factory-cv-review.json) retain the separate
source/state/performance cuts.
OB31 stores fresh factory results in ordinary helper CVs before their actual
same-cell VARIABLE throw. Recipient frame position and cell distinguish recursive
and caller siblings; normal RETURN-to-WRITE and exceptional same-pending restoration
use separate cursors. Only real VM pops exhaust the latter at the original native
C0. The helper's CV releases before native reporting, retaining the departing
FUNCTION and real pending owner. 35 independent groups cover pivotal public validity, guard refusals,
reports/retired receipts, sibling/recursive isolation, clearing, cleanup and staged
local-native ownership; the failed local aggregate and its C0 observation stay zero.
Both public 90-second attempts time out with zero source agreement. No shared
validator or generic owner/return protocol changes; public source performance
remains unfinished. The actual 465-module joined load and 169/306 inventory pass;
complete old30 fixture adaptation is declaration-only.
[Author evidence](coverage/semantics/output-factory-helper-cv-author.json) and
[review](coverage/semantics/output-factory-helper-cv-review.json) retain the scoped cuts and failures.
Generated native `__toString` errors retain actual producer/source authority
through FINAL cleanup: scalar/private-CV return and quiet PINT/string TypeErrors
for the listed arithmetic, shift and bitwise operators; post-body missing-return TypeError; numeric
division/integer modulo DivisionByZeroError,
negative integer shifts ArithmeticError, and pool-integer UnhandledMatchError in
authenticated scan/table modes. Own source/opcode/compiled line, exact request/materialized
identity and native/current/nonowning bounds remain mandatory. Four-field facts
add no owner; live admission rechecks normalized fields, while retired receipts
bind the original source and abandoned native row.

Native T2/Error1 persist through real CV retirement and empty-release/C0;
normal publication retains retvalT1. Catch and bare-finally consume in-body errors;
a finally return prevents the appended missing-return check. Empty method CVs
are admitted for these generated errors; the
structural constructor-birth gate and separate no-CV literal-throw route are
unchanged. No shared match/type/return/root/renderer protocol is broadened.

OB48 authenticates unary PLUS/MINUS TypeErrors at their own source direction and
compiled child0 line. Equal string-times-integer messages and materialized images
add no authority. Three originals agree in 73.094/70.720/43.665 seconds under90;
fourteen affected source/capture/pending/owner/budget/public checks pass; the
positive ten include the real empty-release/C0 boundary. Twelve baseline
observations add zero agreement. All nineteen independent checks pass first applications at the fixed490
cut. Exact source/runtime/test are accepted at `450f53db`; its actual492-module
load passes in 27.782042009 seconds with zero source credit. Private490 evidence
stays separate. Existing bounds and OB31 performance remain unfinished.

Match requires a pool-backed PINT subject and present, equal own/unit mode facts;
the negative-shift and modulo-by-zero issuers require PINT operands.
The direct-CV return proof retains its private, nonreference,
non-global/nonstatic/unbacked cell bounds. Generated-error issuance stays in the
direct by-value native method; owning/noisy/place operands, supplied identities/
COMP88, constructor abort/custom rendering and other held expansions remain outside
these additions. OB31 public performance remains unfinished as above.

| Generated-error coverage | Evidence |
| --- | --- |
| Scalar return checks | [Author](coverage/semantics/output-final-return-type-author.json), [review](coverage/semantics/output-final-return-type-review.json) |
| Empty-CV return checks | [Author](coverage/semantics/output-final-empty-return-author.json), [review](coverage/semantics/output-final-empty-return-review.json) |
| Weak rejection/coercion | [Author](coverage/semantics/output-final-weak-return-author.json), [review](coverage/semantics/output-final-weak-return-review.json) |
| Post-body missing return | [Author](coverage/semantics/output-final-missing-return-author.json), [review](coverage/semantics/output-final-missing-return-review.json) |
| Private scalar CV returns | [Author](coverage/semantics/output-final-cv-return-type-author.json), [review](coverage/semantics/output-final-cv-return-type-review.json) |
| Numeric division by zero | [Author](coverage/semantics/output-final-division-error-author.json), [review](coverage/semantics/output-final-division-error-review.json) |
| Integer modulo by zero | [Author](coverage/semantics/output-final-modulo-error-author.json), [review](coverage/semantics/output-final-modulo-error-review.json) |
| Negative integer left/right shifts | [Author](coverage/semantics/output-final-shift-error-author.json), [review](coverage/semantics/output-final-shift-error-review.json) |
| Pool-integer match scan/table | [Scan author](coverage/semantics/output-final-match-error-author.json), [review](coverage/semantics/output-final-match-error-review.json); [table author](coverage/semantics/output-final-match-table-author.json), [review](coverage/semantics/output-final-match-table-review.json) |
| Quiet integer/string arithmetic TypeError | [ADD author](coverage/semantics/output-final-arithmetic-type-error-author.json), [review](coverage/semantics/output-final-arithmetic-type-error-review.json); [SUB/MUL author](coverage/semantics/output-final-arithmetic-operator-author.json), [review](coverage/semantics/output-final-arithmetic-operator-review.json); [DIV author](coverage/semantics/output-final-divide-type-error-author.json), [review](coverage/semantics/output-final-divide-type-error-review.json); [MOD author](coverage/semantics/output-final-modulo-type-error-author.json), [review](coverage/semantics/output-final-modulo-type-error-review.json) |
| Quiet shift/bitwise TypeError | [Author](coverage/semantics/output-final-integer-type-error-author.json), [review](coverage/semantics/output-final-integer-type-error-review.json) |
| Quiet POWER TypeError | [Author](coverage/semantics/output-final-power-type-error-author.json), [review](coverage/semantics/output-final-power-type-error-review.json) |
| Quiet unary PLUS/MINUS TypeError | [Author](coverage/semantics/output-final-unary-type-error-author.json), [review](coverage/semantics/output-final-unary-type-error-review.json) |

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
remained partial at that cut.

CLASS185 admits anonymous factories in ordinary nonmagic generator methods of
named/anonymous classes and unit0 traits, including admitted nongenerator nested
Closures/arrows and static anonymous methods. Source templates keep compiler key
order while actual saved frames restore method source, receiver and lexical/called
classes across yields and injected throws. Existing ownership handles completion
and escaped Closure lifetime. Shared Generator traces distinguish native API
resumptions from user/`foreach` callers, including lazy child-link errors before
arguments. The [review](coverage/semantics/generator-method-factories-review.json)
separates original source agreements, actual paused/resumed frame and retirement
checks, derived forged-frame refusals and retained explicit source boundaries.
Generator constructors, generator Closure/arrow bodies, attributes, by-reference
factories and wider dynamic/lifetime contexts remained partial at that cut.

CLASS186 admits unit0 method-owned generator Closure/arrow anonymous factories
through the existing source ancestry and lexical-name checks. Actual saved
Closures retain captures, receiver and lexical/called scope across deferred
initialization and resume; closed Generators keep those Closures after execution
frames retire. Static Closures keep source identity after creator retirement.
The [review](coverage/semantics/anonymous-generator-closure-factories-review.json)
separates selected originals, actual paused/resumed/closed ownership and budget
checks, derived refusals and native-only preparation. Generator constructors,
by-reference-return factories, attributes and wider binding/dynamic contexts
remained partial at that cut.

CLASS187 admits anonymous factories in ordinary nongenerator methods declared
with `&` across admitted named/anonymous/Trait owners. Direct compiler return mode
matches the parsed header; nested byvalue Closure ancestry restores that method
mode only in a source-authentication query. Existing returned cells and notice
handling preserve aliases, receiver/child retirement and used/unused temporary
return cancellation. The [review](coverage/semantics/anonymous-reference-method-factories-review.json)
separates source agreements, actual cell/budget checks and derived mode refusals.
Reference constructors/generators/Closure declarations, attributes and wider
binding/dynamic contexts remained partial at that cut.

CLASS188 admits unit0 method-owned nongenerator reference-return Closure/arrow
factories in named/anonymous/Trait owners. The deferred header authenticates its
own return mode independently of the checked parent method. Existing cells and
notice materialization preserve aliases and callback cleanup. Narrow shared
return-source checks authenticate the actual Arrow template/body line and exclude
Arrow expression returns from ordinary implicit-null fallthrough. The
[review](coverage/semantics/anonymous-reference-closure-factories-review.json)
separates exact originals, real cell/notice ownership and budget checks from
derived mode/refusal queries and preserved implementation failures. Reference
generators, reference/generator constructors, attributes and wider binding/dynamic
contexts remain partial.

CLASS189 admits anonymous factories in byvalue nongenerator `__invoke`, `__get`
and `__toString` bodies under existing method/deferred source ancestry. Getters
keep untyped required nonref/nonvariadic/default-free parameters and no declared
return type. Existing real consumers preserve receiver ownership after caller
variables clear. Authenticated named/Trait child checkpoints stay unpublished on
abrupt owner compilation, preserving child warnings before magic signature errors.
A bounded post-body compiler arm supplies the missing plain getter arity fatal.
The [review](coverage/semantics/anonymous-magic-factories-review.json) separates
original observations, source-derived mode bounds and real getter ownership/budget
checks. Reference/generator magic forms, wider getter headers, other magic bodies,
attributes and wider dynamic/binding contexts remain partial.

CLASS190 admits anonymous factories in byvalue nongenerator `__set`, `__isset`
and `__unset` methods using their existing plain-header and actual consumer
contracts. Parentless named/anonymous declaring owners and inherited receivers
keep their source scopes and saved-marker receiver roots. Setter inputs remain
integer CV/literal RHSs: the body receives the captured value while delivery reads
the original cell after receiver destruction. The
[review](coverage/semantics/anonymous-property-magic-factories-review.json)
separates original execution, actual NEW/delivery ownership and budget checks,
with retained Trait/mode/RHS boundaries. Other magic argument protocols, wider
signatures/receivers, attributes and generic dispatch remain partial.

CLASS191–201 admit anonymous factories in ordinary byvalue nongenerator `__call`
and `__callStatic` bodies under their existing plain headers and argument
consumers. Captured scalar/ordinary leaf-object sends stay fixed through later
CV/receiver mutation; real packed arrays and actual lexical/called scope preserve child/payload ownership
after return and receiver cleanup. The
[review](coverage/semantics/anonymous-magic-argument-factories-review.json)
separates exact admitted originals, one real frame/array ownership front and
retained producer/mode boundaries. Zero sends now use explicit empty capture and
the real name and immutable empty array parameters, with actual ownership and budget
checks in the [zero-send review](coverage/semantics/anonymous-zero-argument-magic-review.json).
The [object-CV review](coverage/semantics/anonymous-object-cv-magic-review.json)
promotes byte-exact original191 sources and tracks real captured-object owners;
instance sends retain positional, mixed or explicitly named first object CVs.
Named-only argument tables share the real retained buffer, which can remain the
last payload owner through return before receiver cleanup; the
[named-CV review](coverage/semantics/anonymous-named-object-cv-magic-review.json)
tracks this source/ownership slice. Old Unsupported cuts keep zero credit.
Initial reference-cell first CVs may now hold the same ordinary leaf objects.
BY VALUE SEND owns the copied object value before later alias writes; actual packed
tables and returned children retain OLD after the caller cell changes to NEW or
retires. The [reference-CV review](coverage/semantics/anonymous-refcell-magic-review.json)
records positional instance/static and independent named-Closure originals,
source authentication, real owners and budget/cleanup checks.
First flat-array CVs, including initial reference cells, retain integer/ordinary
leaf-object snapshots through generic COW and caller rebinding; the
[array-CV review](coverage/semantics/anonymous-array-cv-magic-review.json)
tracks source/index authentication and real table/payload owners. The
[reference-array review](coverage/semantics/anonymous-refarray-magic-review.json)
records the real CELL/table owners before and after SEND/COW, shared leaf identity,
real argument tables, returned children and alias/Closure cleanup.
First flat-array literals now use the same contextual collected-value bound, with real transient
array/payload/selected-receiver roots during later sends and returned-child
lifetime in the [literal review](coverage/semantics/anonymous-array-literal-magic-review.json).
A first source-certified nullary ordinary byvalue producer may return the same
flat array; the [producer review](coverage/semantics/anonymous-array-producer-magic-review.json)
retains its exact source and pending-owner cuts. Primitive COPY extends the first
CV/reference-CV and either-position ordinary nullary byvalue user producer to
NULL, bool, int, binary64 and authenticated string carriers, preserving exact
carrier identity and generic SEND ownership. Flat-array leaves keep their prior
integer/ordinary-leaf bound. Unknown byte-only strings remain Unsupported;
request-owned NUL stays held.
The [primitive review](coverage/semantics/anonymous-primitive-magic-review.json)
records 23 distinct source agreements and separate owner/budget packets of 105
and 107 conditions at their recorded cuts. Direct literal sends now authenticate
their exact quiet compiled value and interned string carrier, with raw-source
priority over existing COPY roles. Fixed NULL/bool, scalar and single-sign
numeric literals share the existing protocols; general constant fetches and
other folded expressions stay separate. Explicit unpack prefixes retain their earlier
policy. The [literal review](coverage/semantics/anonymous-literal-magic-review.json)
records five distinct source agreements, separate 112/124 owner/budget fronts,
and a separate 28-condition real-source unpack guard at their recorded cuts.
Indexed second CV sends now check the actual initialized ordinary cell after
earlier argument effects, then retain the copied primitive/leaf value through
handler writes and source-cell detachment. Missing/array/typed/backed reads stop
before warnings or coercions. The [later-CV review](coverage/semantics/anonymous-later-cv-magic-review.json)
records six distinct source agreements, separate 143/153 owner/budget fronts and
a 30-condition pre-warning source guard at their recorded cuts. Unpack prefixes
retain their earlier policy.
Fixed-name USER producers with exact required untyped by-value arguments now
share ordinary inner SEND/parameter/return ownership for quiet primitive/leaf
results. Source/target/formal certificates have priority over old value-only
admission. Nullary routes and contextual first-array returns stay unchanged;
438 preserves earlier unpack prefixes. The
[required-producer review](coverage/semantics/anonymous-user-argument-magic-review.json)
records five distinct source agreements, separate 140/188 owner/budget fronts
and a 27-condition unpack source guard at their recorded cuts.
Fixed named new expressions now admit source-certified effective plain public
constructors with zero/required untyped positional by-value parameters. Generic
constructor/result owners preserve the allocated ordinary leaf instance across
argument effects and ignored scalar returns. Collection binds its exact class;
the old empty no-constructor and unpack-prefix bounds stay unchanged. The
[constructor-producer review](coverage/semantics/anonymous-constructor-magic-review.json)
records five distinct source agreements, separate 160/201 owner/budget fronts and
a 30-condition zero-constructor unpack guard at their recorded cuts.
Keyword `new self/parent/static` arguments now select their allocation class
from the saved caller and real compiled site. Inherited constructors use that
allocated called class; existing This/result/SEND owners ignore constructor
returns and can preserve the ordinary leaf through caller retirement. Real-state
collection keeps the class bound. Wider headers, inner named/unpack and nonleaf
results remain partial; the [keyword-NEW review](coverage/semantics/anonymous-keyword-new-producer-magic-review.json)
retains separate source/state cuts and the original zero-credit timeout.
Fixed class/literal public static USER producers now share the quiet COPY
family with zero/required untyped positional by-value parameters. Actual inherited
scoped targets preserve declaring/called classes before arguments and add no
receiver root. Generic inner snapshots, fresh parameters and returned table/child
owners survive caller mutation and frame retirement. Constructor, nullary,
contextual-array and438 policies stay unchanged. The
[static-producer review](coverage/semantics/anonymous-static-producer-magic-review.json)
records five distinct source agreements, separate 134/204 owner/budget fronts and
a 29-condition real-source unpack guard at their recorded cuts; five intended
Unsupported controls retain zero agreement credit.
Direct literal static no-capture USER Closures now share quiet COPY through
zero/required untyped positional by-value arguments. Original child/template and
compiled INIT authority remain usable after the real target/INSTANCE owner and
parameter frame retire. Inner snapshots preserve old values through caller writes;
real outer tables and children retain the returned payload. Existing constructor,
nullary, contextual-array, header and438 bounds stay unchanged. The
[literal-Closure review](coverage/semantics/anonymous-literal-closure-magic-review.json)
records five distinct source agreements, separate 145/221 owner/budget fronts
and a 29-condition real-source unpack guard at their recorded cuts; six intended
Unsupported controls retain zero agreement credit.
Fresh fixed-name receivers support literal public ordinary method producers and
direct/FCC two-item callable arrays. Actual NEW source/CODE_NAME/class and
no/approved-constructor authority remain separate from call INITs: fixed NEW adds
no INIT, direct arrays use outer INIT and FCC arrays use outer/capture INITs.
Real arguments retain zero/required untyped positional by-value bounds. Original
physical source scope preserves private-first selection; private shadows are refused.
Generic copy positions0/1 remain exact. Direct nonstatic ARRAY_METHOD_TARGET owns
This; nonstatic ARRAYMETHODCLOSURE owns its receiver edge, frame INSTANCE owns
the wrapper and frame RECEIVER borrows This.
Static selection has no selector edge; request snapshots survive real argument
writes and caller/wrapper retirement. Real object RESULT transfers to bare SENT;
generic table/child laws keep separate evidence. The latest array cut has eight
source agreements and558 strict state conditions, with two private source refusals
retaining zero agreement credit. Existing quiet COPY/header/438 bounds remain;
wider array modes stay partial. The
[instance-producer review](coverage/semantics/anonymous-instance-producer-magic-review.json) and
[fixed-name callable-array review](coverage/semantics/anonymous-fresh-array-callable-producer-magic-review.json)
retain separate cuts and earlier zero-credit originals.
Fresh `new self/parent/static` method and invokable producers use saved caller
metadata and actual compiled NEW authority. Direct/FCC literal public methods
and callable arrays, plus normal fromCallable method arrays, retain original
private-first selection; private shadows remain refused. Direct, FCC and normal
fromCallable implicit invokers use allocated effective public nonstatic `__invoke`.
FCC real arguments stay separate from the placeholder. FCC arrays authenticate
actual outer/capture INITs and receiver NEW at its original three-FIELD0 path;
normal factories retain authored CODEEXPR/source line and outer INIT plus NEW.
Direct arrays authenticate outer INIT and the actual receiver/literal item paths.
Direct nonstatic targets own This. Array selection preserves the allocated called
class after temporary-header retirement. Nonstatic METHODCLOSURE,
ARRAYMETHODCLOSURE and FROMCALLABLECLOSURE wrappers own receiver edges; frame
INSTANCE owns the wrapper and borrows This. Static targets have no selector edge
and may release fresh selectors before real arguments. FCC array conversion
allocates after header retirement; normal-factory cleanup can park a wrapper
result in an eager-operation record before restoration. Object RESULT transfers
to bare SENT, while request snapshots survive selector/wrapper/caller retirement.
Constructor, formal, quiet COPY, header and unpack bounds remain exact; generic
table/child laws keep separate evidence. The FCC-array ledger records five source
agreements and504 strict state conditions; its private-shadow source refusal
retains zero agreement credit. Earlier normal-factory166 FALSE and corrected175
fixture cuts remain separate. Inner named/unpack
and wider modes remain required. Authentic cuts and zero-credit originals remain in the
[method](coverage/semantics/anonymous-keyword-new-method-producer-magic-review.json),
[method FCC](coverage/semantics/anonymous-keyword-new-firstclass-method-producer-magic-review.json),
[invoker](coverage/semantics/anonymous-keyword-new-invokable-producer-magic-review.json),
[invoker FCC](coverage/semantics/anonymous-keyword-new-firstclass-invokable-producer-magic-review.json),
[normal invoker factory](coverage/semantics/anonymous-keyword-new-invokable-from-callable-producer-magic-review.json),
[method-array factory](coverage/semantics/anonymous-keyword-new-array-from-callable-producer-magic-review.json),
[direct callable array](coverage/semantics/anonymous-keyword-new-array-callable-producer-magic-review.json) and
[FCC callable array](coverage/semantics/anonymous-keyword-new-array-firstclass-producer-magic-review.json)
ledgers; no family or full-core closure is claimed.

Initialized plain/reference CV receivers now support the same literal public
ordinary instance producers. Actual-time receiver/read and private-first selection
mint a nonowning source/class/method fact on the active outer descriptor; collection
uses that fact after CV rebinding/unsetting or receiver retirement. Future facts
and malformed pending carriers refuse without a default-route bypass. Generic
receiver/SEND/parameter/result/table owners stay unchanged; missing/constrained/
nonleaf cells stop before warning effects. The
[CV-instance review](coverage/semantics/anonymous-cv-instance-magic-review.json)
records six source agreements, separate 147/267 full owner/budget proofs and
24/43/26/45 missing/typed/future/repeated-source guards at their recorded453 cuts.
Seven intended source refusals and all preserved setup, admission and fixture
failures retain zero agreement; the typed-formal guard has an explicit root-context
bridge for completed positives. The actual joined 455-module interface load and
inventory169/306 pass at a2cc73a0c; no source/frontier replay. Broader receiver/call
modes remain partial.
Immediate fixed-source function/public-static USER first-class callables now
produce the existing quiet COPY values. Capture and invocation origins/INITs are
separate; placeholder conversion selects a real wrapper before outer sends.
Generic cleanup releases the wrapper call/INSTANCE owner after return; the tested
unaliased wrappers retire before table/child retention of the result. Collection
uses permanent function/class source.
Raw FCC priority and438 isolation keep old nullary/constructor/array/header bounds.
The [first-class producer review](coverage/semantics/anonymous-firstclass-producer-magic-review.json)
records five distinct first-pass source agreements, separate 194/267 full
owner/budget proofs and a 28-condition eligible-pack guard at recorded455 cuts.
Five intended Unsupported controls retain zero agreement. No209 failures,
corrections, timeouts or native repeats occurred; current456 composition is
independently reviewed without source/frontier replay.
Fresh fixed-name instance FCC producers now reuse the no-ctor/approved constructor
and public ordinary method source certificates. Actual capture and outer arity
remain separate. The wrapper owns its receiver edge; frame INSTANCE retains the
wrapper while `$this` borrows. Return-old releases that edge before the handler in
the tested unaliased case; return-this preserves the receiver in the real result.
The [instance-FCC review](coverage/semantics/anonymous-instance-firstclass-producer-magic-review.json)
records five first-pass original agreements and trimmed107/223 receiver frontiers.
The author compares a bounded retirement fence; the peer proves full split cleanup.
A25-condition eligible-pack guard and five intended Unsupported controls preserve
refusal boundaries with zero agreement. Generic CLASS209 call/table/child laws
are reused; all held/wider modes remain partial.
Literal instance FCC producers now accept initialized plain/reference CV receivers.
Actual capture and outer argument sites remain separate; the guarded read mints
an outer descriptor receipt before conversion. Collection uses it after source-CV
or wrapper/receiver retirement, with existing ownership and value bounds.
The [CV instance-FCC review](coverage/semantics/anonymous-cv-instance-firstclass-producer-magic-review.json)
records four first-pass original agreements, a100-condition return-old frontier,
a corrected168-condition returnThis proof and a25-condition eligible-pack guard.
The new read/cache/conversion budget is1+1+1=3; existing208/210 table/child/full-tail
laws are reused. Five intended Unsupported controls, the original peer cache-phase
fixture failure and its bounded diagnostic retain zero agreement.
Fresh fixed-name USER invokable producers now reuse approved NEW and public
`__invoke` source/formals. Effective runtime selection precedes arguments;
ordinary receiver call owners distinguish return-old release from return-this
result/table/child retention, with no Closure wrapper or CV history.
The [invokable producer review](coverage/semantics/anonymous-invokable-producer-magic-review.json)
records four first-pass original agreements,51/129 complementary owner frontiers,
a25-condition eligible-pack guard and23-condition anonymous-New raw-priority guard.
The one-word class-domain correction preserves the fixed-name source cuts;
five intended Unsupported controls have zero agreement. Generic tail laws are
reused without source/native replay; all wider/held modes remain partial.
Ordinary USER invokable CVs now guard the actual lookup before read/warning
and mint an effective-public-method receipt on the active descriptor. Receiver
call owners and source facts survive CV removal; even zero arguments cannot use
old integer/leaf fallback without a receipt. Stored Closure/string/array values
and wider modes remain held. The
[CV invokable review](coverage/semantics/anonymous-cv-invokable-producer-magic-review.json)
records four first-pass originals,63/128 complementary owner frontiers,39 genuine
zero-argument receipt checks and25 eligible-pack guards at private458 cuts.
Seven intended Unsupported controls retain zero agreement; no failed attempt or
source/native replay occurred. Generic tail laws remain reused.

Literal self/parent/static producers now derive requested and called classes from
the authenticated saved magic caller, then retain effective public static source
through frame retirement. Real-state collection preserves quiet values and mixed
CV receipts without a receiver owner or new history. The
[keyword static review](coverage/semantics/anonymous-keyword-static-producer-magic-review.json)
records four original agreements, complementary70/118 state frontiers and25
eligible-pack guards at private459 cuts. Five intended Unsupported controls,
the corrected source-admission attempt and all fixture failures/diagnoses keep
zero agreement. Only affected checks repeated; no native replay or broader gate.
Keyword-static first-class producers now authenticate separate capture and real
invocation origins/INITs while preserving forwarded called class. Generic wrapper
INSTANCE and parameter/result owners need no receiver edge or new source fact.
Four originals agree on their first model runs; complementary72/109 frontiers
and25 eligible-pack guards pass at private461 cuts. Three intended Unsupported
controls retain zero agreement, with no failure/correction/replay. Generic tail
laws remain reused. [Review](coverage/semantics/anonymous-keyword-static-firstclass-producer-magic-review.json).
This direct/FCC method and literal callable-array producers select public
ordinary instance/static methods from saved caller receiver, function and scopes.
Arrays authenticate actual This-fetch/literal paths and one direct or two FCC INITs;
only real invocation arguments determine formals. Original private-first lookup
stays exact. Nonstatic targets/wrappers add a receiver edge, while static selection
still leaves the independent caller This owner alive through arguments. Returned
This can survive caller retirement. Explicit unpack prefixes and wider modes
remain partial. The [method](coverage/semantics/anonymous-this-producer-magic-review.json)
and [callable-array](coverage/semantics/anonymous-this-array-callable-producer-magic-review.json)
reviews retain their distinct source/state cuts and zero-credit controls.
The callable-array cut has seven normal source agreements and 575 strict state
conditions at private cuts with 486 modules. Two private-source Unsupported controls, the real
unpack boundary and the original FCC checker failure retain zero agreement credit.
The latest preceding actual joined load `ea9ca05c2` with 488 modules passes with
zero source credit; it predates CLASS243 and does not renew the private evidence.
Fixed class-string/public-static direct and FCC callable arrays now reuse whole
compiled-pool authority and effective class-table selection. Real invocation
arguments and one direct/two FCC INITs remain distinct from capture placeholders;
static targets/wrappers add no receiver edge. Seven distinct first source
agreements pass at private488 cuts. Author SL113/130/25 and independent
SL112/62/39/128 checks preserve pool/returned-value ownership, caller retirement,
private refusals and the actual unpack boundary. The original parser, recorder
and helper failures plus the AL timeout retain zero credit. Actual joined
`f2f581dbb`/490 loads cleanly with zero source credit; it does not renew the
private cuts. Generic tails and the factored normal-factory proof are reused
without source/native replay. Wider modes remain partial.
[Review](coverage/semantics/anonymous-static-array-callable-producer-magic-review.json).
Literal USER `Class::method` direct/FCC producers now authenticate complete call
source, normalized CODENAME and actual INITs without requiring a child READ.
Effective public static selection and real arguments retain existing COPY0/1
bounds. STRING_METHOD_TARGET and the real STRINGMETHODCLOSURE preserve spelling,
scopes and returned leaves without a receiver edge. Seven distinct source
agreements and separate author SL102/120/25 and independent SL108/57/34/119
conditions pass on first execution at private490 cuts. Two private-source
Unsupported controls and actual unpack have zero agreement credit; no executed
failure, retry or native/source replay occurred. The direct-origin review fix
preceded modeled execution. Actual `9a5efad9f`/492 loads cleanly with source0,
separate from those cuts. Wider modes remain partial.
[Review](coverage/semantics/anonymous-static-string-callable-producer-magic-review.json).
Scoped self/parent/static instance producers now authenticate requested/effective
method selection against compatible saved callerThis, keeping declaring/called
classes separate. Four originals, separate 66/104 target/context fronts, a
25-check unpack guard and three refusal controls pass first execution at
private461 cuts. Existing static/This source and generic owner laws are reused;
actual462 composition follows empty-excess/default fallbacks. [Review](coverage/semantics/anonymous-keyword-instance-producer-magic-review.json).
Implicit This calls now select inherited public USER __invoke from saved caller
source and real INIT metadata, using ordinary receiver ownership without CV
receipts or Closure wrappers. Three originals, 71/94 focused target/context
fronts,25 pack guards and three refusal controls pass first execution at
private462 cuts;213/216 generic tails remain reused.
[Review](coverage/semantics/anonymous-this-invokable-producer-magic-review.json).
Fresh invokable-object FCC producers now authenticate both INITs, approved NEW
source and effective public __invoke against real outer arguments. Three
originals, separate67/corrected112 owner/escape fronts,25 pack guards and three
refusal controls pass at private462 cuts. Original114/diagnostic retain zero
credit;212/210 generic laws are reused, with actual463 default/absence review.
[Review](coverage/semantics/anonymous-invokable-firstclass-producer-magic-review.json).
Immediate CV invokable FCC producers now guard the actual conversion read and
preserve the selected outer-source receipt through receiver replacement or
removal. Three originals, separate68/112 ownership fronts,47 zero-receipt checks,
31 pre-warning guards,25 pack guards and six refusal controls pass first execution
at private463 cuts. Existing receipt and wrapper laws remain reused.
[Review](coverage/semantics/anonymous-cv-invokable-firstclass-producer-magic-review.json).
Implicit This invokable FCC producers now authenticate original capture and
real arguments from immutable saved caller context. Three originals, separate
67/104 caller/wrapper/escape fronts,25 pack guards and three refusal controls pass
first execution at private463 cuts. Existing receiver/result laws remain reused;
source certification survives the tested This retirement.
[Review](coverage/semantics/anonymous-this-invokable-firstclass-producer-magic-review.json).
Normal fromCallable producers now authenticate compiled fixed strings, factory
CODEEXPR and outer INIT against real invocation arguments. Three distinct source
agreements,65/corrected116 ownership fronts,25 pack guards and four refusal
controls pass at private464 cuts. The initial qualified-name omission and two
peer checker attempts retain zero credit; existing factory/wrapper laws are reused.
[Review](coverage/semantics/anonymous-from-callable-producer-magic-review.json).
Fresh invokable fromCallable producers now reuse original factory parts,
approved NEW and effective public invoke source against real arguments. Three
originals,71/106 argument-owner/wrapper/escape fronts,25 pack guards and three
refusal controls pass first execution at private466 cuts. Existing receiver,
INSTANCE and result laws are reused; fixed-string222 behavior stays pointwise.
[Review](coverage/semantics/anonymous-invokable-from-callable-producer-magic-review.json).
Fresh two-item method-array fromCallable producers authenticate actual item
origins, constructor class and private-first public target in the original
factory scope. Three originals,80/123 array-retirement/receiver-transfer fronts,25
pack guards and four refusal controls pass first execution at private466 cuts.
Existing wrapper/INSTANCE/result ownership is reused; fixed-string and direct
invoker factory behavior stays pointwise.
[Review](coverage/semantics/anonymous-array-from-callable-producer-magic-review.json).
Fixed class-string/static-method callback arrays use compiled parent-pool
authority and effective selection, including the lexical-private contrast. Three
source agreements,92/124 pool/SEND/wrapper fronts,25 pack guards and two refusal
controls pass at private466 cuts. The original runtime guard failure, checker-only
correction and bounded diagnostic retain zero credit; no native/state replay.
[Review](coverage/semantics/anonymous-static-array-from-callable-producer-magic-review.json).
This method-array fromCallable producers now use original CALLER authority and
actual This emission, keeping dynamic array/wrapper edges distinct from the
caller owner. Three source agreements,92/122 transfer/retirement fronts,25 pack
guards and two refusal controls pass first execution at private467 cuts; the
pack fixture correction preceded execution. Existing owners and438 stay fixed.
[Review](coverage/semantics/anonymous-this-array-from-callable-producer-magic-review.json).
Fresh-object method arrays now admit the unchanged plain-static source tail.
Two original agreements,80/121 selector-retirement/history fronts,25 pack guards
and one refusal control pass first execution at private468 cuts. The tested
unaliased selectors die before real argument reads; wrapper metadata adds no
receiver root. Constructor and generic owner rules stay unchanged.
[Review](coverage/semantics/anonymous-fresh-static-array-from-callable-producer-magic-review.json).



Static This-array factories now use an array-specific saved-caller/public-static
certificate. Real array release leaves the caller owner intact; receiver-free
wrapper INSTANCE, inherited scopes, saved arguments and source authority remain
valid through caller retirement. Two exact sources and separate109/125 owner/source/
budget checks pass at private469 cuts; initial setup/peer-fixture failures retain
zero credit. Direct/FCC This,234/438 and actual held bounds stay fixed. [Review](coverage/semantics/anonymous-this-static-array-from-callable-producer-magic-review.json).
Direct literal This-static producers now reuse the same public source proof.
Actual selected STATIC_METHOD_TARGET and its body have no receiver/INSTANCE
owner; the saved caller retains This through argument mutation and SEND until
retirement. Declaring, caller and called scopes stay distinct. Two exact sources
and separate80/85 owner/source/budget checks pass first attempt at private469;
FCC remains separate. [Review](coverage/semantics/anonymous-this-static-producer-magic-review.json).
Immediate This-static FCC producers now authenticate the placeholder capture
and real invocation through the same saved-caller public proof. Receiver-free
METHODCLOSURE/INSTANCE ownership stays separate from callerThis; wrapper and
caller retirement preserve snapshots and scope. Two exact sources and separate
96/111 convert/owner/budget checks pass first attempt at private469.
[Review](coverage/semantics/anonymous-this-static-firstclass-producer-magic-review.json).
Fresh fixed-name static direct/FCC producers now use the existing public-static
source check after unchanged constructor/private-first selection. Static targets
and wrappers retain no selector; actual owners determine retirement. Two exact
sources and separate75/109 selected/convert/owner/budget fronts pass first attempt
at private469, including selector-destructor changes before real arguments.
[Review](coverage/semantics/anonymous-fresh-static-producer-magic-review.json).
Public ordinary CV-object static direct/FCC producers now stamp the existing
SITE/CLASS/METHOD receipt from actual normalized selection. The142 hook preserves
the rewritten descriptor/cache state; old guards and ordinary identity defaults
stay exact. Static targets/wrappers add no selector owner, and real arguments can
replace/remove its CV without changing selected scope or snapshots.
Two exact sources and separate92/115 receipt/owner/budget fronts pass first
attempt at private469; missing receipts and malformed active carriers stay refused.
[Review](coverage/semantics/anonymous-cv-static-producer-magic-review.json).
Later array sends,
unpacking, nested arrays/reference entries, static named sends, Trait,
reference/generator, attributes and wider scope remain partial.

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

COMP182 compiles quiet single attributed constants in initializer/name/metadata
order and activates them through their original declaration. Metadata arguments
stay deferred; structural argument errors retain their per-value order and builtin
target/repetition errors follow every group. Existing compiled-image authentication
and exact closure-template reuse preserve source/code authority and initializer
behavior. The former COMP181 quiet singleton refusal is promoted. Successful
Deprecated metadata remained Unsupported at the COMP182 cut;
wider attributes and full core remain partial. Thirty-seven new source agreements,
two explicit Deprecated refusals, six affected originals and132 strict conditions
across438 modules pass at the recorded cuts. Final pipe controls pass. The failed metadata-array pool case
is preserved; its source-domain fix admits no runtime metadata root.
[Review](coverage/semantics/single-attributed-constant-review.json).

COMP183 pairs literal/null Deprecated metadata with actual source and
`constant()` reads. Installed name/metadata, user versus startup severity,
captured query/prefix selection and recursive-handler protection preserve
warning order across rebinding, namespace shadows and direct handler throws.
Body/retval exits retain the disabled handler through local cleanup and protect
the constant while the saved callback releases; repeated destructor exit keeps
the latest status. At this cut, a fresh local-destructor throw cancelling exit
stayed named Unsupported for COMP184. `defined()` remains quiet. Nonowning primitive/interned
strings are paired; owning values, converted queries, trait collision folding
and wider metadata remain partial. The56-original family has49 exact agreements
and seven separate refusals across preserved disjoint cuts;341 strict conditions
across441 modules,132 affected conditions and six older originals pass. Final
pipe controls pass; parser inputs stay fixed.
[Review](coverage/semantics/deprecated-global-constant-review.json).

COMP184 cancels Deprecated handler exit when a local destructor throws a fresh
Exception, then restores the real saved catch/caller tail. The two existing
marker phases preserve pending exceptions/read/API owners through eager saved
callback release, retain native previous links on replacement and keep exit
status 3 after catch. The unchanged COMP183 refusal source is promoted; five
more originals cover source/API and cleared captured-call ownership. Six exact
source comparisons,550 reached conditions across444 modules and four ordinary
throw/exit controls pass. The requested joined SL444/inventory base load passes;
parser/task/state interfaces stay fixed, so the prior pipe/syntax cuts stand.
[Review](coverage/semantics/deprecated-handler-cancellation-review.json).

COMP185 pairs owning values from existing ordinary constant producers with
Deprecated reads. Direct opcodes retain the fetched value/class before warning;
stable-text APIs and genuine global constant AST initializers retain selection
until successful delivery. Original nonfoldable lookup/class certificates survive
handler-created namespace shadows. Live receipts own pre-warning copies while
borrowed parameter metadata stays empty. Genuine saved binders and readonly eval
control views preserve global-AST exit/cancellation frontiers, including parked
caller frames. Owned parameter, class and static-property defaults remain
Unsupported; function-local dynamic statics remain ordinary opcode reads.
Thirteen new/promoted source agreements, three separate default refusals,
345 owned-state and550 affected conditions across445 modules, plus four older
scalar/builtin throw/exit originals pass at frozen156cfe734. The joined SL445/
inventory base load passes; prior syntax/pipe and other source cuts remain historical.
[Review](coverage/semantics/deprecated-owned-constant-review.json).

COMP186 pairs owning Deprecated defaults with genuine unscoped named-function
receives. Captured prefix/class/read certificates and bounded direct DEFINE cuts
preserve namespace shadowing and reentry. A nested receive can fill the same cache;
the outer value replaces that slot only when cacheable. Cache publication and the
formal's ownership precede type verification, including failure. Fresh/released
exit markers preserve the real parameter binder and retire the receive at its
actual discard. Method/Closure and class/static-property owning defaults stay
explicitly Unsupported. Twelve new/promoted source agreements, two separate
receiver refusals and 449 reached conditions across 446 modules pass at 3b89b723b;
the promoted old default passes six affected conditions. An equivalent user-leaf
discriminator at ded9e52f4 restores the original E_STRICT/eval-cut check: all 76
conditions pass under the unchanged cap. Prior source, pipe and syntax cuts stay historical.
[Review](coverage/semantics/deprecated-parameter-default-review.json).

COMP187 receives owning Deprecated defaults through fixed-name instance/static
calls to ordinary named-class by-value nongenerator methods. Actual descriptors,
default/function identities, declaring/called scopes and saved publication/call
prefixes authenticate reception and handler reentry. Inherited methods share the
declaring cache; formal/cache ownership precedes type failure, and receiver roots
and real binders survive cancellation cleanup. Only user-Deprecated frontiers and
leaves enter this new route. Eleven originals agree exactly, four separate
Unsupported controls retain zero agreement, and 259 author plus220 independent
reached conditions pass across448 modules. Closure/trait/byref/variadic/Generator/
dynamic-call recipients and class/static-property defaults remain partial.
A focused current-manifest SL448 load also passes; source comparisons retain
their recorded cuts without replay.
[Review](coverage/semantics/deprecated-method-default-review.json).

COMP188 receives owning defaults in actual unscoped real Closure literals and
ordinary clones whose same-template history proves Shared/Unscoped. Source donor
checks guard omitted/named-hole cache hits and post-handler binds. Captured reads
and cleanup survive callback-created private siblings, while the real binder
refuses their cache transfer. Actual captures/formals preserve ownership and
type-failure/cancellation order. Twelve originals agree; seven explicit refusals
retain zero agreement. Private reached checks and the joined main SL449/inventory
load pass at their recorded cuts. Bound/scoped/private, unknown/temporary cache
families, arrows and wider defaults remain partial; prior source cuts stand.
[Review](coverage/semantics/deprecated-closure-default-review.json).

COMP189 receives owning defaults through receiver-free same-scope bind/bindTo
REAL Closure copies and ordinary bound clones. Actual binding/API/source proof
and the retired source's known Shared/Unscoped stamp preserve the existing full
family cache guard without retaining the source or its captures. Eight originals
agree, one private scope-roundtrip refusal retains zero agreement, and one actual
binder/cache/formal owner front passes75 strict449 conditions with zero/one-step
budget and resumed/direct equality. Reentry, TypeError and exit cancellation
retain ordinary ownership and cleanup. Empty lexical/called scopes are this
implementation cut; broader This/called-class modes, private/mixed/temporary
cache identities and wider default forms remain core work. The prior source cuts
stand without replay; only460's selected-binding predicate changes.
[Review](coverage/semantics/deprecated-bound-closure-default-review.json).

COMP190 separates receiver-free empty-scope REAL private caches by actual
Closure/default identity, alongside unchanged Shared entries. Scalar-before-donor
and named-invoke preparation use the same owner routing. Genuine receive births
capture nonowning cache owners; same-cache children can fill a pending slot while
other live/retired owners cannot. Fresh clones, COW, type ownership and cancellation
retain native behavior. Private empty-array availability lasts through captured
child callbacks until actual storage release, without pinning Closure/source
objects. Fourteen originals agree at preserved cuts;273 independent strict450
checks cover reentry/provenance, cache/formal roots, retired handles and quiet
drop. Shared/default/class-constant encodings and455 policy stay fixed. Wider
scope/This/temporary/unknown modes and default families remain core work.
[Review](coverage/semantics/deprecated-private-closure-default-review.json).

The combined main SL450 load passes for COMP190, OB23 and GC59; its [shared record](coverage/semantics/deprecated-private-closure-default-review.json) preserves the tested source cut and adds no source-agreement credit.

COMP191 adds ordinary nongenerator REAL `Closure::call` owning defaults through
actual Shared or invocation cache identity. Distinct calls stay separate even
with identical source/receiver/site; receive history cannot transfer a child's
cache across owners. Temporary values survive callee local callbacks, then an
exact nonowning cache-free job precedes API receiver/source cleanup. Same-scope
Shared reuse, TypeError, throw and cancellation preserve native behavior. Ten
originals agree at retained cuts; two fake-method cold/warm controls remain
explicit future refusals with zero agreement. Independent361 strict451 premises
cover the actual cache/formal budget front, local/free/context order and nested
owner isolation. Source-only donor guards also protect scalar cache hits.
Direct scoped, wider receiver/default and held Generator/captured-entry/pending
families remain core work. [Review](coverage/semantics/deprecated-closure-call-default-review.json). The current joined main SL451 load and inventory check pass; the review records their exact tested cut.

COMP192 adds direct class-scoped REAL Closure literals, binding copies and clones
with actual borrowed This and distinct lexical/called classes. Existing Shared
and private owner/birth laws retain clone freshness, named holes, cache reentry,
TypeError and throw behavior. Ordinary scoped-private destruction preserves rows
through capture/static callbacks, then frees them before bound This; pending
HANDLE history alone cannot revive the cache. Quiet and staged receiver-free
copies, including inherited CalledChild, use the same authentic records. Eleven
originals agree; one warmed fake-method refusal retains zero agreement. Separate
107/93/187 strict452 fronts prove roots, exact cache death and owner/scope cuts.
Generator-close release and other held entry families remain outside this law.
[Review](coverage/semantics/deprecated-scoped-closure-default-review.json).

COMP193 adds direct public ordinary instance/static method FCC and
`Closure::fromCallable` default recipients and their clones. Actual captured
descriptor/scope/receiver records select the callee; a nonowning ENTRY witness
preserves Shared history after source/receiver retirement. Genuine child entry
and exact cache-owner proof govern reentry. Fake method statics remain owned by
the original method; private cache-free precedes This-only child cleanup.
The warm scalar-before-owning-donor source is promoted from its complete192
native packet. Twelve owning-default originals and one scalar preservation
original agree; three held controls earn zero agreement. Separate123/114/155/90
strict453 fronts prove ownership, entry history and cache authority. Explicit
wrapper/pending owning invokes, nonpublic/Trait/Generator and held303 cleanup
remain outside this finite family.
[Review](coverage/semantics/deprecated-method-fcc-default-review.json). The current
joined main SL453 load and inventory pass at their recorded cut.

COMP194 receives owning Deprecated globals during ordinary named-class constant
lazy initialization. Actual declaration/binder and selected lookup facts retain
callback cleanup and namespace shadowing. Type validation precedes publication;
a genuine begin-history cut supports nested fills, and untyped replacement
preserves earlier compiler cache views. Historical facts/snapshots add no root;
old computed cache-only values were a future boundary at that cut. Static-property
and Trait initialization and established Generator/303 holds stay separate.
Twelve originals agree, one explicit availability refusal earns0, and355
independent strict454 conditions pass. Current joined454/inventory also passes
at the recorded source cut.
[Review](coverage/semantics/deprecated-class-constant-owned-review.json).

COMP195 replaces computed class-cache arrays through genuine staged old-value
release while one publication task protects the pending new value. Readonly
structural history reconstructs earlier foldable arrays only in a compiler view;
retired containers and opaque Closure leaves acquire no historical owner.
Five originals agree, including one authentic194 native promotion. Separate
106/114 strict455 fronts prove ownership, history, nested lazy initialization
and budget continuation. The throwing-old-child native times out after `H|F|D|`;
its model-only Unsupported control has zero agreement. Wider abrupt,
static-property/Trait and held Generator/303 paths remain separate.
[Review](coverage/semantics/computed-class-cache-replacement-review.json). Current
joined455/inventory also passes at the recorded cut.

COMP196 receives owning Deprecated globals in ordinary named-class deferred
static defaults through actual declaring cells and saved binders. Selected
lookup facts preserve arrays, objects and Closure aliases across shadows;
first-fill, handler cancellation and retired typed-reference constraints remain
intact. Normal old-slot cleanup keeps one pending value owner and commits after
old-item release. Eight originals agree, including one explicit exit; independent
82/63/135 strict456 fronts and current joined456/inventory pass. Busy same-slot,
old-release abrupt, Trait/Generator/303 and wider forms remain separate.
[Review](coverage/semantics/deprecated-static-property-default-review.json).

COMP197 receives owning globals through genuine instance-template binders before
object allocation. Selected lookup records preserve shadowing and exact values;
actual write/link cuts freeze inherited templates and reject stale receipts,
including later legacy overwrites and replayed events. Templates and each object
own their current values; historical records add no root after old computed
containers and Closures retire. Normal replacement protects one pending value
through old cleanup and a different class's initialization. Nine originals agree
(eight normal, one explicit exit); independent strict457 fronts pass 79/73/46/82.
Busy same-template, old-release abrupt, Trait/Generator/303 and existing holds
remain separate. [Review](coverage/semantics/deprecated-instance-property-default-review.json).
Actual current joined457/inventory pass at b6d797120; source/runtime/tests and material review are secured.

COMP198 receives omitted owning defaults through fixed-name public ordinary
constructors. Actual allocated This/scopes and caller CTOR_RESULT govern live
reception; Shared caches compose with explicit/inherited constructor calls and
existing promotion. Closed receipts survive receiver retirement without adding
roots. Actual Deprecated-handler and body exits mark failed construction before
owner release, preserving destructor suppression for escaped This and ordinary
explicit-call behavior. Eight originals agree (six normal, two explicit exits);
independent strict458 fronts pass 91/51/106 conditions, and current joined458
plus inventory pass at e4618952198. Dynamic/anonymous/keyword/default-NEW227,
nonpublic/Generator/wider signatures and held families remain separate.
[Review](coverage/semantics/deprecated-constructor-default-review.json).

COMP199 receives owning constructor defaults through initialized CV class strings.
Exact caller selection and a nonowning birth witness preserve pre-argument class
selection through rebinding, same-site nested calls and receiver retirement.
Different selected subclasses retain their own receipts while sharing inherited
constructor caches. Four originals agree (three normal, one explicit exit7);
independent strict459 fronts pass 70/73/53 conditions. Ordinary CV aliases keep
their existing by-value read behavior; wider selectors and held entries remain
separate. Actual joined459 and inventory pass at ba1bd7c5a9; source/tests and review are secured.
[Review](coverage/semantics/deprecated-class-string-constructor-default-review.json).

COMP200 receives owning constructor defaults through `self`/`parent`/`static`
inside ordinary named method factories. Genuine factory scope/call history stays
distinct from constructor scope and survives factory-receiver retirement without
adding roots. Selected parents require authenticated child cache entries. Four
originals agree (three normal, one exit7); independent strict460 fronts pass
63/63/52/23 conditions. Actual joined460/inventory pass at 8c4a3e17e; the child
omission diagnostic remains zero credit and no completed source/front was replayed.
Captured/service/Trait/Generator/wider and established held entries remain separate.
[Review](coverage/semantics/deprecated-keyword-constructor-default-review.json).

COMP201 receives owning defaults through public ordinary method calls whose
member name comes from an initialized CV string. Actual selected function/scopes
and captured publication history survive rebinding, case aliases and receiver
retirement without a new witness or root. Same-site different methods keep their
function/default caches separate. Four normal originals agree; independent
strict461 fronts pass 55/57/56 conditions, and actual joined461/inventory pass at
95668007e4. Literal/keyword static class Names and existing ordinary alias reads
retain their bounds; callback/nonpublic/magic/Generator/wider and held entries
remain separate. [Review](coverage/semantics/deprecated-cv-method-default-review.json).

COMP202 receives owning defaults in authentic public method shutdown callbacks.
Exact current entry/arguments and a nonowning selected-target witness preserve the
absent callee callsite and closed history after registry reset/receiver retirement.
Registry owners and borrowed This stay unchanged; ordinary implicit This is
included. Five normal originals agree; independent strict462 fronts pass 86/78/83.
Fixed registration/public/by-value/nongenerator and capture/producer/held bounds
remain explicit. Source/runtime/tests are accepted at fae753133a; actual joined462
and inventory pass. [Review](coverage/semantics/deprecated-shutdown-method-default-review.json).

COMP203 receives owning extra defaults in authentic public method error/exception
handlers after four diagnostic arguments or one Throwable. Exact entered-target
proofs and nonowning kind/producer history preserve Shared identity and actual
callback/formal/Throwable owners; borrowed This stays rootless. Four normal
originals agree, including one builtin default deprecation before repeated caught
TypeErrors. Strict463 fronts pass 86 exception/76 error-owner/90 rejection checks;
only the exception front renews budget continuation. Source/runtime/tests are
accepted at fa5139bf5c; actual joined463 and inventory pass. Broader producers and
held domains stay separate. [Review](coverage/semantics/deprecated-handler-method-default-review.json).

COMP204 receives owning extra defaults in authentic ordinary public autoload
methods. One class-name argument, selected callback and real lookup/explicit-call
contours preserve Shared function/default identity. The registry owns its receiver;
current This borrows it, so actual warning-time unregister can retire it before
binding/body. Captured selection/request history stays heap-free; retired receiver
consumers remain held. Four normal originals agree and strict464 fronts pass
76 shifted-cut/scope,96 retirement and86 rejection checks. Source/runtime/tests
are accepted at67b944566d; actual joined465 and inventory pass.
[Review](coverage/semantics/deprecated-autoload-method-default-review.json).

COMP205 receives owning extra defaults in genuine ordinary public tick method
callbacks after their registered arguments. Exact marker/selected-row proof and
nonowning history preserve Shared identity after unregister, with existing registry
and formal owners; active unregister retains the calling row. Four normal originals
agree, including registration-argument rebinding and repeated TypeErrors. Strict466
fronts pass 72 marker/history, 96 owners/continuation and 91 type/cache conditions.
The finite noarg Deprecated donor plan applies while ticks are inactive
(`FREQUENCY=0`); active attributed declarations keep their boundary.
Source/runtime/tests are accepted at 50f1ee75a; actual joined466 and inventory pass.
[Review](coverage/semantics/deprecated-tick-method-default-review.json).

COMP206 receives owning extra defaults in genuine named USER string error,
exception, shutdown, tick and autoload callbacks. Existing family contexts authenticate supplied
arity; their witnesses retain selected function/source/publication. Shared identity
and all argument/cache/Throwable roots stay unchanged. Source-only owning hit checks and
explicit named/method proof domains preserve cold/warm and direct-child authority.
Six normal originals agree, including one builtin Deprecated stderr case. Strict467
fronts pass 59 autoload, 58 child/reentry, 52 cold shutdown, 85 type and 89 exception
conditions; only the exception front renews continuation checks. Runtime/source/
tests are accepted at714d1bd8c; actual joined467 and inventory pass.
[Review](coverage/semantics/deprecated-named-callback-default-review.json).

COMP207 receives owning defaults in direct quiet-CV public method string/array
calls. Full selected-wrapper proof survives argument mutation; normal instance
and static source-object lifetimes stay intact. A nonowning raw-entry bit separates
closed raw/FCC history and rejects missing FCC child ENTRY without changing cache
identity. Five normal originals agree; strict468 fronts pass 63 instance, 52 distinct
functions, 47 raw/FCC, 93 inherited scopes and 87 static-retirement conditions. The
four initial sources retain their genuine-raw bridge; only the affected mixed
source repeated. Source/tests are accepted at e3d2c106c; actual joined468 and inventory pass.
[Review](coverage/semantics/deprecated-raw-callable-default-review.json).

COMP231 composes quiet class CVs with completed runtime string members through
the existing canonical pair. Member effects can rebind the string source or
retire its sole ordinary object beforeH; saved request/member remain exact.
Two originals and 231 first-attempt strict492 conditions pass (105 author,
126 independent), with sole old491 UnsupportedM baseline at zero credit.
Actual MDR retirement, same-DECL request refusal, fresh selection and interface
result/COW retain folded/cache-empty bounds. Existing277 loader-resumed CV
construction is inherited; direct-published natives add no loader witness/claim.
The exact seven-commit source/runtime/test packet is accepted at `ae7d42ee5`;
actual current492 passes (27.030635181 s, source0). Only503+manifest changes,
without new kind/task/root/shared body or producer/reference/held admission.
[CV-class/member review](coverage/semantics/deprecated-cv-class-rvalue-member-constant-review.json).
The preceding composed-rvalue gate retains two originals/274 conditions at its own
cut in the [composed-rvalue review](coverage/semantics/deprecated-rvalue-class-member-constant-review.json).

## Active work

Ordinary named functions returning by value support scalar goto through declare
bodies and empty zero-frequency Declare/Switch bodies. Checked opener/separator
lines preserve compiler adjacency; goto skips directives and prefixes while
reusing loop continuations. Nonowning CV operands read the current environment
after case effects; empty-case/default fallthrough and continue2 use the
existing Switch/loop kernel. Ordinary source/current/saved scalar boundaries and
no-tick identity defaults remain explicit. Direct global `func_num_args()` Switch
subjects also reuse the existing TMP/FREE proof under zero frequency; actual
argument count stays independent of default/formal slots, with runtime argument
views unchanged. [Argument-count review](coverage/semantics/plain-switch-argc-review.json).
Direct `@$cv` subjects use the forced-read TMP proof: snapshot0/NULL survives
case rebinding, with the existing read-before-mask-restore transport. The added
route requires no registered error-handler callback.
[Suppressed-CV review](coverage/semantics/plain-switch-silenced-cv-review.json).
Count-left logical operators also reuse the nonfolding TMP proof under the same
scalar/no-handler boundary, preserving lazy RHS writes and Boolean results;
the source/history guards retain exact root and child-line authority.
[Logical count review](coverage/semantics/plain-logical-argc-review.json).
Source-proved unbuffered USER RHS helpers retain their own current-frame count,
physical scalar locals and the restored caller's Boolean continuation.
[USER-RHS review](coverage/semantics/plain-logical-user-rhs-review.json).
Compact literal-integer exit RHS uses the same source boundary with cold heap,
output and shutdown state. A selected exit discards normal Boolean/assignment
work and unwinds real scalar frames; skipped exit returns normally. Source
evidence separates one normal outcome from one explicit exit13, and 193
focused conditions cover actual status/frame retirement and public resumption.
[Exit-RHS review](coverage/semantics/plain-logical-exit-rhs-review.json).
The distinct native, source, focused and acceptance/load cuts, including earlier
failures, are retained in these ledgers and the
[goto](coverage/semantics/plain-goto-declare-review.json),
[empty Declare](coverage/semantics/plain-empty-declare-review.json) and
[empty Switch](coverage/semantics/plain-empty-switch-review.json) reviews.
Wider payload/protected/callback/resumable contexts gain no route; I140/I106 remain
entirely unstarted.

Computed-property reads in main or a direct ordinary reader leave the CV
receiver unpinned through an exact quiet global-rebind helper. Actual request-cell
identity, relevant reference constraints and a distinct retained old-object CV
bound entry; saved history remains source/context-only. Initialized public
untyped DIRECT slots also support terminal single isset and quiet coalesce with
an integer-literal RHS. Exact consumer/source/line continuations preserve quiet
NULL presence and lazy fallback; existing selected-value copy, cell/owner laws
and pending-writer defaults remain intact. Terminal nullsafe reads check the
original CV before the name, then fetch the current CV without a second checkpoint.
Wider helpers, callers and consumers
remain partial. Source/state/load cuts and original failures stay separate in the
[timing](coverage/semantics/property-cv-dynamic-name-review.json),
[reader/global-cell](coverage/semantics/property-reader-global-name-review.json),
[terminal-isset](coverage/semantics/property-terminal-isset-name-review.json),
[coalesce](coverage/semantics/property-coalesce-name-review.json) and
[nullsafe](coverage/semantics/property-nullsafe-name-review.json) reviews.

Current implementation/reviewer pairs work in private trees under `.tools/`;
their work remains unaccepted until integrated.

| Track | Current work and private trees |
| --- | --- |
| CLASS246 | Literal USER function-name string direct/FCC producer assessment under existing source, CODENAME/INIT and COPY0/1 bounds. |
| REF12 | ALIAS-to-quiet-stdClass array-leaf assessment, requiring fresh cell ownership, retargeting and singleton/shared-copy evidence. REF11 publication closes independently; all holds remain intact. |
| ENUM171 | Unprotected BYREF plain-CV lossy verification; native/current-root assessment of ENV borrowing and used result creation. |
| GC87 (held) | Quiet unique-outer nested-write assessment stopped after recurrent generic service flags; source-only notes preserved, no runtime edits or active jobs. |

Keep V110, GC35, I106, COMP123 and the paused boundaries below held. Preserve
private drafts and external raw evidence; [ARTIFACTS](docs/ARTIFACTS.md) records
recovery locations.

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
