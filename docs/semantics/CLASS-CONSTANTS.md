# Source class constants

The private183/184 increment extends the existing user-constant compiler and
expression machine for PHP8.5.10 CLI. It is partial; inheritance validation,
cross-unit folding and legal Closure/FCC initializers are the next required work.

Class descriptors retain each constant's declaring owner, visibility, type,
initializer origin and folding status; folded values remain in initializer unit pools. Earlier available scalar constants can fold;
forward/deferred expressions remain lazy. Typed constants use strict acceptance,
including integer-to-float promotion. Existing `::class` strings retain their
separate lexical/called-class behavior.

Runtime fetch checks visibility before initialization, evaluates deferred values
in the declaring owner's scope, and publishes a cache value only after successful
evaluation and type checking. Failed initialization can be retried. Arrays remain
owned cache roots and ordinary reads use copy-on-write. Parent private constants
are excluded from inherited lookup. AST constant expressions and ordinary VM
fetch preserve their different class/member evaluation and diagnostic priorities.

Initializer continuations preserve nested global/default contexts, selected class
and member operands, source origins and recursion protection. Simple unresolved
names report the fetch file/line; compound evaluation uses its expression location
and an extra constant-expression frame only when the executor location differs.
Post-evaluation type errors restore the fetch context. Finite controls reject
swapped, duplicated or skipped update tasks and coherently forged selected slots.

The bounded evidence comprises25 original source/native comparisons across
successive private source revisions (7 normal,17 PHP errors,1 static rejection), plus
two finite programs with16+13 predicates. It is not a single-revision25 rerun or
whole-family acceptance. The [ledger](../../coverage/semantics/class-constants-current-review.json)
retains original failures and exact run identities. Maintained source and finite
commands are in `Makefile`; raw files stay outside Git.

The next linking slice must distinguish successful table updates from individual
fetch caches: a child's linking-time AST status controls whether NEW enters the
parent-first updater. The new native inheritance controls expose this boundary;
the original refuted hypothesis remains a failed report. Additional open scope
includes constant modifier grammar/admission, attributes, traits/enums/internal
constants and the existing broader default/property consumers. No reporting-mask,
paused return or full-core obligation is closed by this increment.
