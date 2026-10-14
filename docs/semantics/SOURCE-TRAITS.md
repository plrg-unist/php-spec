# Source trait composition

Modules 228, 238, 254, 259, 266, 274, 290, 297, 299, 307, 347 and 382 compile, link and access source
traits under pinned PHP 8.5.10.
A using class overrides trait methods; trait methods override inherited methods.
Nested uses, duplicate imports, `insteadof`, aliases, visibility changes and final
adaptations preserve Zend's method selection and diagnostics. Abstract trait
requirements are checked against the selected implementation after parent
inheritance and before interface contracts.

Selected direct-trait public by-value statement-body-backed `int` getters import
into a parentless named class. The imported property owns its physical slot, while
a derived callable keeps Trait code/`__METHOD__` and uses Consumer lexical/private
scope; called scope follows Consumer or Grand. A real slot 100→300 produces
113→313. Matching own type/default100 does not permit a property collision.
Two originals and four separate checks/267 premises are recorded in the
[trait-getter review](../../coverage/semantics/trait-imported-backed-getter-review.json).
Other nested hook imports and wider parent/hook shapes remain required.

Direct public virtual get-only `int` trait getters with no initializer also
import into a parentless Consumer. Raw Trait and imported own metadata stay
virtual: the helper default is INITIAL, but Consumer/Grand own no physical
slot. Consumer lexical/private scope returns13 with false backing bypass;
a Grand write raises its read-only Error and keeps storage empty. One source
and three separate checks/242 premises are in the
[virtual-trait review](../../coverage/semantics/trait-imported-virtual-getter-review.json).

Selected body-backed expression trait getters also import. Their expression
tasks use the physical source origin; the actual callable, context and return
retain logical Consumer identity. Consumer private13 receives the Trait hook
magic name; Grand’s backing100→300 yields113→313. One source and three
separate checks/263 premises are in the
[expression-trait review](../../coverage/semantics/trait-imported-expression-getter-review.json).

Selected no-initializer virtual expression getters also import. Their default
helper is INITIAL while actual Consumer/Grand slots are empty. Consumer private13
receives Trait magic bytes through the logical imported getter; Grand’s write
raises its read-only Error and leaves no slot. Physical tasks and logical
implicit13 use the existing expression path. One original, three new states/284
premises and the directly superseded M65 controls75 are recorded separately in
the [virtual-expression review](../../coverage/semantics/trait-imported-virtual-expression-getter-review.json).

Selected backed expression trait getters also import into a named Consumer
with a real source Base parent and no overlapping property name. Admission
checks Base before a Consumer link exists; the published getter requires the
matching SOURCE_PARENT. Inherited marker700 is retained, while Consumer/private13
and Trait magic remain separate from Base parentRead’s lexical scope. A real
Grand100→300 write yields313 without changing marker700. One original and three
checks/294 premises are in the [parented-trait review](../../coverage/semantics/parented-trait-expression-getter-review.json).

Selected public ordinary same-name parent properties now pass import admission
without bypassing inheritance TYPE checks. Base int10 and imported int100 retain
distinct descriptors but select one imported physical value slot plus marker700;
Grand’s write300 yields313. Incompatible Base string fails at Consumer16 during
real deferred linking, with rollback. Two originals and four checks/349 premises
are in the [overlap review](../../coverage/semantics/inherited-overlap-trait-getter-review.json); only the directly superseded earlier controls74 are renewed.

Selected private ordinary same-name parents retain their declaring-owner mangled
key beside the imported public property. Source-normalized visibility/key proof
admits the import; lexical Base private lookup precedes public hook selection.
Base parentRead returns7 without entering a hook, while Grand’s public100→300
write yields313 and preserves private7, marker700 and Consumer100. One original
and three checks/277 premises are in the [private-overlap review](../../coverage/semantics/private-overlap-trait-getter-review.json).

Selected one-level nested backed expression hooks now import through a real
Outer trait row. Final Consumer origins stay flattened to raw Inner; Outer has
no executable hook clone. Inner `__METHOD__`/`__TRAIT__` spelling and Consumer
private scope survive Grand’s write300/get313. Identical plain100 in Outer still
raises the existing hooked-composition CompileError at trait7. Two retained
originals and two checks are in the [nested-trait review](../../coverage/semantics/nested-trait-getter-review.json).

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
After successful trait data binding and a later abstract-verification failure,
the cached method has the failed class's fixed scope. Source-authenticated data
replay distinguishes completed binding, a modeled data fatal and an unknown
phase; an unknown phase cannot fall back to a fresh method. An imported first
birth remains unfixed and retired. An authenticated later callable may report its
failed lexical class's name without granting class publication or member lookup.
One shutdown original and59 supplied phase/scope/default/static conditions pass,
with6 setup clauses separate. Callbacks between fixup and failure remain open.
Retained `new self` proves an unresolved implicit abstract trait requirement
from completed data binding and the exact copied requirements, rejecting construction
before arguments. Imported and own/private targets share the explicit completion
proof; equal scope descriptors alone cannot establish it. Explicit abstractness
is authenticated directly from class source flags and rejects construction even after
an earlier data failure. The failed class stays unpublished, and an unknown proof
stays Unsupported. Three shutdown PHP-error originals and122 supplied NEW/phase/flag
conditions plus18 setup clauses pass at separate cuts.
An old FCC can instead retain a published trait scope while its canonical
function belongs to the failed class. Exact scope and physical-source proof
authenticates its durable SELF selection; the trait rejection precedes arguments
and leaves the pending NEW certificate valid. One shutdown PHP-error original
and37 supplied conditions plus6 setup clauses pass, including all four validators.
Retained `new static` constructs the published called class using its exact
saved scope/source proof, including an old published-trait scope whose raw method
has a different origin from the canonical class copy. Deferred static fills retain
that NEW selection in durable history. Two shutdown PHP-error originals and80
supplied argument-entry/history conditions plus12 setup clauses pass at separate
cuts, including all four global validators and forged certificate rejection.
A source-owned retained `self::n(argument())` selects the exact copied abstract method
after completed data and requirement binding, checks access, and throws before
argument evaluation. Unknown phases stay Unsupported. One shutdown PHP-error
original and41 supplied conditions plus6 setup clauses pass, including unchanged
allocations and all four global validators.
The failed class gains no publication or fresh named-lookup authority.
Parent/interface contracts, including implicit Stringable, remain required.
Dependency fills in held/open compilation, broader differing-owner later births and
wider failed-owner member/construction behavior retain explicit boundaries.
The exact full constructor/default, error-handler and positional/named variadic
parameter-view originals agree with PHP at the original100000-step/45/55 limits.
They retain old trait scope, later fixed class scope and cloned snapshots through
conversion and the old-scope constructor Error. A reviewed ASCII lookup and disjoint
property/header guards preserve bytes, comparison results and target authority.
Broader mixed parameter-view contexts remain unvalidated.
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
attributes, autoload, other hook shapes, lifecycle services and paused return work remain
separate obligations.
