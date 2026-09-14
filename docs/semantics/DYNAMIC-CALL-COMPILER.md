# Dynamic string-call compilation

Code8ec07158 installs the exact paired990/866a6afd implementation.
Compiler109 admits expression callees for the paired user-function lookup in
runtime110. It preserves original callee FIELD0 and argument FIELD1 paths,
argument order, namespace rules, reference modes and the existing named/unpack
binder. A call result remains the ordinary call VAR for107; initial known
builtin special-result lowering remains a separate required dependency.

The pinned compiler has three distinct paths. An initial parser ZVAL string,
including parser-folded numeric/string concatenation, can use finalized-function
parameter flags. Its name is fully qualified and removes one initial backslash;
lexical namespace/import fallback does not apply. Existing20 parser_literal
models that initial folding. A string produced later by ordinary expression
compilation uses INIT_FCALL_BY_NAME with deferred argument modes. Other callee
operands use INIT_DYNAMIC_CALL, also with deferred modes. A later constant value
does not justify known parameter flags.

A later CONST string emits a raw CODENAME at the call root, preserving a leading
backslash. INIT_FCALL_BY_NAME hashes that fixed name; INIT_DYNAMIC_CALL instead
normalizes the evaluated runtime string. The descriptor binds lookup and selected
function identity without retaining past runtime values. Initial literal strings
still use normalized names. Internal PNRESOLVED mode carriers have an explicitly
unused ORIGINAL placeholder; it is not a checked source name or exported source
occurrence. Calls to initial literal builtins remain an explicit compiler
boundary, including their write-context lowering, until that required source
compiler work is implemented.

Each admitted expression call receives CODECALL_INIT in the existing descriptor
list, after compiling its callee and before compiling arguments. This is an INIT
line marker, not a constant, write, effect or argument descriptor. Abrupt callee
compilation adds no marker. Its child CODEEXPR remains unchanged. The call
instruction itself uses existing checked callableExprLine for expression
callees, reflecting the parser's saved line after callable_expr. Ordinary name
calls keep their previous source line. The compiler also preserves the separate
post-argument LOCATION used by surrounding instructions.

Retained native controls distinguish inner call4, INIT5 and outer called-in6.
Parenthesized literal and CV controls confirm the same parser-line rule. Separate
opcode controls distinguish parser ("f" . 1) known SEND_REF from later
("f" . (1+0)) deferred SEND_FUNC_ARG. Ordinary ternary, coalesce and cast callees
materialize TMP operands; suppressed constants retain CONST. Their leading-slash
lookup outcomes distinguish INIT_DYNAMIC_CALL from INIT_FCALL_BY_NAME. A dynamic
reference return used as a by-reference unpack container changes the external
array element, exercising the99/107/108 connection.

The compiler evidence preserves twenty earlier972 originals and twenty-four new
981/764 originals with exact native/parser/lint/request contexts. Nine earlier
and fourteen new opcode runs are separate instrumentation profiles. Initial
fixture/declaration failures, the old CALL4 projection, the actual CALL4vs6 and
CONST-name lookup discrepancies, and the retired dynamic reference-call compiler
expectation retain their original identities. A first test draft incorrectly
compared whole function-body expression lists with a separate access scope;
its failed assertion is retained as a test correction.

On985/614fc2f0,42 source compiler phases, two explicit initial-builtin boundaries
and275 projections pass. Six current-source shared packets pass under the
corrected compiler:29 reference acquisition,39 argument modes,60 named plus one
boundary,29 unpack,58 reference-return, and57 typed plus seven boundaries. Their
native observations retain the earlier985/3eaf contexts. One wrapper failed
only after its maintained39 gate and both worker closures completed; its outer
failure remains explicit. Runtime source/protocol/ownership acceptance and final
installation are linked separately in the
[pairing record](../../coverage/semantics/dynamic-call-compiler-pairing.json). The accepted complete
integration on981/764 remains historical after109/110 activation. Builtin bodies,
remaining callable forms and full core semantics remain required work.
