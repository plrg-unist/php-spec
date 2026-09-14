# Arrow functions after explicit closures

Read [PLAN](../../PLAN.md), [PROGRESS](../../PROGRESS.md), the
[closure review](../../coverage/semantics/closures-review.json) and
[core checklist](CORE-CONTINUATION-CHECKLIST.md). Explicit closures115/116 are
accepted on1017/9325, code875c7867. The proposed next117/118 slice is source-visible
arrow creation, implicit captures and expression-return invocation. It is not yet
implemented. Root release and a fresh interface review precede new source/schema
changes or native campaigns. The compiler's private proposal is
`.tools/compiler7-arrows-next/PLAN.md`.

Pinned `zend_compile.c:find_implicit_binds_recursively` visits ordinary children
in order, uniquifies variable names, excludes direct autoglobals and `$this`, and
visits the name expression of computed variables. Nested explicit closures
contribute their use list, while nested arrows contribute their expression.
Only after discovery are the current arrow's parameters removed. Do not invent a
generic free-variable analysis which subtracts nested-arrow parameters or enters
nested explicit bodies. Distinguish parser-folded variable names, genuinely
computed names, source paths, magic names and emitted lines through bounded
source/opcode originals.

`ZEND_BIND_LEXICAL` with `ZEND_BIND_IMPLICIT` preserves undefined captures without
the explicit-use warning; `ZEND_BIND_STATIC` copies that undefined value into the
invocation local. A completed undefined capture is therefore different from null
and from the current UNINITIALIZED construction suffix. Review the smallest
source-authenticated capture-mode/progress representation before changing it.
Invocation must preserve undefined-read versus quiet-test behavior, fresh local
value cells and existing array/reference/object ownership. Do not weaken explicit
capture completeness or admit arbitrary malformed live objects.

Arrow expression returns need the original expression origin, return type and
reference demand. `zend_compile.c` adds an implicit return except for `never`;
authenticate synthetic return metadata without fabricating a checked source
NStmtReturn. Compiler discovery and runtime undefined/receive/lifetime behavior
are distinct obligations. Existing real object identities and owning call targets
are the shared foundation; no separate arrow object store or named-function
substitute is needed. Class-bound `$this` and method scope remain dependencies.

Before implementation, assign disjoint exact native sources for discovery order,
parameter shadowing, nested arrows/explicit captures, undefined read/quiet timing,
capture-array COW, reference return, expression/type-error priority and
named/unpacked invocation. Review source projection plus actual paused progress,
current/saved owners and arbitrary consistent-value positives. Retain failures
before repair, raw tool closures, exact bytes/modes and complete old1017 response
bridges. Reuse existing native contexts where unchanged. Source activation must
exercise real arrow creation and invocation, not only helpers.

A refreshed broad integration checkpoint is appropriate after arrow acceptance
and before another callable/class representation change. The explicit-closure
checkpoint repaired its discovered shared-consumer defects and passed focused
regressions, but these do not replace full integration. Re-enumerate then-current
ordinary/request/callable/compiler memberships and genuine dependencies on one
frozen identity; preserve profiles and exact originals. Move integration earlier
if a new shared defect warrants it. Historical981/f244a78e stays historical.

Fake first-class callables require their own named/shared static lifetime;
Closure binding/call/clone/fromCallable/reflection, class/method/array-callable
services, ordinary objects, cycle collection, exceptions and dynamic-source
lifetime remain required. The valid `["Closure", "fromCallable"]` type source
currently has an explicit service dependency, not a PHP error or agreement.
Full current syntax and a fresh network-isolated offline rebuild/audit remain
mandatory before complete PHP-core acceptance. Do not push.
