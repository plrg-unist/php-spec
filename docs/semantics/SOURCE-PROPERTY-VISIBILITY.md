# Instance property visibility

Modules153/154 extend backed instance properties with protected and private access.
The scope includes reads, writes, quiet tests, unset, computed names, aliases,
compound and dimension writes, foreach, casts, comparison and clone updates.
[Class static access](SOURCE-CLASS-STATICS.md) has a separate bounded contract.
Asymmetric-set, readonly, promoted and hooked properties and magic access remain
separate dependencies.

A descriptor retains its raw `NAME` and declaring source origin, and adds
`VISIBILITY` and canonical `KEY`. Public keys are raw names; protected keys are
NUL-star-NUL followed by the name. Private keys contain NUL, the declaring class
name in its original namespace/case, NUL and the raw name. Object slots, captured property locations and
typed reference sources use this full-byte key. Diagnostics and foreach keys use
the raw name. A raw computed leading-NUL name cannot address a mangled slot;
embedded NUL remains significant for lookup, while native C-string diagnostics
truncate its display. No duplicate mutable property store is introduced.

Syntax access resolves the raw name in the current lexical class. Protected
compatibility follows the original nonprivate prototype through linked ancestry,
including overridden properties, stopping at a private declaration. Static closures retain lexical access without
a receiver; named nested functions do not inherit it. Public widening replaces
the protected physical key in the same inherited slot position. Narrowing fails
before invariant type checks, for both early and deferred links. Private parents
impose neither invariant types nor access restrictions on a same-name child
declaration; their physical slots remain independent.

An eligible lexical class selects its own private declaration before a child
public, protected, private or dynamic shadow. Otherwise, an inaccessible private
property inherited from another class falls through to the raw dynamic slot; an
inaccessible property declared by the actual runtime class raises Error. For a name with a
declaration, dynamic slot validation permits only that inherited-private fallback. Cast order retains
each private declaring identity alongside nonprivate overrides and dynamic slots.

Quiet denial behaves as an absent value; ordinary access raises Error. Coalescing
assignment reuses the evaluated receiver and name, evaluates its RHS only when
needed, then checks write access. Foreach filters each slot by resolution and
exact selected key and yields the raw name. Array casts and comparison retain
initialized mangled slots independently of caller scope. Clone copies those same
slots and relocates typed sources; clone property updates use lexical resolution.

Source-backed prerequisite corrections in the protected increment are: by-reference
foreach over direct `$this` uses the existing receiver, property `??=` records
memoized write descriptors, and typed reference binding distinguishes constrained
from unconstrained incoming cells. An unconstrained cell may convert before the
old target source detaches. A constrained cell cannot change type; conversion
conflict diagnostics retain conversion effects but preserve the old cell and
slot. Self-rebinding moves the target's type source to the end, matching native
remove/add order. Typed by-reference parameter and return checks stay separate. The private increment
also makes the existing typed-reference location rules disjoint: an aliased slot
uses its cell sources, while only a nonalias slot uses its own typed descriptor.
This preserves constraints through untyped aliases and repeated reference getters.

`property_visibility.py`, `property_visibility_compiler.py` and the two
`property_visibility*_protocol.py` suites under `tests/semantics` cover original
source comparisons, descriptor/key/scope forgeries, captured owners, failed
binding atomicity and budget resumption. The review ledger records distinct
profiles, selections and compatibility bridges; historical public evidence is
not relabeled as complete visibility coverage.

Primary pinned routes: `zend_object_handlers.c` (`zend_get_property_offset`,
`zend_check_property_access`), `zend_inheritance.c` (`do_inherit_property`),
`zend_compile.c` (`zend_compile_assign_coalesce`), `zend_vm_def.h`
(`ZEND_FE_RESET_RW`, `ZEND_FE_FETCH_RW`), and `zend_execute.c`
(`zend_verify_prop_assignable_by_ref_ex`, `zend_assign_to_typed_property_reference`).

The `property_private*` suites and independent `private_property_scope_protocol.py`
add private declaring-key, shadow/fallback, clone alias and saved-scope checks.
Their separate review preserves the historical protected evidence.

Future Throwable field support must migrate payload values into this
same slot store and authenticate a finite internal property catalogue. Source
origins remain source-only here; no unused internal identity or fake AST origin
is introduced.
