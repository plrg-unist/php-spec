# Source error handlers

This slice targets PHP 8.5.10 CLI NTS 64-bit. Modules206/207/211/215/221 implement
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

Keyword class selectors and qualified array methods use resumable deprecations
at registration and dispatch. Outer keyword choice precedes its warning; the live
array method then determines the inner class and split before the compound warning.
Referenced method bytes are read afterward. Dispatch disables the current handler
before these selection warnings. The new API target authenticates compound
`self`/`parent` selection with a foreign `$this`, while ordinary scoped carriers
retain their existing rules. Requested methods take priority over declared
actual-receiver fallback. Inaccessible fallback methods expose the getter's `Error`
at registration; delayed dispatch replaces it with an `Invalid callback` error
whose previous exception retains the getter error, and restores the raw handler.
[The callable contract](SOURCE-METHODS.md#deprecated-api-keyword-and-compound-callables)
and [221 ledger](../../coverage/semantics/keyword-compound-callables-current-review.json)
describe these stages and their remaining consumers.

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
an owner; rebinding and in-place alias writes remain distinct. Module213 adds six casts, selected value copies and ordinary by-value sends,
retaining selected targets and prior argument owners. Direct ASSIGN also performs
its captured-null destination write after a thrown handler. Module220 adds
rejected constrained writes with unchanged values and caller TypeError/previous
priority; private source/state gates and a current scoped-handler interaction pass.
Other live left operands, read-modify-write, dimensions
and other eligible warning producers remain
explicitly `Unsupported`, rather than running a callback after a consumer.

Weak-null `ini_get` and `ini_restore` are admitted internal producers. Their
authenticated unary continuation resumes once after normal handling or false
fallback; a thrown handler aborts lookup. Weak handler argument conversion,
original-null trace operands, caller arguments and raw INI writes are checked
in the [readback ledger](../../coverage/semantics/include-ini-readback-review.json).
Owned unary CONFIG PIPE also composes with public static method handlers: weak
severity reception, saved caller arguments, original-null traces and throw cleanup
remain distinct from USER strict warnings. Other CONFIG warning producers remain open.

Remaining null/Stringable API conversions and magic/autoload/internal callback forms,
reference-return callbacks and later lifecycle dispatch remain open.
[Exception handlers](SOURCE-EXCEPTION-HANDLERS.md) use a separate uncaught boundary
with one Throwable argument and a nullable raw registration stack.
Frameless named/method trace formatting in164 now accepts the authenticated
nonempty function field. Current property and array-caller readback gates validate these shapes on the
tested private source composition.
`REPORTINGINI` retains full raw bytes separately from the signed32 effective mask;
reporting get/set/Restore and modified-entry state are recorded in the
[reporting ledger](../../coverage/semantics/reporting-ini-review.json). Runtime
`E_STRICT` and lossy reporting conversions use authenticated producer tasks in
[diagnostic ingress217](../../coverage/semantics/reporting-diagnostics-review.json).
Their callbacks save/clear/restore constant evaluator facts while retaining
busy class initializations, selected values and genuine emitting frames. Broader
directives and startup profiles remain separate. Uncaught/fatal reporting outside this slice and
broader global/reference behavior also remain core obligations.

[Dimension keys233](SOURCE-DIMENSION-KEYS.md) stage earlier key-CV and conversion
warnings through read/quiet/nested consumers. Native protection and genuine
temporary owners preserve table COW/retirement, live cells and ordered NaN
notices; throws skip the later write. Source, line, mode, constants and owning
operand forms are checked without reconstructing captured dynamic-value history.
[Writable dimensions242](SOURCE-DIMENSION-WRITES.md) add bounded CV-array W/RW
and direct GLOBALS reference fetches. Native separation/protection, exact-one
table acquisition and delayed RHS demand survive callbacks; named fetch precedes
mapping and promotion. [Coalesce/unset249](SOURCE-DIMENSION-EDITS.md) preserves
direct CV-array quiet memoization/write demand and final unset liveness, including
typed-cell/throwing cleanup and authentic read/write lines.
[Nested unset and append255](SOURCE-DIMENSION-TAILS.md) keeps intermediate table
protection, genuine abort temporaries and the distinct late RHS throw boundary.
[Nested coalesce262](SOURCE-NESTED-COALESCE.md) retains genuine quiet rows,
memoized operands and every late-RHS continuation task; typed-entry rejection
restores the emitter and retains the handler's older exception chain.
[Global W/RW269](SOURCE-GLOBAL-WRITES.md) detaches callback-created constrained
aliases on a returning missing fetch; throws preserve callback writes and skip
initialization and delayed RHS demand. Name conversion remains distinct from
ordinary array-key conversion.
[Container276](SOURCE-CONTAINER-WRITES.md) adds initial W/RW storage and final
array-reference ingress: false protection, consumer-specific post-throw effects
and source-backed typed DIM_OP backing retain native behavior. Wider read/quiet/
memoized/GLOBALS containers and string/object producers remain required.

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
get_called_class() Unsupported source keeps zero agreement. Later
[called-class introspection](CALLED-CLASS.md) has separate source and frame checks;
the earlier static::class observations retain their original scope.

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
[Truth continuations](SOURCE-WARNING-TRUTH.md) retain their historical cast control;
the later [consumer slice](SOURCE-WARNING-CONSUMERS.md) covers its admitted path.

The [consumer213 slice](SOURCE-WARNING-CONSUMERS.md) separately accepts mixed21
normal tuples/control0 and236 conditions, plus independent10/197. Fresh source1/94
and cached-callee source1/96 at181f cover the actual static-reference, outer-array
prepass and cached-callable composition. Grouped model timeouts and the original
copy fixture premise remain preserved. Publication retains later released
reporting, parameter backing and named-class paths with no fresh execution credit.
