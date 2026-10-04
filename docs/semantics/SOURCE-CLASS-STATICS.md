# Class static properties

Modules 187/188 implement backed static declarations in ordinary source classes,
including public, protected and private access, typed defaults and uninitialized
values, reads, assignment, quiet tests, dimensions, updates and reference binding.
Modules 200/201 add backed static asymmetric setters and final declarations.
Readonly, instance asymmetric setters, promotion, hooks and magic remain
separate obligations. The [storage ledger](../../coverage/semantics/class-static-properties.json)
and [setter ledger](../../coverage/semantics/static-setter-access-review.json)
keep historical tests distinct from current interaction checks.
Trait composition238 and raw-property warning continuations254 retain distinct
declaring identities, live handler resumption and opcode ownership; see the
[trait contract](SOURCE-TRAITS.md).

Each declaration owns one `CLASSSTATICS` row keyed by its declaring property ID.
An inherited declaration resolves to that same row; a redeclaration owns a new
row. Static declarations do not become instance slots or appear in object casts.
Successful activation publishes the class, parent/interface links and its own
rows together. Failed linking through modules 127/178 preserves the prior names,
links and rows, including an already active parent's cells. Missing compiled
default pools yield explicit Unsupported rather than invented initial values.

Module219 evaluates deferred scalar/array static defaults at the first permitted
fetch or construction. The class updater completes the parent, then class
constants, instance defaults and declaration-ordered static defaults, before
marking the table complete. Each initializer runs in its declaring lexical scope and binds with
strict property types, including int-to-float promotion. A failed later
initializer preserves earlier values and their first-fill history; a retry skips
those values. The existing `CLASSSTATICS` row owns the value and later aliases;
the `CCSTATIC` history entry stores only source/trigger/publication identities.
Compound AST errors retain the constant-expression trace, while a simple unresolved
constant keeps the triggering fetch location. Module229 permits same-default
reevaluation during a callback. Successful outer binding replaces the reentrant
value without duplicating first-fill or table-completion history. Escaped typed
aliases keep nonowning type constraints authenticated by retirement events;
reattachment and rebinding preserve Zend's ordered source removal. Throwing or
strictly rejected outer evaluation leaves the live row and alias intact. Module232
resumes cold non-CV static-reference targets through the genuine class updater.
The queued binder owns the captured RHS cell even if a callback removes its last
other owner; binding begins only after the table completes and reselects the live
target. Failed initialization leaves the RHS unattached and retains successful
default prefixes for retry. Selected dynamic classes and ordinary method
self/parent/static scopes survive callback mutation in source-bound snapshots;
selected fill/retirement/table events retain these identities without owning heap
values. Module239 extends keyword snapshots to captured/rebound source Closures.
Minting requires the authentic live call and its exact scope, binding row or
temporary `Closure::call` source/receiver context;
historical validation uses source/template and arena identities after pruning.
Bound called class follows the actual receiver, including a class unrelated to
lexical scope. Nested creation copies the immediate creator's scope, receiver and
nullable invocation site, retaining error and terminal handler ingress. These
certificates own no Closure, receiver or captured cell. Ordinary method ancestry
checks remain exact. Temporary-call children retain the effective receiver class
after their maker retires; nonstatic children own their receiver, while static
children retain only nonowning receiver evidence. Module246 owns deferred
scalar/array instance templates by requested class and full declaring property
identity. Linking copies the parent's actual template state once: a cold-linked
child evaluates inherited pending defaults separately, while a later-linked
child copies completed values. Initializers use declaring scope, strict types
and the full instance layout, including shadowed private slots, before statics
and allocation. A resumed outer initializer may replace its reentrant template
without duplicating first-fill history; objects and previously linked children
keep their copied values. Template rows own values and arrays; history owns no
heap values. Module252 admits static/no-use source Closure and function/method
callable values, including arrays and class-constant aliases. Object slots copy
the value and retain the same Closure identity; cold inherited templates create separately,
while late children copy the exact successful parent binding certificate. Reentry
replaces only the requested template, and failed/throwing binds publish no object
value certificate. Literal-key array projections retain authenticated source
flow after temporary arrays retire. Receipts carry full declaring identity and
publication prefixes without owning objects. Plain Closure/method clones retain
their genuine copied scope and earlier source authority. Shared trait FCC initializer
ASTs retain the first authenticated callable target; subsequent properties use a
fresh declaration prefix and called class, without rechecking the cached private
target under an unrelated class. Ordinary method ancestry stays exact. Other
object/default producers and wider reference/creation consumers remain required.
Module263 lets a cached property method callable create a source Closure with
the original method's lexical scope and its fresh called class. Children copy
the authentic full method, receipt and invocation evidence; wrapped and plain
clone makers may retire without becoming historical roots. Static and
receiver-free nonstatic children retain private `new self` default scope, and
real child clones copy the same authority. Ordinary creation/ancestry checks
stay exact; wider transformed callable creation contexts remain required.
Module265 applies the shared AST target cache to imported class constants.
Named/method receipts keep current full declaration prefixes; METHOD captures
select fresh called classes. The first exact receipt authenticates the cached private method or namespace
fallback target even after a failed initializer's object retires. REAL constant
Closures retain each declaring owner. Wrapped/plain cached METHOD makers create
children with copied importing identity and private-default scope; successful
readonly constant caches remain owning roots. Compiled keyword NEW under these
METHOD contexts and broader callable/default consumers remain required.
The [deferred-default review](../../coverage/semantics/deferred-static-defaults-review.json)
records eleven earlier source agreements separately from five source-derived guard
programs. Four217 callback comparisons preserve saved initializer contexts,
private declaring scope and compound traces; one cross-file comparison checks
the caller file for a simple constant default. Thirteen new reentry comparisons
and an inherited67-premise fixture cover replacement, failure/retry, array COW,
source order and release of escaped cells; earlier Unsupported controls remain
historical evidence. Seven cold-reference comparisons and one84-premise fixture
check delayed target ordering, visibility, ordinary method keywords, immutable
dynamic selection, sole captured-cell ownership, failure/retry and retirement.
Nine additional Closure sources and three programs/162 premises check immutable
scope/creator identity, unrelated called class, alias retirement and collection.
Six later temporary-call sources and three programs/193 premises check escaping
children, clone/rebinding, callback resume/throw, deterministic ordinary/copied
scope admission and collection. Their separate cutoffs and original validator
failure remain in the review.
Eight later instance-template sources and three programs/172 premises check
phase ordering, strict failure/retry, reentry, parent snapshots and owning roots.
Nine later object-default comparisons and six programs/335 premises check object
identity, constant/array transfers, full declaring authority, partial retry,
reentry, late copies, strict rejection, nested-class defaults and source pruning.
One actual trait-import comparison and98 premises separately check the cached
target, fresh called class/publication, namespace fallback and dead cache sources.
Two later property-method child comparisons and105+65 premises check wrapped
and plain makers, child clones, private defaults, full import/scope/site
transplants and historical evidence after actual source collection. Source and
state cutoffs stay separate; original fixture stops receive no agreement credit.
Three later trait-constant comparisons and58+54 AL/122 SL premises check frozen
targets, fresh called classes, per-import REAL scope, real partial failure,
historical maker authority and successful constant-cache ownership. The complete
constructor fixture uses production SL under the unchanged120s cap; original AL
timeouts receive no pass credit. All source and assertion bytes remain unchanged.
Two later213/215 comparisons
initialize the inherited default
inside a captured private handler and a raw private handler during a Stringable
parameter receive. Captured null survives the first handler's variable write and
the second handler's throw; the warmed typed alias remains the shared static cell.

Lookup retains a selected instance descriptor long enough to check access before
rejecting it as an undeclared static property. Denied and undeclared errors name
the requested class; uninitialized and type errors name the declaration owner.
Quiet lookup treats denial, nonstatic declarations, absence and uninitialized
storage as absent. Names remain case sensitive; class strings use the ordinary
case-insensitive class lookup and do not inherit lexical import aliases.

Explicit setter flags are checked before equivalent read/set visibility is
normalized away. Genuine private(set) is implicitly final; private/private(set)
normalizes to an ordinary private declaration. Explicit final/private rejection
precedes type/default compilation, and inherited finality precedes static/type
override errors. Linking checks run at source entry or the declaration's reached
runtime publication point, rather than merely constructing compiler descriptors.

Setter permission uses lexical declaring scope; diagnostics retain the called
scope. Simple assignment checks read access before fetching a deferred CV RHS,
then checks setter permission before Stringable conversion. Compound/update and
new reference consumers deny before fetching their deferred CV RHS. Reference
and dimension fetch flags retain their initialization/type effects and any prior
exception. A legally escaped alias remains writable under its ordered type sources.

The class selector is evaluated before a computed property name. An object
selector becomes its selected class name; it does not retain the object. Losing
the object's last owner removes its instance-property type sources before the
name callback writes through an alias. A paired `STATIC_PROP_CAPTURE` records
the class name and source occurrence while `STATIC_PROP_NAME` consumes the name.
Both markers carry metadata and add no heap root.
Current and saved callback queues require matching adjacent pairs and exactly
one capture per occurrence. Changing a consuming marker, deleting either half,
duplicating a pair or changing its source/line fails the consistency checks.
Shared exception, return and goto unwinding discards both halves together. These
checks authenticate the declared source and independently retained operand; they
are not a proof of execution history for an adversary replacing an entire state.

Non-CV reference assignment and writable property chains preserve pending bases.
Literal class lookup and property-name CV reads occur at the delayed fetch after
the RHS; dynamic class selection and name-call effects remain early. Pending
operands are rooted and source/line authenticated, including saved callbacks.
Read and quiet operations retain their separate access modes. Writable interior
access permits a raw direct object slot, but denies a reference-wrapped static
slot even when its referent is an object. An uninitialized W receiver checks the
setter, RW raises its read error first, and UNSET skips an undefined receiver.
Nested chains, by-reference sends/returns/foreach and destructuring retain that
demand. Property foreach promotes a shared typed cell; normal and abrupt unset
helpers preserve the already-consumed task's original continuation tail.

An aliased typed row carries a non-owning `CLASS_PROP_SOURCE` in the shared
reference constraint list. Validation checks both the source's live row/cell and
the row's required source. Static values and cells remain heap roots; copied
arrays preserve their embedded reference identities under the existing COW rules.
Binding checks before replacing the prior alias source, so a rejected binding
preserves the old row and cell. Instance and class sources share the same checked
cell writer without conflating their declaring identities.

Simple assignment through a typed property declaration converts against that declaration
before checking the live alias's other type sources. The assignment expression
returns the converted value. Assignment through a variable alias instead checks
the original value against each source, so its conversions and diagnostics can
differ. Compound updates of an aliased property also use those generic source
checks. A failed check preserves the shared cell, row and ordered sources.

The bounded [typed static Stringable consumer197](TYPED-STATIC-STRING.md)
implements weak simple object assignment. It rereads the live static row after
`__toString`, checks the current alias's ordered constraints and preserves callback
side effects, caller scope and cleanup. The current nested Restore source,
earlier ARG/callable source and focused INI source2/755 gates have independent
original-raw acceptance with separate tested identities. Instance/compound
Stringable consumers and broader receiver/reference acquisition remain open.
Static-method reference assignment with untyped return signatures now admits
the selected typed static cells through the existing97/99 protocol. Inherited
getters preserve lexical permission and called-scope diagnostics; legally
escaped aliases retain the shared static row and its type source. Denied binding
releases both the returned task owner and method-result base owner. Typed REF flags initialize nullable
initial slots and raise the nonnullable reference-access error before return;
a denied setter preserves that error as its previous exception. Initialized
typed slots also acquire their reference wrapper when the caller discards the
result. Ordinary by-value getters leave the raw slot unchanged. After a discarded
reference return, static storage alone owns the cell, its edge retains the object,
and the declaration type source remains attached. A current-constants control
uses a literal property default and completes a deferred child constant table
through ordinary access before the getter. It checks the sole static owner after
discard, then static storage plus the live global alias after binding. Deferred
object producers and wider consumers remain open. The
[reference review](../../coverage/semantics/static-method-reference-review.json)
keeps the original instance-spelled control and its preserved StaticCall failure
distinct from fresh static-getter acceptance. Legal untyped object/scalar/null
getters leave ignored values direct and share the real cell when used. Public,
protected and private lexical reads retain inherited scopes. Rebinding a typed
target removes its source from the old untyped cell without dropping other owners;
the old alias can then hold an array. Direct by-reference StaticCall sends retain
the static cell through parameter entry and retirement. These ownership checks
do not establish destructor/GC callback behavior. Broader temporary non-reference
returns, callable resolution and typed return consumers remain open.
A fresh CONFIG PIPE/getter interaction retains raw
INI bytes and restores the inherited static frame before escaping its typed cell.

CV constrained-reference object assignment has separate timing: conversion can
overwrite the captured cell after a callback adds a type source, leaving an
exceptional backing value. Its authenticated186 producer remains unimplemented;
ordinary source execution cannot mint the synthetic reference-conversion witness.
Ordinary singleton references correctly unwrap during clone. A mismatched value
left by exceptional reference conversion needs separate copied-value provenance when
that unwrap produces a direct property slot.

Pinned source routes: `zend_compile_static_prop` in `zend_compile.c`,
`ZEND_FETCH_CLASS` in `zend_vm_def.h`,
`zend_std_get_static_property_with_info` and `zend_class_init_statics` in
`zend_object_handlers.c`, `zend_assign_to_typed_prop` and reference constraint
helpers in `zend_execute.c`, and `do_inherit_property` in `zend_inheritance.c`.
