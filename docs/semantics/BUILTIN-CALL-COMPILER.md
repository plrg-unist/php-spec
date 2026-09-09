# Builtin call result compilation

Target: PHP 8.5.10 CLI NTS 64-bit, the pinned core profile with `zend.assertions=1`.
This compiler contract accompanies positional reference parameters. It specifies
no ordinary builtin bodies. Source execution and the paired runtime checkpoint
are separate from the compiler phase evidence described here.

A call used as a writable DIM base is compiled with the original write context.
`zend_separate_if_call_and_write` rejects the result if special lowering produced
a constant or temporary value. Ordinary calls produce a VAR result, including
ordinary library calls whose execution remains Unsupported. Compiler-known
reference arguments use write mode; forward/self/namespace-fallback calls retain
deferred fetch mode and do not acquire this static rejection merely because the
selected runtime parameter later requires a reference.

Module 87 records the pinned write-context special-lowering decisions:

- Arity selects strlen, type predicates, scalar casts, count/sizeof, gettype,
  clone, get_class/get_called_class and array_key_exists.
- func_num_args/func_get_args require an active function body. The array_slice
  shortcut additionally requires the exact func_get_args call and literal offset.
- defined uses the shared parser-literal helper, including the parser's literal
  concatenation action, and excludes namespace/class separators.
- in_array uses the shared constant-array result, constant strictness and eligible
  element kinds. Loose string lookup rejects complete numeric strings; a leading
  numeric prefix alone does not prevent lowering.
- sprintf uses its bounded format/placeholder decision over the shared compiled
  constant operand. This decision does not implement formatting execution.

chr/ord constant specialization and frameless calls require read mode, so they
are excluded from the write-context decision. call_user_func[_array] and enabled
assert do not produce the temporary kind at issue here. Builtin occupancy remains
source-derived from the pinned registered function table, with case-insensitive
name resolution and the original namespace fallback distinction.

The in_array constant haystack prepass runs before needle compilation, unless
unknown strictness or runtime namespace resolution declines the optimizer. It
reuses module 45, retaining its constant-folding, array validation, source paths
and diagnostics. This preserves which error wins when both arguments are invalid.
No second constant evaluator or host-engine semantic call is introduced.

The write rejection occurs after the expressions the special lowering compiles
and before the outer DIM key. Its line is that last compiled expression's line.
For example, multiline strlen reports its argument line; defined and sprintf with
no value arguments retain the call line. Ordinary user-call trace metadata keeps
its separately reviewed call-site location.

Primary source: `vendor/php-src/Zend/zend_compile.c`,
`zend_separate_if_call_and_write`, `zend_try_compile_special_func_ex`,
`zend_try_compile_special_func`, `find_frameless_function_info`, the named
`zend_compile_func_*` helpers and `zend_try_ct_eval_array`;
`Zend/zend_ast.c::zend_ast_create_concat_op`. The imported source references and
actual copied tools are hash-bound in the evidence archive.

The compiler refinement retains 91 ordered native lint/compiler comparisons:
seven initial write-context originals, 74 selector/context controls, eight
numeric/error-priority controls and two sprintf line controls. Every old source,
checked AST and full compiler/runtime result is retained; Unsupported old runtime
states are not agreements. The final focused compiler repeats include 39 named
phases with all seven pending signature controls, the historical 32 argument
phases, and 111 destructuring phases with 32 metadata controls. The original 48
reference preparation phases and 12 send-kind phases have separate exact input
bindings. These counts do not claim a fresh broad compiler or runtime campaign.
