# User object string conversion

The target is the pinned PHP 8.5.10 engine. A source-class `__toString` is
case-insensitive, nonstatic, public and declares no parameters, including
optional ones. Its declared return type may be absent, `string`, or `never`.
An absent return type has the effective `string` contract; its body uses the
defining file's strictness for return coercion. A private or protected method
emits a declaration warning before the Stringable visibility fatal. Invalid
arity and static declaration errors precede that warning; an invalid return
type follows the warning. A valid method makes its class and descendants
`Stringable` without an explicit implements clause. The installed source
interface rules also admit explicit `implements Stringable` under their
nominal and method checks.

`zend_std_cast_object_tostring` calls the selected live receiver's method with
no arguments while retaining the receiver. The conversion can mutate state,
reenter, throw, or suspend; it cannot be a synchronous `$stringify` rule. A
normal result is a string after the method's return-type check. Missing magic
still raises `Object of class C could not be converted to string`.

The continuation must authenticate the original conversion source occurrence,
line, selected method and saved caller frame; root the receiver through the
call; and preserve the ordinary method trace. Echo operands convert and output
one at a time. Concat evaluates both expressions first, then converts the
left and right. Weak string parameter, return and property conversions invoke
the callback; strict ones reject the object before the callback. The strictness
of an implicit `__toString` return belongs to the method's own source unit.

The required consumer inventory includes echo, print, `(string)` casts,
concat, interpolation, eval operands, weak typed conversions, dynamic variable
names, string-offset assigned values, `exit`, and object-versus-string loose
comparison. Array keys and dynamic method names reject objects without
calling `__toString`. Interpolation currently lacks a general executable
runtime rule and needs a separate compiler/runtime increment. Internal
Throwable `__toString` uses its own finite trace/property protocol; user
subclass overrides remain a separate dependency.

The first private increment admits declarations and the finite implicit
`Stringable` relation. Until the shared callback continuation reaches a
consumer, user-object `$stringify` is explicit Unsupported. The
[source catalogue](../../tests/semantics/user_string_cases.json) includes
native-accepted Unsupported controls; agreement counts must not include them.

Private Stage A checkpoint `448e60b77` on trace base `8d03ed096` passed the
17-case source catalogue: 10 normal and five static rejections agree exactly;
the explicit interface and echo callback controls remain Unsupported. The
ignored raw report is
`.tools/user-string-conversion/.tools/user-string-8h3do684/report.json`
(SHA-256 `865bf9b8999ab6dc5aeeb44d7e8e6ad6b27692214c0d865b353c34865f8b5244`,
input fingerprint `f0de09cf608b1bb9778b08bf842e7899384544668e700843c65056901b8a42ee`).
An earlier 17-case run failed on three typed relations because two `$typed_object_exact`
clauses overlapped; its retained report is
`.tools/user-string-conversion/.tools/user-string-635sjgan/report.json`
(SHA-256 `5a9909a8f5bd161deb207417588573c5cdf8f267954080d3f7d5e355d7ad87f6`).
The clauses were merged before the passing replay.

The same 17-case selection passed again after rebasing the Stage A code to
installed eval-scope base `f94826254` (private code commit `ab76ee8db`). Its
ignored report is `.tools/user-string-conversion/.tools/user-string-686ma8n3/report.json`
(SHA-256 `330a410a71c2109af0b945631973e710bc351d332d11c1e6aaf50f3445c1801c`,
input fingerprint `b459634b25faffa42e53e2504487555cf4d097cdf96689a472c9cd1551bf119f`).

The next private increment uses one authenticated zero-argument method call
and a saved `STRINGIFY_RESULT` continuation for echo, print and `(string)`.
The receiver remains a heap root until the result is consumed. The call
context, saved caller frame, source occurrence, line and consumer task are
checked together, including reentrant calls at the same site. Print still
returns integer `1`; a cast returns the callback's checked string. An echo
operand that is itself a cast or print is converted by that inner operation,
then emitted by echo. These are the only user-object callback consumers
admitted by this increment; the remaining inventory above stays explicit.

The frozen private 32-source catalogue has 20 exact normal outcomes, six exact
PHP errors and five exact static rejections; explicit `implements Stringable`
remains one Unsupported control. Four source-derived paused stages pass 38
assertions for pending and entered calls, same-site reentry, missing or forged
caller frames, and the restored-result root. See the
[ledger](../../coverage/semantics/user-string-callback-author.json)
for hashes and recovery paths. These reports record the pre-Static A private
candidate.

The Static A integration adds two combined controls: a callback calling its
parent's `__toString` and one calling a static method with an output effect.
The current-base catalogue passes 33 exact outcomes and retains one explicit
interface Unsupported control; the same four paused stages pass. The current
fingerprint and ignored raw report hashes are in the ledger. The bridge
checks the shared scoped-call and implicit-call guards together. This
foundation is installed; the remaining conversion consumers are still open.

The installed eval-operand increment reuses the same owned method call. The operand
keeps its child source occurrence through conversion; a returned string then
resumes the checked eval parser request at the parent occurrence. Both generated
source filenames and callback `eval()` frames use the compiled operand line,
including multiline expressions. An authenticated saved caller frame supplies
the pre-parser `eval()` trace frame when `__toString` throws. A missing magic
method raises the ordinary conversion `Error`, and finite internal Throwable
stringification stays on its separate renderer. The [eval ledger](../../coverage/semantics/user-string-eval-author.json)
records 11 exact source outcomes, one explicit Unsupported weak nested-return
control, five paused stages/51 assertions and three exact included-file bridge
rows on the installed file-trace base. The 71 retained eval rows passed on the
earlier include base; the original failing bridge is retained. Weak typed
conversion of a returned Stringable object requires its own resumable callback;
strict return typing still rejects it before another callback.

The installed concat increment uses the same owned callback. Both operand
expressions finish before either conversion; then the left converts before the
right. A right variable or reference is read after the left callback, so its
new value is visible, while a right temporary retains its evaluated value.
The left and right callbacks use their distinct child occurrences with the
compiled concat line, preventing a saved call from swapping phases at one
source site. Continuation tasks root both operands across nested calls,
validate each phase on resumption and restore the parent occurrence after
completion. Fourteen original-source outcomes, five paused stages/41 assertions
and five ordinary scalar/warning regressions passed on the earlier eval
conversion base. Installed null-resolver included-file callback/throw, focused
source and paused checks also pass. The
[concat ledger](../../coverage/semantics/user-string-concat-author.json) binds
their reports and input hashes. Interpolation and typed string conversion
remain separate increments.

The installed typed-return increment covers weak by-value `string` and
string-admitting union returns, including arrow returns and recursive
`__toString` return checks. A selected live object callback owns the original
receiver until the returned string is accepted. If that callback throws, return
verification creates a `TypeError` before the function's catch/finally search
and links the original throwable as `previous`; each nested weak return adds
its own layer. Strict return checks reject the object before a callback, and
the defining source unit supplies strictness and the return-site line.
Exact nominal `Stringable|string` matches retain the object without invoking
`__toString`. A callable/string union remains an explicit source-`__invoke`
dependency because callable acceptance precedes string coercion. By-reference
returns require a separate alias write-back continuation, followed by weak
parameters, properties and constrained references. A disjoint shared
`$throwable_chain` rule now follows live source Throwable subclasses as well
as internal Throwables; it retains cycle and forged-previous rejection. This
allows both return-error chaining and ordinary finally replacement when a
source subclass is the prior exception. On the Throwable-subclass base, 17 of
19 source cases agree exactly with PHP and two remain explicit Unsupported
controls. Six paused stages pass 71 assertions; four two-file strictness cases,
the repository test and inventory also pass. The earlier subclass-chain
interpreter failure remains in the ledger as the repaired counterexample. On
the installed Closure-binding base, a bound closure's typed return that throws
a source `Exception` subclass also agrees exactly with PHP. On the installed
interface base, a class implementing an interface-declared `__toString` matches
PHP on a weak typed return under a measured 90-second model limit; the generic
45-second runner times out on the interface source. The installed tree passes
the same 90-second bridge, one focused paused return-marker stage and inventory.
The [typed-return ledger](../../coverage/semantics/user-string-typed-author.json)
records the bounded checks and these limits.
