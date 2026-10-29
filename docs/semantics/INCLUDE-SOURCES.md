# Include/require source boundary

The default PHP 8.5.10 CLI profile starts with `include_path=.:`. Explicit
registered startup inputs can supply a different initial path. The finite
file snapshot is explicit input to a semantic run. It contains the canonical
main script path and initial CWD. Version 1 has unique `(caller filename,
requested operand bytes)` entries under the fixed profile; version 2 keys
each entry by those bytes plus the captured CWD and `include_path`. Each entry is
either `missing` with a stream-error fact, `open_failure` with a successfully
resolved path, first-warning display path and stream-error fact, or `opened`
with a successfully resolved path or a null resolver result, opened canonical
path, and original file bytes.
Unknown keys are `Unsupported`; they are not modeled as missing PHP files.
Distinct entries naming one opened path must have identical bytes. The opened
path is a trusted, authenticated snapshot fact, separate from the display
filename and the parser's temporary file.
The warning display path and stream-error bytes are explicit finite
OS/stream-open facts supplied by the snapshot; the parser and model do not
derive them from Zend execution. An already included resolved path skips before
those failure facts produce a warning.

An embedded NUL in the converted path fails locally before file-provider or
dynamic-parser requests, nonce allocation or once lookup. Include and include_once
emit one final warning and return false; require and require_once throw `Error`
directly. The message uses the C-string prefix with URL credentials stripped and
captures the effective include_path before handler entry. Handler path writes
persist without changing that message. Even an already included main-prefix path
does not skip this failure; a leading NUL differs from an actually empty ordinary
include/require operand, which raises `ValueError`.

The local descriptor retains the full requested bytes and authenticates its
source, kind, line, caller scope and task suffix without adding a heap owner.
It does not reconstruct arbitrary evaluated bytes from syntax. File contexts,
source units and included identities remain unchanged. Captured/conversion
`SOURCE_OPERAND_RELEASE` tails and an unavailable include_path are explicitly
Unsupported here. Eight NUL originals, two empty regression controls and five
reached fronts/208 premises retain separate cuts in the
[NUL-path evidence](../../coverage/semantics/source-nul-path-review.json), including
a throwing handler's real keyword frame and a genuine temporary-owner refusal.

[Recorded compiler diagnostics](../../coverage/semantics/file-compile-notice-review.json)
precede opened-path registration for ordinary `include` and `require`. The once
forms register before compilation. A warning-handler reentry through the same
canonical path therefore executes `include_once` during an ordinary outer include,
but skips during an outer once form. With no queued diagnostics, ordinary
registration still precedes body execution.

An authenticated notice owner in the current or saved caller permits that delayed
ordinary registration. Normal delivery, handler throw and graceful exit finish it
once, preserving any inner registration. Remaining eligible callbacks are skipped
after throw or exit; ineligible diagnostics retain their ordered default delivery.
A hard fatal retires the context without finishing ordinary registration. Compiler
history replay validates recorded diagnostics without invoking the live handler.
The finite provider and broader dynamic-source obligations remain partial.

[Stringable file operands](../../coverage/semantics/file-operand-review.json)
run the ordinary checked `__toString` callback before resolution, once checks or
provider creation. Conversion retains its receiver after global rebinding;
normal return restores the authentic include parent and samples live CWD/path.
Throw and invalid conversion complete without demanding file facts or allocating
a provider nonce. Pre-parser conversion/warning frames retain the compiled operand line and zero
arguments; executed included-unit frames retain their opened-path argument.

[Array operands287](../../coverage/semantics/source-array-review.json) dispatch
`Array to string conversion` before eval parsing, file resolution and once checks.
Normal callbacks leave the selected bytes fixed as `Array`, even if they replace
the source operand; throw creates no provider nonce. Conversion traces use the
authentic child site and zero arguments. Borrowed CV inputs gain no array root,
including absent or mask-ineligible handlers. Captured inputs retain their sole
owner through provider, parsing and compiler notices, then release it before a
nontrivial included body or parser-error catch search. The context's saved tail
does not retain a second owner after that boundary.

Four destructor-free originals agree and 73/60/45/29 state premises pass.
Parser-rejection helper states use the existing production allocation-pruning
boundary to register ParseError handles; this is not an extra reached VM step.
Maintained tests are `source_array_sources.py` and `source_array_protocol.py`.
The original destructor lifetime witness also agrees in the separately reviewed270
composition. Selected Stringable/undefined ingress, fast helper results and source
retirement traces are installed below; broader producers/providers remain required.

[Stringable sources298](../../coverage/semantics/source-stringable-review.json)
keep the original input owner separate from the cast receiver. Borrowed CVs add
no owner; captured objects and reference-cell contents survive compiler notices
until their authentic release. Returned bytes stay fixed when __toString rewrites
the CV or reference cell. If releasing its receiver throws after a successful cast,
eval still compiles and publishes while preserving that Throwable; an ordinary
empty include raises ValueError with it as previous, while eval/once retain it.
One original and three explicitly named unpromoted/direct-call companions agree,
and37 reached pending/parser-await premises pass. The original promotion cases
remain required core with zero agreement; the function_exists observer is outside
CORE. Maintained source/state helpers accept --semantic-root for the frozen private
cut and default to the repository after integration. Its broader parser/provider
and compiler-emission obligations remain required.

The [separate ordering cut](../../coverage/semantics/source-stringable-ordering-review.json)
selects a sole implicit return from authenticated formal compilation, rather than
AST statement count. Early functions and unused compiled constants, including
arrays and literal strlen, emit no body operations; explicit return and count
take the regular path. Fast include copies1 before captured operand destruction.
A destructor throw then survives assignment/echo until selected C-helper checks;
reporting writes occur before propagation. Eligible warnings skip their handler
and default output while ineligible warnings keep default output. Type/value
argument errors preserve the pending object; arity errors allocate and chain it.
Immediate pending eval compiler fatals preserve the same Throwable and authentic
destructor/keyword trace. Twelve exact comparisons (7 originals/5 direct-call
companions) and42 reached ownership/public-entry/record checks pass. Maintained
ordering source/state helpers default to the integrated repository; --semantic-root
selects the retained private cut. Additional emissions, checkpoints and wider
provider/parser behavior remain required.

The [helper return cut](../../coverage/semantics/source-stringable-helper-review.json)
copies false after empty eval/failed include and true after once skip before
captured operand destruction. A throw then survives assignment/echo until the
reporting helper executes its write and propagates it. The captured helper context
retains its phase, nonce and selected included path; HELPER selects a no-unit
record with canonical unused UNIT0. Three original sources and a separate42 reached
public/heap/ownership/context checks pass. Original41 false remains preserved because
its supposed missing path was the main script, already included at startup.
Maintained helper source/state tests default to the repository after integration;
relocation preparation adds no runtime credit.

The [final-release trace cut](../../coverage/semantics/source-stringable-retirement-review.json)
installs the first authenticated compiled constant-return operand before ordinary
source cleanup. Destructor traces use the actual emitted opcode line: a simple
return, multiline literal and folded binary expression retain distinct child
lines. Their entered include frame keeps its genuine filename argument. Fast
source cleanup instead uses the main keyword location and a zero-argument frame;
completed empty-eval, once-skip and failed-include helpers preserve that wrapper
after their provider context retires. Seven exact original-source comparisons
pass. A separate98-premise fast admission gate authenticates the copied value,
caller, live operation and continuation; corrected empty-eval helper78 also passes.
Original43 false and helper fixture stops retain zero credit. Wider first-emission
forms, helpers/providers and exception
checkpoints remain required. The [first-work extension](../../coverage/semantics/source-stringable-first-work-review.json)
adds the first constant ECHO operand line and the restored lhs line of a
assignment to a literal variable name with a constant, effect-free RHS. It includes
auto-global variable names while excluding `this` and `GLOBALS`. An early
non-op declaration is skipped only by the existing no-runtime-work predicate.
Three exact originals pass (include ECHO5/assignment4 and eval ECHO2); reached
entry46 also passes with genuine compilation/public/heap and malformed
code/history/owner/suffix controls. The original fixture stop retains zero credit.
Other first-work forms preserve the existing entry origin
and remain required.

[Undefined operands293](../../coverage/semantics/source-undefined-review.json)
dispatch the genuine variable warning before eval/file conversion. A direct CV
returns the fixed uninitialized null value even when the callback defines,
replaces or deletes that variable. The continuation borrows its source storage;
it adds no object or array owner. Direct callback traces retain the compiled
operand line and zero-argument keyword frame. Completed computed names retain
their effects, including embedded NUL bytes; their missing-variable fetch runs
before the keyword and has no pre-parser keyword frame.

Ordinary include/require reject the resulting empty path before any provider
request. They do so even when the direct warning handler throws, creating
`ValueError("Path must not be empty")` with the handler exception as previous.
Eval and once operations preserve the handler exception. A computed-variable
fetch that throws never reaches the keyword. Normal empty once operations still
use finite open-failure facts. The maintained source and state suites distinguish
the original trace-printing private source, whose full model run timed out, from
the separately compared 76-line `private-state.php` companion; only its four
trace-printing loop lines are blank. Missing computed-name producers remain
explicitly Unsupported, and wider dynamic sources remain required.
The separate275 composition agrees on that Array original and a fresh handler
object-retval cleanup source. Its admission correction projects only the genuine
saved caller and pairs destructor receiver/site/line with the actual frame;
35 reached positive and malformed controls pass without renewing either source.

The [actual Generator/source composition](../../coverage/semantics/include-source-composition-review.json)
runs undefined eval and a captured coalesce include under active nested delegation.
The Stringable callback clears the actual aliased operand cell; its captured input
survives until entry into the compiled child. An early declaration emits no body
work, so ordinary release uses the first constant ECHO operand's child line5 while
the include wrapper retains main keyword21 and its genuine filename argument.
Strict284 compilation and one exact original agree. A separate 49-premise reached
cut preserves every Generator frame, public/heap admission and the saved caller,
and rejects heap-valid forged provider-owner and missing-body suffix states.
The two explicit maintained selectors preserve older default campaigns; relocated
source/provider construction prepares the same 49 premises with zero evaluations.
Earlier private cuts gain no renewed execution credit.

Failed-open warnings suspend for eligible handlers. The stream message is fixed
before the first callback; the second include warning or required `Error` samples
the live effective path after that callback. Throw skips the remaining failure
phases. Reentrant includes keep the saved warning owner, and normal, throw, exit,
fatal and compiler-stop cleanup retire it at the actual task drop. Fifteen exact
source agreements and 81/148/45 state premises retain separate tested cuts in the
ledger, including shutdown cleanup and active-eval trace composition. Original
count/interpolation observer failures remain preserved with zero full agreement;
interpolation and wider provider/source contexts remain required work.

`parse-file` has a separate checked request from `parse-eval`: request nonce,
file mode and raw CLI profile, requested/resolved/opened identities, and bytes.
The local native extension parses file syntax only. The worker then imports a
PHP-Parser AST; it supplies neither execution results nor filesystem answers.
Native `ParseError` and exact base `CompileError` retain kind, message and line.
The adapter checks resolution against the immutable snapshot before resuming
the machine. A second parse pause only occurs after a newly opened file is
selected. A skipped `*_once` call consumes its request nonce without creating a
new source unit.

Zend's `zend_include_or_eval` checks a successfully resolved path against
`EG(included_files)` before opening it, then checks the opened path and records
that identity before compiling a new `*_once` file. Ordinary include/require
record the opened path after successful compilation. The initial executed
script is already included. The bounded execution rules cover successful file
returns and fallthrough, nested includes, once skips, and finite open failures.
File parser rejection retains a failed source unit and raises a catchable
`ParseError` or base `CompileError`; a static compiler fatal in an accepted file
stops compilation globally. The [source and paused-state ledger](../../coverage/semantics/include-source-author.json)
records the current finite-provider gates and their exact scope.

While a compiled file runs, its authenticated file context contributes an
`include`, `include_once`, `require` or `require_once` Throwable trace frame at
the caller site. The frame's argument is the opened canonical path when an
inner frame precedes it; Zend omits the argument when that file frame leads
the trace. Active file and eval units interleave by fresh source ID within a
call frame, while saved call frames retain their stack order. The
[trace ledger](../../coverage/semantics/include-trace-review.json) records
the direct, nested, caught and prefixed-error checks.

An authenticated null resolver result has no identity for the pre-open once
check. The machine opens the file, then checks its canonical opened path for a
once skip. The bounded source witness uses the identity-transform
`php://filter/read=/resource=...` wrapper: its resolver result is null, while
the opened path, `__FILE__`, and include trace refer to the underlying file.
The [resolver-null ledger](../../coverage/semantics/include-resolver-null-review.json)
records the source, pause and adapter comparisons. Other wrappers and stream
transformations need their own facts and source comparisons.
The [directory failure ledger](../../coverage/semantics/include-open-failure-review.json)
records exact relative and absolute directory observations, including their
different stream-error bytes. This bounded extension is installed.
The installed mutable-context increment records CWD and `include_path` at each
resolution pause. `set_include_path`, `ini_set('include_path', ...)` and
`ini_restore('include_path')` update the live INI value after argument binding.
`chdir` uses a separate one-shot finite OS fact: success supplies a canonical
next CWD; failure supplies `strerror` bytes and errno, while PHP warning
rendering remains authored semantics. A compiled file retains its original
lookup context even after a nested call changes the globals. Once membership
continues to use canonical opened paths. The [mutable-context ledger](../../coverage/semantics/include-mutable-context-review.json)
records the bounded source and paused checks. Wider OS/INI behavior remains
open. Other permission and path errors need source comparisons.

Computed string calls and pipes to `set_include_path`, `ini_set`, `ini_restore`
and `chdir` record the selected intrinsic before evaluating arguments. A
monotone selection nonce is checked across saved
frames and the `chdir` provider pause. Direct calls, fixed pipes and owned
first-class closures retain their existing provenance. The [selected-call
ledger](../../coverage/semantics/include-dynamic-selected-review.json) separates
the historical 35-source catalogue from the projected four-source/nine-stage
bridge and one current reference-return interaction. Broader callable forms
remain open.

The installed Stringable increment runs a weak positional operand's checked
`__toString` callback before requesting a directory fact, using the CWD after
the callback. Strict direct/first-class calls and non-stringable operands raise
`TypeError` before the callback; returned NUL bytes raise `ValueError` before
an OS request. That error's inner `chdir` frame contains the converted string,
while an explicit `Closure->__invoke` frame retains the original object.
Callback throws retain the declaring class and original method spelling,
the intrinsic and explicit invocation frames across nested calls.
The [Stringable ledger](../../coverage/semantics/include-stringable-chdir-review.json)
separates the projected full catalogue/protocol/retained gates from three installed
sources and one directory stage/52 assertions.
The installed named increment admits exactly `directory:` for the callback and
directory pause, including computed and owned callable forms. Unknown,
duplicate and count errors precede conversion; explicit `Closure->__invoke`
keeps weak conversion from a strict caller. Its
[ledger](../../coverage/semantics/include-named-current-review.json) separates
installed author source17/four185 and independent source2/two89 from earlier
private calls-base and c8 evidence. Live-object ownership, saved operands and
exception cleanup have separate paused-state checks.

The installed [unpack increment](../../coverage/semantics/include-unpacked-current-review.json)
captures array entries before later arguments can change referenced cells or
retire the source array. Active array identity, keys, cursor and consumed prefix
remain exact. Completed certificates borrow captured values without adding
heap roots; historical array IDs and integer-key numbers are documentary.
Installed checks accept author source23/six208 and independent fresh
source2/two139. The ledger preserves earlier private evidence, its original
active fixture failure and corrected state checks separately. Wider OS/INI
behavior and Traversable operands remain open.

The bounded [installed Stringable SET increment](../../coverage/semantics/include-set-current-review.json)
runs authenticated weak conversion before reading the old live `include_path`.
A nonempty NUL-free result installs the value and returns the old value after
the callback. Empty results return `false`; NUL raises `ValueError`. Both preserve
callback-installed INI state. Strict direct/first-class calls and non-Stringable
operands reject before the callback; owned `Closure->__invoke` retains weak
conversion. `ini_set` rejects an object value before option lookup or mutation.
Source and paused-state checks separately bind the captured receiver, owner,
saved operand and abrupt cleanup. Installed author checks cover source24/four107
and shared source3/directory1/81, with six separate Unsupported controls.
Independent source2 tuples were recovered unchanged; fresh owner79/finally50
checks and original raw audits complete the bounded installed gate.
The earlier installed SET checks use NUL-free old INI values. The current
[raw/effective prefix implementation](../../coverage/semantics/include-ini-prefix-review.json)
retains full raw `FILEINCLUDEPATH` and scalar `ini_set` old returns.
File request capture, pending/phase guards, diagnostics and both SET old
returns use the C-string prefix. Leading-NUL scalar INI updates return
`false` without mutation; nonempty prefixes permit raw interior-NUL storage.
Suffix-only equivalence applies to pending file requests; raw INI equality
remains exact. The public object invocation union accepts 13 original sources
(ten normal, three expected PHP errors) and thirteen finite fixtures/675
assertions at `6e7ddca894` on `6ba0ee71/1305`. Root, method and inherited
captured-call file guards bind actual owner, receiver, declaring lexical class,
called class and retained capture. Earlier private `8a9f0c789` source18/finite377
evidence stays distinct.
The [Stringable Restore increment](../../coverage/semantics/include-stringable-restore-review.json)
converts weak option objects through ordinary checked callbacks. Lookup compares
the full converted bytes: exact `include_path` resets the initial raw value;
empty, case and NUL-name misses return null and preserve callback mutations.
Direct strict calls reject objects; owned internal `Closure->__invoke` remains
weak. Source-site, invocation owner and child-line authentication survives both
paths. Original `b33f42f080` accepts 34 source tuples and thirteen finite
fixtures/524 assertions, with 28 other-directive Unsupported checks separate.
Two callable-priority sources on `240bf5a75` and two current ARG sources on
`88f8d2bd5` are separate fresh checks. The latter preserves the caller's two arguments
and fixed vector across a callback with zero arguments and an empty vector.
The original AL fixture type failure is retained; current 185-module SL
compilation passes with reused executables. The raw-readback increment below
adds the shared primitive/null option parser.

The [two-slot INI increment](../../coverage/semantics/include-stringable-ini-option-review.json)
binds normalized `option` destination0 independently of written named/unpacked
argument order. Weak scalar/Stringable options convert before array/object value
rejection and full-name lookup. Strict direct calls reject non-string options;
explicit `Closure->__invoke` calls parse weakly. Weak null options deprecate before value validation. A valid `include_path` update
returns the full raw old value sampled after the callback. Null, empty and
leading-NUL values return false without mutation; valid interior-NUL values retain
all bytes. Option-name matching remains full-byte, independent of the effective
file-path prefix. The reporting increment below adds a second directive;
other real INI directives remain explicitly Unsupported.
Current SENT object/array values remain live roots; retired completed PACKS are
historical certificates. Current compiler/property composition `8cc6d7da5`
accepts three normal sources and one full83 state fixture. Earlier `35fb2e410`
author49/finite494 and independent source2 retain separate identities, as do the
failed81/83 fixtures. Wider OS/INI behavior and lifecycle remain open.

The [raw-readback increment](../../coverage/semantics/include-ini-readback-review.json)
returns full raw bytes from `get_include_path()` and exact-name
`ini_get('include_path')`; SET returns and file requests keep their effective
C-string views. Weak Stringable getter options run ordinary callbacks before
reading the live raw value. Empty, case, NUL-name and converted primitive
misses use full-name lookup and return false. The reporting increment below
adds a second directive; other names and missing include-path environment
remain Unsupported.
The same option parser now handles primitive/null Restore calls: strict direct
calls reject non-string options, explicit `Closure->__invoke` calls parse weakly, and weak null
deprecates before lookup. Argument binding/arity errors preserve evaluated side
effects without converting rejected extra operands. Current inherited array
calls and captured clones preserve caller arguments through zero-argument
callbacks. The ledger separates the original ten source passes and rule-overlap
failure from the corrected current composition; runtime/compiler binaries are
reused, without a fresh rebuild claim.

The [reporting increment](../../coverage/semantics/reporting-ini-review.json)
returns complete `error_reporting` INI bytes and parses its C-prefix using the
pinned signed64 `strtol`/low32 boundary. Scalar/null `ini_set` values preserve
empty and NUL bytes, while `error_reporting()` reads the live signed32 mask;
setting the existing mask leaves the raw bytes unchanged. When `@` removes
nonfatal bits, it marks the entry modified without changing its bytes; Restore
resets only a modified entry.
Handler writes can leave raw bytes distinct from the mask restored at silence
exit. Exact scalar options work without file facts; Stringable options retain
authenticated callbacks and late old-value sampling. Twelve normal sources
across two revisions and 74 conditions are accepted. Fifteen nondeprecated
error constants are admitted; the diagnostic increment below adds `E_STRICT`
and handled lossy conversions.

The [startup increment225](../../coverage/semantics/startup-ini-review.json)
accepts registered `error_reporting` and `include_path` bytes before compilation.
The original `bin/php-semantics FILE --startup-ini INPUT.json` entry takes those two keys:
canonical base64 strings, with JSON null also permitted for `error_reporting`.
These are effective registered values: native CLI `-d` expressions have already
been evaluated. Null reporting starts with mask30719; a present empty string
starts with mask0, though both raw getters return empty bytes. Restore returns
the original startup value only when the reporting entry is modified. Silence
can leave an unmodified original raw value with a different live mask; a later
Restore remains a no-op.

Known INI values do not imply known CWD. Stringable INI conversion works with
explicit startup facts alone; CHDIR and file requests still require authentic
directory facts. A file snapshot must use the startup path's C-string prefix.
Nine exact profile comparisons include callback/silence mutation and a genuine
finite include after nondefault path Restore; 99 state and 15 transport controls
authenticate all four ordinary/request/file entry variants. Wider startup
directives, INI parsing/profiles and request lifecycle remain required.

[Live display237](../../coverage/semantics/display-errors-review.json) also accepts
`display_errors` alone, or with the reporting/path pair; its value is canonical
base64 or JSON null. Absent display input retains the baseline raw `stderr`; explicit null
selects stdout and a present empty string selects off, though both getters return
empty bytes. Null is a source-defined control, without a native CLI NULL claim.
Full case-insensitive names precede decimal-prefix/uint8 decoding. Setters preserve
full bytes and sample the old value after Stringable option conversion; Restore
uses the original nullable entry only when modified. Display-only file entries
seed the baseline `.:` path, while ordinary/request entries keep file facts unknown.
Ordinary diagnostics capture their live destination after handlers and retain
output order through later mode changes. Eleven exact comparisons, 76 state
premises and 17 transport controls cover these routes and eval/include retirement.
The held shutdown fatal source also agrees after actual231 composition, with
destination frozen after rendering and before the queue. Its distinct cut remains
in the [shutdown ledger](../../coverage/semantics/shutdown-functions-review.json).
Wider display/configuration stays open.

[Precision272](../../coverage/semantics/precision-review.json) adds an optional
base64 `precision` key, alone or alongside display and the complete reporting/path
pair. It supplies effective registered bytes, so a rejected native startup `-2`
corresponds to the registration fallback 14; JSON null is rejected. Runtime setters
retain raw spelling, sample the old value after option callbacks and mark modified
even when a negative update fails. Restore changes only a modified entry.
Main, eval and opened file units capture effective precision before parsing;
accepted and rejected histories retain it after live writes. File/request wrappers
keep their existing path/CWD distinctions. Sixteen exact comparisons, 194 supplied
state checks and 12 transport controls retain their original cuts. Later genuine
suspended-eval resume epochs preserve compiler conversion precision and exact
image refresh separately from parser creation; their source/state cuts remain in
the same ledger. Array warning continuations are covered by287 above; wider
configuration, source lifetime and provider behavior remain required.

[Diagnostic ingress217](../../coverage/semantics/reporting-diagnostics-review.json)
fetches `E_STRICT` at runtime and dispatches its deprecation through the genuine
206/207 handler continuation. Namespace shadows retain ordinary lookup priority;
the selected 2048 survives handler declarations. Recursive reads of the protected
constant avoid another diagnostic until the pending fetch retires. Defaults and
class constants cache only successful evaluation. Saved frames retain and restore
their constant facts while callback execution uses its own lexical evaluator;
the global class-initialization stack still protects active work.

Lossy float/numeric-string `error_reporting` arguments convert to long before
dispatch. A returned handler leaves the converted integer unchanged; the setter
then samples the live old mask and preserves raw bytes when the converted long
equals that live signed32 mask before narrowing.
A thrown handler prevents that update, retains its own writes and preserves
original arguments in internal/wrapper traces. Compound initializer diagnostics
and thrown constructors retain their separate expression and fetch locations,
including the synthetic constant-expression frame when needed.

Fourteen author and four independent normal-source agreements plus 211 state
conditions retain their distinct tested revisions and original failures. Current
210-module compilation and one scoped private-handler/backing-receive/class-name
source comparison establish the added branch composition separately. Executables
are reused; these earlier results retain their original cutoffs.

[Compound initializer eval locations](../../coverage/semantics/compound-eval-location-review.json)
capture the filename-owning class, genuine constant/default declaration and
current AST child when eval requests parsing. The child's line comes from compiled
source metadata; eval's actual call site and lexical class remain separate.
The saved source identities authenticate later bindings after initializer retirement,
including rebound Closure defaults whose filename owner and child occupy different
units. Plain nested constant fetches retain the outer compound override. Inherited
static defaults use their declaring property owner, preserving the requested table
class and original trace location. Raw private handlers use the emitting user frame.

Genuine parser/preflight ParseError and CompileError allocations use their failed
unit's filename and line; ordinary runtime exceptions, including user-created
ParseError, keep the active execution override. Five original source agreements and
81 controls retain distinct cuts; one current static-default/private-handler source
and 214-module compilation validate that composition separately. The compiler prefix
retains static-fill ordinals without importing property values as class constants.
Wider initializer/callback and compile-warning consumers, INI/startup profiles,
warning producers, OS services and lifecycle remain partial.

Eligible weak-null `ini_get`/`ini_restore` deprecations now suspend through
`CONFIG_INI_NULL_RESULT`. Handlers receive four values weakly; normal handling,
false fallback under suppression and a thrown handler preserve raw mutations
and saved caller arguments. Internal traces retain the original null operand.
The new validator rejects missing source code before reading strictness. Fresh
source2 at `cf7ebe4e` and corrected61 plus independent throwing1 at `f406e96f`
are distinct from getter17/134. Their getter rules compose unchanged with
current setters; 198-module compilation adds no semantic execution credit.
Other producer continuations remain open.

The [two-slot NULL-option follow-up](../../coverage/semantics/ini-set-null-option-review.json)
extends the same marker to ordinary positional `ini_set(NULL, value)` with quiet
primitive values: NULL/bool/int, non-NaN floats and authenticated INTERNED/REQUEST
strings. Source facts authenticate immutable arguments without inventing mutable-CV
history. The returning handler preserves its precision8/live writes before empty-option
`false`; the throwing handler preserves sameException/caller99/sibling2003 and cancels
the body. Strict reception keeps raw NULL/value in its TypeError trace before any
handler. Actual handler traces retain raw NULL and the captured REQUEST value.

Four exact originals retain author3 at `fcac3d863`/`a5ee611ba` and corrected peer1 at
`d4ca9022f`; 623 premises (111+178+113 author,221 independent) pass at the corrected
cut. One default Deprecated is expected; other source PHP stderr and accepted
CLI/SL worker stderr are empty. Ten stable/reaped reports include the preserved
peer interpreter failure with zero credit: a redundant new trace head overlapped
existing module368 INI_SET projection. Removing those three lines reuses the exact
raw projection; accepted author models/native/baseline are not replayed. Owning,
NaN/legacy-string values, packed/PIPE and wider configuration remain partial;
named and retained positional owner forms have separate increments below.
Existing unary rules, source/service boundaries and paused work stay intact.

The [named NULL-option increment](../../coverage/semantics/ini-set-named-null-option-review.json)
removes only the NAMED exclusion from that quiet-value continuation. Existing source
prefixes authenticate named layout and map written argument indexes to normalized
parameter destinations. Actual partial CONFIG_ARGS after `value:` retains its REQUEST
at destination1 while option0 is still a hole; later `option:` effects fill only option0.
Literal reversed and mixed positional/named calls use true handlers. A selected
false handler adds one default Deprecated before the empty-option false result,
preserving precision8. A supplied throw preserves sameException99/precision10/sibling2053
and cancels the body; strict NULL rejects after both effects with handler0.

Four originals and 746 premises (238+159+96 author,253 independent) pass at
`13f605b1f`/`a46b790e0`/405. All nine reports pass on first attempts, are stable/reaped
and have no timeout/interruption/survivor; accepted worker stderr is empty. Only the
selected false-handler source has default PHP Deprecated output. Initial `fb753d7fe`
native/baseline CPU3 remains distinct from later CPU2; baseline Unsupported after
B|V|O| has zero agreement. Old positional623 source-prefix refusals remain valid
without replay. The quiet value boundary stays unchanged. Packed forms beyond the
bounded follow-ups below and PIPE remain partial; retained owners are covered below.

The [retained intrinsic NULL-option increment](../../coverage/semantics/ini-set-owned-null-option-review.json)
adds a disjoint owner-present positional arm to the same validator. Existing source
authentication requires a live `INTRINSICCLOSURE INTRINSIC_INI_SET`; a retained keep
alias preserves it when value effects replace the live callee with an INI_GET Closure.
Ordinary invocation follows caller strictness, while explicit `__invoke` is weak.
Normal true/false handlers preserve captured NULL/value and precision changes before
the false result. A thrown handler preserves Exception identity/caller99/precision10/
sibling2099 and cancels the body. The original setter remains callable afterward.

Four originals agree and 782 premises (161+155+183 author,283 independent) pass at
`5b53c02b0`/`85d287934`/405. The actual peer Exception has handler/ini_set/__invoke/
caller frames and identical raw REQUEST arguments in the API and wrapper frames;
peer native deliberately avoids trace traversal. Owner roots, complete throwing
discard, strict raw-option priority, source/carrier/owner-kind/count refusals and
zero/split budgets pass. All nine reports pass first attempts, stable/reaped with
no timeout/interruption/survivor. Default Deprecated lines8/18 are expected; other
PHP stderr and worker stderr are empty. Initial `9d082a173` CPU5 native/baseline
stays distinct from later CPU2; producer-continuation Unsupported after B|V| stays
zero credit. Only ten module172 lines are added; ownerless/unary/368 trace/root/
discard helpers stay exact, with no old623/746 replay. Packed/PIPE,
sole-owner retirement, owning/NaN/legacy-string values and wider configuration
remain partial; paused work is untouched.

The [named retained-owner increment](../../coverage/semantics/ini-set-owned-named-null-option-review.json)
removes only the owner-present arm's NAMED exclusion. Reversed `value:` then
`option:` evaluation keeps the selected INI_SET owner and REQUEST value while live
callee/option/value writes occur. Actual partial CONFIG_ARGS has destination0 empty
and destination1 captured before later option effects; completing the call fills only
option0. True handling reaches false, false handling adds default Deprecated, and
a supplied throw preserves Exception identity/caller99/precision10/sibling2131 while
cancelling the body. The retained original setter still works after the throw.

Native confirms numeric normalized `__invoke` arguments before the change. Four
source comparisons retain `3563cd099`/`4f7c217d5`; 928 premises (248+170+189 author,
321 independent) pass at `64c24d775`/the same runtime/405. Full four-frame trace,
carrier identity, exact throwing discard, strict ordinary versus weak explicit
mixed calls, source/name/owner/count controls and zero/split budgets pass. Initial
`cc6e09523` native4/baseline on CPU2 stay separate from final CPU3 state checks.
Thirteen stable/reaped reports retain two failed author fixtures at zero: explicit
optional-name bindings fix the first type constraint; the second whole-state finish
expectation now includes the exact existing GC buffer update when the owner task
root is consumed. Shared64 and runtime GC remain unchanged. No accepted source,
native or old782 actor repeats. Only selected default Deprecated line24 is expected;
other PHP stderr and accepted worker stderr are empty. Packed forms beyond the
unpack follow-ups below, PIPE, sole-owner retirement, owning/NaN/legacy-string
values and wider configuration remain partial.

The [numeric unpacked retained-owner increment](../../coverage/semantics/ini-set-owned-unpack-null-option-review.json)
adds one disjoint NULL2 admission arm for a sole numeric two-item pack. Completed
pack entries are historical snapshots: callback mutations of the retained source
array cannot replace earlier NULL/value arguments. Numeric keys3/7 normalize to
API and wrapper slots0/1. Active unpack retains the array; the completed certificate
adds no array root. Immutable compiled facts authenticate literal contents, while
unknown helper/CV captures retain structural source authority without invented
history checks. Ordinary strict reception and weak explicit `__invoke` stay exact.

Four source comparisons and author584 premises (204+173+207) retain `35aa840bc`/
`bbde7c32c`/405; peer330 passes at `dc8798c3b`/the same runtime, totaling914. Actual
unpack cursors, owner roots, four-frame raw REQUEST trace, full throwing discard,
callback pack mutation, returning false/default delivery, retained setter recovery,
source/carrier/count refusals and zero/split budgets pass. Native peer observes
only numeric wrapper arguments; state checks prove carrier identity and full trace.
Initial `a3a17aa48` CPU3 native4/baseline0 precedes implementation; later checks use
CPU2. Eleven stable/reaped reports retain one pre-main peer binder failure0, fixed
only by extracting the snapshot before destructuring its carrier. Source4/author584
are not replayed. Default Deprecated lines7/20 are expected; other PHP and accepted
worker stderr are empty. Existing continuations, traces, roots, discard and GC stay
unchanged; one array-comparison declaration moves from400 to172 before first use.
Multiple packs, PIPE, sole-owner lifetimes and owning/NaN/legacy-string values remain
partial; old623/746/782/928 cuts and paused work are not renewed.

The [named unpacked retained-owner increment](../../coverage/semantics/ini-set-owned-named-unpack-null-option-review.json)
adds a separate NAMED arm for one two-item named/mixed pack, preserving the numeric
arm. Inline array construction stores the earlier REQUEST after V and before O;
both effects finish before unpack begins. Reversed keys send value to slot1 first
(`[HOLE, REQUEST]`), then option to slot0. The completed historical certificate can
outlive its primitive builder. Returning handlers reach false/default delivery;
a supplied throw preserves identity/caller99/precision10/sibling2251 and cancels
the body before retained-owner setter recovery10→12.

Four accepted source comparisons retain author3 at `8175923f8` and reduced peer1
at `43f6c410a`, runtime `9bb10d131`/406. All1,001 premises (265+178+204+354) pass at
the latter cut: literal/pool authority, true/false handling, strict rawNULL versus
weak explicit, actual named cursors, full four-frame raw carrier trace/discard,
source/owner/count/name/carrier controls and budgets. Initial `f7132ab30` CPU2
native4/baseline0 stay distinct from later CPU5. The original native numeric-wrapper
observer remains a native-only witness after its model hit CLI45 timeout0; only
that peer source drops catch trace traversal, while all354 actual trace premises
remain. Eleven stable/reaped reports retain that timeout, with no host timeout or
survivor and no accepted replay. Selected Deprecated24 is expected; other PHP and
accepted worker stderr are empty. Only13 module172 lines and one obsolete coherent
Source66 named-pack refusal change; no914 replay or trace/root/discard/GC change.
Multiple packs, PIPE, sole-owner lifetimes and wider values remain partial.

The [direct/selected unpacked NULL-option increment](../../coverage/semantics/ini-set-unpack-null-option-review.json)
adds one disjoint ownerless admission arm for a sole two-item numeric/named/mixed
pack. Invocation validity authenticates the selected string callee; source replay
authenticates pack destinations and order. Compiled pooled facts constrain literal contents. Inline array V→O
construction stores the earlier REQUEST before later option effects. Completed
snapshots remain historical when a callback changes the retained live pack.
True/false handlers reach false/default delivery; throw preserves Exception identity,
caller99/precision10/sibling2311 and cancels the body, followed by setter10→12.

Four originals agree and 953 premises (316+190+87 author,360 independent) pass at
`51747f166`/`3673267d0`/406. Native strict numeric keys5/9 normalize to raw
`[NULL,2321]` after helper effects and before any handler; the peer intentionally
has no native trace traversal. Its actual three-frame handler/API/caller trace
and authentic REQUEST identity, unpack cursors, precise discard, source/carrier/
selection controls and budgets are state proof. Initial `02f581357` CPU5 native4/
baseline0 precede later CPU2. Nine stable/reaped reports pass without failures or
retries; expected Deprecated lines6/23 accompany quiet accepted workers. Only13
module172 lines change; existing replay/trace/continuation/roots/discard/GC remain
exact. No old control repair or accepted replay is needed. Multiple packs,
Traversable, PIPE and owning/NaN/legacy-string values remain partial.

The [NULL-option rejected-array increment](../../coverage/semantics/ini-set-null-array-value-review.json)
adds a separate positional ownerless arm for retained allocated flat arrays with
DIRECT quiet primitive leaves. Invocation/selection validity authenticates the call;
compiled option facts must allow NULL, while compiled pooled value facts constrain
array contents without equating mutable array IDs or rereading live CV history.
Existing array roots retain the earlier value across handler COW writes. Normal
true/false handling reaches the existing parameter2 TypeError with an empty option;
a handler throw keeps rawNULL, identity/caller99/precision10/sibling2389 and cancels
before value rejection, then the original setter recovers10→12.

Four exact originals and 844 premises (219+188+96 author,341 independent) pass at
`b7a14d47d`/`c33c91205`/406. Native observes converted empty arg0/earlier2333 after
return; peer native has no trace traversal. Actual state proves raw versus converted
API frames, authentic REQUEST array leaves/edges, COW-separated keep/old arrays,
precise restored discard with existing idempotent GC buffering, literal-pool forgery
and malformed leaf/source/count/phase/budget refusals. Initial `c4c7eab2a` CPU3
native4/baseline0 remains distinct from later CPU2. Nine stable/reaped reports pass
without failures or retries; only Deprecated9/20 are expected, accepted workers are
quiet. Only27 additive172 lines reuse existing value-error/trace/root/discard/GC
bodies; no old control repair or67/68 replay is needed. Owned/packed array
values, wider named forms, references/nesting/owning/NaN/legacy-string leaves
and wider configuration remain partial.

The [unary CONFIG PIPE increment](../../coverage/semantics/include-config-pipe-review.json)
replays the authenticated left child and `CODEPIPE_SEND`, rather than an ordinary
call argument. An RHS factory's recorded subcall name cannot replace its returned
string or Closure target; only optimized `f(...)` syntax supplies a fixed name.
The held left object survives RHS writes that retire its original source cell.
Ordinary Closure PIPE follows caller strictness; only explicit `Closure->__invoke`
uses the weak wrapper entry. Getter/Restore callbacks retain full-name lookup and
raw INI writes; SET reads the late C-prefix old value, returns false for empty
results and raises ValueError for NUL results. A thrown callback preserves its
mutation; one-argument INI_SET PIPE rejects arity before stringification.
The ledger keeps twelve earlier normal source tuples and three finite
fixtures/165 assertions. Fresh current borrowed-warning composition adds one
normal SET and one throwing Restore callback check, without replaying those
checkpoints. Ordinary named Restore remains a retained control. Forged roots, left children, lines, selections, owners and
task operands reject; both original model failures remain preserved.
Stringable CHDIR PIPE resumes the genuine inner directory response before
capturing the outer request from the changed CWD. Six normal source tuples and
one provider fixture with 124 checks at `6e63009f3` distinguish success, OS refusal,
NUL rejection and throw while retaining callback effects and the held lhs.
Forged request, nonce, source, conversion, owner and response certificates reject.
The model retains the original object for authentication; native destructor
lifetime is not established.

Failed directory replies now suspend an eligible error handler with the consumed
request certificate. Normal return installs false after preserving handler CWD/raw
writes; throw retires the pending result and restores caller arguments. Nested
directory changes authenticate the original nonce/request and projected saved
owner without requiring the old CWD to remain live. The internal `chdir` trace
contains the converted requested string; explicit `Closure->__invoke` retains its
original object. The ledger separates current `0887697` source1/136, earlier three
source comparisons and the compiler image25 checks. Pure image and directory
resumption calculations are reused once with the same validation branches.
Broader callable consumers, warning ingress, OS/INI and lifecycle remain open.

The [NULL-option stdClass increment](../../coverage/semantics/ini-set-null-stdclass-value-review.json)
adds a disjoint positional ownerless arm for retained allocated table-free
STDINSTANCE values with direct quiet primitive properties. Invocation/selection
and compiled option facts authenticate the call; unknown CV/helper value facts do
not invent object receipts. Returning Deprecated handling reaches the existing
parameter2 TypeError with converted empty option and the same mutable object.
A supplied throw retains rawNULL and shared property writes, cancels rejection,
and preserves Exception identity/caller99/precision10/sibling2459 before recovery.

Four exact originals and author525 pass at `16ce6e0f3`/`aff691607`/406; corrected
peer386 passes at `37d83b736`, totaling911. Native return observes empty arg0 and
same-object arg1/current mark; peer native avoids trace traversal. Actual state
proves raw versus converted two-frame TypeErrors, the three-frame handler
Exception/owning object edge, shared aliases without COW, precise restoration/
discard and existing idempotent GC buffering. Initial `791533507` CPU2 native4/
baseline0 precede CPU1 checks. Eleven stable/reaped reports retain the original
peer negative-state binder collision0, fixed only by a local name prefix; no
accepted source/author/native or earlier-source replay. Expected Deprecated9/20
accompany quiet accepted workers. Only33 additive172 lines change; existing
trace/root/discard/GC/value-error bodies stay exact. Owned/packed forms beyond the
bounded follow-ups below, materialized tables, aliases/deferred/unset/owning
properties and other object kinds remain partial; no Stringable/COMP88 callback
is executed or enabled.

The [named NULL-option array increment](../../coverage/semantics/ini-set-named-null-array-value-review.json)
adds a disjoint ownerless named/mixed call arm for retained allocated flat DIRECT
quiet-primitive arrays. Each written argument name maps to its
normalized destination: option facts permit NULL, while known value arrays use
compiled-pool contents authority. Unknown CV/helper facts remain structural.
The actual partial argument task owns the earlier array in destination1 before
the later option argument separates the live alias by COW. Returning Deprecated
handling reaches the existing converted-empty parameter2 TypeError; supplied
throw retains rawNULL and the captured array and cancels rejection.

Author3 source comparisons retain `9441427317`; the smaller peer source and all
995 premises (282+210+122+381) pass at `c84b49c413`/`4a0c2ce147`/406. The native
literal observer establishes converted empty option/earlier2473; actual state
proves owning task/trace edges, partial named normalization, COW separation,
two-frame TypeErrors and the top-level peer's two-frame handler Exception,
precise restored discard/existing GC buffering and recovery. Peer native has no
trace traversal or physical array-identity claim. Initial `f45bd2c849` CPU2
native4/baseline0 precedes CPU4 author checks and final CPU2 checks. Three earlier
peer CLI45 timeouts and two budget localizations remain inconclusive0; reducing
redundant setup preserves the core counterexample without changing caps/runtime.
Fifteen actor reports retain twelve PASS/three timeouts, plus two diagnostic0
records. Only Deprecated24 is expected; accepted workers are quiet. The22-line
addition preserves positional69/stdClass70/finish/trace/root/discard/GC bodies;
no old control repair or accepted-source replay. Owned forms beyond the bounded
follow-up below, packed arrays, references, nesting/owning/NaN/legacy-string leaves
and wider configuration remain partial.

The [named NULL-option stdClass increment](../../coverage/semantics/ini-set-named-null-stdclass-value-review.json)
adds a disjoint ownerless named/mixed arm using the unchanged live, allocated,
table-free STDINSTANCE validator and DIRECT quiet-primitive property fence.
Invocation/selection validity authenticates the callee; source replay binds the
normalized layout. The new helper maps each written argument to option0/value1,
allowing NULL option facts and unknown captured object facts without inventing
object receipts. The actual partial argument task owns the earlier object before
the later option argument mutates that same object's property. Returning handling
reaches existing converted-empty parameter2 TypeError; supplied throw keeps rawNULL
and shared writes and cancels rejection. Strict mode rejects option after effects.

Source4 agreements retain `5c765213a`/`4b1c27aee`/406; author680 passes at
`398832dc72` and peer429 at `d68941e06`, totaling1,109. Native return observes empty
arg0/same-object arg1/updated mark. Peer native avoids trace traversal; actual state
proves partial owning-slot capture, unchanged object identity/shared updates,
two-frame TypeErrors and top-level handler Exception/owning trace edge, exact
restoration/discard with existing idempotent GC buffering and recovery. Initial
`6cc5796d7` CPU3 native4/baseline0 precedes CPU1 models, CPU4 author and CPU2 peer
state checks. Thirteen stable/reaped reports retain two pre-main fixture binding
failures0; only binding order changes, without accepted source/native/author replay.
Only Deprecated24 is expected and accepted workers are quiet. The21-line addition
preserves positional70/named-array71/stdClass validator/finish/trace/root/discard/GC
bodies. Packed forms beyond the bounded follow-up below, PIPE, sole-owner
lifetimes, materialized tables, declared/deferred/unset/ALIAS or
owning/NaN/legacy-string properties and other object kinds remain partial.

The [named retained-owner array increment](../../coverage/semantics/ini-set-owned-named-null-array-value-review.json)
adds one disjoint owner-present named/mixed NULL2 arm for live flat DIRECT quiet
arrays. Invocation validity authenticates the held intrinsic Closure and call
mode; existing written-name mapping and pooled literal contents authenticate the
normalized option/value slots. Before the later option expression runs, the
partial named task owns both the original Closure and earlier array. Live callee
replacement and alias COW preserve those captures. Returning handlers reach the
existing value TypeError with empty API option; explicit `__invoke` keeps rawNULL
and the same array in its numeric wrapper arguments. Ordinary strict calls reject
rawNULL before handlers, whereas explicit invocation remains weak. A supplied
throw cancels rejection and preserves identity/result99 and callback writes.

Four originals and all1,319 premises (348+286+287 author,398 independent) pass at
`f3a7657f9`/`4fc76dcea`/406. Native return observes E/W/N/2617/2617 for converted
API versus raw wrapper values. Peer native avoids trace traversal; actual state
proves handler/API/wrapper three-frame rawNULL/array edges, owner plus array task
roots, COW/current aliases, exact restored discard with existing idempotent GC
buffering, source-pool forgery refusal, budgets and retained-owner recovery.
The Closure is held by the task and `keep`, not an invented trace-owner edge.
Initial `d527a9877` CPU3 native4/baseline0 precedes CPU1 models/state. Nine
stable/reaped reports pass without failure or retry; only Deprecated18 is expected
and workers are quiet. Only12 additive172 lines change; existing source helpers,
finish/trace/root/discard/GC and historical tests stay exact, without old replay.
Purely positional owned-array calls without unpacking, references/nesting/owning/NaN or
legacy-string leaves, PIPE and sole-owner lifetimes remain partial. Paused
Stringable/COMP88 and other stopped boundaries are untouched.

The [retained-owner stdClass increment](../../coverage/semantics/ini-set-owned-null-stdclass-value-review.json)
adds one owner-present ordinary two-argument NULL2 arm, covering positional,
named and mixed calls through the existing written-destination helper. Invocation
validity authenticates the live intrinsic owner and call mode; value source facts
must be unknown, while option facts permit NULL. The unchanged validator requires
a live table-free STDINSTANCE with undeclared DIRECT quiet-primitive properties.
The held Closure and value are distinct object roots. A named partial task owns
both before later option effects; ordinary positional strict reception retains
its owner before the value helper completes. Shared property writes and live
callee replacement preserve the captured value pointer without array COW.

Four originals and all1,328 premises (300+289+289 author,450 independent) pass at
`816cb419e`/`8e34dfdf3`/407. Returning handling reaches TypeError2 with empty API
option; the explicit numeric wrapper keeps rawNULL and the same updated value.
Native E/W/N/I/I/true74 observations establish that identity/shared-mark behavior.
Ordinary strict calls complete value effects before TypeError1/handler0, while
the same owner's explicit mixed call remains weak. Peer native has no trace
traversal; actual state proves the handler/API/wrapper three-frame rawNULL/value
edges, distinct task roots, shared property records, exact restored discard with
existing idempotent buffers, source/property/table/carrier refusals, budgets and
original-owner recovery10→12. The trace arguments own the value, not an invented
Closure edge. A supplied Exception preserves identity/result99 and cancels rejection.

Initial `c91c9cca8` native4/baseline0 and all later checks use CPU1. Nine
stable/reaped reports pass first attempt; only Deprecated11/19 is expected and
workers are quiet. Only12 additive172 lines change; existing validation/source/
finish/trace/root/discard/GC bodies and old tests stay exact, without historical
replay. Packed forms beyond the bounded follow-up below, PIPE, materialized
tables, declared/deferred/unset/ALIAS or owning/NaN/legacy-string properties, other
value kinds and sole-owner lifetimes
remain partial. Paused Stringable/COMP88 and other stopped boundaries are untouched.

The [packed retained-owner array increment](../../coverage/semantics/ini-set-owned-unpack-null-array-value-review.json)
adds one disjoint owner-present NULL2 arm for exactly one two-item unpack pack.
Numeric, named and mixed keys normalize through unchanged source replay;
invocation validity authenticates the held intrinsic Closure and effective call
mode. The inner ARRAY must be live and flat with DIRECT quiet primitive leaves.
Unknown pack source facts stay structural; known literal snapshots must match
recursive pooled contents and provenance, without equating physical array IDs or
rereading the current outer table. A coherent changed-inner literal forgery is
invocation-valid but fails that source authority.

Before a later inline option expression, the builder owns the earlier inner
array. Actual unpack cursors transfer normalized value roots while retaining the
active outer operand. Completed pack certificates are historical and nonowning;
the earlier inner survives outer retirement or later outer/alias COW and live
callee/value replacement. Return handling reaches TypeError2 with empty API
option and rawNULL explicit wrapper; supplied Exception cancels rejection.
Ordinary strict calls reject rawNULL first, explicit invocation stays weak, and
the original held setter remains usable.

Four originals and all1,280 premises (297+268+253 author,462 independent) pass
first attempt at `e4d97ddf3`/`acf17872c`/407. Initial `2c76281b0` CPU2
native4/baseline0 precedes CPU4 models/state. Nine stable/reaped reports PASS;
only Deprecated9/17 is expected and workers are quiet. Native E/W/N/2783/2783
observes numeric API/wrapper values; peer native avoids trace traversal. Actual
state proves inner/outer identity and retirement, task roots and value edges in
the handler/API/wrapper trace, COW-separated live packs, exact restored discard
with existing idempotent buffers, source/carrier/domain controls and budgets.
No trace-owner edge or native physical-array identity is claimed. Only13
additive172 lines change; existing replay/helpers/finish/trace/root/discard/GC and
historical tests stay exact. Additional arguments/packs, owning/nested/reference
or nonquiet value leaves, PIPE and sole-owner lifetimes remain partial; paused
Stringable/owned-NUL and other stopped boundaries are untouched.

The [direct/selected packed-array increment](../../coverage/semantics/ini-set-unpack-null-array-value-review.json)
removes only the unused OWNER-presence condition from that sole-pack ARRAY arm.
Invocation validity still authenticates fixed, selected-string or retained-owner
call modes; pack count, normalized NULL/value, DIRECT quiet leaves, recursive
literal contents/provenance, nonPIPE and effective-weak guards remain exact.
Selected string metadata is captured before pack effects. Active outer/inner
ownership transfers to normalized inner-only roots; completed snapshots remain
historical without rereading current outer tables. Inline construction captures
the earlier array before O/COW/live-name replacement. Returning handling reaches
empty-option TypeError2, supplied Exception keeps rawNULL/earlier array and cancels
rejection, strict calls reject parameter1 after argument effects, and the original
selected setter remains usable.

Four originals and1,182 premises (292+271+158 author,461 independent) pass first
attempt at `3e6fb6995`/`7d4c579ea`/407. Initial `0f0ac8ca5` native4/baseline0
and later checks use CPU3; nine stable/reaped reports PASS, only Deprecated9/16.
Native E/2843 observes API values; peer native has no trace traversal. Actual state
proves selected records, cursor/root transfer, outer retirement and live-pack COW,
rawNULL/inner-array handler/API two-frame Exception edges, exact idempotent-buffer
restoration/discard, source-pool forgery refusal, budgets and selected-string
recovery. No native physical-array identity is claimed. Existing helper/body/
trace/root/discard/GC and historical tests stay exact without old replay. Additional
arguments/packs, nested/owning/reference or nonquiet inner leaves, packed object
values beyond the bounded follow-up below, PIPE and sole-owner lifetimes remain
partial; paused boundaries untouched.

The [direct/selected packed-stdClass increment](../../coverage/semantics/ini-set-unpack-null-stdclass-value-review.json)
adds one disjoint ownerless NULL2 arm for exactly one two-item numeric, named or
mixed unpack pack. Invocation validity authenticates the fixed/selected string
callee; existing source replay binds normalized destinations and order. The pack
source fact must be unknown (`compiled_read` EPS); source tests witness actual
CV/helper captures without inventing an object receipt or reconstructing history.
The unchanged validator requires a live table-free STDINSTANCE with undeclared
DIRECT quiet-primitive properties, including empty objects.

The historical snapshot saves the object pointer, not its property contents.
Actual unpack cursors transfer the active outer HARRAY root to normalized
HOBJECT ownership; the completed certificate contributes no outer root. Shared
option/handler writes remain visible through the captured object even after outer
retirement, live callee/value replacement or live-pack COW. Returning handling
reaches the existing converted-empty parameter2 TypeError; a supplied Exception
preserves rawNULL/the same updated object and cancels rejection. Strict calls
reject parameter1 after argument effects, and the original string setter recovers.

Four originals and all1,253 premises (306+290+155 author,502 independent) pass
first attempt at `eb31e651e`/`ec84a4ceb`/407. Initial `70f4cfc876` native4/baseline0
and later checks use CPU5; nine stable/reaped reports PASS, only Deprecated12/16.
Native E/I/updated-mark and peer oldpack-value identity/updated-mark observations
are distinct from state-only selected records, cursor/root transfer, retired outer,
actual two-frame handler/API rawNULL/object edge and precise full restoration/
discard with existing idempotent HOBJECT buffering. Peer native has no trace
traversal. Only13 additive172 lines change; helpers/finish/trace/root/discard/GC
and historical tests stay exact, without old replay. Additional arguments/packs,
materialized tables, declared/deferred/unset/ALIAS or
owning/NaN/legacy-string properties, other object kinds, PIPE and sole-owner
lifetimes remain partial; paused boundaries untouched.

The [packed retained-owner stdClass increment](../../coverage/semantics/ini-set-owned-unpack-null-stdclass-value-review.json)
removes only the OWNER-empty restriction from that sole-pack object arm. Invocation
validity still authenticates the allocated intrinsic callee and ordinary/explicit
source mode; replay binds normalized numeric, named or mixed sends. Captured pack
entries are DIRECT after existing dereference; this does not establish original
outer-entry reference freedom. Unknown pack facts (`compiled_read` EPS), table-free
live STDINSTANCE and undeclared DIRECT quiet-primitive property guards stay exact.
The original receiver and value are distinct HOBJECT roots. Unpack retains both
while transferring the active outer HARRAY root; completed certificates remain
historical and nonowning. Shared property writes stay visible after outer retirement,
live-pack COW and live callee/value replacement, without freezing object contents.

Four originals and all1,452 premises (316+293+329 author,514 independent) pass
first attempt at `97ecd7d8a`/`1c19a1812`/407. Initial `9fe932aaa` native4/baseline0
and all later checks use CPU1. Nine stable/reaped reports PASS without failure or
retry; only Deprecated12/16 is expected and workers are quiet. Native E/W/N/I/I/
true78 establishes empty API versus rawNULL wrapper options with the same updated
object in both value slots. Strict ordinary rejects parameter1 after P effects;
the same owner's explicit mixed call remains weak and reaches parameter2.
Peer native has no trace traversal; actual state proves owner+outer to
owner+value+outer to dual-HOBJECT transfer, live shared marks, current outer COW,
rawNULL/same-value edges in the handler/API/wrapper three-frame Exception, exact
full restoration/discard with existing idempotent buffers and strict original-owner
recovery10→12. The trace owns the value, not an invented receiver edge. Only one172
condition is deleted; helpers/finish/trace/root/discard/GC and historical tests stay
exact, without old replay. A pending-unpack flag was corrected during static review
before any actor. Additional arguments/packs, materialized tables, wider properties,
other object kinds, PIPE and sole-owner lifetimes remain partial. Original reference
forms have no new source agreement; paused boundaries remain untouched.

The [rejected getter Closure value increment](../../coverage/semantics/ini-set-null-getter-closure-value-review.json)
adds a separate ownerless positional NULL2 arm for a retained exact bare
`INTRINSICCLOSURE INTRINSIC_INI_GET`. Bounds, allocation and exact body kind
authenticate the live value; no property record or invented creation receipt is
needed. Existing invocation/source checks authenticate the selected string callee
and written arguments: option facts permit NULL, while value facts must be unknown
(`compiled_read` EPS). Actual partial states witness the earlier capture rather
than rereading current CVs. The edge-free getter is an owning HOBJECT argument,
not the INI_SET receiver, and is never invoked during rejection.

Returning Deprecated handling reaches the existing parameter2 TypeError with
converted-empty API option and the same getter despite live value0. Supplied
Exception preserves rawNULL/the old getter and cancels rejection. Strict reception
rejects parameter1 after V effects with handler0. Real getter→string setter→same
getter calls distinguish retained callable identity from the rebound live fields.
Four originals and all1,374 premises (326+353+278 author,417 independent) pass
first attempt at `487f3e446`/`f99899555`/407. Initial `d741939d6` native4/baseline0
and affected checks use CPU4; nine stable/reaped reports PASS, only Deprecated11/17
is expected and workers are quiet. Native E/I establishes empty API option and
getter identity. Peer native has no trace traversal; actual state proves the
partial root-free NULL capture, completed getter root, handler/API two-frame raw
argument edge, existing idempotent buffering and exact restoration/discard.
Only23 additive172 lines change; quiet-value/148 allocation/finish body/trace/root/
discard/GC and historical tests remain exact, without replay. Other callable kinds,
named/unpacked/PIPE forms and sole-owner lifetimes remain partial; retained positional
setter receivers follow below. No paused Stringable or owned-NUL path is exercised.

The [retained setter/getter-value increment](../../coverage/semantics/ini-set-owned-null-getter-closure-value-review.json)
removes only the OWNER-empty restriction from that positional getter-value arm.
Invocation validity authenticates the live exact INI_SET receiver and ordinary or
explicit source mode; the unchanged source shape/destination helper permits NULL
option facts and unknown captured value facts (`compiled_read` EPS). The exact
INI_GET predicate retains bounds/allocation/body-kind authority. Actual pre-V
states witness the held setter and rawNULL before the getter value is captured;
the config then owns two distinct HOBJECTs despite livecallee===getter/value0.
The getter is never called during reception and adds no child/property records.

Four originals and all1,595 premises (384+360+422 author,429 independent) pass
first attempt at `e9d360e44`/`425c5ef28`/407. Initial `4c1ddc2fc` native4/baseline0
and later checks use CPU4. Nine stable/reaped reports PASS without failures/retries;
only Deprecated12/17 is expected and workers are quiet. Native E/W/N/I/I establishes
empty API versus rawNULL wrapper options with the same getter in both value slots.
Ordinary strict reception rejects parameter1 after V/handler0; the same setter's
explicit call remains weak and reaches parameter2/handler1. Returning TypeErrors
have one API frame for ordinary calls and API/wrapper frames for explicit calls.
Peer native has no trace traversal; actual state proves handler/API/wrapper
three-frame rawNULL/getter edges, two task roots, existing idempotent buffers and
exact restoration/discard. The trace arguments own the getter; no receiver edge
is invented. Real getter10→oldsetter10/12→samegetter12 survives supplied Exception.
Helpers/finish/148 allocation/368 trace/root/discard/GC and historical tests stay
exact, without replay. Named/unpacked/PIPE forms, other callable kinds and
sole-owner lifetimes remain partial; paused boundaries remain untouched.

The [shared-reference rejected-array increment](../../coverage/semantics/ini-set-null-alias-array-value-review.json)
adds a separate ownerless positional NULL2 continuation for exactly key0 ALIAS
to a live allocated untyped reference cell holding a quiet primitive. Existing84
reference authority supplies bounds/DEFINED/REFCELLS/allocation; property-reference
and coercion metadata must be absent, and whole-state PARAMETERBACKINGS must be
EPS. The old DIRECT-array predicates remain unchanged. Invocation/source shape
checks authenticate the call and written arguments; option facts permit NULL,
while value facts must be unknown (`compiled_read` EPS). Actual partial states
witness the earlier capture rather than reconstructing current CV history.

The array is passed by value with one shared element reference. Current-container
COW appends31/37/41 without changing the saved one-entry shape; both containers
still reach the same cell, so subsequent leaf writes remain visible. Returning
handling converts the API option to empty before parameter2 TypeError. Supplied
Exception retains rawNULL/old array and cancels rejection; strict reception
completes value effects then rejects parameter1 with handler0. Original string
setter recovery remains usable.

Four originals and all1,261 premises (349+292+202 author,418 independent) pass
first attempt at `5a910116f`/`5ba6dd256`/407. Initial `dc883ec00` CPU3 native4/base0
precedes CPU5 model/public checks; nine stable/reaped reports PASS, only Deprecated12/21,
quiet workers and no failures/retries. Native E/L/A writes the leaf after actual
TypeError/getTrace and reads the updated trace value plus saved shape, without a
physical array-ID claim. Peer native has no trace traversal. Actual state proves
one-frame API TypeErrors, handler/API two-frame raw Exception, transitive
HARRAY→HCELL ownership and exact restoration/discard with existing idempotent
array buffering. HCELL is not directly task-rooted or a possible GC buffer root.
Only29 additive172 lines change; shared84/138/array/trace/root/GC/schema and
historical tests stay exact without replay. Multiple packs/PIPE forms,
additional entries, typed/property/parameter-backed references, owning referents
and sole-owner lifetimes remain partial; paused boundaries stay untouched.

The [retained receiver/shared-reference array increment](../../coverage/semantics/ini-set-owned-null-alias-array-value-review.json)
removes only the OWNER-empty conjunct from that positional ALIAS-array header,
preserving PACKSeps and every reference/domain/source/weak fence. Invocation
validity authenticates the allocated exact INI_SET receiver and ordinary or
explicit method source. The key0 cell remains live/untyped/quiet, property and
coercion metadata absent, whole-state PARAMETERBACKINGS EPS and captured value
facts unknown (`compiled_read` EPS). No shared array/type/trace/GC change follows.

Actual partial config states hold the setter/rawNULL before V; completed sends
also root the earlier array despite live INI_GET replacement and current-container
COW. Both saved arrays continue to reach the same HCELL after later writes.
Returning handling reaches converted-empty API/rawNULL wrapper parameter2
TypeError. Strict ordinary reception rejects parameter1 after effects with
handler0; the SAME held setter's explicit call is weak, enters the handler once
and reaches parameter2. Original setter recovery survives supplied Exception.

Four originals and all1,521 premises (372+321+385 author,443 independent) pass
first attempt at `4eb8c2785`/`5894b4ffc`/407. Initial `3b962c9ea` CPU3 native4/base0
precedes CPU5 affected checks; nine stable/reaped reports PASS, only Deprecated13/21,
quiet workers and no failures/retries. Native E/W/N/L/L/A writes the cell after
actual TypeError/getTrace and observes both saved argument arrays without physical
array-ID equality. Peer native has no trace traversal. Actual state proves the
handler/API/wrapper three-frame raw Exception, both raw argument edges to the earlier
ARRAY→HCELL, owner+array config roots and existing idempotent buffers/full discard. No
receiver trace edge or direct CELL task/buffer root is invented. Helpers/finish/
84/138/trace/root/GC/schema/historical tests remain exact without replay.
Multiple packs/PIPE forms, additional entries, typed/property/backed references,
owning referents and sole-owner lifetimes remain partial; paused paths untouched.

The [named shared-reference array increment](../../coverage/semantics/ini-set-named-null-alias-array-value-review.json)
extends that same exact key0 ALIAS-array continuation to named/mixed calls for
fixed/selected strings and retained setters. Existing destination-aware source
checks replace the positional spelling checks with identical absent-name facts:
option facts allow unknown/NULL and value facts require unknown (`compiled_read`
EPS). Actual partial `[HOLE,oldARRAY]` states witness capture before the later
option helper; the helper never reconstructs current CV history. PACKSeps,
live/untyped/quiet cell authority, absent property/coercion metadata, whole-state
PARAMETERBACKINGS EPS and effective weak reception remain unchanged.

Four source agreements and1,200 author premises (477+325+398) retain `108d62605`;
corrected peer428 retains `b6abcce69`, total1,628 at common `166547069`/408.
Initial `013007e47` CPU3 native4/base0 precedes CPU2 affected checks and the sole
CPU5 peer retry. Eleven stable/reaped reports retain ten PASS plus one optional-name
tuple typing failure0, corrected only by typed bindings/two added premises.
Source4/author1,200/native/base were not replayed. Only selected Deprecated21
occurs; all four accepted SL streams are true LF/quiet/exit0.

Native E/W/N/L/L/A reads both saved arguments after an external post-TypeError/
getTrace cell write, while current `[43,43]` distinguishes their saved shape.
State proves owning partial capture before option effects, normalized old array
with its live HCELL, current COW sharing, one-frame API versus two-frame explicit
TypeErrors, and the peer's actual handler/API two-frame raw Exception after the
post-allocation leaf write. Existing array buffering and whole restoration/discard
remain exact; HCELL is neither directly task-rooted nor GC-bufferable. There is
no physical exported-array identity or frozen-referent claim. Only3+/5-172 lines
change; helpers/finish/trace/root/GC/schema/historical tests stay exact without
replay. Multiple packs/PIPE, additional keys/entries, typed/property/backed references,
owning referents and sole-owner lifetimes remain partial; paused paths untouched.

The [unpacked shared-reference array increment](../../coverage/semantics/ini-set-unpack-null-alias-array-value-review.json)
adds one disjoint NULL2 header for a sole numeric/named/mixed two-item pack,
with either string selection or a retained INI_SET receiver. Normalized sends
hold rawNULL and the same exact key0 ALIAS ARRAY. Invoke/source replay authenticates
the snapshot and mode; compiled pack facts must be unknown (EPS). The existing
live untyped quiet-cell predicate, absent property/coercion metadata, whole-state
PARAMETERBACKINGS EPS and effective weak/nonPIPE fences remain unchanged.
Captured pack entries are DIRECT after dereference; this does not prove that
original outer entries were reference-free.

Four source agreements and all1,719 premises (422+323+430 author,544 independent)
pass first attempt at `6df1a6240`/`c27d6dd58`/408. Initial `733e53bcc` native4/base0
and affected checks all use CPU2; nine reports PASS/stable/reaped, only Deprecated13/19,
quiet workers and no failures/retries. Native E/W/N/L/L/A changes the leaf after
actual TypeError/getTrace and observes both saved arguments with their old shape.
The selected inline builder captures the inner array before later option effects,
then retires its outer pack. Strict ordinary completes pack effects before
parameter1/handler0; the same setter's explicit mixed call is weak and reaches
parameter2/handler1. Normal setter reuse remains usable.

State proves active outer→inner+outer cursor roots and completed inner-only roots
(plus the receiver when present), with the same transitive live HCELL. The retained
peer pack contrasts current outer COW to scalar0 with the old snapshot and observes
the post-Exception leaf through actual raw handler/API two-frame arguments.
Existing array buffering and whole idempotent restoration/discard stay exact;
HCELL is neither directly task-rooted nor GC-bufferable. No physical exported-array
identity, frozen referent or receiver trace edge is claimed. Only12 additive172
lines change; helpers/finish/trace/root/GC/schema/historical tests stay exact without
replay. Additional packs/arguments, PIPE, typed/property/backed references, owning
referents and sole-owner lifetimes remain partial; paused boundaries untouched.

The [undefined INI VALUE increment](../../coverage/semantics/ini-set-undefined-value-review.json)
handles a direct missing CV at positional argument1 after rawNULL option capture,
for selected strings and retained INI_SET receivers. Warning callbacks may define
that CV as an ARRAY and replace the live callee/option; the saved result remains
NULL. Weak reception next dispatches NULL-option Deprecated and returns false;
strict ordinary reception instead raises parameter1 with NULL/NULL API arguments.
Strict explicit reception is weak. A supplied first-Warning Exception cancels API
and wrapper entry, while the original setter remains usable.

Only25 additive207 lines change. Exact count2/INDEX1/PACKSeps/nonNAMED/nonPIPE,
pending selection/owner authority, option compiledEPS-orNULL and direct-variable
source/name/line checks authenticate the read. Its certificate roots only the
captured setter when present; callback-created ARRAYs stay in ordinary globals.
Certified resume completes the NULL send into CONFIG_ARGS, preserving the strict
direct-CV result validator rather than exposing KNOWNNULL at CONFIG_SEND. Existing
166/172/234 validators, generic restore/discard, trace/root/GC/schema and parser
foreign boundary remain unchanged.

Source4 and all1,165 premises (301+257+308 author,299 independent) pass at
`ed96f17f7`/408. Native and initial baseline retain `f2d24d56b`; baseline B| is
Unsupported/zero agreement. Initial/first affected CPU2, field-order retry CPU5
and corrected affected CPU3 retain separate records. Fifteen reports include
13 PASS and two failure0: pre-main malformed-pack field order, then an actual
transient result-integrity failure requiring the fused resume. Earlier model
streams are preserved; only changed runtime justified their repetition, with
native source paths/cwd and caps unchanged. Default Deprecated17/Warning17 are
the only PHPstderr. State proves whole Warning/Deprecated restoration, NULL send
despite live ARRAY, strict API-only trace, actual handler-only pre-API Exception,
idempotent owner-buffer discard and original-setter recovery. No receiver trace
edge or native peer trace observation is claimed. Wider names/packs/PIPE, other
read positions/producers and sole-owner lifetimes remain partial; paused paths
are untouched.


The [two-group NULL/ARRAY increment](../../coverage/semantics/ini-set-two-pack-null-array-value-review.json)
admits exactly two singleton DIRECT unpack snapshots for fixed/selected strings
and retained setters. Normalized sends retain raw NULL and the allocated flat
quiet DIRECT array; each saved pack separately authenticates its source and
compiled fact. Later outer-pack writes never replace these captures. Numeric,
named, reversed and mixed groups reuse existing destination replay. At this pin,
SEND_UNPACK's named-order flag resets per opcode, so a named first group followed
by a fresh numeric second group remains valid. No cross-group ordering fence is
introduced.

Only14 additive172 lines change. Existing weak/nonPIPE, invocation/owner, ARRAY,
finish/trace/root/discard and source validators stay exact. Four originals pass at
`582227151`/409; author1,350=484+404+462 plus independent527 totals1,877 strict-SL
premises. The first484 retains its original cut; the other groups pass at
`7b4fb564a`. Two pre-main fixture binding failures retain zero credit, and only
affected checks repeat. Thirteen reports retain11PASS/two failure0; all accepted
actors are reaped at original limits. Native default Deprecated8/17 is separate
from quiet strict/peer output. State proves active outer/inner root transfer,
retired outer history, captured COW, raw handler/API supplied-Exception cancellation,
full restored/discard identity and setter recovery; native compact observations
do not imply those trace/root facts. Raw records are external with original paths
and hashes. Additional groups/entries, PIPE, wider ARRAY leaves and sole-owner
lifetimes remain partial; paused boundaries remain unchanged.

The original [Iterator CONFIG bridge](../../coverage/semantics/config-iterator-unpack-review.json)
streams one borrowed CV holding an initialized user Iterator into INI_SET. The
Iterator methods have exact signatures, return by value and are non-generators;
current returns plain strings and key returns integers. Rewind, valid, current, key and next execute through genuine callback frames;
current is cached before key, and sending occurs only after key succeeds. Ordered
history preserves repeated integer keys as distinct positional arguments without
constructing a PHP ARRAY or changing historical ARRAY pack certificates.

The original pending call authenticates source and selected callee independently
of this history. DATA owns the Iterator once; completed traversal removes its
cursor and releases DATA before existing API reception. Callback writes to the
live callee do not reselect the call. A supplied Exception from key leaves current
unsent, preserves the existing result, removes the cursor and resumes the same
Exception after cleanup. Reached states distinguish these pre-API key frames from
an API trace frame and validate task roots, exact discard and setter recovery.

Four source agreements and two Unsupported controls retain `612d265ee`/410.
The 742 original author/peer state obligations pass through source-based parts
at `c91927197`, `443002e33` and `6062f4807`; 175 repeated setup conditions add
no coverage. Original fixture/timeout outcomes keep zero credit. The unchanged
genuine report preserves the initial false TypeError; overwritten auxiliary CLI
recorder files remain unavailable, without reconstruction or replay.

Last-owner finish and cleanup stop explicitly before releasing their retained
roots; wider retirement is partial. Both Generator controls retain their Source87
Unsupported cuts; direct Generators and generator-function getIterator are
admitted by the later increments below. At the Source87 cut, builtin WeakMap still
received a false TypeError; the increment below corrects that classification and
bounded producers. Ordinary non-Traversable TypeError is preserved. Named keys,
nonstring/reference/owning values, additional
arguments/packs, other CONFIG callees, suspension, warning/arity reception and
wider lifetime producers remain partial. Paused boundaries remain untouched.

The [WeakMap CONFIG increment](../../coverage/semantics/config-weakmap-unpack-review.json)
admits one borrowed initialized CV containing an externally held empty/singleton
WeakMap into INI_SET. Existing source/callee authority remains intact. Empty
traversal reaches exact2/0 ArgumentCountError at the call line, with empty API
arguments and an explicit __invoke wrapper when present. A live stdClass key in
an occupied map produces Error at the unpack line before copying or sending
current, with no synthetic API/wrapper frame. Supported current values are the
existing quiet scalar domain or a parentless methodless leaf INSTANCE; the map
may solely own that object.

With these external map/key owners, the native iterator/key pins retire silently
inside one authored rule. No PHP ARRAY represents the unpacked map; no iterator
task, cursor or schema is added.
Raw Error preserves the original prep and full heap; normal exception transition
then retires prep before throw search. Raw API allocation temporarily returns its
trace ARRAY, so descriptor checks apply after normalization while raw trace/heap
assertions remain. Actual source-reached state tests cover source/owner refusals,
callee owners, Error identity, recovery and budgets.

Four source agreements and strict410 retain `f90fafb27`; author109+117 and
independent181 conditions retain `dfac5af1b`, total407. The original strict
binding failure and inappropriate raw descriptor assertion retain zero credit.
Native4 and the genuine wrong caught-TypeError comparison retain `334d56943`.
Case-specific inner recorder stems preserve all original genuine files alongside
the later full model; no accepted replay occurs. ARRAY entries, wider object/key
forms, temporary operands, multiple packs, loss of external map/key/callee owners,
GC callbacks and
other CONFIG/Traversable producers remain partial. Existing stdClass TypeError
and the historical generator-function getIterator control stayed disjoint at that cut;
their earlier executions are not renewed.

The [Aggregate CONFIG producer](../../coverage/semantics/config-aggregate-iterator-unpack-review.json)
admits one initialized borrowed CV holding an ordinary user IteratorAggregate.
Its exact non-generator, by-value getIterator returns an externally retained
initialized user Iterator; existing string-current/integer-key streaming follows.
A source-authenticated pending record preserves the selected INI_SET call and
borrowed Aggregate identity. The real borrowed method target creates no Aggregate
pin. Its owned Iterator result transfers atomically into DATA and clears RESULT;
the existing Iterator record and historical CV/site remain unchanged. No PHP
ARRAY represents the Aggregate or returned traversal, and no ARRAY pack receipt
is fabricated.

Producer effects and later Iterator effects occur before API reception without
reselecting the callee. A supplied getIterator Exception has only its genuine
method frame at the unpack line, with no Iterator callbacks, DATA/cursor or
API/__invoke frame. Exact discard and drained cleanup preserve external objects,
Exception identity, the existing assignment and saved-setter recovery. Raw steps at loss of
external Aggregate, returned-Iterator or callee owners stop explicitly with
original roots/result/pending Exception before unsafe handoff or discard.

Native3 and genuine Unsupported0 retain `ac41bce439`; strict411/source3 and
fixed144 retain `a9a12a825`, with runtime `387e02afd` unchanged. Owned63+91 and
peer118+97 original conditions pass through parts at `1472a567d`; 45 repeated
setup conditions add no coverage, giving 513 originals/558 physical conditions.
The original owned154 timeout remains inconclusive0; accepted cases and native
observations were not replayed. References/temporaries, recursive or invalid
returns, Generator/owning currents, named keys, extra packs/arguments, other
callees and wider cleanup/GC/diagnostic histories remain partial. Existing direct
Iterator, WeakMap and generator-function getIterator controls keep their cuts.

The [native Generator CONFIG consumer](../../coverage/semantics/config-generator-unpack-review.json)
admits one initialized CV containing a fresh, named, zero-argument, non-byref
Generator. A source-authenticated CONFIG record retains the original INI_SET
selection, borrowed historical CV and up to two string sends with integer keys.
Native STARTPACK/BORROWED operations borrow the marker's single DATA owner;
no PHP Generator method frame, public iterator cursor, NEXTITER increment or PHP
ARRAY represents the traversal. Rebinding the input or callee during the body
does not replace the retained Generator or selected setter.

The terminal resume runs after both sends, before DATA retirement and API entry.
A supplied terminal Exception keeps both sends pending, result99 and precision6,
with only the genuine producer trace at the unpack line. Exact discard/drained
cleanup preserve its identity and permit saved-setter recovery. At the Source90
cut, raw last-DATA/callee boundaries preserve the original state; the sole-DATA
quiet retirement increment below supersedes only that DATA refusal. Wider producer/cache
modes stop explicitly and remain outside this slice.

Native3/genuine Unsupported0 retain `8d2ecb421`; strict413/source3 and all467
original conditions retain `3e1e67dee`, first attempts. Six source-derived parts
contain523 physical conditions, including56 setup with no coverage credit.
No native/accepted/control execution is renewed. The old Source87 direct-Generator
PHP bytes and historical ID remain exact; only its Unsupported expectation is
removed because the current fresh-CV consumer now admits it. Generator-function
getIterator and bounded temporary user-call inputs are covered below;
references, arguments/Closure/ordinary method producers, named keys,
more sends, owning/reference caches, delegation/Fiber/GC and wider diagnostics or
last-owner lifetimes remain partial; paused boundaries are unchanged.

The [Aggregate-returned Generator bridge](../../coverage/semantics/config-aggregate-generator-unpack-review.json)
admits a non-generator by-value getIterator returning an externally retained
fresh named zero-argument Generator. The real returned RESULT owner transfers
into the existing Generator DATA record; no Aggregate pin, fake PHP ARRAY, public
cursor or direct-Generator CV certificate is added. Historical INPUT remains the
original Aggregate CV even after it becomes23, while the Generator CV can become17.
Existing integer-key/string streaming, terminal resume and reception then apply.

The new admission authenticates the Aggregate callback/source, selected callee,
actual returned Generator, external owners and fresh phase. The old Iterator
promotion stays exact and disjoint. Lost Aggregate/callee/returned-Generator
owners and invalid phase/type/source stop at the raw handoff boundary with the
original task/result. At the recorded Source91 cut, Generator cleanup restoration
protects last-DATA/callee boundaries; the increment below replaces the quiet DATA
refusal. Its separate shared-return admission guard remains intact.

An Exception allocated in getIterator line14 retains its genuine method frame
at unpack line24 when the Generator later throws it after both sends. No new
Generator/API/__invoke frame replaces that saved trace. Same identity/result99,
precision7, discarded DATA and saved-setter recovery7→9 are validated.
Native3/genuine Unsupported0 retain `98c81eb73`; strict414/source3 and all475
original conditions retain `1de318e67` (544 physical,69 source-derived setup).
One invalid taskset wrapper stopped before Python; its log/exit remain zero-credit,
and all six parts passed their first actual evaluations with unchanged90 caps.
Native/genuine/accepted checks were not replayed; all five original genuine files
remain preserved. Generator-function getIterator is covered below; nonfresh or
owning/Closure/ordinary method producers, wider sends/values/lifetimes and paused
boundaries remain partial or unchanged.

The [sole-DATA Generator increment](../../coverage/semantics/config-generator-sole-data-review.json)
handles existing initialized CV ingress when the body overwrites the only outside
Generator owner. A closed named zero-argument Generator with no owning children
can retire through the normal driver before INI_SET reception or caller catch.
No owner is retained to keep validation alive. Existing object-slot metadata
preserves source/function/selected-callee history after allocation retirement.
Active rewind/next/ready/finish still require a live allocation; only invocation
and cleanup-source validation accept the authenticated retired quiet history.

WeakReference observers remain nonowning and become NULL before API success,
post-retirement API arity traces, or caught terminal throw. Last-callee and owning
RETURN boundaries keep exact raw Unsupported restoration; shared-owner behavior
is unchanged. The old Source90/91 hypothetical quiet last-DATA refusals and two
orphan hold-cell bindings are retired; all other original assertions/source bytes
stay exact, their accepted historical counts remain, and no old suite is replayed.

Native3/genuine Unsupported0 retain `d2b91bcce`; strict415/source3 and normal
entry48 retain `44cec5541`. Corrected completion89, owned48/127 and peer99/96
retain `8b7b153ec`, totaling448 originals/507 physical/59 setup. Original89 failed
because a fixture continued from raw PhpStep output before the driver's prune;
source-driven edges correct it without runtime changes or accepted replay. Both
that failure and all five original genuine files are preserved. Bounded temporary
call-result ingress is covered below; ordinary method/Closure producers, owning caches/returns, delegation,
GC/Fiber/destructor callback histories and broader lifetimes remain partial.

The [Generator-method Aggregate producer](../../coverage/semantics/config-aggregate-generator-method-review.json)
admits an initialized CV whose public zero-argument nonbyref getIterator has the
exact Traversable return signature and itself yields. The implicit call still
borrows its Aggregate; only GENERATOR_CREATE's
copied frame gains a real receiver owner. The actual fresh return temporary then
transfers into sole native DATA, without a fake named-function/CV certificate,
unpack ARRAY or public cursor. Inherited method selection retains both the
declaring function and actual receiver.

An optional CONFIG producer receipt holds the original Aggregate identity,
selected method and argument/source history without owning either object.
Stored/paused frames authenticate that exact target; real active contexts retain
ordinary Generator pairing. Closed reception validates immutable history after
receiver/Generator allocation retirement, using Source92's unchanged quiet-DATA
lifetime rule. Receiver WeakReference observers prove survival after input-CV
replacement and death before API entry, or after a caught terminal throw releases
the last outside hold. A method-created Exception keeps its original getIterator
class/type/unpack-line19 trace and identity through two sends and terminal resume.
Last-callee refusal, whole raw discard, normalized retirement and setter recovery
remain explicit.

Native3/genuine Unsupported0 retain `cd2512af4`; strict416/source3 and all574
original conditions retain `c784daf3a`, first evaluations (653 physical,79 setup).
Five old Generator record literals gain only the required EPS receipt; all other
assertions stay exact. Only the Source87 Aggregate control's Unsupported mapping
retires, with its PHP bytes and historical cut unchanged; no old suite is replayed.
Wider temporary/ordinary method/Closure ingress, nonfresh/byref producers,
wider sends/owning values, delegation/Fiber/destructor callback histories and
paused boundaries remain partial or unchanged.

The [temporary Generator-call input](../../coverage/semantics/config-generator-call-result-review.json)
admits an actual result of a direct noarg nonbyref named user call with no name
fallback. Existing emitted-call and UNPACK_VAR facts authenticate its source;
the returned fresh named Generator retains its own independent function/frame
origin. A factory may publish only WeakReference and return its real local value;
no variable is invented as the unpack operand and no factory/Generator identity
is assumed. Existing verified return types remain authoritative. The consumer
still accepts at most two non-NULL string sends with integer keys.

SEND_UNPACK keeps that opcode INPUT while its iterator separately owns DATA.
Native resumes therefore carry two owners. Normal finish or terminal throw first
releases DATA into a real input-release frontier with one live owner; FREE_OP1
then retires INPUT before API entry or caller catch. Raw release equalities stay
separate from driver-managed pruning. Historical reception validates the actual
call source after allocation death, while active stages remain live-only. Quiet
last-owner and captured-callee guards remain; owning RETURN children stop before
the final INPUT release. The old CV and Aggregate modes retain their existing
roots and lifetime behavior.

Native3/genuine Unsupported0 retain `eacd3fd4e`; strict417/source3 retain
`702d51056`. Fixed entry45 retains `1db66515c`; corrected author102/45/120 and
peer126/123 retain `2f4052196`, totaling506 maintained conditions/561 physical/
55 duplicated setup. Two explicit item-binding premises add no behavior credit.
The original completion101 syntax error stopped before evaluation and stays0;
only affected/unrun fixtures repeat. All five genuine files remain preserved.
Factory trace23/identity/result99, source/callee effects, weak death and setter
recovery pass. Wider calls/arguments/references, nonfresh returned or method/Closure
Generators, owning caches/returns, delegation/Fiber/destructor callbacks and
paused boundaries remain partial or unchanged.

The [initial-state CONFIG consumer](../../coverage/semantics/config-generator-initial-state-review.json)
extends direct initialized CV ingress to nondelegating PAUSED and CLOSED named
zero-argument nonbyref Generators. Known temporary call-result ingress remains
FRESH-only; no paused temporary finalizer or new producer receipt is introduced.
At the first yield, native rewind preserves the whole cached state and sends that
value once before continuing. Later resume may replace the source CV; existing
quiet sole-DATA retirement still precedes API entry.

An advanced Generator acquires DATA before native rewind rejects it. Its integer17
current never reaches the string-send gate or API; the complete paused frame/cache,
assignment, configuration and empty native Exception trace survive DATA cleanup.
An already CLOSED Generator rejects before acquiring DATA, throwing from the
original CV state without a resolved RESULT pin or API/Generator-method frame.
Both error paths use the unpack line and permit subsequent retirement and setter
recovery. Loss of the outside advanced-CV owner retains exact raw Unsupported
restoration rather than silently forcing a paused finalizer.

Native3/genuine Unsupported0 retain `75a3e8efd`; strict419/source3 and all361
original state conditions retain `a8492e0ca` (419 physical,58 duplicated setup),
first evaluations with unchanged90 state caps. All five genuine files remain
preserved; no old source/native/state suite is replayed. Only423 changes runtime;
schema, existing source receipts, generic Generator/release and all other modules
remain exact. Nonfresh temporary/Aggregate producers, delegation, broader sends,
owning storage and Fiber/GC/destructor callbacks remain partial; paused lanes stay unchanged.

The [CLOSED RETURN-storage increment](../../coverage/semantics/config-generator-return-storage-review.json)
retires an owning return before CONFIG reception or catch. Its existing source
history must describe a CLOSED Generator with no frame, delegate or borrowed/reference
cache, a string current and integer key. RETURN is a parentless INSTANCE whose
class has no declared properties, interfaces or constants, and its only method
is a source-authenticated public, nonstatic, concrete, zero-argument by-value
destructor without a return type. Actual property slots are empty at admission.
The two-string, integer-key consumer bound is unchanged.

CV overwrite can leave DATA as the final owner; a genuine factory result instead
retires DATA then its separate INPUT. Existing355 supplies the real storage pin.
A callee-only continuation retains the unpack argument origin through callbacks,
and an authenticated eager operation carries a destructor-thrown Exception.
After storage drains, immutable history permits reception or pending cleanup without
reading freed RETURN children. Normal reception restores the call site and rechecks
the retained callee; the abrupt path preserves the same Exception and its genuine
argument-site destructor trace. Weak observers prove both objects die before catch.

Native2/genuine0 retain `c5809eb65`; normal source retains `756e1bcad`, strict420
retains `3e2a1bbb4`, and 426 maintained conditions retain `d30eb5c3b`/`adf3abb6f`
(486 physical,60 duplicated setup). The final peer public-CLI comparison agrees
under a separately reviewed90-second CLI/105-second host budget; both earlier45-second
timeouts retain zero credit. Original source failures, the recovery-frontier fixture
failure and orchestration errors are preserved. Generic355/303/270, schema and
old evidence remain unchanged; broader owning graphs, escaping pins and paused
finalization remain partial. Paused and held lanes stay unchanged.

The [named Generator CONFIG increment](../../coverage/semantics/config-generator-named-unpack-review.json)
accepts string keys from a direct CV Generator in the existing bounded
`ini_set(...$generator)` consumer.
Each yielded current is read before its key; a numeric string key becomes a
positional argument only for the send, while `Generator::key()` retains the raw
string. Other string keys select named parameters. The send checks unknown names,
duplicates and positional-after-named before the next Generator resume. Thus an
error skips later yield side effects and unwinds through the existing DATA and
callee cleanup. History validates completed sends without broadening the user
Iterator domain or the other existing Generator producers. Five original sources
agree with PHP 8.5.10 at `e6213f0b9`, and 74 reached first-send/error predicates
pass across two groups. The unchanged
baseline is explicit Unsupported after its first yield. Non-string currents,
other key types, wider sends and ownership/callback histories remain partial.

The [named Iterator CONFIG increment](../../coverage/semantics/config-iterator-named-unpack-review.json)
accepts string keys from the existing initialized, direct-CV user Iterator
consumer. `current()` runs and caches its by-value string before `key()` may
change the backing CV. The raw key remains in the Iterator task; SEND_UNPACK
normalizes numeric strings only for the argument. Named lookup and duplicate or
positional-after-named errors run before `next()`, so later callback effects are
skipped. Completed history is checked against the authentic call/site before
API reception. An error retains CURRENT/KEY until ordinary cursor/DATA cleanup
before catch. Five original sources agree at `c6b87f1eb`; reached first-send
50 and duplicate-error/cleanup 109 premises pass at `c6b87f1eb`/`0b0d1620d`.
The unchanged first-string baseline is Unsupported. Earlier integer-key paths
remain covered. Two source-checked Aggregate-returned Iterator named cases
inherit this send path, including duplicate rejection before `next()`; wider
Aggregate histories, values, signatures and lifetimes remain partial.

The [temporary Iterator CONFIG increment](../../coverage/semantics/config-iterator-temp-call-review.json)
accepts a direct noarg by-value named user factory returning an initialized
Iterator into `ini_set(...factory())`. The emitted `UNPACK_VAR` call site
authenticates a separate opcode INPUT owner in addition to Iterator DATA.
DATA and the cursor retire before INPUT; quiet final INPUT death precedes
normal API reception or catch after a supplied key exception. The exception
leaves the current unsent and the selected API untouched. Factory key results
stay integer in this slice; string keys and effectful last owners remain
Unsupported. Three original PHP 8.5.10 sources agree across retained,
sole-owner and abrupt paths, with 142+145+131 reached predicates. The
unchanged factory baseline stopped Unsupported after `B|P|`; the Source99
Aggregate inheritance check adds two exact native/model source cases and a
current-rule duplicate control without claiming wider histories.

The [invalid Iterator CONFIG key increment](../../coverage/semantics/config-iterator-invalid-key-review.json)
handles quiet NULL, bool and float `key()` results when the current input CV
holds the selected initialized Iterator. Zend obtains and caches `current()`
before `key()`, consumes an invalid primitive key, then throws at the unpack
site before binding or `next()`. Existing throw cleanup drops the cached
current and DATA before catch; a retained CV keeps the Iterator allocated.
Four direct-CV originals and one separately tested Aggregate-produced Iterator
whose input CV is rebound to that same Iterator agree with PHP 8.5.10. Reached
first/second-key checks cover the untouched API, Error site, cached current,
2-to-1 owner change and source/guard negatives. The original first-key model
baseline remained Unsupported; other producer/key histories remain partial.

The [temporary invalid Iterator key increment](../../coverage/semantics/config-iterator-temp-invalid-key-review.json)
accepts quiet NULL, bool and float keys from the same direct noarg USER factory
and authenticated `UNPACK_VAR` input as the temporary Iterator path above.
The key-type Error consumes the raw key after cached `current()` and before
argument binding, `next()` or API entry. During throw search, Iterator DATA
retires before the distinct temporary INPUT; a sole owner dies before catch,
while an external hold keeps the returned Iterator live. Three PHP 8.5.10
sources agree, including a rejected second key after one positional send.
Reached checks cover 2-to-1-to-0 and retained 3-to-2-to-1 owners, the Error
site, source/guard negatives, WeakReference state and budget resumes. The
unchanged first-key baseline was Unsupported; named temporary keys, other
producers, owning key values and effectful last owners remain partial.

The [fresh Aggregate Iterator increment](../../coverage/semantics/config-aggregate-fresh-iterator-review.json)
accepts an initialized borrowed-CV `IteratorAggregate` whose ordinary by-value
`getIterator()` returns a fresh, unheld initialized user Iterator. The Aggregate
is held externally; its real return temporary transfers into Iterator DATA,
which is then the Iterator's sole owner. A nonowning producer receipt records
that transfer without pinning either object or requiring the original Aggregate
CV to stay bound during callbacks. The quiet Iterator has no destructor or
child roots. After two integer-key string sends, DATA dies before `ini_set`
receives the arguments; a saved second-key Exception instead discards DATA
before catch. WeakReference observations, cached current despite a key callback
changing its source variable, result/configuration and setter recovery agree
with PHP 8.5.10 in two frozen originals. Source-reached checks cover the normal
and abrupt owner transitions, retired ready state, and missing/wrong receipts.
The existing retained Aggregate and CV-rebinding paths remain exact. At this
cut, a fresh Aggregate Iterator with an invalid bool key was Unsupported after
its key callback; owning/effectful finalizers, child roots and wider keys were
open. The three unchanged original baselines were Unsupported with zero source
agreement.

The [fresh Aggregate invalid-key increment](../../coverage/semantics/config-aggregate-fresh-invalid-key-review.json)
recognizes NULL, bool and float keys from that receipt-backed, sole-DATA user
Iterator when its Aggregate producer remains live. `current()` stays cached;
`key()` completes, then `SEND_UNPACK` raises the Error at the call site before
binding the invalid item, calling `next()` or entering `ini_set`. Throw cleanup
retires DATA and clears its WeakReference before catch. Three frozen originals
agree with PHP across first and second keys, including an Aggregate CV rebind
while another variable holds the producer. A stable sole-CV Aggregate also
agrees, and the formerly Unsupported Source109 invalid-bool original now agrees;
the prior Unsupported observation keeps its original zero credit. Two fresh
named-key controls and four adjacent older paths remain exact. Three
source-reached fixtures pass 404 premises and six raw promotion/Error steps.
The existing receipt validator checks live structural identity, not an
unforgeable historical return witness. If a sole Aggregate CV is rebound and
the producer dies during iteration, the model at this cut reported an
interpreter failure; that native-normal case has zero agreement. Effectful
finalizers, child roots, wider keys and producer lifetimes remain partial.

The [retired Aggregate producer increment](../../coverage/semantics/config-aggregate-retired-producer-review.json)
keeps the same nonowning Iterator receipt when a first `key()` callback clears
the only Aggregate CV. The live validation arm remains unchanged; a disjoint
retired arm checks the still-recorded Aggregate class, original source/call
site, nominal `IteratorAggregate`, and linked public `getIterator` signature
without adding an owner. Zend's returned Iterator temporary has already been
copied into Iterator DATA before the producer dies. Three byte-frozen
model-compatible originals agree on normal completion, a second invalid bool
key Error at unpack line 40, and a saved second-key Exception. Source-reached
fixtures start from the checked original calls, authenticate the actual getter
return and DATA promotion, then check dead producer and live sole DATA after
the first key, both WeakReferences dead before API/catch, and unchanged result
and INI state on abrupt paths. Normal 177, invalid 163 and Exception 146
premises pass at separate cuts. The unchanged three-source interpreter-failure
baseline and first erroneous abrupt-budget assertion keep zero agreement.
The receipt remains structurally forgeable by another retired same-class
object; reached-source tests establish its genuine provenance only for these
programs. Effectful producer finalizers, child storage, wider Iterator values
and other CONFIG consumers are still open.

The [returned Iterator finalizer increment](../../coverage/semantics/config-aggregate-iterator-finalizer-review.json)
allows that fresh, sole-DATA Iterator to run a public `__destruct`
after its Aggregate producer has retired. The destructor has no parameters,
reference return, generator body or child roots in this scope. On normal
completion it runs after the final `valid()` and before `ini_set` receives the
arguments. An invalid second bool key or saved second-key Exception instead
releases DATA and runs the destructor before catch; the saved Exception keeps
its identity through destructor operation exit. Three frozen originals match
PHP 8.5.10 byte for byte, including the destructor output, changed stamp,
WeakReferences, Error line and INI/result state. Separate source-reached
checks cover 183+169+178 premises, including retired operation-source validity
after the destructor. The unchanged model rejected all three at Aggregate
return. Destructor throws/reentrancy, child storage, wider values and the
structurally forgeable same-class producer receipt remain open.

The [returned Iterator child increment](../../coverage/semantics/config-aggregate-iterator-child-review.json)
admits one public declared `child` property holding a direct live object, with
that property as the child's sole owner. Both objects have public no-argument
by-value nongenerator destructors; the child has no properties or outgoing
heap edges, and neither object has a materialized property table. The Iterator
destructor still sees its child live. Ordinary object storage release then
runs the child destructor before INI_SET entry or catch, changing the stamp
from 1 to 2. Normal, invalid second bool key and saved second-key Exception
agree with PHP in three frozen originals; 233+216+229 reached premises check
the child edge, extra-owner/edge refusals, destructor order, weak death and
pending Exception identity. The existing object-release machinery is unchanged.
An independent normal source also agrees, including parent weak death before
the child destructor and the child's own live weak reference during that call.
At that cut, an Iterator with no destructor and only a finalizable child was
outside the increment. Wider child graphs and destructor throws or reentry
remained open.

The [child-only Iterator increment](../../coverage/semantics/config-aggregate-iterator-child-only-review.json),
when the Iterator alone owns its Child, also admits a parent with no effective
destructor and the same sole declared child. Shared instance-storage release
marks and logically retires the parent,
clearing its weak reference while a real `INSTANCE_STORAGE_STEP` still pins
its allocation. The Child callback sees itself live; physical parent retirement
follows that callback. A saved key Exception remains in the real operation
until both allocations retire, then resumes the same catch. Retired CONFIG
validation admits the resulting quiet parent image while retaining the storage
marker, source, pending-Throwable and cursor checks. Three retained originals
and one independent saved-Exception/weak-visibility source agree with PHP;
149 source-reached premises check the pin, ownership refusals, marker necessity
and budget resumes. Generic destructor/storage rules were unchanged. At that cut,
additional owners/edges, child storage, wider graphs and destructor throws/reentry
remained open.

The [retained Child increment](../../coverage/semantics/config-aggregate-iterator-retained-child-review.json)
admits outside owners while preserving the same single declared `child` edge
and fieldless Child finalizer guard. Ordinary shared release drops that edge
without calling the Child while an outside owner remains. The parent, with
or without its admitted destructor, retires before API entry or catch; the Child
has one outside owner and is still uncalled. A subsequent real outside `unset`
runs the Child destructor once, with parent weak null and Child weak live during
the callback, then clears Child weak visibility. Three original sources and one
independent parent-destructor saved-Exception source agree with PHP. New reached
checks pass 156 premises through real storage, pending exit and outside UNSET;
67+33 affected legacy return-front checks promote only the former extra-owner
refusals and retain their extra-edge negatives. Historical whole-tail cuts stay
unchanged. Generic storage/destructor rules were unchanged; at that cut, wider
edges/storage, owner forms, shutdown release and destructor throws/reentry remained open.

The [descriptor-backed field increment](../../coverage/semantics/config-aggregate-iterator-layout-review.json)
replaces the literal `child` and single-edge restriction with the actual declared
physical layout. Shared descriptor authentication retains each consumer's policy;
CONFIG folds supported scalar, ordinary CELL, ARRAY and ordinary-instance fields,
including typed/private direct storage and genuinely initial or cleared slots.
Path ancestry rejects ARRAY/CELL/object backedges while allowing repeated roots
and shared descendants. Existing edge extraction preserves every owning edge;
the parent storage pin and saved-Exception operation authority are unchanged.
An outside owner can keep a descendant alive after parent retirement until an
actual outside `unset`. Dynamic/materialized layouts, special cells, builtin
descendants, shutdown release and wider destructor effects remain partial.
Four authored originals and one independent public-parent-destructor saved-Exception
source agree exactly; new reached checks pass 38+190 premises and the affected
CONFIG117 return front passes 33. Earlier whole-tail cuts retain their identities.

The [reference-current increment](../../coverage/semantics/config-iterator-reference-current-review.json)
retains the genuine ordinary reference cell returned by `current()` through
`key()`. Key-time writes affect the selected cell; rebinding its source name or
property does not reselect the cache. Acquisition and send-time reads use the
shared ordinary-cell helper and existing descriptor-backed graph policy.
Sending copies the value into a DIRECT argument before `next()` or DATA/INPUT
retirement, so later writes and destructors cannot change the API arguments.
Other Iterator methods retain their by-value contract.

Callback and cleanup history authenticate the raw cache shape and actual current
return mode independently of the cell's later contents or allocation. Ordinary
release retires a cache-only payload before DATA/INPUT, preserving the supplied
Exception and pending result. Retired stable cell markers own nothing and cannot
authenticate a live value. Original ordinary-cell source/state cuts, including
the then-refused typed control, retain their identities in the linked review.

The [typed-current increment](../../coverage/semantics/config-iterator-typed-current-review.json)
adds a disjoint source-authenticated read for constrained cells. A real nonempty
source row must pass the existing unique/live instance and static source checks,
including declaration, selected slot, alias identity and stored-value type.
The same reader validates CURRENT and DATA HCELL nodes. Reads perform no
conversion and create no owner; normal property/static writes, rebinding and
retirement attach or detach constraints. Cached cell selection and the DIRECT
post-key value snapshot remain independent of later source/name changes.

Five source agreements include one newly promoted original typed control; new
reached recipes check source rows, nullable capture, rebind/detach, pending throw,
actual owner transitions and pooled literal retention. Literal-reference debts,
released cells, active coercion/parameter-backing authorities and wider
graph/lifetime contexts retain their existing boundaries. The ordinary helper,
A65 and scalar invalid-key cleanup remain unchanged.

The [scalar-send increment](../../coverage/semantics/config-iterator-scalar-review.json)
normalizes raw scalar transport on this existing INI_SET Iterator bridge.
KNOWN current receipts and copied ITEMS accept ordinary NULL/bool/int/float/string
values under the shared bounded flat-leaf validator. Genuine reference caches
retain the existing cell/type-source/graph read; key-time writes select the sent
value, and source rebinding does not replace the cached cell. Sending stores a
DIRECT scalar snapshot without coercion, deprecation or another heap owner.
Named destination errors still precede scalar-domain refusal.

After traversal and DATA/INPUT cleanup, existing INI_SET reception binds the
string option using caller strictness (explicit Closure::__invoke remains weak).
Weak NULL deprecates; strict nonstrings reject. The value parameter accepts the
scalar/null union even strict, then stringifies inside the API using live state.
A destructor's precision change therefore affects raw-float conversion while
later cell writes cannot change the copied argument. A completed scalar-call
receipt authenticates source, selected callee and normalized copied slots through
the NULL handler/resume even after the Iterator is gone; it does not reread DATA
or broaden ordinary CONFIG sent-shape validation.

Other CONFIG intrinsic acquisition and Generator value policies remain unchanged.
The [owning-argument increment](../../coverage/semantics/config-iterator-argument-review.json)
adds finite path-acyclic CFG-admitted ARRAY and ordinary non-Stringable root
INSTANCE values on this same INI_SET bridge. Live capture/send reuses the existing
field, reference-source and graph validation. Copied entries become real normalized
call-slot roots, including repeated roots and named holes. Array COW protects each
captured table while embedded reference cells and object properties remain shared.
No PHP ARRAY is invented for the internal buffer.

The copied slots survive `next()` and ordered DATA/INPUT retirement. Owning ready
calls transfer to ordinary CONFIG_INVOKE reception and argument cleanup; scalar-only
ready calls retain their earlier path. Existing API errors build real TraceArgs
owners, so an object can outlive Iterator DATA and die only after its final Error
or outside argument owner disappears. This includes passing the Iterator itself.
NULL diagnostics retain source/callee/copied-slot authority after DATA death and
reuse the existing disjoint API finish cases.

Exact key/send Error producers preserve a live owning cache or copied prefix until
ordinary THROW_SEARCH performs CURRENT, DATA/INPUT, then prefix release. A retained
outside cache owner defers its finalizer. Error priority is independent of send-time
graph admission. Post-retirement records authenticate structural identities and
stages; they do not recover old reference-cell contents or prove complete producer
provenance. Later callback retirement keeps a nonempty copied-prefix witness.

The [final temporary INPUT increment](../../coverage/semantics/config-iterator-input-finalizer-review.json)
admits last-owner cleanup for the existing no-argument named-call temporary when
normalized copied arguments have live heap roots and the Iterator satisfies the
existing finite field/finalizer policy. Copied arguments remain protected while
DATA and then INPUT retire. Normal reception follows the INPUT destructor, so its
configuration writes affect API validation; a supplied Throwable instead releases
the copied prefix after INPUT and keeps the original pending identity. Array COW,
embedded aliases and API TraceArgs retain their ordinary ownership behavior.

Other CONFIG intrinsic acquisition, temporary source/key forms, Stringable/effectful
casts, materialized or special graphs and wider lifecycle contexts retain their
current boundaries. An effectful last INPUT without an admitted live copied root
remains Unsupported. Constructed first-key and graph-rejection
checks do not establish extra native source agreements or broader GC coverage.
All held boundaries, including low-precision DEFINE-name NaN and owned-NUL release,
remain untouched. Original A66/A67/A68 cuts retain their scope and identities.

The [scalar Generator increment](../../coverage/semantics/config-generator-scalar-review.json)
reuses the same flat scalar policy for live VALUE sends and copied-item history on
the existing non-reference CONFIG Generator routes. NULL, bool, int and float
snapshots survive later resumes and source/callee rebinding. Terminal effects and
ordinary DATA/INPUT cleanup still precede INI_SET reception: strict option errors,
weak NULL deprecation callbacks and value conversion using live precision reuse the
existing API helpers. Historical scalar-call authority remains valid after the
Generator retires, including handler return or supplied throw.

Producer, key, initial-state, two-send and owner policies are unchanged. Reference
yields and owning argument buffers remain separate; the existing owning RETURN
storage path keeps its string-cache/integer-key history rule. Wider object/effectful
conversion and all paused boundaries remain outside this increment. The earlier
Generator reviews retain their original string-only cuts without renewed credit.
