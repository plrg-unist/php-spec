# Named function bodies in the source compiler

The first compiler increment admits ordinary named functions with untyped,
required, positional value parameters and untyped value returns. It compiles the
actual checked body in its original source unit. Invocation, frame restoration,
argument ownership and return cleanup are paired runtime responsibilities;
compiler fixtures alone do not admit execution or close the callable inventory.

`ppstate.FUNCTIONS` collects `pfunction` records. `ORIGIN` is the original source
unit and declaration occurrence; `BODY` is its original field-5 statement list.
`NAME`, `SIGNATURE`, `ENV` and `LINE` retain the resolved declaration name, shared
signature helper result, lexical imports/namespace/strictness and declaration
line. `CVS` records parameters before body CV allocations. `CODE` contains that
body's own compiled operands, names, redirects and global-fetch designations;
nested bodies have separate records. The unit-wide compiler still retains all
ordered operand/fact data for one shared constant-pool export. ASTs are neither
cloned nor reparsed to make a function body.

Every body resets loop and header state and restores its parent's context after
compilation. Parameter names are allocated before body variables; a parameter
named `http_response_header` marks its header slot assigned, as required by
`zend_compile_params`. Nested compiler autoglobal requests remain request-wide,
including dead function bodies. `FOLD.FUNCTION` supplies `__FUNCTION__` and
`__METHOD__` to both constant folding and ordinary compilation, and restores the
parent name on body exit. Namespaces and file magic retain the shared source and
lexical interfaces; free function class/trait/property magic remains empty.

`EARLY` distinguishes top-level declarations, including bare statement-list
blocks, from conditional and nested declarations. Bodies compile before an early
function enters the callable namespace. Duplicate checks therefore follow body
errors. Imports conflict before the special assert/__autoload checks; the shared
lexical seen-name table retains declarations from nested bodies for later import
checks. Builtin occupancy uses the source-derived
[initial function registry](BUILTIN-FUNCTIONS.md). Conditional declarations retain
all compiler checks but become callable only when their declaration executes.

`pcode.GLOBALS` records original variable occurrences designated as global by
compilation, including computed names that are known during compilation. A
runtime-computed name equal to a superglobal is not sufficient. Direct special
GLOBALS lowering retains its existing bypass rules. `global` statements have
their own name compilation and try-CV read context; they do not inherit ordinary
whole-GLOBALS assignment rejection or header write flags.

Return statements compile their actual expression, including dead returns; bare
return uses the return token line. Call names use the existing function import
and namespace fallback rules, and ordinary arguments compile left to right. The pinned in_array constant
haystack prepass and builtin write-result checks are specified in
[the builtin compiler contract](BUILTIN-CALL-COMPILER.md). An earlier
compiler error survives later unsupported argument forms. Normalized signatures
with types, defaults, reference returns or variadics remain explicit activation
boundaries until their runtime checks and bindings are connected. Nonliteral
defaults retain the existing constant-expression boundary. These are assigned
next work, not permanent exclusions or native agreements.

The pinned source routes are `zend_compile_top_stmt`, `zend_compile_func_decl_ex`,
`zend_begin_func_decl`, `zend_compile_params`, `zend_compile_return`,
`zend_compile_global_var` and the call/argument compiler in
`vendor/php-src/Zend/zend_compile.c`. `tests/semantics/function_compiler.py`
compares exact ordered native lint diagnostics and phases, checks body context
and constant export, and keeps pending signature controls separate. It retains
source bytes, checked fixtures, native output, compiler fixtures and failures.
Untyped positional reference parameters follow the
[reference compiler contract](REFERENCE-PARAMETER-COMPILER.md).
The paired [runtime contract](SOURCE-CALLS.md) and
[independent acceptance](../../coverage/semantics/calls-final-review.json) bind
actual source execution and ownership evidence separately from compiler fixtures.
