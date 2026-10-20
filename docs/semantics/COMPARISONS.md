# Value comparisons

`52-comparison.watsup` defines `==`, `!=`, `<`, `<=`, `>`, `>=` and `<=>`
for null, booleans, integers, binary64 floats, byte strings and ordered arrays.
The checked source compiler folds eligible constants; ordinary evaluation uses
captured operands and delayed variable reads. `>` and `>=` evaluate operands
in original source order, then compare the resulting values in reverse order.
With NaN or arrays having missing keys, the three-way comparison can return
+1 in both directions; the `>` operator may therefore be false in both
directions. Negating a forward comparison is incorrect.

Null/string comparisons treat null as the empty string. Other boolean/null
comparisons use truth without emitting NaN conversion warnings. Number/string
comparison uses numeric parsing only for a complete numeric string and otherwise
compares formatted numeric bytes. String/string comparison additionally retains
integer overflow provenance from the numeric scanner: twenty significant digits
in the integer prefix set overflow before a decimal/exponent suffix is examined,
even when that suffix rescales the final float into integer range. Equal floats
from same-sign overflowed integer prefixes, and equal infinities, fall back to
original byte comparison. This follows the pinned engine, including its unusual
prefix behavior; the original draft disagreements remain in the ledger.

Undefined CV reads at scalar `<=>` now suspend through the ordinary warning
handler. The missing value stays null even if the callback initializes its name.
A later direct-CV right operand follows the callback's live binding; a computed
value remains captured. Known primitive left operands also survive a missing
right read. Normal, false-returning and throwing handlers keep their ordinary
reporting and unwind behavior. A defined scalar left CV also survives a missing
right read: its current wrapper is read after the callback, including a newly
created reference or rebinding to another scalar cell. The missing right stays
null. Removing the left CV or replacing it with an owning value remains explicitly
unsupported on return, without another warning. See the
[live-left review](../../coverage/semantics/undefined-spaceship-right-review.json).
Distinct direct-CV `==`/`!=`/`<`/`<=`/`>`/`>=` pairs also suspend with one missing operand
and a defined scalar counterpart. The missing value stays null while the opposing
wrapper follows callback writes, late reference creation and rebinding. A missing
right name can remain undefined throughout the callback. False handlers preserve
default Warning order; throws preserve destination/catch/finally. The opposing CV
must remain defined and scalar on return; removal or an owning value stops
Unsupported without another warning. The
[missing-left review](../../coverage/semantics/undefined-scalar-compare-review.json)
and [missing-right review](../../coverage/semantics/undefined-scalar-compare-right-review.json)
and [not-equal/less-or-equal review](../../coverage/semantics/undefined-scalar-compare-ne-le-review.json)
and [greater review](../../coverage/semantics/undefined-scalar-compare-gt-ge-review.json)
record the separate cuts. Zend evaluates `>`/`>=` source expressions left to right,
then reverses physical comparison operands. The single-missing/scalar-throughout
bound makes these source-oriented records valid; removed-right native probes
confirm one Warning without admitting that wider path. Second-Warning chains,
same-CV inputs, owning/removed counterparts and wider producers remain partial. Earlier spaceship cuts remain in the
[scalar warning review](../../coverage/semantics/undefined-spaceship-review.json).

Distinct loose-comparison CV pairs can also begin with both values missing.
Forward `==`/`!=`/`<`/`<=`/`<=>` warn for left first and freeze its NULL while the handler
defines current right. Reversed `>`/`>=` warn for source right first and freeze its
NULL while the handler defines current left. The first name may remain undefined.
A supplied throw suppresses the second Warning while retaining destination,
Exception identity and finally; `zval_undefined_cv` checks the pending exception
before reporting. Returning with the opposing name still missing remains explicit
Unsupported before the second-Warning chain. The spaceship path uses the same
left-frozen record and entry-only predicate; its existing scalar resume guard
still rejects a missing or owning right value. Same-CV, owning/removed counterparts
and wider producers remain partial. The
[forward review](../../coverage/semantics/undefined-scalar-compare-both-review.json)
and [reversed review](../../coverage/semantics/undefined-scalar-compare-both-reversed-review.json)
and [spaceship review](../../coverage/semantics/undefined-spaceship-both-review.json)
record the separate cuts. Affected older entry assertions now select the first
physical missing operand; these maintenance checks do not renew earlier results.

Array comparison first handles identical container identity, then recursion on
the left operand, element counts, and exact normalized key lookup in left
insertion order. Distinct insertion orders alone do not imply inequality.
Values behind references are dereferenced. A revisited left array raises
`Error: Nesting level too deep - recursive dependency?`; input roots survive
comparison and budget resumption. Strict identity remains a separate operation.

[Changed non-Stringable operands](../../coverage/semantics/nonstringable-redispatch-review.json)
after an ordinary `__toString` now finish against the saved first string. A live
stdClass or standard source instance with no effective method fails this second
implicit cast quietly and orders after the string. The original operand order,
CV/COPY/retained-cell identity and aggregate consumer remain intact; nonzero
leaves skip later casts. Explicit casts and other internal handlers are separate.

[Finite internal changed operands](../../coverage/semantics/internal-nonstringable-redispatch-review.json)
also admit normalized real/named Closure bodies and actual Generator/Fiber tags.
Their second implicit string cast fails quietly without executing the callable or
VM. Live admission checks allocation; existing saved text, signed order, retained
cells and cursors finish without a new receiver root. Other internal handlers remain open.

[Weak internal changed operands](../../coverage/semantics/weak-nonstringable-redispatch-review.json)
also admit live WeakMap and WeakReference objects, including wrappers with expired
referents. Their second implicit string cast fails quietly without reading private
entries or referents. Saved text, operand direction, copied values and retained
cells remain authoritative; nonzero array/property leaves skip later casts.
Existing explicit-cast and producer/lifetime domains are unchanged.

[Live WeakMap pairs](../../coverage/semantics/weakmap-comparison-review.json)
also return order zero before recursion protection or any private-entry traversal.
Empty versus populated and different-key/value maps compare equally; strict identity
stays separate. Existing array and declared-property cursors continue to later
values or real casts without adding map-value roots. Existing map producers and
lifetime forms remain partial.

[Mixed standard WeakMap comparisons](../../coverage/semantics/weakmap-mixed-comparison-review.json)
return uncomparable +1 against live stdClass, source INSTANCE and WeakReference
objects in either direction, before property, private-entry or recursion traversal.
Both operands must be allocated and nonfreeing. Reachable source instances use
standard handlers under the existing source/stdClass/finite Throwable parent-link
contract; other internal parents remain unsupported. Neither an effective
`__toString` nor an expired weak referent changes the class mismatch. The seven
operators retain the existing greater-operand reversal, so `<=>` returns +1 both
ways while `>` and `>=` stay false both ways. The mismatch adds no roots or guards;
array and declared-property scans stop before later leaves. Wider producer and
lifetime forms remain partial.

[Finite internal WeakMap mismatches](../../coverage/semantics/weakmap-internal-comparison-review.json)
also admit allocated nonfreeing builtin Throwable kinds, actual Generator/Fiber
and object-body-normalized real/named Closures. Zend selects the left comparison
handler; Closure falls back to standard comparison when the handler pointers differ.
Class mismatch returns +1 in both directions without inspecting captures, saved VMs,
private entries, formatter fields or caches. An exact unchanged-state effect and
negated guard on the older Throwable refusal keep the routes disjoint; non-map
Throwable property comparison remains unsupported. Three exact originals and
468 Boolean premises/16 actual steps cover direct operator rows, closed and paused/
suspended VMs, warmed Exception bytes, zero-prefix aggregates and skipped real tails.
Other Closure representations, internal/custom counterparts and wider lifetimes
remain partial.

[Method-Closure WeakMap mismatches](../../coverage/semantics/weakmap-method-comparison-review.json)
extend the same live allocated nonfreeing admission to normalized METHODCLOSURE
and ARRAYMETHODCLOSURE bodies from actual first-class method producers. Left Closure
fallback reaches the class mismatch before reading fake-Closure fields; Map-left
uses standard comparison directly. Seven-operator rows return `0100001` in either
direction, with strict identity unchanged. The mismatch reads no receiver/capture,
scope row or private entry and adds no roots or guards. Four direct and four genuine
zero-prefix aggregate steps preserve complete state apart from the consumed task,
reset BASE and result; later real casters are skipped. Other producers and wider
lifetimes remain partial. At the retained COMP71 cut, the computed STRING slice
failed before comparison and supplied no coverage for that producer.
[COMP82](../../coverage/semantics/stored-callable-carrier-review.json) later repairs
bounded named-function/static-method stored-name reception with fresh evidence;
none of these retained comparison cuts is replayed.

[Literal method-string WeakMap mismatches](../../coverage/semantics/weakmap-string-method-comparison-review.json)
also admit exact normalized STRINGMETHODCLOSURE under the same live allocated
nonfreeing guards. The Closure handler falls back before fake-Closure target/scope
fields, so class mismatch returns +1 in either direction without receiver or private
traversal. Source witnesses use fixed literals: bound parent selection on a child
and inherited static captures, including a cloned capture with its seed retired.
Two originals and 321 Boolean premises/8 actual steps preserve whole comparison
states, sole receiver owners, scope rows and skipped later aggregate casters. This
extends comparison admission; stored-name reception was outside that cut. Other
producer/representation/lifetime routes remain partial.

[Factory and rebound WeakMap mismatches](../../coverage/semantics/weakmap-factory-comparison-review.json)
extend the same bounded live admission to normalized FROMCALLABLECLOSURE and
BOUNDFAKECLOSURE. Both are native Closures: unlike-handler fallback precedes fake
function, target, receiver and binding fields. Seven-operator rows return `0100001`
in either direction, with strict identity separate. SOURCE indices and optional
copied pclosurescope ORIGINAL remain nonowning; only the current receiver is an edge.
Two exact originals and 361 Boolean premises/8 actual steps include cloned rebinding
on an overriding child after seed/old-receiver retirement, a separate live factory
capture and quiet later aggregate casters. Full source endings verify selected
receiver markers and Parent bodies. Other producers/representations and wider weak
lifetimes remain partial; that increment does not extend stored-name reception.

[Intrinsic/API WeakMap mismatches](../../coverage/semantics/weakmap-api-comparison-review.json)
also admit ordinary eligible INTRINSICCLOSURE and normalized FIBERAPICLOSURE bodies.
Intrinsic admission mirrors the existing ordinary callable predicate, excluding
factory, current-Closure, binding and Fiber special kinds in that representation.
The existing live allocated nonfreeing mismatch guards and unchanged-state ORDER1
effect remain authoritative. Unlike-handler fallback runs before callable/capture
fields, so comparisons neither invoke GC APIs nor start a cold captured Fiber.
Two originals and 279 Boolean premises/8 actual steps preserve the enabled flag,
sole bound Fiber ownership, callback-to-Map edges and skipped later aggregate
casters. Explicit source endings call the APIs and real bodies. This extends
comparison admission; it adds no INI, collection, ephemeron or producer protocol.
Special intrinsic representations and wider weak lifetimes remain partial.

[Fixed special API WeakMap mismatches](../../coverage/semantics/weakmap-special-api-comparison-review.json)
add exact normalized CURRENT and static BIND intrinsic Closure arms while leaving
the ordinary intrinsic guard unchanged. The Closure-left handler falls back and
the Map-left handler uses standard comparison; both decide class mismatch before
callable metadata. The common live allocated nonfreeing admission returns +1 with
unchanged state. Seven-operator rows yield 0100001 in both orientations, with strict
identity separate. Two originals and 372 Boolean premises/eight actual comparisons
preserve child-free APIs, nested REAL frames, Map/API captures, scopes/bindings
and private-value/key owners 1. The callback's original receiver keeps 2 owners
and its target keeps 1. Zero-prefix array
and declared scans stop before real later casters. Explicit API postcalls prove
CURRENT observes the executing real caller and errors outside, while BIND selects
the new receiver/body. The original literal binding-scope carrier source returned
interpreter_failure and stays zero; its sole ::class argument correction retains
the nested witness without API repair at that cut.
[COMP81](../../coverage/semantics/closure-binding-scope-carrier-review.json) later
extends binding-scope reception; COMP82 separately covers bounded stored callable
names. Other special forms and wider lifetimes stay partial. Eight raw steps
are comparisons, not invocation or binding transitions.

[Getter/factory WeakMap mismatches](../../coverage/semantics/weakmap-getter-factory-comparison-review.json)
also admit normalized GETTERCLOSURE and FROMCALLABLEFACTORY through the same live
allocated nonfreeing guards. Native Closure fallback runs before getter receiver,
method/source descriptors or factory site, returning +1 in either direction with
unchanged state. Both producers precede the unchanged-baseline comparison. Two
originals and 353 Boolean premises/10 actual steps cover builtin and inherited
getters, cold caches, trace-array and receiver-to-Map edges, a cloned getter after
seed/maker CV retirement and quiet zero-prefix aggregate tails. The receiver stays
live through its sole capture owner; the factory has no receiver edge. Later source
calls supply message/code values and a real factory-created body. One pre-main
fixture-type failure stays zero. No getter/factory producer, clone or lifetime
rule changes; special intrinsic captures and wider protocols remain partial.

[Sensitive wrapper/capture WeakMap mismatches](../../coverage/semantics/weakmap-sensitive-comparison-review.json)
admit raw initialized SENSITIVEVALUE and normalized CTORCLOSURE with the exact
SensitiveParameterValue base through the same live allocated nonfreeing guards.
The wrapper retains standard comparison: class mismatch precedes private-value
or property export. Its constructor capture is a native Closure, whose unlike-handler
fallback precedes receiver/source fields. Both return +1 in either direction with
unchanged state. Two originals and 264 Boolean premises/8 actual steps preserve
the wrapped Map, private/key owners, a cloned constructor after seed retirement and
wrapper array/CV removal, sole receiver ownership, quiet aggregate tails and budgets.
Explicit getValue and readonly-error source endings reuse existing protocols;
no constructor, clone or lifetime rule changes. SENSITIVEUNSET, other constructor
bases, special intrinsic captures and wider lifetimes remain partial.

[Initialized sensitive-value pairs](../../coverage/semantics/sensitive-value-review.json)
compare the private readonly slot through the standard object handler, independently
of hidden property export. Distinct wrappers sharing a Map are loosely equal;
scalar 2/9 and array/reference payloads determine signed order. Only unchanged-state
closed payload results are admitted, with left-object recursion protection;
callback/diagnostic effects remain explicit Unsupported. Three originals and
413 Boolean premises/11 actual transitions cover eight comparisons and three
shallow clones, preserving ownership, COW/shared aliases and checked budgets.
Equal wrapped values continue outer scans; differing values skip real later
casters. The later peer Stringable callback belongs to the existing outer scan.
One pre-main fixture syntax correction and both unchanged counterexamples stay
zero; uninitialized wrappers and wider protocols remain partial.

[Sensitive constructor-Closure pairs](../../coverage/semantics/constructor-closure-comparison-review.json)
compare equal for two authentic live raw CTORCLOSURE objects selecting the same
SensitiveParameterValue receiver. Each capture site is authenticated independently;
fresh sites and clones share the fixed fake-Closure function/scope metadata.
Different receivers return +1 both ways even when their wrapped Map is identical;
getter/constructor mismatch and strict identity remain separate. The unchanged
model completed normally with the wrong same-receiver rows before the module379
rule. Two originals and 448 Boolean premises/10 actual steps cover all seven
operators, whole states, retired seed/wrapper CVs, receiver and private/key owners,
scopes and budgets. Equal array leaves continue to integer tails (-1/+1); distinct
receiver leaves stop declared-property scans before real later casters. Explicit
readonly-Error calls and casts reuse existing protocols. Other representations,
constructor bases and wider lifetimes remain partial.

[Internal getter-Closure pairs](../../coverage/semantics/getter-closure-comparison-review.json)
compare by authentic receiver, getter method and C owner. The module234 clause now
admits two ordinary direct sources as well as factory selections, with both live
guards preceding indexing. Source sites remain independently authenticated. The
same receiver fixes called scope; the finite method/owner mapping fixes native
function metadata. Different receivers return +1 both ways even when their fields
and held Map match; different methods and strict identity remain separate. Three
originals and 617 Boolean premises/12 actual steps cover getMessage/getValue and
cold inherited __toString captures, preserving scopes, cache and receiver/trace/Map/
private-value/key ownership. Equal arrays continue to signed integer tails, while
distinct-receiver property scans skip real later casters. Later getter/formatter
calls reuse existing bodies. Both unchanged originals were normal-result mismatches;
the direct-to-factory route retained equality. Other representations and wider
lifetimes remain partial.

[Captured factory Closure values](../../coverage/semantics/factory-closure-values-review.json)
compare equal when both raw FROMCALLABLEFACTORY tags have live authenticated sites:
the fixed receiver-free fake function/scope metadata agrees independently of site.
Strict identity and different intrinsic-method captures remain distinct. Cloning
copies the authenticated occurrence into a fresh allocation without scope/binding
rows or children. Three originals and 271 Boolean premises cover four comparisons,
two clone transitions and one getter body. Zero-prefix arrays continue through equal
factory leaves to signed integer tails; a factory-created getter survives retirement
of every factory, callback array and receiver CV with saved nonowning provenance.
Physical receiver owners fall from 2 to 1 when its actual getter task completes.
The unchanged pair was a full normal-result mismatch; the clone returned a failed
derivation, not Unsupported. One budget-fixture failure retains zero; its corrected
full-driver resumption check includes ownership/GC. Wider factory forms, transformed
representations and clone-with-properties remain partial.

[Generator/Generator and Fiber/Fiber pairs](../../coverage/semantics/generator-fiber-comparison-review.json)
return order zero through the standard zero-default-property shortcut. The pair
predicate tests arena bounds and exact runtime tags, independently of saved VM
state or captures, before any property traversal or recursion protection. Strict
identity, cross-class and Closure controls agree with PHP. New, suspended and
completed fronts preserve storage; array/declared-property comparisons continue
to later values or real casts. Internal numeric Notice admission remains separate.

[Numeric object Notices](../../coverage/semantics/object-numeric-comparison-review.json)
now suspend ordinary source instances compared with int/float through module402
and the existing error-handler machinery. The failed cast captures the numeric
type; after handling, private 1/1.0 is compared with the captured opposing CV,
pre-unwrapped cell, property/array location or copied value. A newly read ordinary
object emits a second Notice against that saved number, without rereading the
original pointer afterward. Numeric conversion does not invoke `__toString`.
Aggregate cursors retain their original arrays/declared slots and guards across
the callback; only zero resumes later entries. Notice↔Stringable handoffs preserve
the same source consumer and selected-case continuation.

The raw handler is disabled during its own body and restored before subsequent
Notice dispatch. The original quiet-terminal cancellation remains available.
A [bounded pending-exception remainder](../../coverage/semantics/pending-exception-comparison-review.json)
also skips later registered Notice callbacks and source `__toString` calls,
while Notices excluded by the live handler mask retain default reporting.
The original thrown object reaches catch/finally after the C comparison finishes;
only events and the fatal snapshot may change. Builtin Throwable/string formatting,
materialization, cache updates, recursion and wider lifetime effects remain outside
this adapter. Documentary receiver/leaf images add no owner;
actual operands, cursor pins and callback selection retain their existing roots.
[Builtin and inherited Throwable string casts](../../coverage/semantics/pending-throwable-comparison-review.json)
also skip their internal handler in this authenticated pending remainder. The
failed cast gives object-after-string order without reading formatter fields,
previous links or caches; its nonzero result stops before later numeric Notices.
Cold/warm caches, both orientations, array/property scans and same-error cleanup
pass three exact sources and 509 Boolean premises/11 raw steps. Normal formatting
and calls executed by source finally remain on their existing routes.
[Builtin stdClass leaves](../../coverage/semantics/stdclass-numeric-comparison-review.json)
now use the same int/float Notice route. A local class image distinguishes their
fixed name from real source origins in both phases; allocation is checked at
admission, while documentary post-message images require bounds and kind.
Second Notices compare private 1/1.0 without rereading a late live value.
[Throwable numeric leaves](../../coverage/semantics/throwable-numeric-comparison-review.json)
add finite builtin kinds and source descendants with authenticated internal
parents. Names come from the kind or source class, never allocation origins.
Numeric conversion does not call `__toString` or read formatter fields;
caches and previous links stay intact. A direct static read is a copied value,
distinct from an aggregate pre-unwrapped cell retained across rebinding.
[Finite Closure/resumable numeric leaves](../../coverage/semantics/internal-numeric-comparison-review.json)
now admit normalized real/named Closure bodies and actual Generator/Fiber tags.
Their fixed names authenticate Notice messages without consulting callable, capture
or VM contents. Live admission checks allocation; documentary post-message images
check bounds and tags without adding owners. Private second-Notice targets and
existing aggregate pointers/guards survive handlers. The numeric cast itself
does not invoke a callable or resume a VM.
Other Closure bodies remain outside that original admitted slice.
[WeakMap and WeakReference numeric leaves](../../coverage/semantics/weak-numeric-comparison-review.json)
also authenticate fixed builtin Notice names through exact outer tags. Live admission
requires allocation and nonfreeing storage; documentary post-message images use only
bounds and tags, without reading private entries or weak referents. Expired referents
remain valid. Captured 1/1.0 and existing CV/COPY/retained-cell selection govern both
callbacks, even after live9 writes. The authenticated pending remainder skips later
eligible weak Notice handlers and string casts while preserving the same Throwable.
Real ALIAS/COW cursors, private-value ownership and fresh guard cleanup retain the
existing mechanisms. Wider producer, handler and lifetime forms remain partial.

[Initialized SensitiveParameterValue numeric leaves](../../coverage/semantics/sensitive-numeric-comparison-review.json)
use the same Notice route with a fixed builtin image/name. Live admission checks
allocation and nonfreeing storage; documentary images use only bounds and the raw
initialized tag. The numeric cast neither exports nor unwraps the private value.
Private 1/1.0 retains the original scalar type across both callbacks, while captured
CV/COPY/retained-cell selection and aggregate COW keep their existing behavior.
Two originals and 373 Boolean premises/14 actual transitions cover both orientations,
SECOND redispatch, supplied throw, skipped later callbacks and fresh guard cleanup.
Wrapped Stringable/Map/scalar9 values remain untouched until explicit source use;
creating the primary clone and retiring its seed are source prerequisites,
without new clone-step credit.
Uninitialized wrappers and private-payload comparison effects remain separate.

[Method Closure numeric leaves](../../coverage/semantics/method-numeric-comparison-review.json)
add exactly normalized METHOD/ARRAYMETHOD/STRINGMETHOD images to the existing
Closure class. Live admission still checks allocation/nonfreeing; the documentary
post-message image needs only bounds and the saved body. Two originals and 381
Boolean premises/11 actual transitions preserve CV/COPY selection, signed order,
cross-tag SECOND numeric targets, authentic scope rows and physical owning edges.
A real first handler may retire its selected capture, receiver, held Map and private
value before comparison returns. The saved image stays valid without those owners,
weak observers return null and private 1/1.0 finishes normally. Captured methods
and private casters are not invoked by the comparison. Later explicit calls/casts
and clone/seed retirement reuse existing rules; other representations and wider
lifetimes remain partial. Producer/visibility/magic-callable admission is unchanged.

[Factory and API Closure numeric leaves](../../coverage/semantics/closure-numeric-comparison-review.json)
extend the same class image to normalized fromCallable, bound-fake, finite getter,
exact SensitiveParameterValue constructor, fromCallable factory, ordinary eligible
intrinsic, CURRENT/static BIND and Fiber API captures. Ordinary intrinsic eligibility
is exactly148's predicate; the two Closure API kinds have separate exact arms.
The synthetic FROM/BINDTO/FIBER_CURRENT exclusions are local predicate checks,
without a blanket claim about every raw Fiber kind; unproduced INVOKE stays excluded.
Four originals and 594 Boolean premises/17 actual transitions preserve CV/COPY,
private typed SECOND targets and whole dispatch/result/budget states. Actual first
handlers retire the bound capture/receiver/Map/private graph or cold Fiber/callback
graph; retired SOURCE/copied ORIGINAL and WeakReference targets remain nonowning
history. Documentary class images then remain valid while fresh live admission
fails. Later real calls and explicit casts reuse existing routes, with GC evidence
limited to the enabled flag and noninvocation. The 24 native Notices, source clone
prerequisites and 18 pure controls remain separate from raw transition credit.

Other internal/custom comparison handlers, legacy materialized callbacks without a
retained cursor and wider handler/lifetime behavior remain open.

Evidence derives from `vendor/php-src/Zend/zend_operators.c` (`zend_compare`,
`zendi_smart_strcmp`, `_is_numeric_string_ex`) and `zend_hash.c`
(`zend_hash_compare_impl`); `zend_compile_greater` establishes evaluation order.
`tests/semantics/comparison.py` covers original source, compiler folding,
scanner boundaries, array identity/cycles, delayed operands and resumed states.
The full source campaign also includes retained phase/line originals and errors.
Full object/resource handler coverage and engine stack exhaustion remain pending;
these bounded increments do not close the complete operator family.
