# Callable default and variadic reception

Module248 stages deprecated keyword and compound callable checks for completed
defaults and positional/named variadic operands. Supplied fixed parameters keep
the221 source route. All three use the genuine receiving frame's lexical scope,
called class and receiver; a foreign constant declaration does not supply access.
Exact scalar/array and nominal union branches precede callable checking and emit
no callable deprecation.

Parameter defaults keep class-constant references deferred, matching
`zend_compile_params`' constant-substitution flags. A literal omitted default
skips receive verification, while a resolved AST default, including a cache hit,
is checked. Named-hole preparation resolves all missing defaults before formal
reception; the prepared holes are then checked in parameter order. This preserves
later default warnings or throws before an earlier hole's callable warning.
Completed default values belong to their real formal cell during suspension.
An omitted/defaulted BYREF formal starts with an ordinary cell rather than an
invented caller reference.

Variadic checks use the actual `EXTRA` or `NAMED` operand and collection position.
Referenced current/future operands remain live, while by-value operands retain
their send snapshots. Class selection and string boundaries remain fixed across
the221 warnings; referenced method bytes are reread. Successful lookup inserts
the current operand value without a second callable check. A callback can replace
the whole current array with an integer that the body then observes. When that
array retires, an authenticated live method alias can still supply the borrowed
historical item receipt; the query adds no container or cell owner.

Failed lookup enters Zend's slow scalar path once. Existing typed reference
sources reject before conversion, including values changed to an exact union
type. The slow parsers do not repeat exact or callable admission. Lossy integer
conversion freezes its numeric input/result across a second deprecation callback;
a normal callback write is overwritten by that result, while a throw/finally
mutation remains uncommitted. Weak string fallback invokes a genuine Stringable
converter even when the replacement object also has `__invoke`. Saved receiving
frames, selected objects and checked reference writes retain their real owners.

The [ledger](../../coverage/semantics/callable-receives-review.json) records
original-source comparisons, independent default/retired-array/throw checks and
author entered-warning/converter checks at their separate cutoffs. Original
compiler, fixture and Unsupported results stay distinct from agreements.
Maintained tests are `callable_receives.py` and `callable_receive_protocol.py`;
the affected221 hole/variadic controls now expect normal completion.

Other internal callable APIs, user-return warning consumers, magic/autoload and
shortened or kind-changing retained method buffers remain required. This slice
does not resume paused return verification or claim complete core. Primary paths
are `ZEND_RECV_INIT`, `ZEND_RECV_VARIADIC` and `zend_handle_undef_args` in vendored
`Zend/zend_vm_def.h`, `zend_check_type_slow` in `Zend/zend_execute.c`, and the weak
parsers and callable resolver in `Zend/zend_API.c`.
