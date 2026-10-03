# Source error handlers

This slice targets PHP 8.5.10 CLI NTS 64-bit. Modules206/207 implement
`error_reporting`, `set_error_handler`, `restore_error_handler`,
`get_error_handler`, `trigger_error` and `user_error` through the checked source
call machinery. Its bounded source/frame gates are accepted privately; the
current-master interaction gates and canonical installation remain pending.

Registration stores the raw callback and signed32 mask, and pushes the previous
pair even when clearing the callback. Dispatch resolves the raw callback again
and supplies severity, message, filename-or-null and line. Named functions,
closures and public concrete source `__invoke` methods are admitted. Malformed
callback arrays preserve Zend's ordered shape errors; method-resolution errors
and array callback dispatch remain explicit pending boundaries. Pending
callbacks and the registration stack retain their real heap owners.

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
Missing-left binaries retain the later right read; missing-right binaries require
a known or temporary left value. Live/reference left operands, truth/cast/copy,
read-modify-write, dimensions and other eligible warning producers remain
explicitly `Unsupported`, rather than running a callback after a consumer.

Null/Stringable API conversions, broader internal/array/visibility callback forms,
reference-return callbacks, exception handlers and lifecycle dispatch remain open.
Frameless named/method trace formatting in164 now accepts the authenticated
nonempty function field. Current property and array-caller readback gates remain
pending before installation.
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
failures remain preserved. New current-master interaction checks are separate,
with no inherited execution credit. The [review ledger](../../coverage/semantics/error-handlers-review.json)
locates the exact revisions, raw commands, exits and mixed evidence. Local tools
are reused; installation, a fresh offline rebuild and complete core remain open.

From the private project root, prepare and run the exact report separately:

```sh
python3 -B tests/semantics/error_handler_prepare.py
python3 -B tests/semantics/error_handler_run.py .tools/error-handlers/PREPARED/report.json
```

Use the actual preparation directory for `PREPARED`. The runtime runner checks
the complete maintained selection before optional affected-case filters, records
full streams/exits and stops on the first failure. The ordinary13 profile uses
native45s, model90s and finite300s producer limits, serially; reused local binaries
do not establish a fresh build, offline closure or complete PHP semantics.
