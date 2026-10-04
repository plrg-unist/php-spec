# Class static properties

Modules 187/188 implement backed static declarations in ordinary source classes,
including public, protected and private access, typed defaults and uninitialized
values, reads, assignment, quiet tests, dimensions, updates and reference binding.
Modules 200/201 add backed static asymmetric setters and final declarations.
Readonly, instance asymmetric setters, promotion, traits, hooks and magic remain
separate obligations. The [storage ledger](../../coverage/semantics/class-static-properties.json)
and [setter ledger](../../coverage/semantics/static-setter-access-review.json)
keep historical tests distinct from current interaction checks.

Each declaration owns one `CLASSSTATICS` row keyed by its declaring property ID.
An inherited declaration resolves to that same row; a redeclaration owns a new
row. Static declarations do not become instance slots or appear in object casts.
Successful activation publishes the class, parent/interface links and its own
rows together. Failed linking through modules 127/178 preserves the prior names,
links and rows, including an already active parent's cells. Missing compiled
default pools yield explicit Unsupported rather than invented initial values.

Module219 evaluates deferred scalar/array static defaults at the first permitted
fetch or construction. The class updater completes the parent, then class
constants, then declaration-ordered static defaults, before marking the table
complete. Each initializer runs in its declaring lexical scope and binds with
strict property types, including int-to-float promotion. A failed later
initializer preserves earlier values and their first-fill history; a retry skips
those values. The existing `CLASSSTATICS` row owns the value and later aliases;
the `CCSTATIC` history entry stores only source/trigger/publication identities.
Compound AST errors retain the constant-expression trace, while a simple unresolved
constant keeps the triggering fetch location. Same-default reevaluation while an
initializer is suspended in a callback returns explicit Unsupported. Resumed
updates must eventually retain escaped reference constraints even when the live
property row is replaced. Instance and object-bearing defaults and synchronous
references into an incomplete table also remain required open work.
The [deferred-default review](../../coverage/semantics/deferred-static-defaults-review.json)
records eleven earlier source agreements separately from five source-derived guard
programs. Two later213/215 callback comparisons initialize the inherited default
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
instance/object-bearing defaults and synchronous references into incomplete tables remain
Unsupported. The
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
