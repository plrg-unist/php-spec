# Source class constants

The 183/184 increment extends the existing user-constant compiler and
expression machine for PHP8.5.10 CLI. The implemented scalar/array subset remains
partial; legal Closure/FCC initializers are explicitly Unsupported.

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

Inheritance checks preserve finality, different-owner ambiguity, visibility and
type covariance in that order. Same-owner interface diamonds remain unambiguous;
private parent constants do not constrain a child's replacement. Real linking
checks constants before methods, while the early availability probe keeps its
separate method/property/constant order and defers only unresolved types.

Append-only link, cache-fill and table-completion origins preserve temporal AST
status. Individual fetches never mark a class fully updated. NEW enters the
parent-first updater only when the requested class still needs it; successful
earlier fills survive a later failure, and retry retains the unfinished work.
Source-derived inverse controls reject incorrect task order, missing completion
markers, unrelated update sites and a class used before its publication.

The earlier bounded evidence comprises25 original source/native comparisons
across successive revisions and finite16+13. The later linking slice accepts
twelve further tuples (6 normal,5 static rejections,1 PHP error) and five finite
programs with27+13+19+18+16 overlapping predicates. These are distinct cutoffs,
not a single-revision37 rerun or whole-family acceptance.
The [ledger](../../coverage/semantics/class-constants-current-review.json) retains
original failures, including the refuted native update hypothesis. Maintained
source and finite commands are in `Makefile`; raw files stay outside Git.

Included/evaluated units import only earlier published scalar/constant-array
values that were folded or successfully cached before that unit entered. Uncached
initializers stay lazy even when their referenced global is now defined. Imported
arrays are copied into the new pool, and later fills cannot retroactively change
a compiled image. Five further native comparisons (3 normal/2 static) and one
finite fixture/31 predicates validate this boundary. The original negative
transport expectation is retained as a fixture failure.

Current-runtime checks add six native agreements for static access priority,
runtime array FCC owner/called-class scope, handler fetch, completed reference
aliasing and static unset. Their two source cutoffs remain separate. A later
borrowed strict-identity callback fills a deferred array cache and reads it after
handler retirement (`7ne7`). On the current StaticCall-reference composition,
NewC completes its table before a getter exports the property cell; alias mutation
changes the property while the cached constant stays unchanged (`32`). The
maintained catalogue contains 50 agreements across these preserved revisions.

Accessible references into an incomplete class table are explicitly Unsupported;
the separate rejected control is not a native agreement. Unretained
computed/scoped table-update selectors and named `::class` in constant expressions remain
Unsupported, as do legal static Closure/FCC initializers. Constant modifier
admission, attributes, traits/enums/internal constants and broader default/property
consumers stay open. These checks reused the recorded runtime; they add no fresh
copied rebuild, reporting-mask, paused return or full-core closure.
