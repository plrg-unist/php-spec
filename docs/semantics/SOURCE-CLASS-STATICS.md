# Class static properties

Modules 187/188 implement backed static declarations in ordinary source classes,
including public, protected and private access, typed defaults and uninitialized
values, reads, assignment, quiet tests, dimensions, updates and reference binding.
Readonly, asymmetric set access, promotion, traits, hooks and magic remain separate
obligations. The [ledger](../../coverage/semantics/class-static-properties.json)
keeps historical source matrices distinct from current-base bridges and reviews.

Each declaration owns one `CLASSSTATICS` row keyed by its declaring property ID.
An inherited declaration resolves to that same row; a redeclaration owns a new
row. Static declarations do not become instance slots or appear in object casts.
Successful activation publishes the class, parent/interface links and its own
rows together. Failed linking through modules 127/178 preserves the prior names,
links and rows, including an already active parent's cells. Missing compiled
default pools yield explicit Unsupported rather than invented initial values.

Lookup retains a selected instance descriptor long enough to check access before
rejecting it as an undeclared static property. Denied and undeclared errors name
the requested class; uninitialized and type errors name the declaration owner.
Quiet lookup treats denial, nonstatic declarations, absence and uninitialized
storage as absent. Names remain case sensitive; class strings use the ordinary
case-insensitive class lookup and do not inherit lexical import aliases.

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

An aliased typed row carries a non-owning `CLASS_PROP_SOURCE` in the shared
reference constraint list. Validation checks both the source's live row/cell and
the row's required source. Static values and cells remain heap roots; copied
arrays preserve their embedded reference identities under the existing COW rules.
Binding checks before replacing the prior alias source, so a rejected binding
preserves the old row and cell. Instance and class sources share the same checked
cell writer without conflating their declaring identities.

Typed object-to-string assignments remain explicit dependencies pending resumable
property and constrained-reference consumers. A successful consumer must inspect
the live static row after the callback: `__toString` may replace it with a different
alias. It must preserve callback effects and route the converted value through
the current cell's constraints. Typed reference return conversion has a distinct
Zend timing contract and does not authorize weakening these ordinary writes.
Ordinary singleton references correctly unwrap during clone. A mismatched value
left by reference-return conversion needs separate copied-value provenance when
that unwrap produces a direct property slot.

Pinned source routes: `zend_compile_static_prop` in `zend_compile.c`,
`ZEND_FETCH_CLASS` in `zend_vm_def.h`,
`zend_std_get_static_property_with_info` and `zend_class_init_statics` in
`zend_object_handlers.c`, `zend_assign_to_typed_prop` and reference constraint
helpers in `zend_execute.c`, and `do_inherit_property` in `zend_inheritance.c`.
