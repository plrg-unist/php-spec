# Successor: named argument binding

Start from accepted959/4854ee08: codeb49a564c, compiler3c27910a,
author81a7b991 and independent4187c887. The
[positional contract](SOURCE-POSITIONAL-VARIADICS.md) and
[review](../../coverage/semantics/variadic-review.json) bind full files/modes.
Semantic959/cee5 differs only in the older function-compiler expectation (4d69),
then the dense-test allowance (4854). Both exact prepared fixtures passed under
900 seconds; the original300-second timeout remains retained. Use final4854 for
new baselines; preserve the original source/native profiles rather than renaming
historical951/942 evidence current.

Reuse79/80/83/84/86/91/95/101/103 ownership, source-send, default-cache, type and
cleanup interfaces. Positional fixed receives precede tail collection. EXTRA
retains sent operand slots while the packed tail also owns entries; coercion can
change earlier fixed/tail aliases. Guard source metadata and finite stages, not
past values or already-verified types. Reporting is signed32/request-global;
frame SILENCES restore through normal and abrupt cleanup independently of TODO.

## Retained preparation and required design

Compiler preparation is `.tools/compiler7-named-next/PLAN.md`, archive
88d514f881b8a512152d51aa17dcc8466079952b8eeb9bccce77b9b189821b70:
20 native/current951 originals,18 separately profiled opcode observations and
two static cases. Later STARTUP qualifications and three extra-only controls are
outside that frozen archive. The latter are retained under
`.tools/runtime7-variadic-baseline-parser951/.tools/compiler7-named-tail-originals-3meluysg`.
Preparation and opcode facts do not establish admitted runtime behavior.

Named arguments need separate source-send order, destination fixed slots, highest
supplied fixed position for holes, effective positional ARGC (including positional
variadic tails) and ordered extra named keys. The variadic
parameter's own name is an extra key, not a fixed slot. Existing positional source
argument-count equality and83's positional-only trace text cannot be reused.
Only extra named keys with a required fixed prefix produce native “0 passed”
arity wording; missing middle fixed slots instead use “not passed”. Extra-only
callee errors preserve names in traces, such as `f(z: 3, y: 4)`; an omitted default
can execute without appearing as an explicit fixed trace argument.

Pinned CHECK_UNDEF_ARGS evaluates and caches missing defaults below the highest
supplied fixed slot before ordinary typed RECV. It does not perform the ordinary
parameter type verification. Contiguous supplied slots retain the usual receive
order. Existing91's coupled default-bind/type continuation therefore needs a
separate hole preflight. Retain cache-before-later-failure and fresh omitted
reference cells, with uncoerced cached values and declaration context.

Independent user-constant controls are in `.tools/review10-named-preparation.md`
and archive9369a2a0dad345aed390081de09d66b61117b288f2ef9b224f241665b5decc24.
Both sources parse/lint cleanly and are Unsupported on951/440f. With default
`C+1` and `C="2x"`, reordered `f(z:3,x:[])` warns before TypeError and traces
`f(Array, 3, 3)` despite two source expressions; contiguous `f(x:[])` type-errors
before that warning and traces `f(Array)`. Actual cache-state assertions remain
required in the paired implementation; native output alone does not prove cache
contents. Compiler's literal deferred-warning controls are separately retained.

Name-error timing depends on the operand path. The retained call/DIM controls
execute operand effects before SEND raises an unknown/duplicate name error;
CHECK_FUNC_ARG selects mode and does not itself raise those errors. The initial
opposite inference is explicitly corrected in preparation. Delayed undefined CV
reads are different: named SEND_VAR handles the name before fetching the CV.
Retain those missing native controls before implementing that path. Also verify
named-tail TypeError numbering: the pinned named RECV_VARIADIC loop does not
increment its argument number for each named element.

Reuse existing builtin parameter-name facts, but do not infer default filling,
body execution or callback behavior from that inventory. Bound the first named
slice to supported callees while keeping the builtin contract dependency explicit.
Array argument unpacking follows named destinations/string keys; Traversable,
dynamic callables, closures and caught exceptions remain required dependencies.

## Coordination and gates

Root coordinates compiler7/runtime7 and independent review10. Preserve concrete
native/current originals before admission, agree source/slot/default/trace schema,
freeze a coherent pair, and retain finite guard counterexamples with arbitrary
consistent values. Test alias coercion, cache/receive priorities, saved/held/tail
owners, source lines and meaningful resume cuts. Publish small reviewed commits;
never push. Full current callable integration and final all-source/full-syntax/
fresh network-isolated offline checks remain mandatory. Objects, exceptions,
reporting configuration/handlers, dynamic sources, generators/Fibers, lifetime
and core intrinsics remain in the full goal; no callable family closes here.
