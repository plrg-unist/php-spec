# Source error handlers

This slice targets PHP 8.5.10 CLI NTS 64-bit. Modules206/207/211 implement
`error_reporting`, `set_error_handler`, `restore_error_handler`,
`get_error_handler`, `trigger_error` and `user_error` through the checked source
call machinery. Its bounded private source/frame gates and fresh current-master property,
array-caller and trace interactions are independently accepted.

Registration stores the raw callback and signed32 mask, and pushes the previous
pair even when clearing the callback. Dispatch resolves the raw callback again
and supplies severity, message, filename-or-null and line. Named functions,
closures, public concrete source `__invoke`, ordinary public method arrays and
class-method strings are admitted. Referenced array members are read at dispatch;
later mutation preserves the entered selected target. Copied direct members
still authenticate its method bytes and selector. Malformed arrays and known
public lookup failures preserve ordered PHP diagnostics. Pending callbacks,
the registration stack and entered targets retain their real heap owners.

Class-name API callbacks use the genuine emitting USER frame for compatible
implicit `$this` and called-class forwarding; requested Parent descriptors stay
distinct from an overriding Child. This differs from computed direct method
dispatch. The selected target authenticates against that saved emitter, while
mutable referenced members remain opaque after entry. Static selections retain
no receiver; a raw object-array callback still owns its selector until dropped.
The registry retains raw values, rather than caching an entered target.

Eligibility depends on the handler mask, independently of `error_reporting` or
`@`. The active raw handler is cleared during the callback, allowing an installed
replacement to handle a nested diagnostic. Automatic normal/throw cleanup restores
the old raw handler only if no replacement remains; it preserves the live mask.
Only exact `false` requests default reporting, using the mask after the callback.
Callback `finally` runs before restoration; caller catch/finally runs afterward.

Direct trigger callbacks receive arguments weakly through the internal trigger
frame. Implicit user-opcode callbacks preserve source strictness. Byref callback
parameters receive temporary references to four passed values, with ordinary
default warnings while the original handler is disabled. Trigger traces retain
the converted message and original supplied level. `E_USER_ERROR` first raises
its deprecation; a thrown deprecation prevents the fatal phase. Default fatal
handling exits255 even when reporting is masked. Masked fallback displays nothing;
unmasked fallback displays its fatal diagnostic and captured stack. Fatal arguments
are captured before the callback; later errors clear that snapshot even when
masked. A nonfatal false fallback preserves any inner fatal snapshot, rendering
its stack without adding heap owners. Fatal bailout precedes raw restoration.

Missing-CV read continuations suspend the existing consumer and retain a null
result even if the callback defines the variable. The admitted consumers are
output, simple assignment, unary signs and six arithmetic/identity operators.
Missing-left binaries retain the later right read; missing-right binaries admit
known or temporary values and initially-reference CVs in strict identity comparisons.
Module208 retains the borrowed old cell through the saved caller without adding
an owner; rebinding and in-place alias writes remain distinct. Other live left operands, cast/copy,
read-modify-write, dimensions and other eligible warning producers remain
explicitly `Unsupported`, rather than running a callback after a consumer.

Weak-null `ini_get` and `ini_restore` are admitted internal producers. Their
authenticated unary continuation resumes once after normal handling or false
fallback; a thrown handler aborts lookup. Weak handler argument conversion,
original-null trace operands, caller arguments and raw INI writes are checked
in the [readback ledger](../../coverage/semantics/include-ini-readback-review.json).
Owned unary CONFIG PIPE also composes with public static method handlers: weak
severity reception, saved caller arguments, original-null traces and throw cleanup
remain distinct from USER strict warnings. Other CONFIG warning producers remain open.

Remaining null/Stringable API conversions, compound/scope-keyword, nonpublic,
magic/autoload/internal callback forms,
reference-return callbacks, exception handlers and lifecycle dispatch remain open.
Frameless named/method trace formatting in164 now accepts the authenticated
nonempty function field. Current property and array-caller readback gates validate these shapes on the
tested private source composition.
`REPORTINGINI` records reporting setters; it is not wider INI readback or a new
request-profile initializer. Uncaught/fatal reporting outside this slice and
broader global/reference behavior also remain core obligations.

Primary contracts are `zend_error_zstr_at` in `vendor/php-src/Zend/zend.c`, the
six API bodies in `Zend/zend_builtin_functions.c`, the undefined-CV read helpers
and `zend_verify_arg_error` in `Zend/zend_execute.c`, legacy ZPP conversions in
`Zend/zend_API.c`, and `php_error_cb` in `main/main.c`.

The maintained selection has eighteen normal and five expected PHP-error tuples,
plus one Unsupported ingress control with zero agreement credit. Author eight
fixtures/298 and independent three/240 pass across retained and focused runs;
the independent three normal source comparisons retain their native originals.
Original allocation, fatal-stack, pooled-array, checkpoint and receive-validator
failures remain preserved. Fresh current-master author source2/75 and independent
source1/87 are separate, with no inherited execution credit. The [review ledger](../../coverage/semantics/error-handlers-review.json)
locates the exact revisions, raw commands, exits and mixed evidence. Local tools
are reused; a fresh combined offline rebuild and complete core remain open. The
[method-handler ledger](../../coverage/semantics/handler-callables-current-review.json)
keeps source15/five258 and independent source9/three185 separate from current
PIPE source1/state93, including the preserved failed attempts. Its early
get_called_class() Unsupported source has zero agreement; corrected static::class
observations do not implement that introspection body.

In a private project root with the built local SpecTec algorithmic tool at
`.tools/spectec/bin/p4spectec`, prepare and run the exact report separately:

```sh
python3 -B tests/semantics/error_handler_prepare.py
python3 -B tests/semantics/error_handler_run.py .tools/error-handlers/PREPARED/report.json
```

Use the actual preparation directory for `PREPARED`. The runtime runner checks
the complete maintained selection before optional affected-case filters, records
full streams/exits and stops on the first failure. The ordinary13 profile uses
native45s, model90s and finite300s producer limits, serially; reused local binaries
do not establish a fresh build, offline closure or complete PHP semantics.

Module209 also retains original-null branch, loop, short-circuit, NOT and
ternary-condition choices across handler mutation and throw. Its mixed ordinary
author8/225 and independent native-reused model3/160 remain distinct from PIPE
normal/throw source2 and69/corrected96, and deferred-cache normal/throw source2
and95/89 at `8c74e624`. These gates validate their tested private compositions;
source-equivalent promotion adds no execution or rebuild credit.
The tested211 composition at `38cab574` separately accepts author source1/93
and independent source1/107 across original-null truth decisions and strict
instance-emitter parameter rejection, preserving raw restoration and saved frames.
[Truth continuations](SOURCE-WARNING-TRUTH.md) keep casts/copy/SEND and broader
reporting open.

The private [consumer213 slice](SOURCE-WARNING-CONSUMERS.md) adds casts, selected
value copies and ordinary by-value sends, including direct assignment null writes
through handler throw. Its compiler-only236/197 and native4 characterization do
not yet establish new source/model/state agreement or canonical installation.
