# Closure foundation after initial-main statics

Read [PLAN](../../PLAN.md), [PROGRESS](../../PROGRESS.md), the
[main-static review](../../coverage/semantics/main-statics-review.json) and the
[core checklist](CORE-CONTINUATION-CHECKLIST.md). Complete PHP core remains the
objective. Compiler113/runtime114 are accepted on1008/2829; no closure execution
or new closure representation has been admitted.

The proposed next foundation is runtime closure identity, explicit captures and
invocation. Arrow implicit captures and fake first-class named callables need
separate source evidence. A real closure receives its own capture/static table;
fake named callables share the named function's table. Declaration origin alone
therefore cannot identify every future persistent slot. By-value captures initialize
local bindings per invocation; by-reference captures and static cells share their
respective persistent cells. A selected closure needs an owner throughout argument
effects and transfer into the active call context. Review the smallest
value/heap/frame interface that preserves copies, aliases, invocation and eventual
object lifetime before changing shared state. Review source-visible closure value
operations such as truth, type checks, identity, conversions and array-key errors
alongside creation/capture/invocation; helper-only identity tests do not establish
closure execution. Do not treat a callable string as
a closure object or silently reuse named-function lifetime.

Compiler7's plan-only proposal is `.tools/compiler7-closures-next/PLAN.md`.
Pinned source routes include `zend_compile_closure_binding`, lexical-variable
checks and parameter conflicts in `zend_compile.c`, plus real/fake table handling
in `zend_closures.c`. Recheck the exact PHP8.5.10 source before choosing the initial
scope; closure binding APIs, objects/destruction, methods/traits/inheritance,
exceptions, include/eval and repeated op-array lifetime remain separate obligations.

Preserve exact native/source/request originals before admission and reuse retained
native observations across semantic identities. Require independent actual
source/state counterexamples and finite descriptor guards, arbitrary consistent
value/alias positives, ownership and dense resumption, complete old-state bridges,
full byte/mode maps and actual tools. Fixture failures, Unsupported, tool errors
and timeouts never pass. Publish small reviewed milestones without pushing.

Historical broad runtime and syntax reports retain their own identities. Full
current syntax, a fresh network-isolated offline rebuild/audit and every in-scope
core obligation remain mandatory before full-core acceptance.
