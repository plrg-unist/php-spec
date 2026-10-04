# Source class constants

The 183/184 increment extends the existing user-constant compiler and
expression machine for PHP8.5.10 CLI. Scalar/array constants and selected static
Closure/fixed first-class callable initializers execute; the family remains partial.

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
earlier catalogue contains 50 agreements across these preserved revisions.

Static anonymous Closure initializers require no explicit use-list and create
with the declaring owner as both lexical and called scope, without a receiver.
Fixed function callables preserve the first successful namespace/fallback target
even when a later initializer error discards the object. Static-method callables
retain the method owner and selected called class separately, including private
access from the initializer owner. Literal string class selectors use global
spelling, while named selectors keep their namespace/scope rules. Invalid
nonstatic/use/dynamic forms and literal nonstring names retain PHP compile errors.

Object caches retain genuine constructor identity and recursive array/alias
certificates; objects never become cross-unit folded pool values. Nonowning
creation records preserve retired selection history. The cache owns the object
and its scope and static cells. Clones copy the current body/scope/static state
without acquiring the original constructor marker. Four finite fixtures reject
coherent scalar erasure, wrong array sites, substituted clones with invented
records, invalid selection prefixes/scopes and missing roots (159 predicates).
A later literal-class fixture adds 44 predicates. Twenty-two new full native
comparisons bring the maintained catalogue to 72 (32 normal, 22 PHP errors, 18 static
rejections). Source and finite cutoffs remain separate; promotion adds no rerun.
A later current-source comparison registers a cached constant Closure as a handler.
Its GLOBALS write leaves the folded false-left expression's original null intact,
and repeated identity/direct invocation retains the static counter (`1null:same:2`).
This brings the maintained catalogue to 73; the earlier 72 sources stay unchanged.

Named constexpr `::class` folds namespace/import spelling without class lookup.
Known self uses the declaring owner; known parent retains its source spelling.
Closure and eval contexts resolve deferred self/parent from authenticated lexical
scope, including rebound defaults. Contextual defaults bypass origin-only caches;
ordinary defaults retain their existing cache ownership. Literal class strings
and parser-folded literal concatenation follow Zend's separate class-name route.
Live static/computed forms and nonstring literals retain their PHP errors, while
folded dead branches disappear before admission.

Seventeen constant-context and two ordinary keyword-form comparisons add nineteen
agreements (11 normal, one PHP error, seven static rejections), bringing the
catalogue to 92. Two focused fixtures add 25/38 predicates for coherent folded
spelling substitution and a forged contextual default cache/rebound scope.
Original Unsupported and elaboration failures stay preserved; the earlier
binding-premise draft remains unrun.
the original concat rejection hypothesis remains refuted by normal `GhostName`.
These source and finite cutoffs are separate; current parameter composition is
pending and maintenance adds no execution credit.

Accessible references into an incomplete class table are explicitly Unsupported;
the separate rejected control is not a native agreement. Unretained
computed/scoped table-update selectors remain
Unsupported. Constructor contexts outside class constants, builtin FCC targets
and object transfers without an authenticated source/cache relation also remain
Unsupported. Constant modifier
admission, attributes, traits/enums/internal constants and broader default/property
consumers stay open. These checks reused the recorded runtime; they add no fresh
copied rebuild, reporting-mask, paused return or full-core closure.
