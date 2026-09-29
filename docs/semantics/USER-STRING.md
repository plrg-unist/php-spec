# User object string conversion

The target is the pinned PHP 8.5.10 engine. A source-class `__toString` is
case-insensitive, nonstatic, public and declares no parameters, including
optional ones. Its declared return type may be absent, `string`, or `never`.
An absent return type has the effective `string` contract; its body uses the
defining file's strictness for return coercion. A private or protected method
emits a declaration warning before the Stringable visibility fatal. Invalid
arity and static declaration errors precede that warning; an invalid return
type follows the warning. A valid method makes its class and descendants
`Stringable` without an explicit implements clause. General interface
declarations, including explicit `implements Stringable`, retain the existing
interface dependency.

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

A private eval-operand increment reuses the same owned method call. The operand
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
