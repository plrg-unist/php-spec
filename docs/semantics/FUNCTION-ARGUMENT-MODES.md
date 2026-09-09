# Positional argument compilation and deferred fetches

This compiler work is paired with the accepted [source-call runtime](SOURCE-CALLS.md)
and [independent review](../../coverage/semantics/calls-final-review.json). The original value-call checkpoint remains historical; positional reference
parameters extend these modes through the
[reference compiler contract](REFERENCE-PARAMETER-COMPILER.md). Defaults,
named/unpacked arguments, builtin bodies and remaining callable protocols keep
their separate activation boundaries.

At PHP 8.5.10, an earlier finalized exact function name supplies compile-time
argument modes. Forward calls, conditional declarations, the function currently
being compiled, and names requiring namespace fallback do not. Runtime lookup
still selects the actual active function before evaluating its arguments. These
are separate facts: later availability cannot retroactively change compilation.

For example, `function f($x){} f($a[]);` is a compile error, while
`f($a[]); function f($x){}` compiles and throws `Error` while fetching its first
argument. An undefined function throws before argument fetching. A dead
self-recursive call containing `$a[]` compiles and has no runtime effect.

The compiler's PPF mode represents `BP_VAR_FUNC_ARG` on actual variable and
dimension fetch occurrences. A direct ordinary CV argument first uses the native
try-CV read path; dimension ancestors retain PPF. Keys, computed-name expressions
and nonvariable bases use ordinary reads. This also preserves the op-array-local
`http_response_header` deprecation distinction. Earlier finalized user functions
are taken from the existing ordered declaration records; imports and namespace
fallback use the existing lexical resolver.

Each actually compiled PPF occurrence exports CODEARG beside its CODEEXPR. The
same per-body occurrence filter owns both descriptors. CODEARG carries no runtime
function pointer or inferred argument value. Value, write, effect, quiet-write
and scope descriptor traversals explicitly preserve their own classifications.
Runtime consumes these source-bound fetch designations; malformed or missing
markers require the paired public integrity checks.

The configured initial builtin namespace has 780 functions. Its positional send
flags come from the same 13 preprocessed C registration tables used by the
namespace inventory. `scripts/generate-builtin-argument-modes.py` follows each
registered arginfo array, requiring the pinned `_ZEND_ARG_INFO_FLAGS` expansion
for every parameter. Required-reference and prefer-reference modes both select
writable variable compilation; variadic reference tails extend beyond the final
fixed position. Absent ordinary parameters use value compilation. This metadata
specifies compilation, and does not execute builtin bodies.
The generated pure table is 25-builtin-argument-modes.watsup. The source report
binds the producer root, generator hashes, configured inputs, raw preprocessing
and each exact arginfo array. A separate native Reflection metadata comparison
checks all 780 rows; 7,508 pure assertions include case-folding and extra positions.

Authoritative pinned sources:

- `Zend/zend_compile.c`: `zend_compile_call`, `fbc_is_finalized`,
  `zend_compile_args`, `zend_try_compile_cv`, `zend_compile_simple_var_no_cv`,
  `zend_delayed_compile_dim`.
- `Zend/zend_compile.h`: `zend_check_arg_send_type`,
  `ARG_SHOULD_BE_SENT_BY_REF`, `_ZEND_SEND_MODE_SHIFT`, `_ZEND_IS_VARIADIC_BIT`.
- `Zend/zend_API.h`: `_ZEND_ARG_INFO_FLAGS` and generated arginfo macros.
- `Zend/zend_vm_def.h`: `ZEND_CHECK_FUNC_ARG`, `ZEND_FETCH_DIM_FUNC_ARG`.

`function_argument_compiler.py` compares 39 complete lint phases and 21
argument/body/header descriptor controls after the multiline call-site repair. Runtime comparisons and malformed-descriptor
public resume tests are separate. Original native/compiler/full-state failures
remain retained; Unsupported, timeouts and interpreter errors are not agreements.
