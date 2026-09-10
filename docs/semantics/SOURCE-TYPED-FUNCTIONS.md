# Typed positional parameters and value returns

Accepted in code **0ed17419**, compiler evidence **2ea12015**, author evidence
**dabc28d9** and [independent review e097f95e](../../coverage/semantics/typed-function-review.json).
Canonical926/599f3963 differs from tested926/baa85f57 only by one standalone
protocol output helper; all925 other bytes and all926 modes are unchanged.

Target: pinned PHP 8.5.10 CLI NTS64. This increment connects normalized source
signatures to the existing positional call, default and ownership machinery.
It admits builtin scalar/container singleton types and legal unions of `null`,
`true`, `false`, `bool`, `int`, `float`, `string`, `array` and `mixed`; return types
also admit `void` and `never`. Existing 16/17 phase ordering and default
normalization remain authoritative. This is partial core coverage, not callable
or type-family closure.

## Receive and return behavior

Arguments are evaluated and bound before typed receives. A function with typed
parameters then receives slots in order: an earlier provided type failure wins
before a later missing required parameter. Functions with only untyped parameters
keep their existing schedule. Caller strictness governs parameter verification;
callee strictness governs return verification. Strict mode admits the prescribed
int-to-float conversion. Weak mode follows exact-type preference and PHP scalar
conversion order, including numeric-string classification, overflow rejection and
precision diagnostics.

A by-reference parameter conversion writes its bound reference cell. Parameter
types impose no continuing constraint after entry: later writes, or conversion of
another parameter sharing the same cell, may change its type. By-value return
conversion produces a detached result and does not overwrite a referenced local,
global or parameter. Type failures use the existing frame cleanup and ownership
rules, retaining externally rooted values.

Stored float defaults materialize as floats even when the original literal pool
contains an integer. Successful deferred evaluation installs the uncoerced cache
value and class before parameter verification; a later type failure retains that
cache. Evaluation failure does not install it. Fresh omitted parameter cells and
array/reference ownership follow the existing default contract.

Value returns are checked before unwind. `void` may fall through; `never`
fallthrough raises its distinct TypeError. Other declared return types, including
`mixed` and nullable types, reject falling through without a return. Explicit
return diagnostics use the compiled return instruction's emission line;
fallthrough diagnostics use the function's source end line.

## Source metadata and resumed states

Compiler 94 restores the surrounding return context after nested declarations,
records function `ENDLINE`, and records return-root `CODEEXPR` entries after
compiling each return expression. Runtime 95 consumes these source projections.
Typed receive tasks bind the current function, receive index, previous defined
slots and sole work queue. They do not reconstruct previously received values or
types. Fallthrough tasks bind a current function with a declared return type.
Return tasks bind the owning function's source unit, actual return root and
compiled line. Saved tasks are checked under their saved caller context.
Unit return-root metadata is compared with the source compiler projection,
including units without function declarations.

Uncaught CLI rendering follows pinned `zend_exceptions.c`: exact TypeError and
ArgumentCountError messages containing `, called in ` receive the temporary
` and defined` display suffix. The semantic diagnostic message remains unchanged.

The review binds15 native profiles plus3 ticks dependencies,5 dense states/1357,
19 retained protocol controls/217 and2 complete untyped917 state bridges. Author
38 source profiles plus3 cache projections/12,4 states/1096 and compiler56+8/38
pass onbaa. Corrected fresh protocol19/218 and canonical CLI8 pass on599. Source
sets overlap; these counts are not added.

## Required continuation

Mixed caller/callee strictness is an interface requirement. The retained native
same-file witnesses use a `ticks` declaration block that remains outside current
source execution. They are dependency controls, not admitted runtime agreements.
Cross-unit/dynamic/callback integration must exercise that distinction through
its own checked source route.

Class/object/callable/iterable types, reference returns, variadics, named and
unpacked sends, methods and other callable forms remain required. So do other
declare directives, builtin body execution, ordinary exception control, dynamic
sources, generators/fibers and the rest of the core checklist. The full callable
integration campaign and final current-source/full-syntax/fresh offline gates
remain mandatory. Unsupported outcomes and tool failures never count as agreement.

The [runtime successor handoff](RUNTIME-REFERENCE-RETURNS-HANDOFF.md) supplies
the exact926 starting point and reference-return/call-acquisition preparation.

The later [call-reference increment](SOURCE-CALL-REFERENCE-ASSIGNMENT.md) on933
corrects shared post-argument emission locations: a retained typed return around
a multiline call now reports native line5 instead of926 line4. Historical typed
gates and the926/baa-to599 test-only bridge above retain their original scope.
