# Call results in reference assignments

Compiler96/runtime97 connect named positional calls to reference assignment on
PHP8.5.10 CLI NTS64, paired933/7391ccdf. Acceptance and exact evidence are recorded
in [the independent review](../../coverage/semantics/call-reference-review.json).
Reference-return declarations remain a separate required increment.

For a value-returning call, `$x =& g()` emits `Only variables should be assigned
by reference`, then performs an ordinary target write. Existing target aliases
survive for literal variables, computed variables and dimensions. An assignment
expression retains an existing reference wrapper when present; a value consumer
detaches its value using the established ownership rules. A real returned
reference follows the binding path. Protocol controls exercise that path with
an existing valid cell; they do not claim source reference returns are admitted.

The RHS call runs before the delayed target fetch. Target/key captures retain
their established timing, while target fetch errors precede the assignment
Notice. A callee TypeError prevents that Notice and releases held call state.
Returned arrays preserve COW and ownership across nested frame cleanup.
`ZEND_MAKE_REF` wraps CV/indirect locations but leaves an ordinary call VAR value
unwrapped; a uniform fresh-cell conversion would lose the target-alias behavior.

Compiler admission is limited to a direct call on a reference-assignment RHS.
Generic writable-call compilation is unchanged. Array reference items containing
direct calls are rejected after their key and before call arguments. Existing87
builtin write-context diagnostics remain active; registered builtin bodies are
still Unsupported. Temporary call-result dimension/send/list paths retain their
existing rules.

The shared compiler correction records a call instruction at its own source
line while preserving the post-argument compiler location for its enclosing
instruction. Multiline reference assignments and typed returns can therefore
have different emission lines from the nested call. The retained926 typed-return
counterexample reported line4 where native reports5; paired933 reports5. Existing88
constant diagnostic-location restoration remains unchanged.

`ACQUIRE_CALL` must belong to an actual call occurrence on an assignment RHS.
The active stage accepts owning values/references, including arbitrary consistent
substitutions; a deferred VARIABLE operand is rejected before stepping, including
through leading AT/ORIGIN_RETURN wrappers. Queued/saved stages validate source
metadata without inspecting another stage's current result. Assignment-root and
call-line descriptors are tied to their exact source projections. The original
accepted forged Notice line103 is retained before repair.

Final gates comprise author17 source profiles, compiler26 exact phases plus3
explicit boundaries/29 projections, protocol13/227, and the selected typed38 and
adjacent13 source regressions. Independent gates cover7 native profiles plus4
pending reference-return controls, protocol13/227, three dense states/819 and two
complete926 state comparisons at seven cuts with no normalization. Author two dense
states/553 cover target rebinding and append ownership. Sets overlap; historical
compiler and preliminary runtime gates retain their original fingerprints.

Next, activate source reference returns with owning cells surviving frame release,
distinct return/send/assignment notices, value consumers, and typed shared-cell
coercion. Reuse the retained13b3 preparation and independent reference-owner
originals. Named/unpacked/variadic calls, closures, objects, exceptions/finally,
dynamic sources, generators/Fibers, lifecycle and core intrinsics remain required.
The callable integration campaign and final current-source/full-syntax/fresh
offline checks are still mandatory; no core family closes here.

Authority: pinned `vendor/php-src/Zend/zend_compile.c` (`zend_compile_assign_ref`,
`zend_compile_call_common`), `zend_vm_def.h` (`ZEND_MAKE_REF`, `ZEND_ASSIGN_REF`),
and `zend_execute.c` (`zend_wrong_assign_to_variable_reference`). The source pin
is34308a6666b2d489c509541ea9befea9e2b42348.
