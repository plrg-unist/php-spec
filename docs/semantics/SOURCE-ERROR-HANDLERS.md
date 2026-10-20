# Source error handlers

This slice targets PHP 8.5.10 CLI NTS 64-bit. Modules206/207/211/215/221 implement
`error_reporting`, `set_error_handler`, `restore_error_handler`,
`get_error_handler`, `trigger_error` and `user_error` through the checked source
call machinery. Its bounded private source/frame gates and fresh current-master property,
array-caller and trace interactions are independently accepted.

Registration stores the raw callback and signed32 mask, and pushes the previous
pair even when clearing the callback. Dispatch resolves the raw callback again
and supplies severity, message, filename-or-null and line. Named functions,
closures, public concrete source `__invoke`, ordinary public method arrays and
class-method strings are admitted. Referenced array members are read at dispatch;
later mutation preserves the entered selected target. Copied direct members
still authenticate its method bytes and selector. Malformed arrays and known
public lookup failures preserve ordered PHP diagnostics. Pending callbacks,
the registration stack and entered targets retain their real heap owners.

Class-name API callbacks use the genuine emitting USER frame for compatible
implicit `$this` and called-class forwarding; requested Parent descriptors stay
distinct from an overriding Child. This differs from computed direct method
dispatch. The selected target authenticates against that saved emitter, while
mutable referenced members remain opaque after entry. Static selections retain
no receiver; a raw object-array callback still owns its selector until dropped.
The registry retains raw values, rather than caching an entered target.

Keyword class selectors and qualified array methods use resumable deprecations
at registration and dispatch. Outer keyword choice precedes its warning; the live
array method then determines the inner class and split before the compound warning.
Referenced method bytes are read afterward. Dispatch disables the current handler
before these selection warnings. The new API target authenticates compound
`self`/`parent` selection with a foreign `$this`, while ordinary scoped carriers
retain their existing rules. Requested methods take priority over declared
actual-receiver fallback. Inaccessible fallback methods expose the getter's `Error`
at registration; delayed dispatch replaces it with an `Invalid callback` error
whose previous exception retains the getter error, and restores the raw handler.
[The callable contract](SOURCE-METHODS.md#deprecated-api-keyword-and-compound-callables)
and [221 ledger](../../coverage/semantics/keyword-compound-callables-current-review.json)
describe these stages and their remaining consumers.

Eligibility depends on the handler mask, independently of `error_reporting` or
`@`. The active raw handler is cleared during the callback, allowing an installed
replacement to handle a nested diagnostic. Automatic normal/throw cleanup restores
the old raw handler only if no replacement remains; it preserves the live mask.
Only exact `false` requests default reporting, using the mask after the callback.
Callback `finally` runs before restoration; caller catch/finally runs afterward.

[Object/numeric comparison Notices402](../../coverage/semantics/object-numeric-comparison-review.json)
now provide the producer continuation for ordinary source instances against
int/float. The original severity/message/file/line reaches the handler before
comparison resumes with private 1/1.0 and a live CV/cell or copied opposing value.
Restoration permits a second Notice after the first callback; the same handler
stays disabled during its own nested numeric comparison. Captured aggregate
owners and recursion guards persist through the actual handler frame/finally.
A thrown handler retains the original quiet-terminal path. The
[bounded remaining comparison](../../coverage/semantics/pending-exception-comparison-review.json)
now skips later PHP callbacks while preserving excluded numeric Notices through
default reporting and the original thrown identity through catch/finally.
Null registration inside the handler still permits automatic raw restoration;
a real replacement with a Notice-excluding mask produces the default Notice.
Throwable formatting and wider storage/lifetime effects remain outside this adapter.

[Pending Throwable comparisons](../../coverage/semantics/pending-throwable-comparison-review.json)
now skip builtin and inherited internal string handlers within the authenticated
numeric C remainder. Their failed cast stops before later masked default Notices,
without reading formatter fields or changing caches and previous links. The same
thrown object reaches catch/finally; source-finally calls and normal post-catch
formatting retain their existing behavior.

[Builtin stdClass comparison Notices](../../coverage/semantics/stdclass-numeric-comparison-review.json)
retain the fixed class name, severity and original file/line through PRIMARY
and restored SECOND dispatch. A second float Notice keeps private 1.0 despite
the handler writing 9.0 to its old cell; throw/finally uses the same quiet
remainder cancellation and handler restoration. No receiver owner is added.

[Throwable numeric comparison Notices](../../coverage/semantics/throwable-numeric-comparison-review.json)
preserve finite builtin and real source-subclass names through both phases.
Numeric failure invokes no `__toString`, even a source override. A second
handler can throw the original compared Exception while preserving its
previous link, cold cache, caller catch/finally and existing quiet cancellation.

[Closure, Generator and Fiber comparison Notices](../../coverage/semantics/internal-numeric-comparison-review.json)
reuse restoration and saved 1/1.0 through both phases for admitted runtime tags.
A captured real Closure can become the second receiver and throw the supplied
TypeError while retaining genuine child edges, recursion guards and finally cleanup.
The numeric cast itself does not invoke a callable or resume a VM; those sources
retain their original quiet pending-exception validation cut.

Private-final compiler diagnostics retain E_COMPILE_WARNING (128) severity
and bypass callbacks in both direct reporting and dynamic compile queues.
The reporting mask still controls display. E_WARNING (2) and E_DEPRECATED (8192)
remain eligible even when the global mask omits them. Two exact original eval
programs and 231 source-frontier checks plus 10 pure reporter projections validate
that distinction, including an original shared Throwable before caller catch;
[the severity ledger](../../coverage/semantics/compiler-warning-severity-review.json)
keeps the initial mismatch separate. Wider compiler producers remain required.

Direct trigger callbacks receive arguments weakly through the internal trigger
frame. Implicit user-opcode callbacks preserve source strictness. Byref callback
parameters receive temporary references to four passed values, with ordinary
default warnings while the original handler is disabled. Trigger traces retain
the converted message and original supplied level. `E_USER_ERROR` first raises
its deprecation; a thrown deprecation prevents the fatal phase. Default fatal
handling exits255 even when reporting is masked. Masked fallback displays nothing;
unmasked fallback displays its fatal diagnostic and captured stack. Fatal arguments
are captured before the callback; later errors clear that snapshot even when
masked. A nonfatal false fallback preserves any inner fatal snapshot, rendering
its stack without adding heap owners. Fatal bailout precedes raw restoration.

[Binding-warning callbacks](../../coverage/semantics/binding-warning-trace-review.json)
now register their held API context through the same hooks. Fresh Exceptions retain
an internal handler frame, bind/bindTo frame and ordinary caller, using original
captured arguments after live CV writes. A strict-source string severity parameter
receives `2` weakly from the C callback. Explicit trace arguments own their values;
bindTo's implicit Closure owner does not become an argument. Three exact sources
and 241 Boolean premises/eight typed steps cover fresh allocation, dispatch,
throw and trace return, with source-only weak reception/finally/retirement evidence
kept separate from raw-step credit. Other producers/lifetimes remain partial.

Missing-CV read continuations suspend the existing consumer and retain a null
result even if the callback defines the variable. The admitted consumers are
output, simple assignment, unary signs and six arithmetic/identity operators.
Scalar `<=>` additionally admits a missing left CV with a captured primitive or
defined direct-CV right operand, and a captured primitive or defined scalar
direct-CV left with a missing right CV. The latter follows the current left
wrapper after the callback, including reference rebinding; it adds no borrowed
old-cell owner. If the callback removes this already checked left CV, the exact
right-frozen spaceship record restores a known-NULL left task and compares to 0
without another Warning. A surviving alias retains its cell; the missing right
name need not be initialized. The
[checked-left removal review](../../coverage/semantics/undefined-spaceship-checked-unset-review.json)
checks quiet restoration separately from an unread right removed during a
missing-left Warning, which still warns again.
Distinct direct-CV `==`/`!=`/`<`/`<=`/`>`/`>=` pairs also admit either missing
operand with an initially defined scalar counterpart, following that counterpart's
current wrapper after the callback. A missing right name need not be initialized.
Both protocols freeze null while preserving the opposing read. Other owning
comparison counterparts remain unsupported; a missing later physical CV can warn
again after the first read, including one removed by the first handler.
All seven comparisons permit a live flat primitive array at the opposing CV on entry or return, including
reference rebinding and COW. Both-missing/shared-name entries retain physical order.
Current arrays compare by emptiness against frozen NULL; rebound scalars keep
their ordinary rules. Nested/internal-object entries remain partial; the
[spaceship](../../coverage/semantics/undefined-spaceship-array-resume-review.json)
and [Boolean array resume reviews](../../coverage/semantics/undefined-scalar-compare-array-resume-review.json)
record resume bounds, certificates, roots and discard. The Boolean extension
keeps physical order, current alias/COW ownership and known-NULL second records.
The [initial-array extension](../../coverage/semantics/undefined-comparison-initial-array-review.json)
widens only four entry premises: saved reads add no initial-table owner, and
existing quiet-removal, unread-retry, scalar/array resume and discard stay exact.
At `<=>`, captured allocated flat DIRECT primitive tables enter through
two exact saved-read shapes. Existing TASK/RESULT/BASE roots retain snapshots
through callback COW and source removal, then release the saved owner on compare or throw;
see the [captured-array review](../../coverage/semantics/undefined-spaceship-captured-array-review.json).
The six Boolean operators now admit captured flat arrays with bounded source
certificates checking the missing direct CV and both compiled expressions. Their
scalar default explicitly rejects known arrays, so liveness/flatness cannot be
bypassed. Saved owners and generic restore/discard are unchanged; the
[Boolean captured-array review](../../coverage/semantics/undefined-scalar-compare-captured-array-review.json)
records source, COW and abrupt-release checks. Those certificates also admit
captured primitives while preserving both compiled descriptors and the missing CV.
Current alias writes cannot replace the saved bytes/value, and actual second
Warnings still freeze NULL; see the
[primitive review](../../coverage/semantics/undefined-scalar-compare-captured-primitive-review.json).
All seven comparisons now admit captured ordinary non-Stringable objects through
the generic saved shapes. Boolean known objects cannot bypass their live-domain
guard through the scalar default. Existing saved roots retain identity and shared
property effects. When no other owner remains, saved-operand release runs the
destructor before the outer store or catch; surviving aliases retain their lifetime.
See the
[captured-object review](../../coverage/semantics/undefined-comparison-captured-object-review.json).
Live direct-CV ordinary objects also enter/resume through their current unblocked
defined cell, without adding a saved object root. Rebinding can destroy the old
object inside the handler; replacement lifetime follows current owners through
normal return or supplied throw. Existing removal/retry and source certificates
stay unchanged; see the [live-object review](../../coverage/semantics/undefined-comparison-live-object-review.json).
The existing flat-array entry guard now receives the reached state and admits
DIRECT primitive or live ordinary-object leaves. Saved tables retain their
children through COW; current-table replacement may release them inside the
callback. Final table release runs child destructors only when no other object
owner remains. Source certificates, roots and restore/discard stay exact;
Object/array-valued ALIAS entries and nested/internal/Stringable leaves remain partial. See the
[object-array review](../../coverage/semantics/undefined-comparison-object-array-review.json).
Primitive ALIAS entries also pass when their cell is a live allocated reference
with a defined primitive payload. Saved table roots retain the entry-to-cell
edges; table owners do not multiply them. COW unwraps singleton references while
shared cells preserve writes across copies, including after a saved table is
released by a throw. Source/restore/discard machinery stays exact; the
[reference-array review](../../coverage/semantics/undefined-comparison-reference-array-review.json)
records normal/default/throw cell lifetimes and budgets.
Internal/Stringable objects, resources, nonflat arrays and wider producers remain partial.
Source certificates stay valid through those changes;
entry/resume domain guards refuse unsupported values without another Warning.
[The equality/less review](../../coverage/semantics/undefined-scalar-compare-review.json)
and [missing-right review](../../coverage/semantics/undefined-scalar-compare-right-review.json)
and [not-equal/less-or-equal review](../../coverage/semantics/undefined-scalar-compare-ne-le-review.json)
and [greater review](../../coverage/semantics/undefined-scalar-compare-gt-ge-review.json)
record the scalar continuations and their separate validation cuts. Greater
operators reverse physical VM operands; the same source shapes apply within the
single-missing/scalar-throughout bound.
Both-missing distinct direct CVs may enter the first Warning: forward
`==`/`!=`/`<`/`<=` freeze left NULL before reading current right;
reversed `>`/`>=` freeze right NULL before reading current left. The first
name may remain undefined. `<=>` shares forward entry and can fetch a missing
right afterward. The shared ingress-only predicate distinguishes both
shapes; a missing later physical CV can trigger the second Warning below. A pending
Exception suppresses the second Warning and follows ordinary discard. The
[forward review](../../coverage/semantics/undefined-scalar-compare-both-review.json)
and [reversed review](../../coverage/semantics/undefined-scalar-compare-both-reversed-review.json)
and [spaceship review](../../coverage/semantics/undefined-spaceship-both-review.json)
record fresh owners and entry/resume separation. `<=>` also permits the same
initially missing CV twice: first NULL stays frozen while the second read sees
the shared name initialized by the handler. The
[same-variable review](../../coverage/semantics/undefined-spaceship-same-review.json)
records its one-premise entry extension; source/resume/discard stay unchanged.
Forward `==`/`!=`/`<`/`<=` also admit one missing ordinary CV twice, reusing the
first-NULL/current-read record. Both compiled CV occurrences still authenticate
the source. A scalar or reference initialized by the first handler can make
equality nonreflexive; the
[Boolean same-variable review](../../coverage/semantics/undefined-scalar-compare-same-review.json)
records false/default and supplied-throw checks. The
[shared second-read review](../../coverage/semantics/undefined-scalar-compare-second-same-review.json)
also permits the first callback to leave or remove that name: the next Warning
freezes its second NULL, independent of later writes or continued absence.
All seven comparisons, with distinct or shared direct CVs, now restore when
the later physical CV remains missing or was removed
by the first handler. Existing ingress stages its second Warning and known-NULL
record; later writes cannot change the NULL/NULL result or cause a third Warning.
[Second-Warning review](../../coverage/semantics/undefined-spaceship-second-review.json)
covers both callbacks, default order and second supplied throw. No task variants,
fields or discard rules are added. The
[forward review](../../coverage/semantics/undefined-scalar-compare-second-review.json)
adds only a narrow known-NULL-left source arm authenticating both compiled,
direct CVs and the RHS read line. The
[reversed review](../../coverage/semantics/undefined-scalar-compare-second-reversed-review.json)
adds an exact right-frozen restore and NULL-only right INPUT certificate,
authenticating both compiled CVs before the source-left second Warning. Its
default reports stay right then left; late reference creation cannot change the
two captured NULLs. The
[shared reversed review](../../coverage/semantics/undefined-scalar-compare-reversed-same-review.json)
admits identical CV names only for the greater operators' right-frozen shape and
inverse NULL-only certificate; ordinary forward right-frozen shapes stay distinct.
Owning comparison values outside the flat-array bound and wider producers remain partial.
Forward `==`/`!=`/`<`/`<=` also quietly fold a checked left CV removed during a
missing-right Warning to NULL against the frozen right NULL. Their distinct scalar
right-frozen record preserves surviving alias owners and yields true/false/false/true
without another report; see the
[forward checked-left review](../../coverage/semantics/undefined-scalar-compare-checked-unset-review.json).
Reversed `>`/`>=` now also consume an already checked source-right CV removed
during the missing-left Warning quietly. Their old left-frozen record preserves
TASK/first NULL and restores RESULT as NULL, yielding false/true with surviving
aliases and one report; the opposite unread-left path still warns again. The
[reversed checked-right review](../../coverage/semantics/undefined-scalar-compare-checked-unset-reversed-review.json)
records this bounded restore. Other owning values and wider producers remain partial.
Missing-left binaries retain the later right read; missing-right binaries admit
known or temporary values and initially-reference CVs in strict identity comparisons.
Module208 retains the borrowed old cell through the saved caller without adding
an owner; rebinding and in-place alias writes remain distinct. Module213 adds six casts, selected value copies and ordinary by-value sends,
retaining selected targets and prior argument owners. Direct ASSIGN also performs
its captured-null destination write after a thrown handler. Module220 adds
rejected constrained writes with unchanged values and caller TypeError/previous
priority; private source/state gates and a current scoped-handler interaction pass.
Other live left operands, read-modify-write, dimensions
and other eligible warning producers remain
explicitly `Unsupported`, rather than running a callback after a consumer.

[Destructuring key warnings](SOURCE-DESTRUCTURING-WARNINGS.md) include module410's
lossy float CV conversion at value and reference fetches in flat direct-CV source patterns.
Defined null CV keys also deprecate before selecting the empty string at value or
reference fetches. For value fetches, their captured array or source cell survives
key retirement/rebinding;
lookup follows the callback and a miss enters module409 before storing null.
Undefined CV keys at these by-value fetches first warn under their own table
protection. A surviving table then enters null conversion without rereading the initialized or rebound key;
expiry at the first release skips deprecation and lookup. Separate callbacks can
handle the variable Warning, null deprecation and missing-key Warning, with a
deprecation-only handler still following default variable reporting.
For lossy-float value fetches, it retains the converted integer and table before E_DEPRECATED,
then looks up the table after return. A present embedded reference reads its new value; a miss enters the
module409 warning before any target store, honoring handler replacement and
default deprecation before an E_WARNING-only handler. Throws cancel lookup and
result delivery. In mixed patterns, a by-value fetch also protects the old table
alongside its saved source cell. Releasing that protection precedes lookup:
retirement silently supplies null, while a surviving table can enter the missing
warning. Later reference fetches and result delivery resolve the saved cell,
including after source-name rebinding or null replacement. A selected lossy-float or defined-NULL reference
fetch first makes its source writable before dispatch. Null or reference-wrapped
false creates an empty mutable array without a false-conversion deprecation; an
undefined CV first acquires a null reference silently. The key handler sees the
created table, and a throw preserves earlier null stores while cancelling binding.
When the source and NULL key share a cell, initialization instead makes the key an
array and raises `TypeError` before deprecation or binding.
After protection is released, exactly one remaining table owner permits reference
acquisition there; zero or multiple owners yield a fresh detached null reference.
For a key still NULL after preparation, existing empty-slot aliases are read after
the callback; key writes cannot redirect that selection or its reference identity.
Writable missing slots are created silently, and throws cancel binding. Wider
conversion producers remain partial.

Array-literal module413 freezes a finite lossy-float CV key across deprecation,
then reads a live unwrapped null/bool/int/float element CV or inserts its retained
runtime array temporary. The builder stays owned through the callback and is
released on throw; duplicate positions and later item evaluation stay ordered.
Reachable objects and owning CV values remain outside the initial scalar/temporary
producer.
The [array-literal ledger](../../coverage/semantics/array-literal-float-key-warning-review.json)
records its separate source/state cuts. A reference-element continuation now
transfers its acquired owner when the CV still names the same cell, including
unset/rebind to that cell. Retargeting to an ordinary null/bool/int/float inserts
the live scalar and preserves the acquired count, cancelling old debt first or
retaining an unmatched request owner, also on throw.
Ordinary-scalar completion admits primitive or bounded untyped flat-array old
values and keeps the builder object-free.
The [reference-element ledger](../../coverage/semantics/array-literal-float-ref-key-warning-review.json)
records repeated owners and singleton-copy observations. Different-reference
retargets now preserve both the old owner and a per-cell new-owner deficit through
return and supplied throw. Admitted primitive cells
may be shared or unwrapped according to their effective count. Inverse retargeting
cancels the biases. The [deficit ledger](../../coverage/semantics/array-literal-float-ref-deficit-review.json)
checks deletion, abrupt cleanup and balanced lifetime. Validated ordinary live
instance-property type sources now survive the same callbacks and cleanup.
Physical singleton copies unwrap without the constraint; shared copies and the
original property aliases still enforce/coerce typed writes. The
[typed-source ledger](../../coverage/semantics/array-literal-float-ref-types-review.json)
checks int-property singletons, two sources, typed old cells and supplied throws.
Untyped wrappers may also contain mutable nonpool flat arrays. DIRECT entries
hold null/bool/int/float or validated byte strings; ALIAS entries satisfy the
primitive bounds below. Wrapper debt and child-table
owners remain distinct across singleton unwrapping, later child COW, entry
deletion and supplied-throw builder cleanup.
Old arrays also complete with ordinary-scalar DIRECT insertion, retaining their
acquired wrapper count or cancelling its existing debt. Repeated unmatched counts
remain request owners, and their child table keeps ordinary COW semantics. Both
payloads must differ from the builder. The [array-to-scalar ledger](../../coverage/semantics/array-literal-float-ref-array-scalar-review.json)
checks live scalar values, normal/throw ownership and debt cancellation.
The [flat-array ledger](../../coverage/semantics/array-literal-float-ref-arrays-review.json)
checks stable/inverse transfer and safe final retirement. Effective-zero retirement,
array-valued type sources, nested or pooled/immutable
arrays, other owning values, static/hooked/queued or retired sources,
coercion/backing records, active collection and outstanding request-end debt remain
explicit Unsupported before pruning.

Ordinary by-value array CVs have their own table continuation. It pins the old
table across the handler, inserts an unwrapped live array CV, and separately
tracks the old HARRAY owner and omitted new-table owner. Same-table transfer does
not require the original CV cell to survive. Array payloads must be mutable nonpool
flat arrays with the same bounded DIRECT or ALIAS entries,
distinct from the object-free builder.
Deletion and supplied-throw cleanup preserve net table counts; an inverse retarget
balances them before normal COW and teardown. The [ordinary array-CV ledger](../../coverage/semantics/array-literal-float-array-cv-review.json)
keeps its source/state cuts separate. Mixed null/bool/int/float and flat-array
retargets also resume: initial scalar admission captures no table, while initial
array admission pins its old table. Scalar-to-array insertion owes an owner or
cancels a retained count; array-to-scalar insertion preserves the acquired count
or cancels debt. The same updates apply to supplied-throw cleanup. These two
initial plans remain disjoint, and captured runtime-array temporaries incur no
debt. The [mixed-CV ledger](../../coverage/semantics/array-literal-float-mixed-cv-review.json)
records balanced cycles and entry-independent deletion/throw deficits. Initial
wrapped string CVs, wider tables and unsafe debt retirement remain Unsupported.
An initially ordinary array CV can become an untyped wrapper during conversion,
so even a by-value item may insert ALIAS rather than DIRECT. Its retained old
HARRAY owner and omitted new-CELL owner survive deletion or builder retirement.
A reciprocal reference-element callback can unset/recreate an ordinary array CV,
whose DIRECT insertion cancels both biases before cleanup. The
[CV/reference cycle ledger](../../coverage/semantics/array-literal-float-cv-ref-cycle-review.json)
checks primitive/array wrapper payloads, singleton versus shared copies, child
snapshots and old-table COW. These new arms exclude outer property/coercion/backing
records and direct string CELLs, retaining the initial classifiers, source/error
authentication and existing positive-lifetime guard.
Initially wrapped array CVs use the same ARRAY marker with a borrowed
REFERENCE payload-slot locator. Zend dereferences before dispatch, so a callback's
new CV binding is ignored while writes through the surviving old alias supply the
DIRECT array value. The acquired old table remains owned; the captured CELL adds
no root. Source authentication reconstructs the actual VARIABLE spelling/line and
can survive locator retirement, while readiness requires an allocated marked
CELL without CELL debt or coercion/backing records and a bounded array payload
in the same logical-pruned live set. Missing live slot ownership, strings/objects and the
active builder refuse explicitly. Deletion/throw preserves the HARRAY deficit;
a separate ordinary table owner keeps it positive until the reciprocal slot
retarget balances both table biases. The
[wrapped array-CV ledger](../../coverage/semantics/array-literal-float-wrapped-array-cv-review.json)
separates fresh stable/cycle/deletion/throw witnesses from the unchanged initial
scalar/ordinary gates and graph/count/prune/driver algorithms.
Initial wrapped primitives now earn BORROWED ROOT in the existing scalar marker.
Only the builder is rooted; the captured CELL must remain live independently.
A separate completion helper reads primitive or bounded-array payloads from that
slot, leaving global input/value/live classifiers exact. ARRAY capture can also
complete as a DIRECT primitive. Opposite captured-slot cycles cancel table debt
or retained counts through normal and throw cleanup, while source metadata can
still authenticate a retired locator before readiness refuses. The
[wrapped mixed-CV ledger](../../coverage/semantics/array-literal-float-wrapped-mixed-cv-review.json)
records fresh bool/int/float/NULL and table-copy witnesses. Captured slots may
also use existing nonempty unique ordinary property sources whose types accept
the payload. Their objects must survive the same logical pruning even debt-free;
source authentication remains metadata-only, while readiness/discard refuse a
missing source object despite a positive CELL/payload count. The
[typed captured-CV ledger](../../coverage/semantics/array-literal-float-typed-wrapped-mixed-cv-review.json)
checks fresh public int|array coercion/rejection, safe source detach and independent
DIRECT copies through normal/deletion/throw cycles. Type/write helpers and all
marker roots remain exact; direct strings, wider sources and unsafe lifetimes
stay excluded.
An ARRAY returned by an ordinary no-argument named function also survives the
float-key callback as a frozen owning value. Authentication uses its checked
nonconstant call occurrence, compiled name without fallback, active user function
and by-value signature; current producer globals do not participate. The existing
KNOWN task/frame owner transfers directly to the literal, with no count bias.
The [return-value ledger](../../coverage/semantics/array-literal-float-return-array-value-review.json)
checks global/reference sources, COW, sole-owner entry deletion and supplied throw.
By-reference returns, arguments and wider call producers remain outside this arm;
existing mutable/nonpool, builder and object-free readiness guards stay exact.
A defined NULL key on a by-value literal CV item now has a separate Deprecated
continuation. Zend backs up the value and restores its captured ordinary CV after
the handler, before either empty-string-key insertion or supplied-throw cleanup.
The handler's writes remain observable inside its body. Distinct key changes
survive; a shared key/value NULL CV is restored too. Source authentication keeps
the checked item/spelling/line, while readiness requires the same live unmarked
slot and safe current payload. ARRAY snapshots remain allocated owning arguments
when throw cleanup pops the saved marker, so restoration precedes pruning even
without another old-table owner. The
[NULL-key ledger](../../coverage/semantics/array-literal-null-key-warning-review.json)
checks two saved table edges, normal COW/deletion and restoration before catch.
Unset/rebound ordinary slots, typed/coercion/backing slots, direct strings/objects
and wider payload graphs stay Unsupported; the paused LIST-key boundary is unchanged.
An initial untyped reference-wrapped value instead captures a borrowed old CELL
payload locator. Its snapshot resets that live payload before insertion/catch,
while a rebound source name continues to name its new CELL. Range-only locator
metadata delegates to the actual VARIABLE source spelling/line; a lost or retired
captured CELL remains authentic but fails readiness/discard explicitly. Both CELL
and bounded current payload need logical liveness and empty property/coercion/
backing records with no CELL debt. The
[wrapped NULL-key ledger](../../coverage/semantics/array-literal-null-key-wrapped-cv-review.json)
checks captured-slot restoration, two pending ARRAY owners and independent COW;
no global input classifier, task owner or count/prune/driver rule changes.
Initially typed captured payloads reuse existing accepting ordinary property
sources. Readiness validates current source objects and the bounded current
payload in the same logical live set, then checks all current constraints against
the frozen snapshot. Snapshot allocation, rather than a fresh graph root, is
required after marker-pop during throw cleanup. Missing live sources or an
incompatible newly attached source explicitly refuse reset; safe source detach
can restore eligibility. Fresh public `int|array`/`int` witnesses distinguish
weak44, rejected strings, transient restrictive-source refusal, DIRECT snapshots,
deletion and restoration before the same supplied Throwable reaches catch. See
the [typed NULL-key ledger](../../coverage/semantics/array-literal-null-key-typed-wrapped-cv-review.json).
String leaves validate canonical bytes or existing carrier records. Their table
and wrapper counts stay separate from copied string bytes: debt-time writes may
share a table while a string snapshot stays unchanged. Singleton reference
entries unwrap before child/string COW, then an inverse restores shared ALIAS copying.
The [string-leaf ledger](../../coverage/semantics/array-literal-float-string-leaf-review.json)
checks normal/same-table, deletion and supplied-throw paths. Direct string CV/cell
payloads remain Unsupported. No string-conversion callback or identity rule changes.
Embedded ALIAS leaves now admit live untyped cells holding null/bool/int/float
or validated byte strings, with no property/coercion/backing receipts or CELL debt. Their ordinary counts remain
separate from outer HARRAY/CELL biases: child-table COW keeps shared aliases or
unwraps singleton leaves, while sibling slots reveal table sharing independently.
Positive surviving tables preserve every leaf edge. The
[alias-leaf ledger](../../coverage/semantics/array-literal-float-alias-leaf-review.json)
records normal, deletion and supplied-throw paths with balanced inverse cleanup.
The [string-alias ledger](../../coverage/semantics/array-literal-float-string-alias-leaf-review.json)
checks string byte writes across shared and singleton leaf copies, independent
snapshots, deletion and supplied throws. Only the embedded leaf-cell predicate
broadens; direct string CV/CELL retargets, array-valued leaves outside the bound
below, object-valued or indebted leaves and recursive graphs remain Unsupported.
Embedded null/bool/int/float or validated byte-string ALIAS leaves also admit
validated ordinary instance-property type sources. Both ordinary table-CV and
wrapper-payload continuations use this bound. For debt-bearing payloads, every
source object must survive logical pruning with its actual property alias;
metadata adds no owner.
Shared leaf copies keep typed rejection/coercion. Explicit property unset removes
its source while the object remains rooted, allowing later singleton copies to
unwrap. The [typed-leaf ledger](../../coverage/semantics/array-literal-float-typed-alias-leaf-review.json)
records int-property coercion/rejection, multiple sources, deletion and supplied
throw. The [typed string-leaf ledger](../../coverage/semantics/array-literal-float-typed-string-alias-leaf-review.json)
checks shared byte writes, integer-to-string coercion, rejected array writes and
independent snapshots, with singleton byte COW after explicit property unset.
Global direct string CV/CELL retarget admission remains unchanged.
Object-valued leaves, static/hooked/queued or retired sources,
coercion/backing records and unsafe debt retirement remain Unsupported.
Embedded array-valued ALIAS leaves admit one mutable nonpool child
table of DIRECT null/bool/int/float or validated byte strings. The child has no
outgoing owner edge or HARRAY debt, and the leaf has no CELL debt or
coercion/backing records. Validated ordinary instance-property type sources may
constrain its array value. For debt-bearing payloads, logical-pruned liveness
includes the child and every source object, not only the leaf CELL. This bounded
shape needs no recursive eligibility or new count/prune algorithm: surviving
outer tables keep the leaf and its child edge.
Shared leaf writes propagate; singleton leaf copies unwrap before child-array
COW, keeping snapshots independent. The
[array-alias-leaf ledger](../../coverage/semantics/array-literal-float-array-alias-leaf-review.json)
separates table sharing with sibling slots and covers deletion, supplied throw,
inverse balancing and cleanup. The
[typed array-leaf ledger](../../coverage/semantics/array-literal-float-typed-array-alias-leaf-review.json)
adds public array-property witnesses with scalar rejection and nested child COW,
including source removal by explicit property unset. Other accepted property
descriptors compose existing type-source validation. Deeper owning children and
indebted descendants stay out.
DIRECT child-array entries share the same bounded child eligibility, with no
embedded leaf CELL: children are mutable nonpool tables of DIRECT
null/bool/int/float or validated byte strings, without outgoing owner edges or
HARRAY debt. Existing entry-node traversal requires each actual child to survive
logical pruning and preserves duplicate edges. The
[direct child-leaf ledger](../../coverage/semantics/array-literal-float-direct-array-leaf-review.json)
checks independent child COW, repeated-child owner multiplicity, deletion and
supplied throw while outer table/wrapper biases cancel before cleanup. No new
recursive eligibility, source authentication or ownership algorithm is introduced.
Outer array-valued reference cells also retain ordinary validated property type
sources accepting the bounded payload. The actual payload and every source
object use the same logical-pruned live set for debt safety. Physical count1
copies unwrap to DIRECT values, permitting scalar replacement and independent
payload COW while the original property remains typed; restored shared copies
keep the ALIAS and its type constraint. Explicit source removal is tested with an
extra alias through inverse balancing, avoiding effective-zero retirement. The
[typed outer-array ledger](../../coverage/semantics/array-literal-float-typed-array-ref-review.json)
records public array-property witnesses, including deletion, dual-source supplied
throw and initial typed-old capture. Other accepting descriptors compose existing
validation; global primitive/string gates, type writers and count/prune rules stay exact.

Missing-key module409 retains a
CV/literal array snapshot through real handlers, supplies null after insertion,
then fetches later items with shared embedded references intact. Throws cancel
the pending store and later items. CV leaves and implicit/compiled keys, plus
quiet CV keys in recursive by-value CV/literal and mixed CV patterns, bound this
producer.
Selected converted keys survive key-cell retirement/rebinding; later keys are read
afresh after the previous target store. Ancestor contexts retain compiler locations
and saved operands without reselecting through changed ancestor keys or parent tables.
Wider diagnostics remain required.
Literal admission checks the actual RHS occurrence. A pattern with reference
targets and a literal RHS is rejected at compilation. Pooled roots require exact table identity;
runtime roots use source-compatible nonconstant descriptors and live tables.
Literal sources retain pool owners or the sole runtime temporary, preserve old
embedded reference cells after CV rebinding, and cancel known-result delivery
when a handler throws.
Mixed direct-CV patterns retain a root cell and separate reference-bearing child
cells. Each cell's value replacement affects its later fetches, while parent/CV
replacement leaves saved children authoritative. By-value children retain tables.
The interrupted fetch supplies null before later reference acquisition/COW;
callback null replacement can autovivify an array at that later fetch.
Nested writable fetches can create both root and child arrays after root-null
replacement; later outer items and result delivery still resolve the held root.
Recursive by-value CV/literal nesting retains captured tables and compiler locations.
Outer missing reads feed silent nulls into the child; inner warning-task discard
can leave the outer continuation owning both tables until later unwind cleanup.
Saved row tasks retain their old arrays after callback replacement of a shared row
cell, while the returned root can expose that cell's new value.
Literal root authentication uses its pool identity or nonconstant runtime descriptor;
captured child tables retain separate authority through callback row-cell writes.

Weak-null `ini_get` and `ini_restore` are admitted internal producers. Their
authenticated unary continuation resumes once after normal handling or false
fallback; a thrown handler aborts lookup. Weak handler argument conversion,
original-null trace operands, caller arguments and raw INI writes are checked
in the [readback ledger](../../coverage/semantics/include-ini-readback-review.json).
Owned unary CONFIG PIPE also composes with public static method handlers: weak
severity reception, saved caller arguments, original-null traces and throw cleanup
remain distinct from USER strict warnings. Other CONFIG warning producers remain open.

Remaining null/Stringable API conversions and magic/autoload/internal callback forms,
reference-return callbacks and later lifecycle dispatch remain open.
[Exception handlers](SOURCE-EXCEPTION-HANDLERS.md) use a separate uncaught boundary
with one Throwable argument and a nullable raw registration stack.
Frameless named/method trace formatting in164 now accepts the authenticated
nonempty function field. Current property and array-caller readback gates validate these shapes on the
tested private source composition.
`REPORTINGINI` retains full raw bytes separately from the signed32 effective mask;
reporting get/set/Restore and modified-entry state are recorded in the
[reporting ledger](../../coverage/semantics/reporting-ini-review.json). Runtime
`E_STRICT` and lossy reporting conversions use authenticated producer tasks in
[diagnostic ingress217](../../coverage/semantics/reporting-diagnostics-review.json).
Their callbacks save/clear/restore constant evaluator facts while retaining
busy class initializations, selected values and genuine emitting frames. Broader
directives and startup profiles remain separate. Uncaught/fatal reporting outside this slice and
broader global/reference behavior also remain core obligations.

[Dimension keys233](SOURCE-DIMENSION-KEYS.md) stage earlier key-CV and conversion
warnings through read/quiet/nested consumers. Native protection and genuine
temporary owners preserve table COW/retirement, live cells and ordered NaN
notices; throws skip the later write. Source, line, mode, constants and owning
operand forms are checked without reconstructing captured dynamic-value history.
[Writable dimensions242](SOURCE-DIMENSION-WRITES.md) add bounded CV-array W/RW
and direct GLOBALS reference fetches. Native separation/protection, exact-one
table acquisition and delayed RHS demand survive callbacks; named fetch precedes
mapping and promotion. [Coalesce/unset249](SOURCE-DIMENSION-EDITS.md) preserves
direct CV-array quiet memoization/write demand and final unset liveness, including
typed-cell/throwing cleanup and authentic read/write lines.
[Nested unset and append255](SOURCE-DIMENSION-TAILS.md) keeps intermediate table
protection, genuine abort temporaries and the distinct late RHS throw boundary.
[Nested coalesce262](SOURCE-NESTED-COALESCE.md) retains genuine quiet rows,
memoized operands and every late-RHS continuation task; typed-entry rejection
restores the emitter and retains the handler's older exception chain.
[Global W/RW269](SOURCE-GLOBAL-WRITES.md) detaches callback-created constrained
aliases on a returning missing fetch; throws preserve callback writes and skip
initialization and delayed RHS demand. Name conversion remains distinct from
ordinary array-key conversion.
[Container276](SOURCE-CONTAINER-WRITES.md) adds initial W/RW storage and final
array-reference ingress: false protection, consumer-specific post-throw effects
and source-backed typed DIM_OP backing retain native behavior.
[Scalar reads282](SOURCE-CONTAINER-READS.md) stage missing-base, key-CV and offset
warnings while preserving borrowed selections and genuine temporary owners.
Missing-base null, post-key message sampling, quiet predicates and throw suppression
remain distinct. String/object/ArrayAccess, wider base and memoized/GLOBALS producers
remain required.

Primary contracts are `zend_error_zstr_at` in `vendor/php-src/Zend/zend.c`, the
six API bodies in `Zend/zend_builtin_functions.c`, the undefined-CV read helpers
and `zend_verify_arg_error` in `Zend/zend_execute.c`, legacy ZPP conversions in
`Zend/zend_API.c`, and `php_error_cb` in `main/main.c`.

The maintained selection has eighteen normal and five expected PHP-error tuples,
plus one Unsupported ingress control with zero agreement credit. Author eight
fixtures/298 and independent three/240 pass across retained and focused runs;
the independent three normal source comparisons retain their native originals.
Original allocation, fatal-stack, pooled-array, checkpoint and receive-validator
failures remain preserved. Fresh current-master author source2/75 and independent
source1/87 are separate, with no inherited execution credit. The [review ledger](../../coverage/semantics/error-handlers-review.json)
locates the exact revisions, raw commands, exits and mixed evidence. Local tools
are reused; a fresh combined offline rebuild and complete core remain open. The
[method-handler ledger](../../coverage/semantics/handler-callables-current-review.json)
keeps source15/five258 and independent source9/three185 separate from current
PIPE source1/state93, including the preserved failed attempts. Its early
get_called_class() Unsupported source keeps zero agreement. Later
[called-class introspection](CALLED-CLASS.md) has separate source and frame checks;
the earlier static::class observations retain their original scope.

In a private project root with the built local SpecTec algorithmic tool at
`.tools/spectec/bin/p4spectec`, prepare and run the exact report separately:

```sh
python3 -B tests/semantics/error_handler_prepare.py
python3 -B tests/semantics/error_handler_run.py .tools/error-handlers/PREPARED/report.json
```

Use the actual preparation directory for `PREPARED`. The runtime runner checks
the complete maintained selection before optional affected-case filters, records
full streams/exits and stops on the first failure. The ordinary13 profile uses
native45s, model90s and finite300s producer limits, serially; reused local binaries
do not establish a fresh build, offline closure or complete PHP semantics.

Module209 also retains original-null branch, loop, short-circuit, NOT and
ternary-condition choices across handler mutation and throw. Its mixed ordinary
author8/225 and independent native-reused model3/160 remain distinct from PIPE
normal/throw source2 and69/corrected96, and deferred-cache normal/throw source2
and95/89 at `8c74e624`. These gates validate their tested private compositions;
source-equivalent promotion adds no execution or rebuild credit.
The tested211 composition at `38cab574` separately accepts author source1/93
and independent source1/107 across original-null truth decisions and strict
instance-emitter parameter rejection, preserving raw restoration and saved frames.
[Truth continuations](SOURCE-WARNING-TRUTH.md) retain their historical cast control;
the later [consumer slice](SOURCE-WARNING-CONSUMERS.md) covers its admitted path.

The [consumer213 slice](SOURCE-WARNING-CONSUMERS.md) separately accepts mixed21
normal tuples/control0 and236 conditions, plus independent10/197. Fresh source1/94
and cached-callee source1/96 at181f cover the actual static-reference, outer-array
prepass and cached-callable composition. Grouped model timeouts and the original
copy fixture premise remain preserved. Publication retains later released
reporting, parameter backing and named-class paths with no fresh execution credit.
