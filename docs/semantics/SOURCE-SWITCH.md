# Switch source increment

The switch compiler compiles the subject, folds the eligible leading case
conditions, then compiles all case conditions and bodies. It preserves the
order of constant-fold warnings, semicolon-case deprecations, and static errors.
At runtime, cases are compared in source order until the first match; a default
is selected only if none matches. Execution then falls through bodies until a
break, continue, return, or error. Typed loop depth gives `continue` targeting
a switch its matching compile warning. The subject remains live through the
chosen bodies: a CV or reference is reread after case effects, while a temporary
owns its value until normal or abrupt switch exit.

Compiled boolean subjects have a distinct branch path. The compiler emits an
authenticated `CODESWITCH_BOOL` fact for a constant true or false subject;
runtime compares each case through boolean conversion, including the NaN
warning. An evaluated variable or assignment subject uses ordinary loose
equality. `CODESWITCH_COMPARE` records the post-condition line, and source
recompilation checks the switch root and comparison descriptors together.

The rules are in `124-switch-compiler.watsup` and `125-switch-runtime.watsup`.
The pinned engine anchors are `determine_switch_jumptable_type` and
`zend_compile_switch` in `vendor/php-src/Zend/zend_compile.c`, plus comparison,
conditional jump, and free handlers in `Zend/zend_vm_def.h`.
[The review record](../../coverage/semantics/switch-review.json) distinguishes
the maintained source/compiler/paused tests from independent original-source
and ownership audits. Object-dependent comparisons, class linking, and the
remaining control constructs are separate core obligations.
