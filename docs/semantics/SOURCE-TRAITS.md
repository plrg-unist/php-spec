# Source trait composition

Modules 228, 238, 254, 259, 266, 274, 290, 297, 299, 307 and 347 compile, link and access source
traits under pinned PHP 8.5.10.
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
Deferred trait parameter constructors retain their selected class and scope while
class-table work enters other initializers. The continuation preserves the actual
arguments, source line and constructor/allocation branch. Existing selected table
histories authenticate the exact canonical method/default source after restoration.
Ordinary captures use a published class certificate that survives capture retirement;
matching invalid selection markers cannot fall back to generic source authority.
The ordinary constructor/retirement source and38 supplied reached checks (6 setup)
pass at1fa6af571 without unpublished-FCC307 dependencies.
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

Module290 also creates a static, capture-free REAL Closure for a constant owned
by the unpublished composing class. Its borrowed collision marker checks the
exact source, table, lookup chain and declaration/user prefixes. A nonowning birth
receipt keeps that original prefix and lexical/called scope after publication;
the completed cache owns the Closure. Module297 retires failed import owners while
retaining source-authenticated dead receipts and already-published dependency
caches. Dead receipts grant no live Closure or class lookup authority.
Module299 reserves the earliest case-folded class name after a fatal trait link,
without publishing the class. Later declarations reject before parent autoload
or trait/default evaluation; returning link Errors permit retry. An early include
collision retains its physical declaration lines and genuine include frame.
The actual313 join at `cc9411c1e` over `064d382d` passes strict compilation,
one fresh REAL/default-constructor source and46 supplied reached conditions (6 setup).
The genuine selected constructor allocates its args7 object; releasing the ordinary
method capture leaves the separate REAL cache, birth receipt and history valid.
Earlier accepted290/297/299 source/state cuts remain separate in the collision ledger.

Already-published Closure/FCC dependencies use the real class-constant initializer
and binder. Full declaring identities, callable receipts and source transfer proofs
authenticate their values; cache roots retain objects together with their scope and
receipt rows. Captured declaration/user prefixes rederive dynamic array keys, and
literal dimensions select the last matching source entry. Failed composition keeps
public-owner object caches while releasing temporary arrays and Error allocations.
Errors inside these callable dependencies use the real failing runtime step and
Throwable continuation. Typed rejection restores the binder's demand context;
an incoming constant collision authenticates its composing file and physical fetch
line across the borrowed initializer, retaining the real constant-expression frame.
The full source/cause and rederived typed step supply this override. Property,
expression and array-key failures retain their ordinary authenticated continuation.
Actual Throwable fields and trace supply the later default report. Cleanup releases
failed initializer/Throwable owners while retaining completed nested caches and
the outside handler registry's captured graph; scratch handler dispatch stays
isolated. Further initializer contexts, unpublished-owner FCC births and wider object
transfers remain required.

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
After a failed class link, caches filled for already published declaring owners
survive rollback; fills for the unpublished importing class are retired. This
includes an initializer Error reported before the composition fatal. Failed raw
trait composition uses its real trait declaration and kind; direct trait-constant
access remains denied before dependency evaluation.
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
conditions; six generated setup checks are recorded separately. Reported Errors
after fills add three PHP-error comparisons and188 supplied cache-cause/cleanup
conditions, with six generated setup checks separate.
Real callable-initializer failures add four PHP-error comparisons and four reached
groups/678 supplied source/context/registry/cleanup conditions;12 generated setup
checks are separate. Genuine expression children supply expression-error traces,
typed binding restores its demand context, and failed temporary owners retire
without dropping completed nested caches or the original handler graph.
Cross-file typed constant demand adds two PHP-error comparisons and139 supplied
reached conditions; five multi-file service/setup checks are separate. Source and
declaration-image mutations cannot borrow a foreign diagnostic context.
Other native preparations remain uncredited until implemented.

Module307 preserves unpublished FCC targets and their birth-time parameter scope
through method fixup, with canonical code, defaults, returns and statics unchanged.
Failed first-target imports retain source-authenticated dead receipts through exact
method-copy reconstruction and history replay. Access uses the unfixed exporting
trait's scope, so a private/protected copy cannot authenticate a forbidden FCC birth.
Focused source2 and87 supplied
conditions cover failed retirement and equal lexical/called scope; the current
default/TYPE checkpoint stops at the genuine old-U constructor Error.
Live concrete FCC aliases and visibility changes recover the exact adapted copy
after ordinary lookup misses, including aliases of an excluded method and aliases
retained beside a using class's own override. Birth scope, defaults and canonical
class/alias static cells are preserved.
Later failed imports authenticate the already published first owner's cached
method at the new birth prefix. A different own method is never substituted;
the later owner retires while the first cache remains live. One PHP-error source
and68 supplied retirement conditions pass, with6 setup clauses separate.
Module347 retains a failed first target's exact canonical metadata without
restoring class publication or imported methods. Later collision-backed and
ordinary published receipts recover that cached target and its original lexical
scope, including private own methods and aliases absent from the later class.
Three shutdown originals and115 supplied checkpoint conditions cover literal
defaults and clone-shared statics;12 setup clauses are separate. The first Closure
stays retired and cannot regain a live value or scope.
If the later import also fails, its dead receipt still selects the first target
after the authenticated first-owner failure, at the later birth prefix. Both
owners retire; the first latent cache
metadata remains distinct from live value/scope authority. One shutdown original
and59 supplied rollback conditions pass, with6 setup clauses separate.
Dependency fills in held/open compilation, broader differing-owner later births and
wider failed-owner member/construction behavior retain explicit boundaries.
Wider parameter-view full-source constructor, handler and variadic cases remain
unvalidated obligations.
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
