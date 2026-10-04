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

[Stringable file operands](../../coverage/semantics/file-operand-review.json)
run the ordinary checked `__toString` callback before resolution, once checks or
provider creation. Conversion retains its receiver after global rebinding;
normal return restores the authentic include parent and samples live CWD/path.
Throw and invalid conversion complete without demanding file facts or allocating
a provider nonce. Pre-parser conversion/warning frames retain the compiled operand line and zero
arguments; executed included-unit frames retain their opened-path argument.

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
`display_errors` alone, or all three keys; its value is canonical base64 or JSON
null. Absent display input retains the baseline raw `stderr`; explicit null
selects stdout and a present empty string selects off, though both getters return
empty bytes. Null is a source-defined control, without a native CLI NULL claim.
Full case-insensitive names precede decimal-prefix/uint8 decoding. Setters preserve
full bytes and sample the old value after Stringable option conversion; Restore
uses the original nullable entry only when modified. Display-only file entries
seed the baseline `.:` path, while ordinary/request entries keep file facts unknown.
Ordinary diagnostics capture their live destination after handlers and retain
output order through later mode changes. Eleven exact comparisons, 76 state
premises and 17 transport controls cover these routes and eval/include retirement.
Shutdown fatal freezing remains required after actual231 acceptance; its held
native source adds no model agreement yet. Wider display/configuration stays open.

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
