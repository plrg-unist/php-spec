# Dynamic-source first emitted work

For the selected nontrivial child programs, PHP 8.5.10 retires an owned include
operand after compilation but before the child's first instruction. A throwing
destructor reports that instruction's line even though the child body never runs.

Module 314 adds three nonconstant ECHO cases to 298's accepted constant/assignment
selection: an ordinary CV emits ECHO at line 5; a literal instance-property read
after an ordinary CV emits FETCH_OBJ_R at property-name line 6; a resolved named
nonbuiltin call receiver with no arguments or namespace fallback emits INIT at
line 5 before the property fetch. Authored CODEEXPR/CODENAME rows certify the
occurrences. The existing completed-image, source-entry suffix and exit checks
authenticate their use; AST start lines alone do not choose them.

The rules follow vendored `zend_compile_echo`, `zend_try_compile_cv`,
`zend_delayed_compile_prop` and `zend_compile_call`. Ordinary CV classification
excludes `this`, all auto-globals and `http_response_header`. Dynamic property
names, builtin/argument receivers and wider expressions retain the earlier
fallback and remain required first-emission work.

The [ledger](../../coverage/semantics/source-expression-emission-review.json)
records an independently accepted isolated 277-module cut: strict compilation,
three exact normal source agreements, 57 genuine entry/image/heap/public premises and 72
matching-compiler-image shape premises. The two original fixture-only stops
remain zero credit. Relocated tests prepare the same 57/72 with zero applications.

The isolated 277-module cut is reproduced using the ledger's
explicit `--semantic-root .tools/source-stringable-expression-emission-314`;
canonical module 314 is installed after Fiber308 on the 286-module parent. One
fresh nested-Generator property source and 70 genuine entry/retirement/public
premises pass there, including heap-identical receiver/image/owner/suffix
forgeries. The maintained generator case prepares70 with zero applications.
Earlier literal, retirement and Generator-composition cuts keep their original
identities. Broader emission, complete core and the final combined, fresh offline
rebuild remain required.

Module316 adds literal core auto-globals except `GLOBALS`: direct ECHO emits
FETCH_R at the variable line, and a literal property receiver emits that same
fetch before the property instruction. Both expression records retain their
real lines and the source-entry hook authenticates the complete image.
The [separate ledger](../../coverage/semantics/source-autoglobal-emission-review.json)
records isolated278 source2 with explicit request facts, independent79 genuine
MAIN entry/retirement/heap/image/resumption premises, computed-name11 and a new
maintained72 classification cut. The source cases use the reviewed FD198 request
provider; `scripts/build-request-provider.sh` prepares it. Relocation earns zero
renewed source credit. `GLOBALS`, `this`, `http_response_header`, computed names
and broader producers remain required. Current-parent integration is pending.
