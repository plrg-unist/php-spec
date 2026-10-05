# Source trait composition

Modules 228, 238, 254, 259, 266 and 274 compile, link and access source traits under
pinned PHP 8.5.10.
A using class overrides trait methods; trait methods override inherited methods.
Nested uses, duplicate imports, `insteadof`, aliases, visibility changes and final
adaptations preserve Zend's method selection and diagnostics. Abstract trait
requirements are checked against the selected implementation after parent
inheritance and before interface contracts.

Imports retain two identities. The declaring owner and lexical `self` scope are
the using class; the body, filename, line and `__TRAIT__`, `__METHOD__` and
`__FUNCTION__` remain those of the original trait method. Aliases have their own
class/name identity and declared spelling in traces. `__CLASS__` and contextual
class-name defaults use the selected import or authenticated rebound Closure
scope. `new self` and `new parent` in trait method parameter defaults use the
selected method's lexical scope, including the source-owned constructor protocol.
Its callback retains the saved import, default AST and locals. Cold static-property
reference selection likewise retains the using and called classes after deferred
initialization. A pending reference fetch requires its selected source/class/member
marker; the actual fetch still requires its prepared base. Imported Closure cold
selectors retain copied scope evidence without owning the retired creator.
An inherited method keeps its original import identity.
Goto and include/eval entry retain the physical checked body
while authenticating the selected importing scope.

Method static cells are separate for every using class and alias. Inherited
methods and their captured/clone callables share the selected import's cells;
explicitly reusing the trait in a child creates new cells. Real Closures keep
per-instance storage and their creating import's lexical/called class after
other classes import the same body. Retired private method captures retain a
source-compatible maker and caller-scope certificate without acquiring a new
receiver owner. These are structural wellformedness checks, not a reconstruction
of arbitrary retired execution history.

Classes and composed traits containing a real trait use always defer early
publication. Linking resolves parent names, trait names and interface names in
that order, then validates adaptations and binds concrete methods before parent
inheritance. Abstract requirements follow parent checks. This preserves prior
output, missing-name priority, final/abstract conflicts and failed declaration
rollback. Successful declaration history is replayed from raw source images;
imported descriptors and alias identities must equal that replay's result.

Private-final alias warnings use `E_COMPILE_WARNING`128 and do not enter ordinary
error handlers. Concrete adaptation warnings are recorded before data comparison;
abstract adaptation warnings follow parent linking. They join the ordered
post-publication batch, or default-only diagnostic flush before a later fatal. Direct
static access to an accessible concrete trait method emits the native deprecation
before arguments or first-class capture. A throwing handler aborts the pending
call; capture emits the warning once and subsequent invocation uses the selected
callable.

Logical method entry and finalizer continuations retain the complete selected
class/alias identity. Protected regions use the physical source method only
after authenticating CURRENT; saved frames restore their own scope and locals.

Trait data composition checks constants before properties and before parent
inheritance, after concrete method selection. It compares visibility, native
flag masks, invariant types and evaluated strict values in the composing class.
Property finality and setter visibility do not participate in the trait
compatibility mask; inherited final/access checks still do. Type comparison
retains the exporting trait's scope, including Zend's singleton raw-name shortcut
and case-sensitive `self`/`parent` spelling. Runtime types then bind to the using
class; runtime member errors retain source keyword spelling, while inheritance
errors display resolved parent types. Readonly-class rejection precedes member
publication; readonly storage retains its separate boundary.

Each imported property or constant keeps a full using-class identity and its
physical declaration/default occurrence. Nested traits defer contextual defaults
until a class imports them. Genuine constant/static/instance initializer bindings
supply the using scope independently of the live caller CURRENT; physical source
projection never replaces the binder or typed-reference identity. Inherited static properties share the
original slot, while explicit child reuse creates a fresh slot from the original
default. A shared reference retains every importing class's type constraint and
array defaults retain ordinary copy-on-write behavior. Deferred scalar and array
instance defaults use the owning requested-class templates from module246.
Linking copies the actual parent template state;
explicit trait reuse creates a fresh declaration and evaluates its own default.
Whole-table initialization checks instance defaults before static reads or object
allocation, while an individual constant fetch leaves property templates alone.

Pure collision evaluation uses the checked expression folder in a scratch arena;
temporary arrays do not become live descriptor values. Source class aliases use
the actual compiled fetch name. Runtime inherited property/constant faults retain
`E_COMPILE_ERROR` and their completed-declaration phase, while early compiler
cutoffs remain static rejections. Deferred typed operands compare before table
conversion; compiled literal defaults retain their compile-time conversion.

Module259 records `E_STRICT` and arithmetic/key collision diagnostics in a
source-owned scratch fold isolated from the live handler, display and mask.
Runtime array evaluation demands each key, then its value, then insertion before
the next entry. Recorded diagnostics retain checked AST lines; a bare constant
root retains the executing declaration line. Constants evaluate the incoming
operand first; properties evaluate
the existing operand first. Temporary values do not fill the compared defaults.
Successful class publication precedes delivery through the live handler registry.
A delivery exception preserves that publication; a later link fatal flushes
earlier diagnostics through the default renderer without calling user handlers.
The sampled constant-name prefix and actual source/default roots authenticate
each recorded item independently of later handler mutations.

Module 266 binds a referenced deferred class constant in its real declaring scope,
including typed conversion, before comparing the outer temporary. Its cache
persists between operands and later reads; the compared property/constant stays
unfilled. Full import identities separate caches for different using classes.
Each cache owns its value; recursive dependencies can share one array, and
later static writes retain copy-on-write. Source-owned collision tables, lookup chains and publication prefixes
authenticate these fills without making an unlinked composing class public.
Only already-inserted constants are available before parent inheritance.

Module 274 stops supported collision expressions at the first endogenous Error,
preserving earlier diagnostics and skipping the second operand. It flushes those
diagnostics without user handlers, renders the uncaught Error through Zend's
default exception route, then reports the composition fatal without a second
trace. Real caller frames and checked constant-expression locations remain
distinct; transient Error, trace and scratch allocations are released. Named
classes use the public registry, while `self` sees only the composing table.
A held primary fatal intercepts this failure before the inner Error reports;
source-owned failed-class replay retains the exact class and dynamic unit origin.
Cyclic lookup errors follow the genuine source chain and compare full imported
constant identities, including recursion through an earlier distinct dependency.
After a hard failed class link, caches filled for already published declaring
owners survive rollback; fills for the unpublished importing class are retired.
A source-rederived failure marker authenticates the original collision and public
owner prefix without granting publication or held-primary authority.

Raw trait static-property access emits `E_DEPRECATED` after lookup, access,
table initialization and a required typed read. Quiet probes can therefore warn
on an uninitialized slot while an ordinary read fails first. Each access reaching
this phase warns; importing-class access uses its ordinary property table. A retained
source, root, declaration, name and access mode survive handler rebinding and
saved frames. Resumption reads the live selected cell, including handler writes.

Assignments preserve Zend's operand order: a simple RHS variable is read after
the warning, while a computed RHS is retained before address lookup. Direct
assignment, compound update, increment and reference binding finish their opcode
before a handler exception propagates. A reference fetch can promote a nullable
slot but abort the following assignment or call. Pending exceptions suppress
secondary typed rejection and user Stringable entry; valid scalar conversions
can still finish. A new nonnullable reference error chains
the handler exception. The address receipt owns no value. Its store task owns
one additional RHS reference; a compiled literal's pool owner remains intact.
Default initialization uses the raw declaring trait scope independently of the
live caller, with physical `__TRAIT__` preserved through nested imports.

The source truth is `Zend/zend_compile.c::zend_compile_class_decl`,
`Zend/zend_inheritance.c::zend_do_link_class` and its trait binding helpers,
`Zend/zend_object_handlers.c::zend_std_get_static_method`,
`zend_std_get_static_property_with_info`,
`Zend/zend_execute.c::zend_fetch_static_property_address_ex`, and the trait branch
of `Zend/zend_ast.c::zend_ast_evaluate_ex`.
Pending exception and fatal output follow `Zend/zend.c::zend_error_zstr_at` and
`Zend/zend_exceptions.c::zend_exception_error`.

Run author source controls with
`python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_cases.json`.
Independent source catalogues cover composition, warning masks, abstract priority,
retired caller scopes and finalizers; `trait_method_review_protocol.py` checks selected
import identity, defaults, static keys, closures, source scope and rollback.
The [method review ledger](../../coverage/semantics/trait-methods-review.json) records
actual cutoffs, commands, original failures and finite limits.
The data catalogues `trait_member_review_cases.json` and `trait_data_*cases.json`
cover compatibility, scope, sharing, source names, diagnostics and publication;
the reference/initializer/type-identity and instance-template protocols check
genuine full import states, including a distinct live caller during initialization.
The [data ledger](../../coverage/semantics/trait-data-review.json) keeps original
failures, actual-parent interactions and explicit dependencies separate.
The `trait_property_*review_cases.json` catalogues and two property protocols
cover warning resumption, saved emitters, access modes, abrupt opcode completion
and RHS ownership. The [property-access ledger](../../coverage/semantics/trait-property-access-review.json)
records 33 source agreements and 286 reached state premises at their actual cuts.
The [collision ledger](../../coverage/semantics/trait-collisions-review.json) records
14 original source tuples and97 publication/callback assertions, plus five
affected operation/array comparisons and47 queue/array-owner assertions at their
separate cuts. Ordered private-final delivery adds four affected sources and43
alias/queue assertions; the two existing128 mask controls are identified separately.
The successful dependency-cache checkpoint adds10 normal sources and201 unique
cache/lookup/owner assertions;20 repeated setup checks are excluded.
The Error checkpoint adds ten PHP-error source comparisons and156 reached
first-failure/cleanup assertions, with ten separate formatter helper checks.
The actual275 held-primary interaction adds one source and112 replay assertions.
Direct and two-hop cyclic lookups add two PHP-error comparisons and87 reached
chain/cleanup assertions at separate cuts. Hard failed-cache disposition adds
three PHP-error source comparisons and194 supplied restoration/history/owner
conditions; six generated setup checks are recorded separately.
Other native preparations remain uncredited until implemented.

Dependency fills followed by a reported endogenous Error, held/open compilation,
failed raw-trait composition and object-bearing values remain required. These
wider failed-fill paths keep an explicit Unsupported boundary.
An excluded `parent::` collision control terminated the pinned engine with
SIGSEGV; it supplies no language-level oracle result or agreement.
Historical reached
deprecation controls remain zero agreement at their old cuts; module254 has its
own source and state evidence. Missing/private/unset errors retain their earlier
priority. The original instance-template Unsupported controls remain historical
evidence, with actual246 interactions recorded separately. A parentless
trait `parent` parameter remains a valid declaration; receiving that unresolved
dependent type retains the existing Unsupported boundary. Closure keyword NEW
defaults use the separate module245 protocol; broader body keyword NEW retains
its existing boundary. Broader
attributes, autoload, hooks, lifecycle services and paused return work remain
separate obligations.
