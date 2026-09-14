# Builtin named argument compilation

Module106 supplies fixed parameter-name lookup for the configured 780 builtin
signatures. Module104 uses the resulting zero-based index to choose the existing
positional fetch mode: PPR for value parameters and PPW for required or preferred
reference parameters. Call results, nonvariable expressions and `$GLOBALS` retain
ordinary expression compilation. This is compiler support; builtin execution,
default filling, callbacks and runtime name errors remain separate dependencies.

The generator reads configured, preprocessed C registration tables and arginfo.
It folds function names to lowercase, compares parameter names as exact bytes,
and excludes the variadic descriptor from fixed lookup. Unknown names and the
variadic parameter's own name remain deferred. Namespace fallback also remains
deferred; imported aliases and fully qualified builtin names select known modes.
No PHP execution or Reflection supplies the generated semantics.

The matching engine routes are `zend_get_arg_num` and `zend_compile_args` in
`vendor/php-src/Zend/zend_compile.c`, with internal fixed `num_args` established
in `Zend/zend_API.c`. Variable operands at known indices use BP_VAR_R/BP_VAR_W;
unknown named indices use the existing deferred CV/FUNC_ARG distinction. The
known-name test also preserves the distinction between a literal CV's emitted
line and the argument-list line used for deferred sends. Original SOURCE metadata
is unchanged. Existing module25 positional flags are byte-identical.

`zend_try_compile_special_func` rejects all named/unpacked argument lists before
special or frameless lowering. Module87's positional-only shortcuts remain
unchanged. For example, `strlen(string:"a")[0]=1` compiles normally, although its
ordinary native execution fails when writing through a scalar return value.
A named `strlen(string:$a[])` is statically rejected for reading an append
location, while unknown `strlen(z:$a[])` compiles a deferred operand. These
examples do not imply that builtin bodies execute in the model.

The retained evidence starts with ten exact historical builtin sources, replayed
on accepted968/ab389 without repeating native execution. Fourteen new originals
cover namespace and alias resolution, case, call/$GLOBALS/nonvariable operands,
and multiline known/deferred/static priorities. Eleven separate preoptimizer
profiles supplement the ordinary native/parser/lint streams. Actual source
execution has eleven exact native static outcomes and thirteen explicit builtin
body boundaries. Unsupported executions are not native agreements.

First969/8079 passes actual adapter structural execution and all24 compiler phases.
Its old named compiler test fails at the first stale builtin Unsupported assertion;
that original failure is preserved. The maintained972/e1bf snapshot changes only
test selection/additions and Makefile wiring after the first semantic snapshot.
Its gates pass780 signatures/6,589 lookup assertions,24 native compiler phases/33
source projections,59 existing named compiler phases/129 projections with two
remaining catch/unpack boundaries,91 builtin-write phases, and7,508 existing
positional-mode assertions. The positional native metadata check remains validation
of configured facts, not the source of the generated definitions.

Two isolated source copies each reproduce both generated modules from238 configured
inputs and14 recorded compiler commands. Only the configured Makefile's absolute
include paths are relocated;237 other input files remain exact. The raw commands,
preprocessor identity, source hashes/modes and resulting780 records are retained.
The generated argument report is installed with its exact gate-consumed bytes;
its argument records are unchanged while producer provenance records this run.

The [originals manifest](../../coverage/semantics/builtin-named-compiler-originals.json)
and [pairing record](../../coverage/semantics/builtin-named-compiler-pairing.json)
bind snapshots, tools, streams, failures and canonical installation. Compiler-only
results retain their actual identities. Array call unpacking, builtin bodies and
required core intrinsics remain open; this prerequisite closes no core family.

Canonical code84fc35f5 passes public CLI checks for four static outcomes, three
explicit builtin boundaries and one existing usernamed reference-tail control.
The first CLI producer incorrectly expected process exit0 for Unsupported; the
public CLI intentionally returns1. Its exact failure is retained beside the
corrected eight-case gate, with no semantic changes or repeated native execution.
