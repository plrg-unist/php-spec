# Runtime successor: first source calls

This handoff continues the complete-core task. First calls are a reviewed increment,
not a completed call family or full-core closure. Read AGENTS.md, the php/php-spec/
p4-spectec skills, PLAN.md, PROGRESS.md, SOURCE-CALLS.md, and the current reviewer and
compiler handoffs. Root orchestrates; runtime6 owns the positional-reference
successor, compiler5 owns compiler work, and review9 is independent. Runtime5 and
review8 own the historical firstcalls evidence below. Never push. Use the sole pinned PHP8.5.10 NTS64 oracle and actual pure
SpecTec rules. Preserve original failures before repairs, including complete states,
source bytes, primitive profiles and actual executable inputs.

## Publication state

Final production root is `.tools/runtime5-calls-production`, 869 inputs,
`c946394c29704e4df20b5fa88137b42108de51bb17da30ef72eebda664bd2dd6`.
Its 40 code paths are installed canonically; all 869 content hashes match. Existing
executable mode of bin/php-semantics is retained. The exact reviewed standalone
builtin_argument_modes.py remains canonical; an unused .watsup.txt prototype is
omitted. No compiler/adapter/numeric binary was rebuilt.

Code commit `a8fdac1e` is independently approved. Fresh production869 state9
passed2079 assertions, source139 and protocol40 passed, and canonical CLI8 passed.
Independent final state audit is `.tools/review8-final-state-audit.json`. Runtime author **d907c5db**, compiler author **04ac151f** and independent
acceptance **f3149e32** bind the completed milestone.

Accepted prior integration: fullquiet ordinary5706+21 and explicit request263,
author83cce919/c9fce8c9, independentdf1ddd18/ba2e421a. Builtin occupancy780 and
argument-mode780 prerequisites are separately accepted; argument codeeef227b2,
author8603870c, reviewc931cd66. Current inventory remains169 constructors and306
obligations; only oracle pin is closed.

## Runtime and compiler interface

`pfunction` retains original ORIGIN, NAME, SIGNATURE, CVS, ENV, CODE, BODY, EARLY,
LINE. Per-body compilation resets/restores CVS/header/magic/lexical context; BODY
is declaration path + PCFIELD5. Request CODE includes disjoint body descriptors;
function.CODE excludes nested bodies. Original occurrence identities remain unique.

Runtime fields GLOBALTABLE, FRAMES and CURRENT explicitly move symbol tables.
First entry moves main table into GLOBALTABLE, nested entry saves caller locals,
last exit moves main table back. Saved main frame has no duplicate local table.
Saved TODO/HELD/locals, current and saved EXTRA operands, and trace values own heap
nodes. Parameter names borrow CV cells. RETURN_UNWIND and ERROR_UNWIND clean
origins/iterators and preserve returned values before discarding callee roots.

CALL_ARGS and CALL_SEND retain selected function ORIGIN, not redundant descriptor
copies. Lookup occurs before argument effects; selected namespace fallback remains
stable when an argument activates the previously absent namespaced declaration.
Arguments and surplus values remain owners; too-few diagnostics preserve exact
supplied/default-free parameter and trace state.

Modules79/80/81 implement frames/calls/global statements,82 routes compiler-designated
superglobals,83 implements pure traces. Dynamic names equal to superglobal spellings
remain local unless the compiler emitted the actual global-fetch designation.
Request callbacks update GLOBALTABLE when a call is active, preserving old aliases
and the separate HTTPROOTS value owners.

Module84 validates source-derived metadata once at public drive entry; recursive
steps use drive_steps. It recompiles the checked original UNIT with FILE/requestCWD
and checks registry/function projection, call names/emission lines, CODEARG and
CODE.GLOBALS, active/saved contexts and held tasks including AT wrappers. ARGC equals
original positional NArg count; EXTRA length equals surplus count; CALL_ARGS/SEND
indices, remaining syntax suffixes and held operand counts match original source.
Runtime values are not reconstructed or restricted by source history. Already
terminal outcomes retain their classification. Invalid normal resume state rejects
before further effects even at zero budget.

PPF models deferred argument variable fetches; CODEARG marks actual PPF occurrences.
Known earlier exact value callees use PPR, while forward/self/conditional/fallback
calls retain deferred mode. Keys and nonvariable bases use PPR. Module85 preserves
nested-key/name/base effects and warnings before deferred [] read errors; direct
CV append avoids an unintended undefined-variable read. Compiler78 restores outer
call emission line only after successful argument compilation.

## Evidence and open boundaries

Final870 source139 and278 raw worker responses match reviewed866 states exactly;
all observations have explicit shared primitive native/provider profiles. Protocol40
includes registry/context/metadata/descriptor rejection and fallback suspension.
Production869 is a consumer-only bridge from870; current869 state9 verifies actual
ownership/return/iterator/error/deferred/fallback suspension cuts. Each-cut one-step
checks and seven selected full resumes are explicit; do not claim all-cut full
suffix runs. Historical owner8/3504, argument6/1962, scope5/986, iterator2/564 and
old868state9/2079 retain their actual identities.

Compiler5 independently reviewed broad5751 lints/5783 aggregate includes all5706
quiet source bytes. Focused seven aggregates cover848 native phases. No additional
broad compiler rerun is needed solely for final runtime84 guards/test consumers.
No final fullsyntax/offline rebuild/fullcore closure is claimed.

Source execution currently admits named functions, plain untyped by-value positional
parameters and value returns, recursion, global declarations and exact core errors.
By-reference/default/typed/variadic/named/unpacked arguments and reference returns,
closures/arrows, objects/methods, dynamic source, exceptions/handlers, generators/
fibers and remaining intrinsics remain work. Registered ordinary-library execution
may stay outside scope, but compiler name occupancy/argument modes are core facts.
The sole intended namespace-relative static divergence is class-scope declaration
typing; named global-signature rejection is now source reachable and agrees natively.

## Next bounded reference-parameter stage

Compiler5 froze `.tools/compiler5-reference-parameters/reference-delta.{json,patch}`
with five paths, including REFERENCE-PARAMETER-PREPARATION.md. It permits untyped
positional reference parameters while retaining no defaults/variadics/value return.
Known user parameter BYREF selects PPW; forward/deferred uses existing PPF. Compiler46
allows function-result write-DIM bases via PPR, while array-literal DIM known-write
remains a native compile rejection.48 native compiler phases and16 descriptor/header
assertions pass; no runtime admission is claimed.

Original archive2521 paths SHA
`3cc3c691795ab36a51b6577d753c27943aca15075aa7b88dc1af4d2d8a53a6cc`.
Runtime must send actual locations for required-reference parameters, promote/bind
reference cells and preserve ownership and diagnostic send lines. Reuse normalized
psparam.BYREF and existing location protocols. Do not infer Zend VAR/TMP status from
syntax: returned call values can require Notice+fresh reference, while literals and
many assignment/update expressions error. WholeGLOBALS compiles PPR then runtime
errors. Capture forward `f([1][0]); function f(&$x){...}` before consumer changes;
existing48 includes known arrayliteralDIM static fatal, not that deferred variant.
Compiler5 subsequently captured the missing variant separately under
`.tools/compiler5-reference-successor/.tools/reference-successor-originals-36ywdi7m`: native lint0, then runtime Error Cannot use temporary expression in write context,
no body output. Its23-file supplemental archive is separate from frozen48; old866
compiler/runtime Unsupported states are preserved.
Retained multiline-call `function f(&$x){}f(\n1\n);` gives reference-send Error at
argument line2 while outer call metadata stays line1; use the measured send line.

## Reproduction and ownership

Base author history and supplement preserve content-addressed raw payloads, original
paths/modes/symlinks and all actual tool bytes. Canonical coverage names:
function-call-history.{json,tar.xz}, function-call-history-supplement.{json,tar.xz},
function-call-publication-originals.{json,tar.xz}; function-call-publication.json
binds source/state/protocol reports and exact current bridges. Compiler5 owns its
six separate archive groups listed in first-call-compiler-evidence.json; next-ref
archive is excluded from firstcalls evidence.

The strict recorded_worker retains exact request/response bytes, stderr, partial
failures, timeout and closure status; it rejects trailing stdout/nonempty stderr
and nonzero exit. Both frontend/adapter always close even if the first close rejects.
Original decoded-response gates and first permissive-close prototype remain history.
Do not relabel those as strict current raw gates.

## Startup and exact next compiler stage

Re-read the mandatory skills, AGENTS.md, PLAN.md and current PROGRESS.md;
coordinate with the current compiler and independent reviewer before edits.
Runtime5 has no surviving processes. Read
`.tools/compiler5-reference-successor/HANDOFF.md` and the frozen
`.tools/compiler5-reference-parameters/reference-delta.json` / `.patch` before
pairing positional reference sends. Preserve the original48+114 observations and
the separately retained forward arrayliteral-DIM error.
