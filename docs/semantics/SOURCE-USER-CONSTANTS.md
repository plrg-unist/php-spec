# Ordinary source user constants

Ordinary `const` declarations and reads use the checked source compiler and runtime for the pinned PHP 8.5.10 CLI profile. Scalar/array, certified Closure/FCC and bounded user-instance NEW values are supported; the constant family and full core remain partial.

## Declaration and lookup

The compiler handles each actual `NConst` initializer before validating its declaration name. Shared constant-expression preparation preserves selected/skipped branches, compile diagnostics, and deferred expressions. `CODENAME` and `CODEEXPR` at the declaration origin retain the resolved name and emitted opcode line; initializer paths remain the original source paths. The compiler contract describes the admitted constant-expression boundary.

Runtime `CONSTANT_INIT` evaluates one initializer through the ordinary expression machine, then `CONSTANT_BIND` activates its value before the next declaration starts. A missing name or other initializer error leaves earlier constants active. A duplicate name evaluates its initializer first, emits the native duplicate warning, releases its temporary value ownership, and preserves the earlier binding. Constant-AST diagnostics use the recorded declaration opcode line, including multiline initializers.

The request-local table normalizes namespace prefixes to lowercase and preserves terminal-name case. Reads use the compiler-resolved primary and namespace-fallback names in order. Constants become visible when their declaration executes; source declaration presence does not preactivate the value. Existing constant-name compilation handles imports and namespace contexts.

## Values and allocation classes

`USERCONSTANTS` entries own their ordinary runtime values. Constant reads, array copies, nested value calls, reference sends, and temporary foreach references use the existing heap and copy-on-write machinery. The table's roots are included across active and saved frames and abrupt cleanup. A failing initializer clears pending initializer work and scratch facts while retaining existing table and request roots.

Allocation provenance is a separate non-owning tree: `PVSCALAR`, `PVSTRING bool`, `PVCLOSURE` with its exact object identity, nonfoldable `PVINSTANCE` with object identity and NEW source, or `PVARRAY bool` with ordered keyed child classes. The flag records the source-backed non-refcounted case needed by subsequent default-receive semantics. It is not inferred from final bytes or length. Both string flags can accompany empty bytes; an allocated array can be empty. The shared empty-array class requires empty topology. Generic `PVOBJECT` is not admitted as certified global NEW.

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
values and bounded array snapshots, including authenticated interned and request strings. Existing CONFIG
argument evaluation and retained dynamic-callee selection supply the actual
completed arguments. Registration stores the primitive value or copied array
snapshot in `USERCONSTANTS`; later
changes to the name or value CV do not change the row. The string class follows
its actual carrier (`PVSTRING true` for interned, false for request strings).
Identity-unknown legacy string values are explicitly Unsupported.

Registration normalizes the namespace prefix without stripping a supplied leading
separator; the final component stays case sensitive. `defined` removes a leading separator
for lookup separately. Fixed global/explicit-global `define` and retained dynamic
selection authenticate the call site; namespaced fallback is outside this slice.

Public row checks require a genuine source/selection, canonical unique name,
matching primitive/carrier class and empty read/receive metadata. Available immutable
positional literal facts constrain names and values. Variable-derived payloads keep
the existing structural value policy: the row is the runtime capture, not a full
proof of past argument evaluation. Validators never reread mutable CVs.

Primitive duplicate `define` of an existing user constant emits the ordinary
level2 Warning and returns false without publishing its candidate. A named handler
may suppress default delivery or append another constant; the original binding
survives both. The retained CONFIG
resume keeps actual arguments, selection and the pre-warning table prefix. Public
checks require the duplicate key within that prefix, so later-only keys cannot
authorize it. Two exact sources and two public fronts/207 premises cover default,
false-handler and handled delivery in the
[duplicate ledger](../../coverage/semantics/dynamic-constant-duplicate-review.json).

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
caller destination and callback mutations. A key already present at that point is
explicitly Unsupported because its pending duplicate Warning needs a separate
protocol. The corresponding boolean-true abrupt registration tail remains open. The
[scalar-flag review](../../coverage/semantics/define-scalar-flag-review.json)
binds four source agreements and462 public premises; NULL/NaN flags, wider values
and coerced flags with scalar/null names remain separate.

Fresh two-argument array definitions recursively dereference source cells into
new DIRECT entries. Reinserting surviving keys rebuilds NEXT, positions and serial
metadata; ordinary copies and later source/reference writes preserve the constant.
Nonempty acyclic trees contain primitive/carrier leaves, whose actual string
classes are retained. Repeated noncyclic children may copy independently.
Public checks require a canonical DIRECT tree and available literal-array facts,
comparing ordered keys and leaf values rather than internal array IDs. Variable
payloads keep structural authority without replaying past CVs. Two exact sources
and two public fronts/219 premises cover request strings, gap appends, nested
reference freezing and a later literal registration in the
[array ledger](../../coverage/semantics/dynamic-constant-array-review.json).

Top-level empty values use the existing source-pool or retained immutable flag.
An authenticated immutable empty keeps its table and `PVARRAY true eps`; a mutable
emptied input becomes a fresh canonical table with `PVARRAY false eps`, rebuilding
its append index. Literal validation checks this class as well as contents, so a
same-content mutable clone cannot replace a fixed empty literal. Variable payloads
retain structural authority. Two exact sources and two public fronts/162 premises
check these distinctions and later copies in the
[empty ledger](../../coverage/semantics/dynamic-constant-empty-review.json).

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

Plain `constant`/`defined` calls also receive integer, boolean and float query
names. Weak callers use the existing string conversion after
argument effects; strict callers raise `TypeError` before conversion. The captured
call keeps its original value and selected callee. Available immutable argument
facts must match that exact value. Conversion changes only the API slot: a weak
missing-name Error shows the received string in its trace, while strict TypeErrors
retain the original argument and actual parameter name. Caller CVs stay unchanged.
Stringable/array reception and packed/owning forms remain separate.
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

User-array queries retain the stored root and child identities. The admitted
tree contains nonstring scalars, raw strings, authenticated string carriers,
certified `PVINSTANCE`/`PVCLOSURE` leaves and arrays with matching key/class trees
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
result. Generic `PVOBJECT`, stored ALIAS/cyclic array trees, Stringable/array name
reception and packed/owning calls remain outside this slice. The original ordinary `const` string producer refusal retains
its historical cut; the string-publication follow-up above admits that producer
domain without renewing the older lookup campaign. The [global-query ledger](../../coverage/semantics/global-constant-review.json)
binds the source and public-state cuts without closing the constant family.

The matching engine routes are `ZEND_FUNCTION(define)`/`ZVAL_COPY`,
`validate_constant_array_argument`/`copy_constant_array`, `zend_register_constant`,
and `ZEND_FUNCTION(defined)`/`zend_get_constant_ex`. `PHP_FUNCTION(constant)` uses
exception-class lookup and `ZVAL_COPY_OR_DUP`; `zend_declare_typed_class_constant`
interns direct string values before installation.
Nested empty values in `define`, cycles, objects, array duplicate/third-argument paths,
Stringable/array names, array/object values with scalar or null names, true/coerced
flags with scalar or null names, startup/special-name warnings,
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
binder/two fixture failures remain zero credit. Internal and Throwable NEW,
nested autoload, earlier initializer facts, named/unpacked autoload arguments,
wider object-producing/lifecycle forms and remaining builtin/query behavior remain
open. Class/default and callable consumers keep their separate evidence; no
complete-core claim.
