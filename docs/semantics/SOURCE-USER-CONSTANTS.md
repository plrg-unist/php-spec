# Ordinary source user constants

Ordinary `const` declarations and reads use the checked source compiler and runtime for the pinned PHP 8.5.10 CLI profile. Scalar/array, certified Closure/FCC, bounded user-instance NEW and bounded stdClass values, including ignored arguments and rejected duplicate-value retention, nested arrays and selected newborn ternary/coalescing leaves, are supported; the constant family and full core remain partial.

## Declaration and lookup

The compiler handles each actual `NConst` initializer before validating its declaration name. Shared constant-expression preparation preserves selected/skipped branches, compile diagnostics, and deferred expressions. `CODENAME` and `CODEEXPR` at the declaration origin retain the resolved name and emitted opcode line; initializer paths remain the original source paths. The compiler contract describes the admitted constant-expression boundary.

Runtime `CONSTANT_INIT` evaluates one initializer through the ordinary expression machine, then `CONSTANT_BIND` activates its value before the next declaration starts. A missing name or other initializer error leaves earlier constants active. A duplicate name evaluates its initializer first, emits the native duplicate warning, releases its temporary value ownership, and preserves the earlier binding. Constant-AST diagnostics use the recorded declaration opcode line, including multiline initializers.

The request-local table normalizes namespace prefixes to lowercase and preserves terminal-name case. Reads use the compiler-resolved primary and namespace-fallback names in order. Constants become visible when their declaration executes; source declaration presence does not preactivate the value. Existing constant-name compilation handles imports and namespace contexts.

## Values and allocation classes

`USERCONSTANTS` entries own their ordinary runtime values. Constant reads, array copies, nested value calls, reference sends, and temporary foreach references use the existing heap and copy-on-write machinery. The table's roots are included across active and saved frames and abrupt cleanup. A failing initializer clears pending initializer work and scratch facts while retaining existing table and request roots.

Allocation provenance is a separate non-owning tree: `PVSCALAR`, `PVSTRING bool`, `PVCLOSURE` with its exact object identity, nonfoldable `PVINSTANCE` or distinct `PVSTDCLASS` with object identity and NEW source, or `PVARRAY bool` with ordered keyed child classes. The flag records the source-backed non-refcounted case needed by subsequent default-receive semantics. It is not inferred from final bytes or length. Both string flags can accompany empty bytes; an allocated array can be empty. The shared empty-array class requires empty topology. Generic `PVOBJECT` is not admitted as certified global NEW.

Shared compiler facts export `PCCLASS` beside existing `PCONSTANT` values. The compiler records classes while folding actual child facts. Runtime `CONSTANT_OBSERVE` records the result of actual evaluation and propagates classes through the same selected children and operations. A fully stored initializer applies direct-root string interning at declaration installation; strings inside its arrays retain their own classes. Deferred initializers preserve operation and imported-value provenance. The allocation-class contract records the pinned scanner, literal-installation, cast, concatenation, bitwise, and array distinctions.

String values and scratch facts admit authentic `PSTRING_CARRIER` identities.
Request identities must match `STRINGDATA`; fact validation retains the actual
carrier alongside existing source, pool and lookup checks. A scanner class can be
`PVSTRING false` even when direct declaration installation interns the received
value. The legacy allocation-class policy is unchanged; validation does not infer
the class from a carrier tag. The [string-publication review](../../coverage/semantics/const-string-review.json)
records source-backed publication, array/default consumers and public resume checks.

## Resumption invariants

Static/no-use REAL Closure and named/static-method FCC initializers retain an
exact full `NConst` receipt, callable source path and publication prefix. REAL
Closures use the source unit's immutable entry class for both lexical and called
scope, with no receiver; an inherited include/eval therefore uses its declaring
method scope rather than its forwarded called class. Named functions remain
unscoped. Wrapped objects and genuine plain clones retain exact receipt authority.
Registration checks the actual value against its allocation class and certified
source transfer; array aliases retain existing object identity.

Duplicate registration suspends through the genuine warning dispatcher. Its
continuation owns the actual discarded candidate and captures the preceding
constant-table prefix plus its completed alias-read facts. Return or throw
preserves the installed binding and releases the candidate. Raw-trait method
capture similarly suspends before allocation; its
saved source/target/publication facts authenticate resumption. Receipt metadata
adds no roots, and successful constants remain owners after local variables die.

Each nonfoldable global alias read records its full consuming `NConst`, leaf
source, selected donor declaration, allocation class and table prefix. The
observer checks the actual result before minting this proof. Binding and later
row validation use each read's captured prefix, bounded by the consuming row's
preceding table or duplicate continuation's bind prefix. A callback may therefore
shadow a name between two operands without changing the first selection. Arrays
still copy their containers normally. Installed rows retain filtered nonowning
read facts; failed evaluation clears scratch facts and retry selects afresh.

Global NEW uses prepared constructor phases after class-table completion. It
allocates the selected user instance, evaluates every argument even when no
constructor exists, then checks constructor access. Named classes and self/parent
selectors use the immutable declaration-entry scope; inherited file/eval entries
retain their declaring Owner rather than the caller's forwarded Child class.

`CONSTANTOBJECTS` records exact object, full `NConst`, NEW source, requested class
and publication prefix without owning the object. An incomplete birth becomes
complete only at the authentic ended no-constructor or returned constructor
phase, with the same live object/result and no pending saved phase. Transfer
requires that completed identity; changing mutable fields does not change its
authority. A throwing constructor may leave an incomplete object genuinely owned
through GLOBALS or a CV, but cannot install it as a completed constant value.

For ordinary declarations, public source-state checks bind table names and declaration tasks to actual `NConst` origins and compiler descriptors. They check unique names, valid task indexes, initializer/bind/observer ordering, declaration context, exact source-derived pooled class facts, and value/class tag and ordered array topology. Metadata adds no heap owners.

Initializer scratch facts retain a scalar operand or an array's non-owning class tree. Their origins must belong to the active initializer. Pooled origins agree with the fixed pool class. Conditional and coalesce facts must agree with the already recorded condition truth or left nullness, so an unexecuted opposite arm cannot determine the selected class. These checks inspect current values and continuation relationships; they do not replay expressions or reconstruct arbitrary runtime values from source. Positive tests change condition values and selected string bytes while preserving the source-consistent branch.

The quiet-coalesce path captures the already computed left result before temporary-base disposal, only while an initializer context is active. It does not perform another read, evaluate a key twice, or add events. A missing string offset contributes null to this observation. Outside a constant initializer the added helper is the identity; independent ordinary quiet-source and resumption checks cover that shared boundary.

## Dynamic global constants

Module400 implements `define`/`defined` for global string names, primitive
values, certified stdClass/user-instance donors and bounded array snapshots,
including authenticated interned and request strings. Existing CONFIG
argument evaluation and retained dynamic-callee selection supply the actual
completed arguments. Registration stores the value, captured object pointer or
copied array snapshot in `USERCONSTANTS`; later
changes to the name or value CV do not change the row. The string class follows
its actual carrier (`PVSTRING true` for interned, false for request strings).
Identity-unknown legacy scalar string payloads remain Unsupported. Array leaves
also admit byte-only strings, including compiled literals, without manufacturing
a carrier identity.

Registration normalizes the namespace prefix without stripping a supplied leading
separator; the final component stays case sensitive. `defined` removes a leading separator
for lookup separately. Fixed global/explicit-global `define` and retained dynamic
selection authenticate the call site; namespaced fallback is outside this slice.

Retained intrinsic DEFINE Closure callees also admit primitive values, bounded
array snapshots or existing supported direct objects, string names and
omitted/raw Boolean flags or separate raw NULL reception, through ordinary or
explicit `__invoke` calls.
Preparation records the exact captured owner with a nonce before arguments run;
the live CONFIG must match that owner, site, kind and line. Its durable selection
record owns nothing and authenticates the saved intrinsic tag after the callee
dies, so fresh rows and later queries do not reread a mutable callee CV. Legacy
string selections carry an empty owner; owned records have no original string.
Repeated same-site calls preserve inactive historical records while requiring
the current nonce for active tasks. Named capture, frame retirement and normal
or throwing duplicates preserve the earlier primitive arguments and old row.
Other flag/name coercions, packs and PIPE remain outside this owned-call
slice. This call header does not extend leaf authority; intrinsic Closure values
are covered separately below.
[Owned DEFINE call review](../../coverage/semantics/define-owned-closure-review.json).

Owned arrays reuse the existing authenticated leaf, canonical copy and query
policy. Capturing an earlier raw array preserves its identity through later
callee/source CV changes; copying dereferences its current alias cells into
DIRECT entries. Query COW copies containers while sharing object leaves. A
rejected private candidate retains its own child after the raw alias becomes
NULL, then retires that child before the captured callee. The child destructor
observes the callee alive; it has retired when false is delivered or the original
Exception reaches catch. A returning handler may replace the raw alias with a
different owning child: rejected-copy cleanup runs first, call argument owners
are released next, and the callee last. Both child destructors observe the callee
alive. The owned Boolean header admits omitted or raw Boolean flags; separate
NULL reception can enter the same array path after a normal weak callback.
Ownerless quiet-flag delegates and other intrinsic cleanup orders stay exact.
[Owned array call review](../../coverage/semantics/define-owned-array-review.json).

Owned direct objects reuse the existing value classifier without changing leaf,
certificate, scope or live-storage authority. The originals publish an ordinary
INSTANCE and a cached stdClass, retaining pointer and child identity after source
and callee retirement; cast-view COW keeps the stdClass table intact. A normal
rejected INSTANCE argument runs its destructor while the callee is held. A
throwing duplicate's raw API/__invoke object arguments instead outlive the
callee. After the Exception and trace retire, the last raw argument views can
release the object with no pending Exception and the callee gone. Other existing
certified object and supported bare Closure/factory classes compose structurally
without new producer credit. Intrinsic Closure values are covered separately
below; other coercive flags/packs and global/default policies remain unchanged.
[Owned object call review](../../coverage/semantics/define-owned-object-review.json).

Raw TRUE preserves the captured argument while emitting the ignored-case Warning
before lookup or array copying. A returning handler may install the target key,
so the outer call then reports a duplicate and returns false; the row retains
the inner fixed call's source authority. Reference writes during the first
callback are observed by the later canonical ARRAY snapshot. A supplied Exception
does not cancel fresh registration: the captured direct object gains its row
root before that same Exception reaches catch. Raw API/__invoke views retain
TRUE and the shared object after callee retirement; the row still owns the object
after those views retire. These originals execute primitive, ARRAY and ordinary
INSTANCE values; other current value classes compose structurally. Existing name,
leaf, receipt, argument-before-callee cleanup, global/default and paused policies
remain exact.
[Owned true-flag review](../../coverage/semantics/define-owned-true-review.json).

Raw NULL uses separate pre-body reception. Strict ordinary calls raise
parameter-3 TypeError after all argument effects, without invoking the handler
or registering a row. Explicit `__invoke` remains weak even in a strict source:
its Deprecated callback precedes lookup and ARRAY copying, so a normal return
copies the current alias value. A supplied Exception cancels registration;
raw API/wrapper arguments retain NULL and the object after callee retirement.
After those trace owners retire, normal disposal runs with no pending Exception.
Existing receipt, Boolean-header, value and cleanup authority stays exact;
owned class-qualified names and wider flag coercions remain outside this slice.
[Owned NULL-flag review](../../coverage/semantics/define-owned-null-review.json).

Public row checks require a genuine source/selection, canonical unique name,
matching value class and empty read/receive metadata. Available immutable
positional literal facts constrain names and values. Variable-derived payloads keep
the existing structural value policy: the row is the runtime capture, not a full
proof of past argument evaluation. Validators never reread mutable CVs.

Positional `constant`/`defined` calls with zero or two primitive arguments check
arity before string reception or lookup. All argument expressions run first;
the selected callee and raw captured arguments determine the ArgumentCountError,
even after an extra argument changes the caller's CVs. A raw NULL remains NULL in
the API trace, without a deprecation or strict parameter-type error. The caller's
unassigned destination and completed argument effects survive.

Module400 authenticates the original CONFIG/source, immutable argument facts and
string carriers before using the existing count-error/trace machinery. Its new
shape is excluded from the broad class-query fallback; one-slot routes remain
unchanged. The [query-arity review](../../coverage/semantics/constant-query-arity-review.json)
binds four exact originals and 392 premises across five genuine CONFIG error
fronts. Author 289 retain 6d62201c0; independent 103 pass at 027fc5877 after a one-line
fixture type correction. The original pre-main failure and unchanged Unsupported
baseline retain zero credit; the fixture correction leaves source execution and
runtime rules unchanged.
The excess-count follow-up now rejects every positional primitive query count
other than one through the same guarded path. A single count predicate widens;
source/capture/carrier, message and raw-error construction stay exact. Zero/two
admission and normal one-slot reception are unchanged. Count rejection also
precedes class-name lookup, preserving autoload and class metadata.
The [excess-query review](../../coverage/semantics/constant-query-excess-arity-review.json)
binds four new originals and 487 premises at e29316a34: counts 3/4/5, raw NULL and
request captures, strict priority, five actual errors and a genuine selected
`defined('TRUE')` recovery. Two old Source48 shape controls now admit count3 while
rejecting source-length-inconsistent records; fresh equivalent controls run here
without replaying its 392 premises. No actor failed or repeated; the unchanged
Unsupported baseline retains zero credit. Owning arguments, owners and
packed/named/FCC arity-error handling remain partial.

One positional array name now raises parameter-one TypeError in `constant` and
`defined` before lookup, independently of caller strictness. The bounded domain
is empty/flat live arrays with primitive nonstring or authenticated string-carrier
leaves, stored directly or through live scalar reference cells. The raw API trace
owns the captured array; ordinary COW separates plain fields while embedded
references still share their backing cell. Argument effects and caller results
survive the error.

Thirty module400 insertions authenticate the query shape, source/literal array
facts, live array/cells and leaf carriers before the existing error allocator.
No copy fold, task/schema or shared trace/ownership rule changes. The
[array-name review](../../coverage/semantics/constant-query-array-name-review.json)
binds four exact originals and 533 premises at 46a59b565/runtime38e5756d: five real
CONFIG errors, actual caller/snapshot/trace COW endings and two reached reference
updates. All checks pass on their first attempts; the unchanged Unsupported baseline
retains zero credit. Nested arrays, objects, legacy PSTRING leaves and
owner/named/packed/FCC forms remain partial.

Positional `define` with two/three arguments now rejects the same bounded flat
array-name domain before optional flag reception or registration. Candidates and
present flags are primitive nonstring or authenticated string-carrier values.
The parameter-one TypeError precedes weak NULL flag deprecation, strict flag type
rejection and the ignored-true Warning, after all argument effects. A captured
array keeps earlier ordinary fields while embedded reference cells reflect later
argument writes; the API trace retains the original candidate and flag.

Exactly 24 module400 insertions reuse the flat-name/source/carrier guards and raw
error allocator, with a disjoint broad-DEFINE exclusion. No task/schema/shared
trace or ownership rule changes. The
[define-array-name review](../../coverage/semantics/define-array-name-review.json)
binds source4 at 1b9723050 and 590 premises at cb250bda2/runtimea6677ebfc: five real
CONFIG errors and a normal `defined('Array')` recovery. The first state fixture
reused one expression variable for two literal ASTs; that retained failure has
zero credit. Only its binder changes before affected/unrun state checks, without
source/model/baseline replay. Nested/legacy-string/object leaves, nonprimitive
candidates/flags and owner/named/packed/FCC forms remain partial.

Positional `define` calls with primitive arguments now reject every count outside
two through three before receiving the name or optional flag. Too few arguments
produce `at least 2 arguments`; excess arguments produce `at most 3 arguments`,
with the actual count. This precedes weak NULL diagnostics, strict type rejection,
the ignored-true Warning and registration, after the argument expressions finish.
The API trace retains their raw captured values and selected builtin even after
later arguments mutate the caller's CVs; the destination remains unassigned.

Exactly 21 module400 insertions reuse the existing source/primitive/carrier and
error helpers. The broad define receiver excludes only this new count shape;
valid two/three-argument routes and query arity handling are unchanged.
The [define-arity review](../../coverage/semantics/define-arity-review.json) binds
four exact originals and 444 premises at 88f96c261 across five real CONFIG error
fronts. Counts 0/1/4 and independent 5 cover raw NULL/request captures, a true-flag
body bypass, canonical API/caller traces, caller99/no publication, source/carrier/
immutable/count controls and budgets. No actor failed or repeated; the unchanged
Unsupported baseline retains zero credit. Arity-error handling of owning values,
owners and packed/named/FCC forms remains partial.

Primitive duplicate `define` of an existing user constant emits the ordinary
level2 Warning and returns false without publishing its candidate. A named handler
may suppress default delivery or append another constant; the original binding
survives both. The retained CONFIG
resume keeps actual arguments, selection and the pre-warning table prefix. Public
checks require the duplicate key within that prefix, so later-only keys cannot
authorize it. Two exact sources and two public fronts/207 premises cover default,
false-handler and handled delivery in the
[duplicate ledger](../../coverage/semantics/dynamic-constant-duplicate-review.json).

Exact non-NUL string names of modeled fixed startup primitives now take the same
duplicate Warning/false path with primitive candidates and omitted or bool-false
flags, including strict calls. They predate every user-table prefix: only its
bounds matter, and no user row is published for the builtin. A returning handler
may append a sibling and mutate the caller; a throwing handler keeps the same
Exception, callback effects and caller destination. Raw captured request strings
remain in the API trace. Trace projection selects the saved startup call in handler
scope, while continuation validation authenticates it in restored caller scope.
The [startup-duplicate review](../../coverage/semantics/define-startup-duplicate-review.json)
retains four exact sources at b55e4edaf, literal199 at f9a7e2cb9 and callback/strict/
throw415 at 7891c0df5. The projection correction preserves observed string values;
fresh peer state checks the actual Throwable trace and full discard. The pre-main
syntax failure, later trace-guard counterexample and unchanged Unsupported baseline
retain zero credit. Unknown startup values, coerced names, other
flags and owning/wider candidates remain partial.

Non-NUL special names `true`, `false` and `null` also warn and return false with
primitive candidates and omitted/bool-false flags. Their recognition ignores case,
while the duplicate message and raw API trace retain the captured spelling. They
never publish a user row. Ordinary/strict calls and handlers preserve the special
values and callback effects; throws leave the caller result unchanged.
The [special-name review](../../coverage/semantics/define-special-duplicate-review.json)
binds four exact originals and 645 public premises at 84817642f, including actual
dispatch/handler/resume/discard, raw request strings, immutable spelling versus
mutable-name message authority and budgets. Two old Source43 protocol files repair
obsolete refusals with admission plus stale-message rejection; fresh equivalents run
here without renewing its 614 campaign. Only two name predicates widen; all other
admission, trace-projection, return and discard code stays exact. Unknown startup values,
other flags/coercions and owning/wider candidates remain partial.

The boolean true `case_insensitive` flag emits its level2 ignored-flag Warning
before registration and leaves name lookup case sensitive. Its authenticated
resume retains the original true argument. Registration then uses the live table:
a handler's inner definition can create the name first, causing the outer call's
separate duplicate Warning and false result. Two exact sources and two public
fronts/221 premises cover genuine callback entry, both argument-preserving resumes,
the inner row origin and the later duplicate prefix in the
[ignored-flag ledger](../../coverage/semantics/dynamic-constant-flag-review.json).

String-name calls with primitive values also receive int, string and non-NaN float
flags. Weak boolean parsing distinguishes `"0"` from `"false"` without replacing
the raw flag in CONFIG or API traces. Normal ignored-warning callbacks resume
against the current table, so an inner definition can cause the later duplicate
Warning. Strict calls retain raw arguments and raise the third-parameter bool
`TypeError` after every argument effect. Normalized source sends and authentic
string carriers constrain all three captured inputs; row-history rules are unchanged.

If the first ignored-warning handler throws while the name remains fresh, Zend
still registers the captured value before propagating that exception. The narrow
pending tail changes only the constant table and preserves the original Throwable,
caller destination and callback mutations. The pending duplicate case is
covered below. The [scalar-flag review](../../coverage/semantics/define-scalar-flag-review.json)
binds four source agreements and 462 public premises. NaN reception is covered
below; the bounded false-flag scalar-name follow-up is also covered below. Wider
values and other coerced flags with scalar/null names remain separate.

Boolean true uses its original warning marker for the fresh registration tail
after a handler throws. The step appends the captured primitive after any unrelated
callback definitions and changes only the constant table, preserving the original
Throwable and caller destination. Strict selected calls retain true and the exact
request-string candidate despite later argument and callback mutations. The
[boolean-tail review](../../coverage/semantics/define-bool-flag-pending-review.json)
binds two source agreements and 196 public premises; its unchanged normal-but-wrong
baseline remains zero credit. A key already present after the throw
uses the pending duplicate continuation below.

When the name is already bound after the first ignored-warning throw, registration
still reaches its duplicate report. A currently eligible PHP handler is skipped
because the original Exception is pending; its undefined result causes no fallback.
An excluded Warning level instead uses the default reporter and current reporting
mask. Neither branch replaces the old row, changes captured arguments or chains a
new exception. The ordinary fatal-trace snapshot is cleared. The
[pending-duplicate review](../../coverage/semantics/define-pending-duplicate-review.json)
binds three source agreements and 206 state premises, including callback-created
and preexisting rows, strict named capture, actual discard steps, a source-backed
seeded trace and reporting-zero controls. The existing nonowning primitive-value
and string-name boolean/scalar-flag gates bound this continuation.

A NULL third flag has a separate pre-body reception path. Weak calls emit the
parameter-3 deprecation, then use false after normal callback return without
rewriting the raw flag. Publication reads the current table, so a callback may
create a binding that causes a second duplicate Warning. Both API trace views
retain NULL. A throwing first handler cancels registration and preserves completed
sibling definitions and caller mutations; strict calls retain raw arguments and
raise TypeError after all argument effects, without the deprecation. Existing
string-name row-history validation is unchanged. The
[NULL-flag review](../../coverage/semantics/define-null-flag-review.json) binds four
source agreements and 349 public premises. Primitive values, ordinary string
names and nonowning three-argument calls bound this slice.

A NaN third flag has a separate bool-reception Warning before the C body. Normal
return proceeds with true to the ignored-flag Warning while CONFIG and API traces
retain the captured NaN bits. The two phases have distinct authenticated markers;
old quiet/scalar markers still reject NaN. A conversion-handler throw cancels the
outer definition and preserves completed callback mutations, including an inner
binding. A later ignored-warning throw instead reaches the existing fresh or
pending-duplicate registration tail. Strict calls keep raw arguments and raise
TypeError after all argument effects without warning. Immutable source arguments
compare structural bits, independently of PHP's false NaN self-identity test.
The [NaN-flag review](../../coverage/semantics/define-nan-flag-review.json) binds
four exact originals and 472 public premises across four genuine source fronts,
including actual first/second throw discard steps and budget resumption. Ordinary
string names, primitive values and nonowning three-argument calls bound this slice;
wider names, values, producers and owning/packed forms remain partial.

For omitted/bool flags, a non-NUL string name containing `::` raises parameter-1
ValueError before the ignored-true Warning. The test is a byte search, including
malformed spellings such as `::` and `A:::B`; no class is resolved and no constant
table is read or changed. Normalized source arguments and authentic name/value
carriers retain the original API trace despite later argument effects. Strict
bool calls have the same priority. The
[class-name review](../../coverage/semantics/define-class-name-review.json) binds
four exact originals and 450 public premises across seven genuine CONFIG fronts,
including raw two/three-argument traces, real caller frames, state preservation,
immutable/source/carrier refusals and budgets. Quiet scalar flags follow below;
NULL/NaN flags, NUL-containing names, wider values and owning/packed forms remain separate.

For these non-NUL `::` names, int/string/non-NaN float third flags use a separate
reception route. Weak boolean parsing is quiet and leaves the raw argument intact;
the body then raises the same name ValueError before any ignored-flag Warning.
Strict calls reject the raw flag with parameter-3 TypeError before that body check,
after all argument effects. Neither route resolves a class or accesses the table.
The [scalar class-name review](../../coverage/semantics/define-class-scalar-flag-review.json)
binds four exact originals and 620 public premises across nine genuine CONFIG
fronts, including truthy int/string/float flags, raw negative zero and authenticated
request `"0"`, selected named captures despite live mutations, actual API/caller
traces, preserved stores/events/table/handler registry, refusals and budgets.
The omitted/bool route is unchanged; NULL flags follow below. NaN flags for these
names, NUL/coerced names, wider values and owning/packed forms remain partial.

A NULL flag for a non-NUL `::` name first emits the parameter-3 bool deprecation.
After normal return, a distinct conversion-only marker raises the name ValueError
using the original captured arguments. Callback writes to name/value/flag/callee
cannot alter that check, and quiet inner bindings survive it. A throwing first
handler instead cancels the body, preserving the same Exception, callback effects
and caller destination. Strict raw NULL raises parameter-3 TypeError after argument
effects without deprecation. No path reaches registration or class resolution.
The [NULL class-name review](../../coverage/semantics/define-class-null-flag-review.json)
binds four exact originals and 429 public premises across default reporting,
returning handler, strict rejection and throwing-handler groups. Actual transitions
cover raw API/caller traces, source file/line, Previous NULL, preserved stores/table,
complete restored-state discard equality, forged captures/markers and budgets.
Default PHP stderr retains its one Deprecated line; the other originals are quiet.
Old flag routes are unchanged; NaN flags follow below. NUL/coerced names, wider
values and owning/packed forms remain partial.

A NaN third flag with a non-NUL `::` name first emits its bool-conversion Warning.
Normal return reaches the captured-name ValueError before the ignored-true Warning;
a false handler also retains the conversion diagnostic. A throwing handler cancels
the body and keeps the same Exception, callback effects, inner binding and caller
result. Strict calls reject the raw float after all argument effects without warning.
The [NaN class-name review](../../coverage/semantics/define-class-nan-flag-review.json)
binds four exact originals and 441 public premises across default/false-return,
strict and throwing-handler groups. Actual transitions check raw API/caller traces,
immutable canonical-NaN refusal, genuine runtime INF-minus-INF captures, complete
restored-state discard equality and budgets. Native self-inequality observes NaN;
negative-NaN bit assertions are SL source-state facts. Default and false-return PHP
stderr each contain one conversion Warning; strict/peer are quiet. Previous marker
domains are unchanged; NUL/coerced names, owning/wider values, wider NaN producers
and full family closure remain partial.

Fresh array definitions with an omitted, boolean, NULL or admitted quiet scalar
third flag recursively dereference source cells into new DIRECT entries. Reinserting surviving
keys rebuilds NEXT, positions and serial
metadata; ordinary copies and later source/reference writes preserve the constant.
Nonempty acyclic trees contain primitive/carrier leaves, byte-only strings and
certified live stdClass or user-instance donors. Existing carrier classes and
object birth classes are retained; copied containers share the exact object
pointers.
Repeated noncyclic children may copy independently.
Byte-only strings keep their exact bytes in 0..255 and use conservative `PVSTRING false`
without string-table allocation or recovered scanner/refcount provenance. This
does not extend scalar string admission, default caching or INI pointer identity.
The [literal-string review](../../coverage/semantics/define-literal-string-array-review.json)
covers literal constraints, query bucket COW, real carrier composition and normal
or abrupt duplicate retirement.
Public checks require a canonical DIRECT tree and available literal-array facts,
comparing ordered keys and leaf values rather than internal array IDs. Variable
payloads keep structural authority without replaying past CVs. Two exact sources
and two public fronts/219 premises cover request strings, gap appends, nested
reference freezing and a later literal registration in the
[array ledger](../../coverage/semantics/dynamic-constant-array-review.json).
The [object-leaf snapshot review](../../coverage/semantics/define-stdclass-array-review.json)
adds literal/eval and selected named originals: one shared source cell becomes
two DIRECT object edges, later cell rebinding leaves the snapshot intact, and
real query bucket-reference COW changes caller containers while property writes
still reach the stored objects. Queries add only a root owner and allocate
nothing. The leaf classifier reuses completed/live birth guards; producer,
canonical-table and cycle guards are retained.

Duplicate user keys with nonempty array candidates copy before the Warning.
A dedicated marker owns the private canonical root and the unchanged original
CONFIG, so callback cell rebinding changes the API/Exception trace input while
the copied candidate keeps its earlier values. Candidate validation checks its
canonical tree, live leaf classes and the saved old-row prefix without re-copying
mutable input aliases. A true handler suppresses reporting; false handlers retain
the exact source-tagged Warning. Normal false delivery or abrupt handler cleanup
retires the private copy while preserving the old row, callback writes and any
real Exception trace owners of the original input. The established primitive and
carrier fold is reused; new exact sources discriminate certified object leaves.
[Array-duplicate review](../../coverage/semantics/define-stdclass-array-duplicate-review.json).

Array calls also admit an explicit captured boolean-false third slot. Copying
follows all argument effects: a late flag expression can rebind cells already
present in the captured input. Reporting retains false even if a callback changes
the live flag; the original API input and private snapshot keep their distinct
owners. The existing fold also composes with primitive/carrier trees and fresh
top-level empties; new exact sources focus certified object leaves. Stored-row
source validation remains structural and does not reconstruct a past mutable
flag. Other flag conversions remain partial.
[False-flag review](../../coverage/semantics/define-stdclass-array-false-flag-review.json).

A captured true flag emits its ignored-case Warning before recursive validation,
copying and key lookup. A normal callback may repair or create a captured cycle,
or install the target key before duplicate reporting. Current reference values
determine the later snapshot; caller container writes still COW away from the
original CONFIG input. The header checks source, name carriers, live input and
available literal facts without folding the input before the Warning.

If that first callback throws, a fresh acyclic array is still copied and
registered while the same Throwable continues. The destination stays unassigned;
the original API trace and copied row keep distinct owners. A later duplicate
Warning uses the existing private-candidate cleanup and retains the old row.
The established array fold and historical row policy are unchanged; new exact
witnesses focus primitive and certified stdClass leaves.
[True-flag review](../../coverage/semantics/define-array-true-flag-review.json).

When that first callback leaves an exception pending, cyclic validation fails
without allocating a new ValueError, copying or looking up the target. The same
Throwable, Previous chain, result and trace arguments continue. For an acyclic
duplicate, canonical copying still precedes registration; the existing pending
warning policy skips an eligible callback, and ordinary cleanup retires the
unregistered containers. The old row, callback side rows and trace-owned input
survive. Real trace-bucket references and a fresh false-flag retry distinguish
shared source cells from copied recovery/query containers. Other flag conversions
remain partial. [Pending-array review](../../coverage/semantics/define-array-true-pending-review.json).

Quiet nonboolean array flags admit integers, finite floats and existing string
carriers. Weak reception computes a C boolean without replacing the captured
argument. False values proceed directly; truthy values use the existing ignored
Warning and only then validate/copy/register. A throwing Warning preserves the
same pending cyclic/fresh/duplicate behavior under that original raw capture.
Strict calls reject nonboolean flags before the Warning or recursive-array check,
after all argument effects. Header/source/known-value and carrier guards run
without folding the array; primitive duplicate markers remain separate from the
private-array marker. Exact sources distinguish callback caller-CV COW, retained
request-string flags, copied candidates and trace-only inputs, with real bucket
references and query COW. Nonfinite-float flags remain outside this extension.
[Scalar array-flag review](../../coverage/semantics/define-array-scalar-flag-review.json).

NULL array flags use the existing parameter-3 bool Deprecated diagnostic before
the C body. Reception authenticates the raw capture without traversing the array.
A normal callback may repair a cycle before canonical copying, create a cycle
that raises ValueError before duplicate reporting, or install the key that the
outer call subsequently finds. The private duplicate copy remains distinct from
the original API input and is retired through ordinary cleanup. A throwing
Deprecated callback cancels validation/copy/registration, retaining the same
Exception, raw NULL trace, callback effects and unassigned caller destination.
Strict calls instead raise TypeError before Deprecated or recursive validation,
after argument effects. Trace-owned inputs retain original aliases and append
history while queries use canonical copied tables.
[NULL array-flag review](../../coverage/semantics/define-array-null-flag-review.json).

Byte-only `PSTRING` array flags use the same reception path when their contents
are valid bytes. Compiled literal-array element reads are a genuine producer: the raw
value remains separate from later COW writes to the caller's flag array. Empty
and `"0"` are false; other nonempty byte strings are true. Normal and pending
Warnings keep those captured bytes while copying the current array graph;
strict calls reject before cycle validation. This adds no carrier, string
allocation identity or cache authority: the shared scalar constant classifier
still refuses these values. Malformed bytes and invalid authenticated carriers
remain rejected. Existing source/known-value and array-ownership guards remain
unchanged; wider identity-sensitive consumers remain partial.
[Byte-only array-flag review](../../coverage/semantics/define-array-byte-flag-review.json).

Top-level empty values use the existing source-pool or retained immutable flag.
An authenticated immutable empty keeps its table and `PVARRAY true eps`; a mutable
emptied input becomes a fresh canonical table with `PVARRAY false eps`, rebuilding
its append index. Literal validation checks this class as well as contents, so a
same-content mutable clone cannot replace a fixed empty literal. Variable payloads
retain structural authority. Two exact sources and two public fronts/162 premises
check these distinctions and later copies in the
[empty ledger](../../coverage/semantics/dynamic-constant-empty-review.json).

Empty-root duplicates reuse the same reporting marker. An authenticated immutable
argument retains its pooled table without allocation; the abstract marker may
name that ID both as candidate and as API input. A mutable emptied argument gets
a distinct canonical empty candidate with NEXT0, preserving its captured input's
old append history. Caller writes COW away from that input, so Exception traces
retain the original empty table and append index. Normal false delivery and
throwing-handler discard release the mutable private root before API input;
a trace can keep the latter alive while the immutable pooled table stays pinned.
Root counts describe abstract owners, not Zend refcounts.
[Empty-duplicate review](../../coverage/semantics/define-empty-array-duplicate-review.json).

Empty descendants follow the same provenance policy at every recursive descent.
Authenticated immutable children retain their table and class; each occurrence
of a mutable emptied child becomes a distinct canonical empty table with NEXT0,
even when source entries share one reference cell. Copying follows all argument
effects. Stored queries return the existing tree; caller branch writes use COW.
Duplicate candidates keep these DIRECT children while callbacks and Exception
traces retain the original ALIAS cells and append history. The ancestor guard
also covers empty heads; canonical class/history, allocation and cycle refusals
remain enforced. [Nested-empty review](../../coverage/semantics/define-nested-empty-array-review.json).

For ordinary string user keys with omitted or captured false flags, recursive
array arguments raise `define(): Argument #2 ($value) cannot be a recursive array`
before copying or duplicate-key reporting. A partial live-edge walk dereferences
current source cells and checks ancestor paths, so repeated acyclic children are
allowed. Late flag effects can create or break a cycle after VALUE capture.
The Error keeps the original CONFIG arguments in its ordinary trace without a
canonical candidate, leaves old rows and caller destinations unchanged, and emits
no duplicate Warning. Explicitly breaking edges allows a fresh retry or ordinary
duplicate reporting. Invalid edges remain separate from genuine recursion, and
known compiled literal payloads cannot be replaced by forged cyclic captures.
[Recursive-input review](../../coverage/semantics/define-recursive-array-review.json).
Plain compiled string leaves remained a separate boundary at that cut; the
literal-string follow-up above admits them without replaying that campaign.

String-name `define` also retains an already-certified live stdClass donor or
completed user instance with an omitted, boolean or NULL flag. Registration stores
the captured object pointer and its completed-birth class, transferring the call owner
to a constant-row owner
without allocation. Named/selected sends retain their earlier value even when
a later argument rebinds the caller's CV. Duplicate warnings keep the original
row and callback property writes; throwing handlers preserve the Exception trace
owners until ordinary catch/unset cleanup. Historical rows validate their stored
birth/value and source policy, without reconstructing a past mutable CV or flag.
[Certified define review](../../coverage/semantics/define-stdclass-review.json).
User-instance admission derives the exact object/SITE class from its recorded
global construction and reuses completed-header, publication-prefix, no-busy-phase
and live-allocation guards. Copying arrays shares the same instance pointer;
property writes remain visible through donor rows and copied leaves. No constructor
is replayed, and existing destructor/trace cleanup keeps its ordinary owners.
[Instance define review](../../coverage/semantics/define-certified-instance-review.json).
True flags emit the ignored-case Warning before registering the captured object
pointer. Rebinding the caller's candidate CV does not replace that pointer;
property writes through its aliases remain shared. A supplied Warning Exception
still permits fresh registration with the same pending Throwable and unassigned
caller destination. NULL flags instead deprecate before the body: normal return
uses the current key table, while a throw cancels registration. Strict NULL raises
TypeError before callbacks. Normal true/NULL duplicates preserve the old row and
release the captured call owner through existing eager cleanup; source donors and
published rows keep their own roots. The exact sources observe shutdown destructors,
not early destruction or native refcounts. The pending-existing-key object helper
is covered by a pure, undriven composition control, not another executed callback.
[Object-flag review](../../coverage/semantics/define-object-flag-review.json).
Direct certified payloads also receive quiet integers, finite floats, byte-only
strings and authenticated string carriers as flags without replacing the raw
argument. Weak false flags publish quietly; truthy flags warn before current-key
lookup and may publish with the same pending handler Exception. Callback CV
rebinding leaves the captured pointer intact while property writes stay shared.
Strict nonboolean flags raise TypeError first and retain the raw API arguments.
Existing duplicate release and historical receipt validation are reused.
[Quiet object-flag review](../../coverage/semantics/define-object-scalar-flag-review.json).
Arrays, stdClass and ordinary user class instances used as flags instead raise
parameter-3 TypeError in weak and strict calls before the value reaches the body.
A recursive value or existing key cannot cause validation, copying or a duplicate
Warning first. The original flag and value remain in the API trace despite later
CV rebinding, array COW and shared property writes. An ordinary unpinned flag
object remains alive while the Error owns its trace, then uses normal destructor
cleanup when the trace is released. This rejection needs live argument authority,
not a new publication receipt.
[Invalid-flag review](../../coverage/semantics/define-invalid-flag-review.json).
Live Closures used as flags also reject before invocation or body work. The
existing Closure authority requires completed lexical capture or a valid named,
method or other supported callable record. A recovered lexical Closure preserves
its actual reference cell; a method Closure keeps its unpinned receiver through
the Error trace, and ordinary destruction follows release of that chain. Flag
rejection grants no publication authority and leaves callable conversion
unchanged. Other object flag kinds remain Unsupported.
[Closure-flag review](../../coverage/semantics/define-closure-flag-review.json).

Already certified Closure values can be published directly or inside array
snapshots. The existing durable record, exact object/site identity, source prefix
and live value validator supply the certified class; the structural runtime
policy below does not manufacture that certificate. Direct rows and copied array
leaves share the original pointer and static cells. A normal duplicate keeps the old row, and an ignored
true-flag Warning throw can still publish the captured Closure while propagating
the same Exception. Query bucket COW changes only the caller containers. These
checks execute omitted/false publication and true pending publication; other
admitted flag routes reuse the existing classifier and guards without additional
source credit.
[Certified Closure define review](../../coverage/semantics/define-certified-closure-review.json).

Ordinary live class-instance values without a constant-NEW record also use the
existing `PVOBJECT` tag in DEFINE rows and canonical array leaves. The exact
INSTANCE header, resolved nonabstract class and live allocation supply structural
authority; no allocation history or durable receipt is fabricated. A present
record must still validate as its certified class. Direct `constant()` queries
require a DEFINE origin; global constant/default-object policies stay unchanged.
An unpinned duplicate object retires before false delivery, and a private array
copy can keep the sole object owner after its source alias is cleared, running
its destructor before the original handler Exception reaches catch. The originals
use no-constructor classes and omitted/false flags; inherited flag delegates
compose through the classifier without extra source credit.
[Runtime object define review](../../coverage/semantics/define-runtime-object-review.json).

Bare runtime REAL, METHOD and NAMED Closures also use dynamic-only `PVOBJECT` authority.
REAL values require completed capture, valid static cells and scope completeness.
Their selected scope must either be absent with no binding, pass the existing
class-scope row validator with no binding, or pass the existing binding-source
validator with no ordinary scope. METHOD values use the existing live
method/receiver-scope validator.
Exact outer tags and absent callable records prevent invalid certified wrappers
or present records from falling through. Direct queries retain the DEFINE-origin
fence; global/default policies stay unchanged. Lexical aliases, per-Closure
statics and method receivers remain shared through canonical copies. When a
private duplicate array is the last Closure owner, its retirement can run the
receiver destructor before catch while the raw trace still observes a cleared
source alias. The REAL/METHOD originals execute ordinary unscoped lexical and bound method
Closures with omitted/false flags; structurally valid clones and inherited flag
delegates receive no additional execution credit.
[Runtime Closure define review](../../coverage/semantics/define-runtime-closure-review.json).

Class-born REAL originals also exercise inherited lexical Base/called Child
scope with separate private shadows, both with a receiver and receiver-free
static property access. Direct publication, duplicates and array/query COW
retain the same Closure, static cells and receiver edge. An explicit handler
invocation can mutate the receiver before the private array copy retires it,
running its destructor before the original Exception reaches catch. Only these
omitted/false originals receive new execution credit; valid bindings, coherent
clones and inherited flag delegates retain structural support. Selected binding
validation preserves genuine prior bound values while refusing malformed
presence-only projections; no producer history or certificate is fabricated.
[Scoped REAL define review](../../coverage/semantics/define-scoped-runtime-closure-review.json).

Bare NAMED user-function Closure values also use dynamic-only PVOBJECT
publication under live function/name-map authority, with no scope, binding or
callable certificate. Distinct first-class objects and direct calls share the
function's request STATIC cells, which are independent roots and never Closure
child edges. Canonical/query copies share the Closure pointer while preserving
array COW and append history. Retiring the last Closure leaves function statics
alive; an explicit later direct-function clear can destroy their held child.
Only ordinary first-class-function omitted/false originals receive new execution
credit; coherent clones and inherited flag delegates retain structural support.
[Named Closure define review](../../coverage/semantics/define-runtime-named-closure-review.json).

Bare array-selected method Closures use dynamic-only `PVOBJECT` authority through
the existing live selection-site, method/capture and lexical/called/receiver-scope
validators, with absent binding/callable-certificate records. Original callable
arrays and member cells are conversion inputs, not Closure children. Publication,
queries and canonical array COW retain the selected pointer and optional receiver
after input mutation or retirement; method static cells remain independent
request roots. A private duplicate array can become the only Closure owner,
retiring its receiver before the original handler Exception reaches catch.
Global/default policies and the DEFINE-origin direct-query fence stay unchanged.
Ordinary instance/static first-class-array omitted/false originals are distinct
from structural coherent-clone/inherited-flag support, which gains no execution
credit.
[Array-method Closure define review](../../coverage/semantics/define-runtime-array-closure-review.json).

Bare string-selected method Closures use the same dynamic-only `PVOBJECT`
policy with existing full-string/source-site, target and live scope
validation, plus absent binding/callable-certificate records. A fixed
Base::read capture inside an inherited method on a Child receiver preserves
the Base descriptor despite a Child override, with called Child and the
original receiver. A computed qualified static string retains its selected
class/method after its source CV changes. Original strings and creator
frames are not Closure children; only an optional receiver is. Method
static cells remain independent request roots. Direct publication and
canonical/query COW share the pointer, and private duplicate-copy
retirement can run its receiver destructor after handler output but before
the original catch. Global/default policies and the DEFINE-origin
direct-query fence stay unchanged. Only ordinary
fixed-instance/computed-static omitted/false originals gain execution
credit; coherent clones and inherited flag delegates are structural
support. Factory/intrinsic and other Closure domains remain separate.
[String-method Closure define review](../../coverage/semantics/define-runtime-string-closure-review.json).

Bare FROMCALLABLECLOSURE values use dynamic-only `PVOBJECT` authority through
existing live scope and saved source, USER permission, selected method and
receiver validators. A captured factory may retire: its saved source still
authenticates the invocation, whose USER scope supplies selection permission.
Private Base selection remains distinct from a Child same-name method when
the selected Closure is later invoked globally. Source callback arrays, factory
objects, creator frames and frozen input/history fields are not Closure children; only
an optional nonstatic receiver is. Method static cells remain independent
request roots. Direct publication, canonical/query COW and pending duplicate
retirement preserve pointer/scope identity and the original Exception; the last
private receiver can be destroyed after handler output and before catch.
Certificate/wrapper priority, global/default policies and the DEFINE-origin
query fence stay unchanged. Only ordinary direct instance/static and captured
factory-instance omitted/false originals gain execution credit; coherent clones
and inherited flag delegates retain structural support. Factory values have
separate source guards below; other excluded object forms gain no new authority.
[From-callable Closure define review](../../coverage/semantics/define-runtime-from-callable-review.json).

Bare FROMCALLABLEFACTORY values use dynamic-only `PVOBJECT` authority with
existing live fixed-creation source validation and absent scope, binding and
callable records. Creation metadata supplies no USER permission or receiver
edge. A queried class-created factory invoked globally still rejects private
access; a queried factory invoked inside a Base USER frame can select its private
method. Normal duplicate disposal can retire the last rejected factory while
a derived method Closure retains valid saved source without owning that factory.
Canonical/query COW preserves factory identity, including explicit `__invoke`;
method statics remain independent request roots. On private denial, both Error
trace frames share the raw callback array and its single receiver edge. Later
Error/view retirement releases that receiver through normal cleanup with no
pending Error. Global/default policies, certificate priority and the DEFINE-origin
query fence stay exact. Only ordinary omitted/false direct/array originals gain
execution credit; coherent clones and inherited flags remain structural support.
Other intrinsic Closure forms retain their existing boundaries.
[Factory Closure define review](../../coverage/semantics/define-runtime-from-factory-review.json).

Bare INTRINSICCLOSURE values reuse PVOBJECT under existing supported intrinsic
typed/live checks, absent scope/binding/certificate records and the exact outer
tag. Queries and canonical ARRAY copies preserve the same pointer. A queried or
trace-recovered DEFINE Closure can become a writer using its own existing
selection receipt, despite later callee-CV replacement. A supplied duplicate
Exception keeps the rejected VALUE after its distinct same-kind callee dies;
later trace retirement can kill that VALUE while its primitive row remains
source-valid through nonowning history. Intrinsic Closures add no child edges.
The originals execute DEFINE VALUE and ARRAY DEFINE/DEFINED/CONSTANT identities;
only DEFINE is invoked. Other supported intrinsic kinds compose structurally;
existing typed/live eligibility and global/default policies stay exact.
[Intrinsic Closure VALUE review](../../coverage/semantics/define-intrinsic-closure-review.json).

Ordinary `stdClass` values also use dynamic-only `PVOBJECT` authority when their
selected property record and optional cached table validate, including live
physical reference cells and their immediate values. A present stdClass birth
record retains certified `PVSTDCLASS` priority and cannot fall through if invalid.
No producer history is reconstructed; global/default policies stay unchanged.
Direct queries keep the DEFINE-origin fence. Object/property identity remains
shared through cast-table COW and canonical array/query copies. A private copy
can retain the last box-to-table-to-reference-to-child path after a throwing
handler clears the source alias, running the child destructor before catch.
The originals use ordinary NEW with omitted/false flags; coherent casts/clones
and inherited flag delegates have no additional execution credit.
[Runtime stdClass define review](../../coverage/semantics/define-runtime-stdclass-review.json).

Other Closure forms, internal object values, other owning
array leaves, nonfinite direct-object flags, coerced names and wider owning define domains
remain partial.

Class-qualified `defined` queries reuse inherited lookup and the actual caller's
lexical visibility. Missing or inaccessible members return false. The initial
folded-value slice did not evaluate deferred descriptors. An absent
class can enter the named autoload queue and resume the same captured query once.
The loader receives the class name while the API trace retains the full query/carrier
and dynamic selection. A loaded class's missing member never reloads it. Two exact
sources and two public fronts/288 premises bind these paths and malformed query,
carrier, selection and resume rejection in the
[qualified-defined ledger](../../coverage/semantics/class-qualified-defined-review.json).

Class-qualified `constant` uses the same captured query and actual lexical access,
but returns a folded primitive or authenticated literal string and raises an API
`Error` for missing/inaccessible lookup. Direct string installation normalizes its
raw pool allocation class through the existing interning rule; parser provenance
still authenticates the returned carrier. The named loader receives only the class,
while its API trace and one-shot resume keep the full query and selected callee,
even when the loader changes both caller CVs. Loaded-member misses do not reload.
Two exact sources and two public fronts/384 premises cover value types, current
Error traces, actual CV mutation and malformed continuation authority in the
[qualified-constant ledger](../../coverage/semantics/class-qualified-constant-review.json).
Folded nonempty literal-array queries return the existing pooled root, preserving
nested sharing and raw leaf-string allocation classes. Ordinary COW writes detach
only the written tables; acquiring a reference separates the mutable root/child
while the constant and by-value peer retain their original leaves. The source
initializer and pool class authenticate a DIRECT primitive tree with canonical
ordered keys and table history. No define-style recursive snapshot is taken.
Two exact sources and two public fronts/326 premises cover same-root/no-allocation
returns, root/nested detachment, actual reference acquisition and tree/history
refusal in the [array-query ledger](../../coverage/semantics/class-qualified-constant-array-review.json).
Immutable empty roots and children retain their exact pool class and table.
Admission reuses the existing exact-empty allocation/source-pool authority;
empty topology alone is insufficient. An emptied mutable copy keeps its append
history, and a canonical mutable clone cannot impersonate a pooled literal.
Acquiring a reference to an empty bucket separates its parent while the reference
cell still holds the shared immutable child; append separates that child later.
Two exact sources and two public fronts/244 premises cover these distinctions in
the [empty-query ledger](../../coverage/semantics/class-qualified-constant-empty-review.json).
Deferred untyped class members with a plain global-name initializer use the
existing per-value evaluator/cache. The captured API query stays in its real resume;
a nonowning selection must match the adjacent declaration binder and that exact
resume. An unrelated bad sibling is not evaluated, and these queries never mark the
whole class table updated. Missing globals raise `Error` with the API line and full
query trace; failed evaluation restores context without a cache entry, so later
definition permits retry. Successful runtime string values retain their authenticated
carrier and allocation class, without the direct-literal interning step. Class-only
fact/cache guards compare that carrier with its immutable global row; generic global
publication rules are unchanged. Existing structural variable-input policy remains.
Two exact sources and two public fronts/314 premises cover those distinctions in the
[deferred-query ledger](../../coverage/semantics/class-qualified-constant-deferred-review.json).
Qualified `defined` also runs this bounded requested initializer, then returns
true rather than its cached value. Visibility is checked first, so an inaccessible
member does not initialize or cache even if its global is missing. A visible
failure preserves the captured `defined` API frame and permits a genuine retry.
The exact declaration binder must precede the same `DYNAMIC_DEFINED_RESUME`;
fixed global/explicit-global and retained selected sites authenticate entry.
Fixed namespace fallback stays outside this deferred path. Two exact sources and
two public fronts/415 premises cover quiet rejection, failed context restoration,
retry, boolean results and request-string cache identity in the
[deferred-defined ledger](../../coverage/semantics/class-qualified-defined-deferred-review.json).

Keyword queries retain the captured raw query while resolving `self` from lexical
scope, `parent` from that scope's source parent and `static` from the called class.
Inherited-method eval preserves its immutable lexical binding separately from the
called class. Both APIs raise scope Errors before quiet member lookup; ordinary
unscoped calls do not borrow an outer frame's scope. Folded keyword `defined`
returns a boolean; keyword `constant` returns only the authenticated folded
primitive/literal-string domain. Two exact sources and two public fronts/368
premises cover six eval queries, two actual Error traces and budget resumption in
the [keyword-query ledger](../../coverage/semantics/class-keyword-query-review.json).
Internal/bound-Closure scopes and other keyword initializer/value domains remain open.

Mutable-empty/deferred/nonliteral class-array query values and wider domains remain open.

Global `constant` queries now read primitive user values, authenticated interned or
request strings, special `true`/`false`/`null`, and the modeled primitive startup
constants. The received string supplies the full query: remove one leading
separator, lowercase only namespace components, and preserve terminal-name case.
Caller namespaces and imports do not prefix the string. Lookup occurs after
argument effects. Stored string carriers retain their allocation class; the API
does not intern or rebuild a result. Named and positional literal arguments use
immutable compiler facts, while mutable arguments retain the existing capture
policy.

Retained DEFINED/CONSTANT Closure callees also accept one captured non-NUL global
string name, through the existing live matching-intrinsic owner and source/site,
line and named-call validation. `SELECTION` stays empty: these reads create no
durable selection record. Immutable argument facts must still match the captured
value, and request string carriers retain their existing authentication.
Argument effects can replace the live callee/name and register a constant before
lookup without changing the captured call. Ordinary and explicit `__invoke`
calls share this admission. A missing-name explicit call retains raw API/wrapper
trace arguments on Error; the callee retires before catch, while a later
ordinary call through an independent reader recovers.
Returned arrays use the same stored root and existing query COW/append history.
The three originals and focused state checks cover these paths without extending
name coercion, class-qualified/HALT/NUL names, packs or PIPE.
[Captured query review](../../coverage/semantics/constant-owned-query-review.json).

Captured query callees also receive Boolean, integer and finite-float names under
the existing live matching-owner and source/argument-fact checks. The original
ownerless scalar predicate stays exact; the owning route requires empty selection
and packs and excludes PIPE. Nonfinite owning names remain separate; NULL uses
the continuation below.
Strict ordinary calls reject the captured raw scalar after argument effects.
Explicit `__invoke` receives weakly even in strict source. Existing pure string
conversion supplies the lookup spelling without writing caller CVs; lookup sees
constants registered by earlier argument effects. A weak missing-name Error uses
the received string only in its API frame and the original scalar in the explicit
wrapper frame. The raw call continues to authenticate source, callee and line.
Native originals distinguish late integer and false/empty-name lookup, ordinary
false Error, strict true TypeError and explicit finite-float Error/recovery.
Existing CONFIG ownership retires each selected callee after return or throw;
retained trace arguments survive a later independent reader. No receipt, root,
schema or conversion policy is added.
[Captured scalar query review](../../coverage/semantics/constant-owned-scalar-query-review.json).

Plain `constant`/`defined` calls also receive integer, boolean and float query
names. Weak callers use the existing string conversion after
argument effects; strict callers raise `TypeError` before conversion. The captured
call keeps its original value and selected callee. Available immutable argument
facts must match that exact value. Conversion changes only the API slot: a weak
missing-name Error shows the received string in its trace, while strict TypeErrors
retain the original argument and actual parameter name. Caller CVs stay unchanged.
Stringable and bounded array query reception are covered below; packed/wider
owning forms remain separate.
The [scalar-name review](../../coverage/semantics/global-constant-scalar-name-review.json)
records source-backed reception, trace values, source rejection and budgets.

Null query names keep the original call through the weak-call deprecation.
While the handler runs, the API trace keeps the raw null argument. Normal return
converts it to the empty string and only then queries the current table.
A handler can therefore publish the requested empty-name binding. Caller mutations
do not replace the captured value or selected callee. A missing-name Error after normal return shows
the converted string; a throwing handler keeps null in the API trace and cancels
the lookup. Strict null calls raise `TypeError` without dispatching a deprecation.
The [null-name review](../../coverage/semantics/global-constant-null-name-review.json)
records genuine warning/resume fronts, source refusals and budget continuation.

Captured NULL query callees reuse the same live matching-owner and source/fact
authority with empty selection/packs and no PIPE. Existing
`DYNAMIC_NULL_CONSTANT_RESULT` and callback tasks retain that owner through the
warning and handler. A normal return converts NULL after callback effects; a
false return delivers the default Deprecated before lookup. Ordinary strict
calls reject before warning dispatch, while explicit `__invoke` stays weak in
strict source. A missing-name Error separates its received empty-string API
argument from the wrapper's raw NULL. A throwing handler preserves raw NULL in
both frames and cancels conversion/lookup, including when its own empty-name
definition succeeds. Shared cleanup retires the callee before catch. Existing
continuation bodies, schema, roots and receipts remain unchanged.
[Captured NULL query review](../../coverage/semantics/constant-owned-null-query-review.json).

One positional Stringable query name now uses the existing user-method conversion
pipeline. Weak `constant`/`defined` calls retain the raw object through
`__toString()`; a normal string return replaces the API slot in a separate CONFIG
step before ordinary non-NUL global lookup. A missing-name Error therefore traces
the received string. Strict calls reject the raw object without method entry.
A method-created Exception keeps the real method/API/caller trace, raw receiver,
identity and callback effects while both conversion consumers are discarded.
Dedicated saved-site guards enforce one positional argument even in file-enabled
states; query kinds stay outside the broad string-conversion kind predicate.
The [Stringable-query review](../../coverage/semantics/constant-query-stringable-name-review.json)
binds source4/author463 at bc3590e16 and independent179 at 9fa625b8b, all runtime
931f6caac. The sole pre-main peer frame-field assertion failure retains zero credit;
only its one-line fixture correction repeats. Retained propertyless receivers,
ordinary typed-string returns and existing global values bound the validated slice;
ownerless sole-owner destruction, wider receiver/return lifetimes, NUL/HALT names
and named/packed forms remain partial. No task/schema or shared stringifier change.

Captured DEFINED/CONSTANT callees also receive one positional Stringable name.
The live matching owner and existing source/site checks authenticate the raw
call; the argument must have no immutable compiled value fact. Selection and
packs stay empty, PIPE is excluded, and normal conversion must return a non-NUL
global name. Ordinary calls hand off the received string before lookup, releasing
the raw argument while the callee stays alive. Its destructor can therefore
publish the name that lookup reads, even after conversion rewrites caller CVs.
Explicit `__invoke` finishes lookup with the received string while retaining the
original object in its wrapper argument. Normal DEFINED can return false before
destruction publishes that name; a missing Error has a string API argument and
an object wrapper argument. The callee retires before catch, while a copied raw
wrapper-argument array can retain the object after Error/trace release. Strict
ordinary calls reject without method entry and retain the raw object in their
TypeError trace. Eager release drops both explicit argument slots before its callee
when both become unreachable together. No schema, root or receipt policy is added.
[Captured Stringable query review](../../coverage/semantics/constant-owned-stringable-query-review.json).
Class-qualified/HALT/NUL results, named/packed calls, known-value arguments,
supplied conversion throws and wider receiver/return forms remain partial.

Retained propertyless Stringable query names returning non-NUL class-qualified
text now reach the existing user-class lookup guards after conversion. One finish
predicate and its comment change; source/carrier/saved-site checks, the global arm
and class/autoload machinery stay exact. Actual loaded folded-member value,
`defined` true/false and missing-member Error fronts preserve earlier selection
and the returned string. A named loader receives the bare class only after that
handoff; a supplied throw preserves caller99, callback siblings and live writes.
The [Stringable class-query review](../../coverage/semantics/constant-query-stringable-class-name-review.json)
binds four exact originals and 1,026 state premises (271+189+260 author, 306 independent)
at 5f47101bd/runtime 4a7f0f801. The peer native observes loader output, saved Exception
identity/message and effects without trace traversal. Its actual three-frame
loader/converted API/caller trace, authentic request carrier, recursion-key cleanup
and full-state discard are state assertions. Same-object global TRUE recovery
exercises the unchanged arm. Nine stable reports pass on their first attempts;
quiet PHP/worker stderr and all children reaped. Initial 8fd2/CPU2 baseline
Unsupported/B|S| retains zero credit; later actors use CPU1. Only the old Source53
`A::B` finish control changes, freshly covered here without renewing 642 or Source57's
844. NUL/HALT results and wider lifetime/lookup/value/call domains remain partial.

Retained ordinary nonStringable instances and `stdClass` names now fail the
query's string parameter before lookup, in weak and strict calls.
A separate live-instance guard excludes Stringable receivers and other internal
object kinds. It reuses the same source/positional checks and direct raw TypeError
allocator without launching conversion or changing the captured object. An ordinary
public `toString()` method does not make a class Stringable. Earlier argument
captures survive live callee/name changes, and a later ordinary query recovers.
The [nonStringable-query review](../../coverage/semantics/constant-query-nonstringable-name-review.json)
binds author3 at c77c7abca and corrected peer1 at 7e8a3c0ce, with all 508 state premises
at 7e8/runtime6282a8468. The original peer's `__call` declaration stops before B|
in the existing method-compiler boundary and retains zero agreement; only that peer
changes to an ordinary `toString()` method, followed by previously unrun state checks.
Source53's conversion/trace/lifetime rules and accepted642 cuts stay unchanged.
Propertyless retained receivers bound this validation; sole-owner destruction,
other internal objects, `__call` declarations and wider forms remain partial.

Retained propertyless Stringable names now convert before positional `define`
registration with primitive candidates and an omitted/bool-false flag. Dedicated
arg0/source and saved-site guards keep DEFINE outside the broad string-kind
predicate. A successful method returns to a separate converted CONFIG before
current-table registration, so a method-created key selects the real duplicate
Warning. Strict calls reject the raw object before method entry. A method throw
retains its raw receiver/earlier candidate API trace and discards both consumers.
The converted CONFIG preserves its authenticated name carrier; later user-duplicate
traces keep the existing name byte projection, without name-carrier identity credit.
The original candidate carrier and false flag remain exact.
The [Stringable-define review](../../coverage/semantics/define-stringable-name-review.json)
binds literal agreement at83a7b816b and final captured/strict/peer agreements plus
all717 state premises atf13b5e451/runtime83a7. The captured source observes exact
Warning metadata, supplied Exception identity, caller99 and callback effects;
its actual full trace/message/PreviousNULL and discard are checked at reached
state fronts. Earlier trace-observing native originals remain native-only: two
CLI45 timeouts and one prior DSL binding failure retain zero credit. Only the
changed source and affected/unrun checks repeat; Source53/54 evidence is unchanged.
Sole-owner destruction, wider receivers/returns, NUL/HALT results, owning
candidates, coerced flags outside the NULL follow-up and
named/packed/owner forms remain partial.

Retained propertyless Stringable `define` names returning non-NUL `::` text reach the
existing class-name ValueError before registration, with primitive candidates and
omitted/bool-false flags. The sole change widens the finish predicate; source,
carrier and saved-site guards, the global arm and the existing class receiver
stay exact. Actual API traces keep the returned string carrier and earlier
candidate/false, without a stale method frame or receiver edge. Method-created
siblings and caller99 survive; autoload/classes/cache stay untouched.
The [Stringable class-name review](../../coverage/semantics/define-stringable-class-name-review.json)
binds four exact originals and 844 state premises (171+190+274 author,209 independent)
at 309d70e25/runtime 96f871d40. Bare `::` then global publication with the same retained
receiver proves recovery. All nine reports pass on their first attempts, with
quiet PHP/worker stderr and all children reaped; initial d414/CPU2 baseline
Unsupported/B|S| retains 0 and later actors use CPU3. One obsolete Source55 `A::B`
finish control now admits converted CONFIG/class shape; new reached fronts cover
that extension without renewing Source55's 717 or Source56's 556 evidence. NUL/HALT
results and wider lifetime/value/flag/call domains remain partial.

Retained propertyless Stringable `define` names now admit captured boolean true
with primitive candidates and non-NUL global or class-like results. One raw-call
shape alternative reuses the existing conversion, ignored-Warning, duplicate and
pending-exception rules. Conversion completes before the ignored-flag Warning;
class-name ValueError and strict raw-object TypeError precede it. Normal fresh
publication returns true, and normal duplicates warn again and return false.
A method-created Exception cancels both conversion consumers without registration
or an ignored Warning. A Warning-handler Exception instead registers a fresh
captured primitive value before propagation; callback siblings/live writes and
caller99 survive. The converted CONFIG keeps its authentic name carrier, while
that Warning's API trace retains the existing name-byte projection and exact
candidate/true captures. Native throw observers avoid trace traversal; state
checks inspect both actual traces and entire restored discard states.
The [Stringable true-flag review](../../coverage/semantics/define-stringable-true-flag-review.json)
binds four exact source agreements and 974 premises (383+179+99 author,313 peer)
at d731cddc8/runtime d4055de44 across six genuine DEFINE fronts. All nine reports
pass on their first attempts: literal default delivery has exactly three PHP
Warnings, other accepted cases are quiet, and all worker stderr is empty. Initial
1d6ea057f native/base and later d731 actors use CPU3; Unsupported/B| retains zero
credit. Source55/56/57 evidence stays at its earlier cuts without replay. Pending
duplicates under a Stringable-derived Warning throw, owning candidates, coerced
flags beyond the follow-ups, wider lifetimes and call forms remain partial.

Retained propertyless Stringable `define` names now receive captured NULL flags
with primitive candidates, for the existing admitted non-NUL user-global and
class-name result domains. One raw-shape alternative hands the converted CONFIG
to unchanged NULL reception/registration rules. Conversion precedes Deprecated,
including before a class-name ValueError; strict calls reject the raw object
before conversion or NULL reception. The actual NULL-handler API trace preserves
the returned REQUEST name, earlier candidate and raw NULL, unlike the separate
true-Warning name-byte projection. A returning deprecation handler may publish
the key first, so the outer call reaches a later duplicate Warning/false result.
A supplied deprecation-handler Exception instead cancels registration, preserving
the same Throwable, caller99, callback sibling1877 and live writes. Native peer
observes effects/identity without trace traversal; state checks the actual trace
and entire restored discard.
The [Stringable NULL-flag review](../../coverage/semantics/define-stringable-null-flag-review.json)
binds four exact originals and 1,084 premises (396+273+97 author,318 independent)
at af0ba7814/runtime b2c1de3bc across six actual Stringable DEFINE fronts. All nine
reports pass on their first attempts, with default3 Deprecated+1 Warning, selected1 Warning,
strict/peer quiet and empty worker stderr. Initial7ec085 native/base and lateraf0
actors use CPU3; unchanged Unsupported/B| retains zero. Two old55 append-NULL
raw-shape refusals become source-valid refusals, with all other controls/counts
unchanged; genuine NULL3 and mismatched2/4 controls cover that admission without
renewing Source55's717 or Source59's974 cuts. Startup/special/HALT results,
flags beyond the follow-ups, owning candidates and wider lifetimes/call forms remain partial.

Retained propertyless Stringable `define` names now receive quiet nonboolean
integer, non-NaN float and authenticated INTERNED/REQUEST string flags with
primitive candidates in admitted non-NUL user-global/class-name domains.
A separate three-argument raw head leaves bool/NULL/omitted guards and all
source/carrier/saved-site, conversion, reception, trace and discard code unchanged.
Conversion preserves the raw flag: false skips the ignored Warning, truthy warns
before duplicate lookup, and class-name ValueError precedes that body Warning.
Strict calls still reject the raw name before method/flag processing. Returning
handlers can install the target before the outer duplicate; a duplicate-handler
Exception preserves the old row, sibling and caller99. Actual state API traces
retain the returned REQUEST name, earlier candidate and raw REQUEST flag; peer
native observes effects/identity without trace traversal.
The [Stringable scalar-flag review](../../coverage/semantics/define-stringable-scalar-flag-review.json)
binds source4 and 1,203 premises (482+282+100 author,339 independent) at cc7f88f54
across seven genuine DEFINE fronts. Initial59d native/base and peer-native af678
keep their cuts; Unsupported/B| remains zero. The first model and CONFIG diagnostic
localization remain zero; the documented Cons/Fixed overlap limitation required
only an equivalent exact-length Cons pattern, with no vendor change or PHP divergence.
All twelve reports are stable/reaped with no timeout/interruption/survivor;
accepted PHP Warning counts are2/1/0/0 and accepted worker stderr is empty.
One old60 PINT0 refusal becomes positive raw shape; genuine quiet0 fronts cover
that boundary without old1084 replay. Bare legacy PSTRING flags, NaN flags,
startup/special/HALT results, owning candidates and wider lifetimes/forms remain partial.

Positional `define` now rejects retained ordinary nonStringable instances and
`stdClass` names before primitive optional flag reception or registration, weak
or strict. Later arguments have already run: raw receiver, request candidate and
true/NULL/integer flag captures survive live callee/name/value/flag changes.
A public ordinary `toString()` remains uncalled. The separate guarded route reuses
the live query-object classifier and primitive/carrier/source checks, allocates
raw TypeError directly and consumes the original CONFIG tail. It leaves Source55
Stringable conversion and the shared trace/ownership machinery unchanged.
The [nonStringable-define review](../../coverage/semantics/define-nonstringable-name-review.json)
binds four exact originals and all 556 state premises at 4a71a12f7/runtime ead614ee6:
author166+110+105 and independent175 across five actual errors and a selected normal
query recovery. Raw owner edges/API/caller traces, receiver property projection,
untouched stores/table/events, source/carrier/liveness/domain controls and budgets
pass. All nine reports pass on their first attempts; initial afb8 native/baseline
uses CPU3, later actors use CPU5 and baseline Unsupported/B| retains zero credit.
Primitive tail strings require authenticated interned/request carriers. Other
internal objects, owning values, sole-owner destruction and wider forms remain partial.

`define` also receives int/bool/float names with nonowning primitive values and
an omitted/already-false flag. Each source send maps to its normalized captured
slot before available immutable facts are checked, including reordered named
arguments. Weak calls convert at live precision; strict TypeErrors retain raw
arguments and publish no row. Registered keys survive later precision changes.
Historical immutable-name checks retain the same scalar and allow a possible
conversion without reconstructing the actual past precision.

Scalar-name duplicate warnings retain the original call, received carrier,
call-time precision and pre-warning table prefix. Returning handlers preserve the
old value and return false; a handler that changes precision and throws still shows
the received name in the API trace. The caller's scalar and assignment destination
stay intact. The [scalar-define review](../../coverage/semantics/define-scalar-name-review.json)
binds four sources and351 public premises, with failed initial checks kept separate.

Positive infinite float names now enter the existing protected duplicate path when
conversion produces `"INF"`, with primitive candidates and omitted/bool-false
flags. Two guard disjunctions admit that received name without a user-table row;
all source, carrier, strictness and prefix checks remain unchanged. The raw float
capture stays authoritative while duplicate API traces contain the received string.
Returning handlers keep the builtin and return false; throws retain the same
Exception, callback siblings and unassigned caller result. Negative infinity still
publishes the fresh `"-INF"` key at precision14.
The [infinite-name review](../../coverage/semantics/define-nonfinite-name-review.json)
binds four source agreements and 529 public premises, including actual default,
handler, resume and discard transitions. The peer changes live precision14 to1;
the saved conversion still shows `"INF"`. Pinned `zend_gcvt` truncates a new
precision1 conversion to `"I"`, so that alternate historical precision is refused,
while 3 and -1 remain possible. The initial incorrect precision premise retains zero
credit; only affected state fixtures repeated. Strict NaN names reject the raw
float before conversion. The full-NAN weak follow-up is below; nonbool flags with
nonfinite names and owning/wider candidates remain partial.

Weak NaN `define` names whose rendered spelling is full `"NAN"`, with primitive
candidates and omitted/bool-false flags, now dispatch the string-conversion Warning
before the protected duplicate Warning. Rendering and
request-string allocation precede the first callback; its API trace still contains
the raw NaN. Normal return uses that saved string even if the callback changes
precision or caller name/value/flag/callee CVs. The second callback sees the converted
name while the candidate and false flag remain raw. Default delivery warns twice
and returns false without publishing a user NAN row. A supplied throw from either
phase cancels the remaining work, preserving its Exception, callback effects and
unassigned caller result.
Two authenticated RESULT/DUPLICATE task alternatives retain the allocated carrier,
saved precision and later table-prefix bound. The old scalar NaN received/duplicate
refusals remain exact. A state-aware entry selects only weak full-NAN conversion;
strict calls and low initial precision `"N"`/`"NA"` take their unchanged old routes.
The [NaN-name review](../../coverage/semantics/define-nan-name-review.json) binds four
exact originals and 451 public premises, including raw-first/converted-second API
traces, live1 versus saved14 rendering, both actual throw discards, immutable
NaN-bit/source/carrier/phase/bounds refusals and budgets. Native self-inequality
observes NaN; payload bits are model facts, not native bit observations. No failed
actor or retry occurred. Truncated-name callback protocols, other flags and
owning/wider candidates remain partial; no earlier evidence is renewed.

Int/bool names accept nonbool false scalar flags: integer 0, empty/`"0"` strings and
signed float zero. The existing scalar-name path converts the name before quiet
bool reception, leaving the raw third argument in duplicate API traces. Strict
parameter-1 errors precede nonbool third-parameter rejection after all effects.
An optional-third carrier guard authenticates request strings; legacy two-argument
and bool-false paths keep a trivially true guard. Only 20 module400 insertions extend
the existing marker domain; receive, duplicate, trace and strict code are unchanged.
The [false-flag name review](../../coverage/semantics/define-scalar-false-flag-review.json)
binds four exact originals and 595 public premises across fresh/default duplicate,
captured publication, strict and throwing empty-key duplicate groups. They check
converted names/raw request flags, old binding/sibling effects, full restored-state
discard equality, literal/carrier/prefix refusals and budgets. Nonfinite float names with
these flags, truthy/NULL/NaN flags and owning/wider forms remain partial; the bounded
NULL-name false-flag follow-up is below.

Finite float names also receive these quiet false scalar flags. Name conversion
uses call-time precision and leaves the flag raw; `-0.0` and `0.0` register distinct
`"-0"` and `"0"` keys. A duplicate marker retains the converted name, precision and
original table prefix across handlers. Strict calls reject the raw float name
before nonbool flag parsing, after all argument effects. Four module400 lines
extend only the finite-float parser domain; receive/duplicate/trace and legacy
omitted/bool-false code are unchanged. Two older float-shape refusals are updated
to shape admission plus immutable-source or received-name mismatch controls.
The [float false-flag review](../../coverage/semantics/define-float-false-flag-review.json)
binds four source agreements and 603 public premises. Reached signed-zero/literal37,
captured request-flag and precision-changing throw fronts exercise those changed
controls without replaying the historical 595 campaign. Nonfinite names with these
flags, truthy/NULL/NaN flags and owning/wider forms remain partial.

Null `define` names use a separate weak-call deprecation before conversion and
registration, with the same primitive-value and omitted/already-false flag boundary.
The first callback sees the raw null API argument. Normal return converts it to
the interned empty string and checks the current table; a callback-created binding
therefore causes a separate duplicate Warning. That warning retains the raw call
authority but exposes the converted name in its API trace. Returning handlers keep
the old binding and return false; a throw cancels the remaining registration.
Strict calls evaluate every argument before raising `TypeError` with raw arguments.
Available immutable null/name and value facts constrain the installed empty-key
row without rereading caller CVs or storing a conversion receipt.
The [null-define review](../../coverage/semantics/define-null-name-review.json)
binds four source agreements and396 public premises; the failed optional-field
fixture and unchanged baseline retain zero agreement credit.

NULL names also receive integer-zero, empty/`"0"` string and signed-zero float
flags. The first 8192 callback sees raw NULL and the original flag; normal return
converts only the name and checks the current empty-key binding. The duplicate
callback therefore sees an empty string name while the flag stays raw. A throw
from the first callback cancels registration; strict parameter-1 errors precede
nonbool flag rejection after all argument effects. Four module400 insertions reuse
the existing NULL receive/duplicate/trace path and authenticate optional-third
string carriers, deliberately extending only this marker domain.
The [NULL-name false-flag review](../../coverage/semantics/define-null-name-false-flag-review.json)
binds four source agreements and 755 public premises across separate retained cuts,
including current-table duplicate return, actual first-throw discard equality,
raw request flags, source/carrier refusals and budgets. The original source timeout,
pre-main fixture failure and baseline keep zero credit; only affected checks were
repeated. Other coerced flags, nonfinite float names with these flags and owning/wider forms
remain partial.

User-array queries retain the stored root and child identities. The admitted
tree contains nonstring scalars, raw strings, authenticated string carriers,
certified `PVINSTANCE`/`PVCLOSURE`/`PVSTDCLASS` leaves and arrays with matching key/class trees
and canonical table history. Immutable empty
arrays require their actual provenance; mutable empty copies remain distinct.
Lookup does not clone, allocate or intern values. Existing COW handles writes and
reference acquisition without changing the constant or other results. The
[array-query review](../../coverage/semantics/global-constant-array-review.json)
records repeated NaN-root identity, nested writes, empty roots, request leaves and
source-derived malformed-state/budget checks.

Object leaves retain the same completed-NEW or callable creation certificate as
top-level query results. Returning the stored array adds an array root owner;
it does not add an embedded-object edge. A later COW write creates another
physical array-to-object edge while keeping the object identity, property storage and
Closure static cells shared. References acquired in a caller copy can replace
its bucket without changing the stored tree. The
[object-leaf review](../../coverage/semantics/global-constant-object-array-review.json)
records genuine first/during-COW/post-release fronts and malformed certificates.

Queries also return installed `PVINSTANCE` user instances. The existing NEW
certificate authenticates the exact object identity, original initializer site,
completed construction and live allocation. Constant aliases retain that original
certificate. Returned objects keep their current mutable properties; the ordinary
RESULT owner supplements the table's owner. Lookup performs no construction,
cloning or property reset. The [instance-query review](../../coverage/semantics/global-constant-instance-review.json)
records plain/completed-constructor queries, shared aliases/property references,
actual owner increments, malformed certificates and budget resumption.

Installed `PVCLOSURE` rows also retain their original object identity and creation
certificate. Existing live-allocation, wrapper and source guards remain authoritative.
An alias keeps its own declaration origin and the original callable's creation
certificate. Querying does not rebuild the Closure or its static cells. Literal
Closure, named-function FCC and inherited static-method FCC results preserve
static storage and lexical/called scope. The
ordinary RESULT adds one owner alongside every installed table alias. The
[Closure-query review](../../coverage/semantics/global-constant-closure-review.json)
records actual query fronts, shared counters, alias roots and certificate refusals.

Absent names raise `Error` with the stripped lookup spelling and the full received
string argument in the API trace. Unknown startup values retain their prior Unsupported
result. `PVOBJECT` rows without the DEFINE-origin/live class-or-callable authority
above, stored ALIAS/cyclic array trees, Stringable/array name reception, packed
calls, and owning calls beyond the string/Boolean/integer/finite-float/NULL global-name
routes remain outside this slice. The original ordinary `const` string producer refusal retains
its historical cut; the string-publication follow-up above admits that producer
domain without renewing the older lookup campaign. The [global-query ledger](../../coverage/semantics/global-constant-review.json)
binds the source and public-state cuts without closing the constant family.

The matching engine routes are `ZEND_FUNCTION(define)`/`ZVAL_COPY`,
`validate_constant_array_argument`/`copy_constant_array`, `zend_register_constant`,
and `ZEND_FUNCTION(defined)`/`zend_get_constant_ex`. `PHP_FUNCTION(constant)` uses
exception-class lookup and `ZVAL_COPY_OR_DUP`; `zend_declare_typed_class_constant`
interns direct string values before installation.
Stored cyclic trees, other objects, nonfinite array flags,
Stringable names beyond the bounded retained query/DEFINE domains,
array names beyond the bounded flat query/DEFINE domains,
array/object values with scalar or null names, true/NULL/NaN
flags with scalar names, nonbool flags with nonfinite float names, true/NULL/NaN flags with
null names, special/startup names with flags or values beyond the bounded follow-ups,
internal/trait/interface/enum class queries, deferred keyword initializers and
keyword `constant` array values, other deferred initializers,
owning/FCC call forms and wider conversion/arity paths remain Unsupported. The [dynamic ledger](../../coverage/semantics/dynamic-constants-review.json)
keeps the source and public-state cuts separate; it makes no native allocation-identity
or full constant-family claim.

## Validation and remaining work

The maintained author catalogue compares 75 exact native stdout/stderr/exit profiles and checks 46 class/scratch assertions. Public protocols cover 14 table/class controls, 14 context/task controls, and six branch variants with 126 assertions. Three author state programs pass 821 assertions over adjacent steps and selected full resumes. Independent source, constant-owner, quiet-path, historical call-state, and compiler gates are recorded separately in the acceptance evidence.

The initial final reports used 899 inputs at `e7d552ec`; the final state report uses 899 at `ca3c06e5`. The explicit bridge changes only the state-test expectation from an empty allocation set to the initial request allocation set. Runtime/compiler bytes and modes are identical. The failed fixture outcome remains retained.

Nine new global callable originals pass at separate414/5d0/92ff source cuts; seven
source-derived AL programs/341 premises pass at21b5. The
[default ledger](../../coverage/semantics/deferred-static-defaults-review.json)
retains exact profiles, failures and fixture recovery. Matching8.5.10 sources are
`zend_compile_const_decl`, `ZEND_DECLARE_CONST`, `zend_ast_evaluate_ex` and
`zend_register_constant`: evaluate in the executing op-array scope, then register,
and destroy a duplicate candidate only after its warning finishes.

Three further exact originals pass at9619d2f57. The maintained
`global_constant_prebind_protocol.py` passes mixed90 and retry94 AL premises at
4262f787e, including before/after selections, wrong donor/leaf/holder/result,
consumer-prefix bounds, failed-unit transplants and candidate collection. Original
compile and fixture failures retain zero credit; earlier nine/341 cuts are not
renewed.

Three global NEW originals pass at17c12b379. The maintained
`global_constant_objects_protocol.py` retains argument103 at041ce1, inherited84
at00578e and escaped-retry87 atbc44da (274 AL premises). These check real pending
and saved phase owners, premature completion, full declaration/source/class/
prefix/result mutations, mutable-field identity, immutable include/eval access
and actual GLOBALTABLE-to-MAIN-ENV ownership. Original optional-tuple and restored
MAIN fixture failures retain zero credit. Duplicate-candidate and argument-abort
destructor originals remain uncredited until genuine eager release is available.
A separate cold no-constructor source passes atd2fb and80 AL premises ata1e14a2b4
check the pending instance table, true construction marker, warning order2→4,
fresh incomplete allocation and sole installed-constant ownership. A further
source1/81 AL premises at97dab9f8b check Error before target allocation/receipt/
registration, the retained pending template and fresh full declaration/NEW
identities on same-text eval retry. The earlier cold fixture's three
elaboration stops and one slice-length execution failure remain zero-credit;
no runtime rules or prior source/state gates changed.

Global initializer autoload now suspends a direct root NEW with empty prior facts,
retaining the exact declaration, source, line and live binder as a nonowning
certificate. Lookup precedes allocation and argument reads; only actual class-name
publication permits constructor selection. A miss creates Error before a target
receipt or constant row; unwind restores context before a fresh eval declaration.
Two exact sources and 326 SL premises (141 success and 185 retry premises) retain
runtime diff f3cd41fa in the [autoload ledger](../../coverage/semantics/global-constant-new-autoload-review.json).
The immediate THROW_SEARCH checkpoint checks its real cleared context and pending
binder; full public validation follows actual unwind. Pure malformed certificates
are never driven. The unchanged baseline's premature missing-class Error and the
binder/two fixture failures remain zero credit. Other internal and Throwable NEW,
nested autoload, earlier initializer facts, named/unpacked autoload arguments,
wider object-producing/lifecycle forms and remaining builtin/query behavior remain
open. Class/default and callable consumers keep their separate evidence; no
complete-core claim.

Direct-root zero-argument `new stdClass()` now uses the real `STDINSTANCE` heap
allocation and separate `CONSTANTSTDOBJECTS`/`PVSTDCLASS` certificates, without a
fabricated user class origin. A pending no-constructor phase owns the new object;
completion permits installation and ordinary reads. Historical certificates may
survive object death, while value admission still requires the exact live object.
Duplicate registration holds its candidate through the genuine Warning callback,
then discards it without replacing the original binding or its callback writes.
Two exact originals and 225 SL premises (110 root, 115 duplicate) at 369ebde3 cover
alias owners3→1, candidate1→0, source/tag authority and budget resume. The original
invalid duplicate observer remains zero credit; only its corrected local-alias
version supplies that source comparison. The producer milestone keeps embedded trees, default
caching and callable folding outside its slice; existing `defined()` presence
lookup remains unchanged. Other
internal/Throwable NEW and wider lifecycle forms remain partial.
[stdClass producer ledger](../../coverage/semantics/global-constant-stdclass-review.json).

Global `constant()` also returns certified `PVSTDCLASS` rows. The sole module400
value arm delegates to the existing exact completed-birth and live-allocation
checks, then reuses ordinary CONFIG completion. Literal and retained selected
calls share the stored pointer and property writes; RESULT adds one owner without
allocating or changing the constant table, birth history or object storage.
Repeated visits to one selected call site use their own captured query and nonce,
so changing the next query from one constant to another selects the second object.
The [query ledger](../../coverage/semantics/global-constant-stdclass-query-review.json)
records two exact originals, reached state fronts, budget resumption and undriven
certificate refusals. The unchanged Unsupported baseline remains zero credit;
generic objects and wider owning/coercing query forms remain partial.

Certified stdClass aliases may now be leaves in literal global constant array
trees. Shape admission permits their nonowning class facts; existing captured
lookup prefixes and recursive live-value checks still authenticate each donated
leaf. Whole-tree aliases retain those receipts. The query leaf rule delegates
to the same completed-birth/live-allocation check as a direct stdClass query.
Lookup shares the root and child arrays and adds only a root owner. Real nested
COW creates another physical array-to-object edge; properties stay shared, while
replacing a caller bucket leaves the installed DIRECT tree intact. Eval donor
sources retain their own unit origins. Default caching and callable folding keep
their separate consumer boundaries.
[stdClass array-alias review](../../coverage/semantics/global-constant-stdclass-array-review.json).

Zero-argument stdClass NEW also executes at nested array sites and selected full
or shorthand ternary leaves. The initializer path stops at closure bodies;
full context validity retains earlier facts and branch consistency. Immediate-arm
transfer follows the newborn's SITE to its completed receipt, while value guards
separately require the live allocation. Eval duplicate candidates create distinct
leaves, then retire while nonowning birth history remains. Four exact sources and
1,107 SL premises retain their [nested-birth cuts](../../coverage/semantics/global-constant-stdclass-new-review.json).
Conditional aliases/whole-array transfer and defaults remain partial.

Newborn stdClass coalescing leaves retain a nonnull left value or select the right
after a captured NULL, including nested chains and eval units. Two module283 flow
heads follow immediate source operands to the same completed receipt; separate
value checks still require a live allocation. Existing literal DIM projection
and quiet capture compose with ternary selection, then retire their temporary
array while preserving the chosen object. The
[coalescing review](../../coverage/semantics/global-constant-stdclass-coalesce-review.json)
records source, handoff and ownership checks. Alias/whole-array coalescing remains partial.

Global stdClass constant-AST NEW evaluates ordinary positional and uniquely named
arguments before dropping their values, even for unknown names. Earlier values
retire on an argument Error; the target keeps an incomplete birth receipt and
the constant stays absent, while fresh eval can retry with a distinct birth.
Donated object identity survives ignored root/array owners and real user-value destructors run
before continuation. [The argument review](../../coverage/semantics/global-constant-stdclass-arguments-review.json)
retains the initial duplicate-name counterexample. Its bounded follow-up now
captures the exact rejected current value in a request-owned record, including
array containers and their physical object edges. Earlier arguments and the
unfinished target retire through ordinary eager cleanup before catch search;
the rejected value remains live through shutdown callbacks. Current source/index,
birth/value and saved lookup-prefix checks survive alias release and fresh eval
publication without retaining earlier values or their full fact context.
[Duplicate-argument review](../../coverage/semantics/global-constant-stdclass-duplicate-arguments-review.json).
Other owning current classes, references, unpacking, default caching, generic NEW
duplicates and broader lifecycle consumers remain partial.
