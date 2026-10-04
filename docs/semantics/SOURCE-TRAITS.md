# Source trait composition

Modules 228, 238 and 254 compile, link and access source traits under pinned PHP 8.5.10.
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

Private-final alias warnings use `E_COMPILE_WARNING` and do not enter ordinary
error handlers. Abstract alias warnings occur after parent linking. Direct
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
cutoffs remain static rejections.

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
ordinary typed/Stringable conversion; a new nonnullable reference error chains
the handler exception. The address receipt owns no value. Its store task owns
one additional RHS reference; a compiled literal's pool owner remains intact.
Default initialization uses the raw declaring trait scope independently of the
live caller, with physical `__TRAIT__` preserved through nested imports.

The source truth is `Zend/zend_compile.c::zend_compile_class_decl`,
`Zend/zend_inheritance.c::zend_do_link_class` and its trait binding helpers,
`Zend/zend_object_handlers.c::zend_std_get_static_method`, and the trait branch
of `Zend/zend_ast.c::zend_ast_evaluate_ex`.

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

Effectful or unresolved collision evaluation remains required. Historical reached
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
