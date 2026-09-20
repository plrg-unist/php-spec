# Pipe source increment

The pipe operator evaluates and forces its left operand before evaluating or
selecting the callable on the right. The forced value becomes one positional
argument. Named user functions and existing callable closures use the ordinary
call binder, including reference-result mode; the first-class `f(...)` source
form uses its checked optimized lookup. A left expression that yields a
reference is read at the left operand's line before right-side effects. The
`CODEPIPE_SEND` descriptor records the later send line separately from the
callsite and lookup lines, and the compiler authenticates the pipe root, both
children, and marker together.

The syntax grouping and bare-arrow rejection are described in
[the syntax review](../../coverage/semantics/pipe-syntax-review.json). Runtime
rules are in `122-pipe-compiler.watsup` and `123-pipe-runtime.watsup`, with
narrow shared task and call-integrity changes. Matching-engine evidence starts
at `zend_compile_pipe` in the pinned `Zend/zend_compile.c`, with value sends and
calls in `Zend/zend_vm_def.h`.

[The runtime review](../../coverage/semantics/pipe-review.json) binds 12
private source outcomes (7 normal, 5 PHP errors), separate original-source
replays, and paused ownership/authentication controls. The maintained source
and protocol checks are `tests/semantics/pipe*`. Builtin, method, array and
other object callables remain explicit dependencies; this is partial pipe
coverage, not a full callable-family claim.
