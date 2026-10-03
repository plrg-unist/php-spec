# Include/require source boundary

The pinned PHP 8.5.10 CLI profile starts with `include_path=.:`. The finite
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
file-path prefix. Other real INI directives remain explicitly Unsupported.
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
misses use full-name lookup and return false; other directives remain
Unsupported. Missing raw environment also remains Unsupported.
The same option parser now handles primitive/null Restore calls: strict direct
calls reject non-string options, explicit `Closure->__invoke` calls parse weakly, and weak null
deprecates before lookup. Argument binding/arity errors preserve evaluated side
effects without converting rejected extra operands. Current inherited array
calls and captured clones preserve caller arguments through zero-argument
callbacks. The ledger separates the original ten source passes and rule-overlap
failure from the corrected current composition; runtime/compiler binaries are
reused, without a fresh rebuild claim.

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
lifetime is not established. Broader callable consumers, warning ingress, OS/INI
and lifecycle remain open.
