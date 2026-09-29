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
