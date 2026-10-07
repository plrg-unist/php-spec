# Backed readonly lifecycle

Module294 implements the ordinary backed-property slice at PHP 8.5.10. Public
readonly declarations receive implicit protected(set); explicit public(set)
permits global first initialization. Outside a genuine clone allowance,
initialized writes fail before setter or value-type checks. Failed first type
reception leaves the slot uninitialized.
Inheritance preserves readonly identity and distinct parent-private slots;
implicit readonly-class members and the affected trait imports obey the same
rules. The pinned routes are `zend_declare_typed_property`, property compilation,
inheritance/trait binding and `zend_std_write_property`.

Direct updates read and calculate before their write error. Nested writes retain
already evaluated keys/RHS before the indirect error. Outside clone allowances,
initialized unset fails;
whole uninitialized unset still checks setter scope, while nested unset of an
uninitialized container leaves it unset. Raw object interiors remain
mutable. Whole source references to raw objects allocate detached cells, while
target reference assignment raises `Cannot assign by reference to overloaded
object`. Backed readonly slots never become aliases or reference type sources;
object foreach rejects references to initialized readonly slots and skips
uninitialized slots.

Weak first string assignment uses the genuine `__toString` continuation, owning
its captured target and RHS and restoring the saved writer scope. Initialization
inside the callback does not revoke the earlier admission: the converted outer
write still commits. Immutable `$this`/known receiver and literal name links,
source lines, saved setter scope and each callback's own consumer are checked,
including recursion at the same source site. This is bounded source/address
authentication, without arbitrary mutable RHS/destination history.

[Maintained source controls](../../tests/semantics/readonly_lifecycle_sources.py)
cover 39 ordinary normals, 18 declaration errors and one separate Fiber reentry
composition. [Reached controls](../../tests/semantics/readonly_lifecycle_protocol.py)
evaluate 109 reentry, 53 detached-reference, 50 recursive and 31 affected instance
reference conditions. [The ledger](../../coverage/semantics/readonly-lifecycle-review.json)
keeps original failures, separate cuts and SL275/application0. MODULE288's
historical350 result remains preserved; its raw-object target-reference expectation
is superseded by the new native distinction and focused31 conditions.

[Genuine clone callbacks](SOURCE-CLONE.md) now open object-owned one-shot readonly
allowances through normal, throw, exit and Fiber lifetimes. Their separate300
cut passes 20 normals, five declaration errors, one explicit exit and 264 reached
conditions. Ordinary shallow clones without a callback keep initialized slots
locked. [Nonempty clone-with updates](READONLY-CLONE-UPDATES.md) now use their
independent second window and retain committed prefix values through failures.
Last-owner CV release, retained temporary receivers and conversion-throw priority
have thirteen native-only controls, including borrowed nested receivers,
real temporary RHS owners and an unreachable owning cycle.
Deprecated-method prebody handler dispatch is explicitly Unsupported. These,
promotions, hooks and broader typed conversions
remain open; this slice does not complete readonly semantics.
