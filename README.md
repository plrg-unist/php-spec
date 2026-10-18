# PHP syntax in P4-SpecTec

Compressed historical evidence is stored outside Git; see the
[artifact locations and commit map](docs/ARTIFACTS.md) for lookup and recovery.

This project specifies the abstract syntax of **PHP 8.5.10** and connects
PHP-Parser 5.8.0 to checked P4-SpecTec values. The grammar/scanner inventory
contains 169 constructors. The [publication review](coverage/semantics/compiler-publication-review.json)
records a fresh offline rebuild of private revision `4b3c1a85`, including the
complete classified gate for 30,980 corpus entries/profiles and grammar/scanner/encoding
inventories. Earlier [inheritance](coverage/semantics/inheritance-review.json),
[frontend repair](coverage/frontend-syntax-repair.json), [switch syntax](coverage/semantics/switch-review.json)
and [portability](coverage/portability.json) records retain their original scopes.
Executable core semantics are now being implemented; see the
[plan](PLAN.md), [progress](PROGRESS.md) and [core contract](docs/semantics/CORE.md).
The syntax reports above do not establish semantic coverage. BOLA verification
remains later research.

[Missing-key destructuring warnings](docs/semantics/SOURCE-DESTRUCTURING-WARNINGS.md)
now retain captured arrays or source reference cells through handlers, including
recursive by-value CV/literal and mixed CV patterns, with ordered null delivery
and normal/throw cleanup. Recursive CV-source patterns also freeze converted variable
keys across callbacks while later key variables are read afresh.

The [checked eval parser service](docs/semantics/DYNAMIC-SOURCE-SERVICE.md)
accepts raw eval-source bytes, uses a native parse-only scanner for rejection
facts including catchable parse-time `CompileError` provenance, and validates
the PHP-Parser AST as a formal program. Its
[transport evidence ledger](coverage/dynamic-eval-helper-review.json)
separates 11 focused eval-source cases from the 30,980-entry existing file-syntax
regression. The [native diagnostic ledger](coverage/dynamic-eval-native-diagnostics-review.json)
records the separate parse-only bridge; the [exception-kind extension](coverage/dynamic-eval-parser-exceptions-review.json)
records the later CompileError classification. [Reached eval execution](docs/semantics/DYNAMIC-EVAL.md)
and [finite-provider include/require](docs/semantics/INCLUDE-SOURCES.md) use checked
machine pauses. A finite version-2 provider supports checked CWD and
`include_path` changes. [Stringable include/require operands](coverage/semantics/file-operand-review.json)
convert before path lookup and once checks. Failed-open warnings resume handlers
with live path sampling, saved owners and zero-argument file traces; fatal cleanup
preserves frozen output before shutdown callbacks.
Embedded-NUL paths [fail locally](coverage/semantics/source-nul-path-review.json)
before provider or once lookup: include warns once and returns false, while require
throws `Error`. Messages freeze the current path and redact credentials from the
C-string display prefix. Stringable conversion tails remain explicitly Unsupported.

[Backticks](docs/semantics/SHELL-DISPATCH.md) now construct commands through
ordinary interpolation, retain compiler deprecations and `shell_exec` errors and
traces, and consume explicit finite pipe/output facts. Requests preserve raw
environment order and current CWD; the semantic process never launches a shell.

[Default output buffers](docs/semantics/OUTPUT-BUFFERS.md) now route exact bytes
through nested default handlers, chunk/clean/flush/get/status operations and
request-end flushing after shutdown/destructors. [User output handlers](docs/semantics/OUTPUT-HANDLERS.md)
support explicit flush/clean/end/get and normal positive-chunk callbacks from
echo, print and inline output, with copied snapshots, source call contexts and
PHP8.5 callback-output deprecation. Automatic and explicit API reception failures
or callback throws preserve pending cleanup and stack operations before caller
catch. Defined scalar returns survive callee cleanup throws, with callee-only
reference wrappers and borrowed method receivers. Explicit API argument-warning
throws release only the prepared prefix before failed-buffer cleanup.
Callback exit, wider warning-handler throws, other byte producers,
request-end dispatch and buffered stdout diagnostics remain dependencies.

[Tick callbacks](docs/semantics/TICKS.md) use source-derived marker plans and a
shared request counter. The live registry preserves captured arguments, callback
mutation and cleanup order; wider compiler placement and callable forms remain
explicit dependencies.

[Recorded file-compiler diagnostics](coverage/semantics/file-compile-notice-review.json)
now delay ordinary include/require registration through warning callbacks;
the once forms register before compilation. Handler throws and graceful exit
finish registration, while a hard fatal skips ordinary registration.

Array eval/include operands now dispatch the real conversion warning before
parser or file-provider work. [The Array operand ledger](coverage/semantics/source-array-review.json)
records frozen `Array` bytes after callbacks, borrowed versus captured owners,
late path/once lookup and cleanup before nontrivial file bodies or catch search.
Four exact sources and 207 state premises pass; the destructor lifetime original
also agrees in the separately reviewed eager-release composition. Wider source/provider behavior remains required.

[Undefined eval/include operands](coverage/semantics/source-undefined-review.json)
resume real warnings with fixed null after handler writes and retain the native
empty-path error priority. [Stringable source ownership](coverage/semantics/source-stringable-review.json)
keeps converted bytes and borrowed/captured owners through cast and destructor
failures. Separate [ordering](coverage/semantics/source-stringable-ordering-review.json)
and [helper-result](coverage/semantics/source-stringable-helper-review.json) cuts
cover compiler fast returns, delayed exceptions and copied false/true results.

[Final-release traces](coverage/semantics/source-stringable-retirement-review.json)
authenticate child opcode lines, genuine filename arguments and zero-argument
fast/helper frames. The [first-work extension](coverage/semantics/source-stringable-first-work-review.json)
adds constant ECHO and assignment to a literal variable name entry lines. Each ledger retains
its original source/state cuts and failures; the installed rules add no renewed
credit to those cuts. One new [Generator/source composition](coverage/semantics/include-source-composition-review.json)
passes strict compilation, an exact source original and 49 reached premises.
[Nonconstant first emission](docs/semantics/SOURCE-EMISSION.md) now distinguishes ordinary CV ECHO, literal property FETCH and no-argument named-call INIT lines. The separate actual286 Generator/property cut passes one original and 70 reached entry/retirement premises. Wider source producers, emissions and providers remain open.

Literal auto-global first FETCH has a separate [private278 cut](coverage/semantics/source-autoglobal-emission-review.json): two explicit-request originals, independent90 source/retirement premises and new maintained72 classification premises. A separate cc397-parent291 readonly-clone join passes one exact original and64 independent premises. The actual293 join passes compilation, the same exact original and47 focused collector/source-retirement premises. Broader first emissions remain required.

Literal `$GLOBALS` first FETCH is integrated with a separately reviewed [private294 cut](coverage/semantics/source-globals-emission-review.json): four exact originals preserve later coercion/property warnings, and67 independent premises retain authentic lines, global tables and snapshot timing. Actual296 passes strict compilation with independently reviewed Arrow/Fiber compatibility; earlier source/state credit stays separate.

Literal `$this` first FETCH is integrated with a separately reviewed [private297 cut](coverage/semantics/source-this-emission-review.json): four exact originals retain method/private scope and retirement before the missing-instance error, with70 independent premises and9 affected classification checks. Actual303 passes strict compilation with independently reviewed property/default/argument compatibility; earlier source/state cuts retain their inputs.

Computed variable names from resolved no-argument user calls have a reviewed [private304 cut](coverage/semantics/source-computed-emission-review.json): operand retirement exposes INIT6 before helper/FETCH/property execution, with four exact originals across separate cuts and188 independent premises. Missing-name warning callbacks retain their writes while the interrupted read returns null. Actual307 passes strict compilation with independently reviewed collector/Generator/ArrayAccess compatibility; earlier source/state results retain their inputs.

Ordinary CV-computed names have a reviewed [private308 cut](coverage/semantics/source-cv-name-emission-review.json): the outer FETCH6 precedes a later property8, with four exact originals and174 independent premises. Retirement changes the live name before lookup; handler name/target writes survive fixed-null resume. Actual310 passes strict compilation with reviewed Fiber/collector/constructor compatibility; earlier source/state results keep their inputs.

Computed names from a resolved user call with one positional ordinary CV argument have a reviewed [private311 cut](coverage/semantics/source-call-argument-emission-review.json): operand retirement uses the INIT6 location before argument lookup, while outer FETCH7 precedes property10. Five exact originals and275 independent premises preserve live argument reads and fixed-null argument/target warning resumes after handler writes. The initial parser stop and wrong argument-certificate trace retain zero affected credit. Actual316 passes strict compilation with reviewed trait/ArrayAccess/collector compatibility; earlier source/state cuts retain their inputs.

One named ordinary CV argument now retains INIT6 before known FETCH8/property11 and unknown-name Error7 before CV demand. [Six exact originals and325 independent premises](coverage/semantics/source-named-argument-emission-review.json) preserve second-slot binding, default holes and fixed-null warning resumes. Actual320 passes strict compilation with reviewed Fiber/property/collector compatibility; earlier cuts retain their inputs.

An undefined ordinary CV used as a computed variable name now warns before conversion, then reads the live caller CV after the handler returns. [Seven exact originals and171 independent premises](coverage/semantics/source-missing-name-cv-review.json) retain private321, including local scope, handler-false fallback, throw priority and include retirement. A later missing-target warning still returns null after handler writes. Actual324 passes strict compilation with reviewed bound-Fiber/Generator/collector/array compatibility; wider conversion callbacks remain required.

[Stringable ordinary computed-name CVs](coverage/semantics/source-stringable-name-review.json) now keep returned name bytes through cast-receiver retirement, then read the live target. Destructor exceptions retain the default missing-target warning while suppressing an eligible registered handler. Eight exact originals and134 independent premises retain private325; actual329 passes strict compilation with reviewed current-parent compatibility. Special targets and wider producers remain required.

[Array-valued ordinary computed-name CVs](coverage/semantics/source-array-name-review.json) now resume warning handlers with fixed `Array` bytes before live target lookup. Borrowed array children can retire inside the handler; handler and child exceptions abort the fetch. Seven exact originals and117 independent premises retain private331; actual335 passes strict compilation. Wider producers remain required.

[First dimension reads](coverage/semantics/source-dimension-emission-review.json) now retire owned include/eval operands at the key compiler line before reading an ordinary CV base and CV or literal key. A narrow writable array-property receiver separates the protected array; a later literal property warning resumes with fixed null. Seven exact originals and245 independent premises retain their private336 cuts; actual340 passes strict compilation. Wider emission and receiver forms remain required.

[Named noarg DIM key calls](coverage/semantics/source-call-key-emission-review.json)
now retire owned include/eval operands at the first INIT line. The ordinary CV
base stays borrowed through the call; the returned key is fixed before live base
lookup. Six exact originals and128 independent premises retain private341;
actual343 passes strict compilation with reviewed Generator storage compatibility.
Dynamic/builtin/argument/fallback calls and wider emissions remain required.

[Direct named noarg ECHO calls](coverage/semantics/source-direct-call-emission-review.json)
retire owned include/eval operands before INIT, including late function installation.
Returned Stringable temporaries and reference wrappers survive until bytes are
printed; a mutated referent can retire earlier without losing successful cast
bytes to its pending exception. Ten exact originals and247 independent premises
retain private344; actual349 passes strict compilation over CALLS362. Borrowed CVs
keep their separate release path; wider call and output consumers remain required.

[Direct ECHO with one positional CV argument](coverage/semantics/source-echo-cv-call-review.json)
retires the owned source operand at INIT5 before SEND8 reads the live CV.
Returning warning handlers send fixed null; function, retirement and handler
errors retain their priority. Returned temporary/reference owners preserve bytes
after argument mutation, with conversion and final destruction at ECHO8. Nine
exact originals and236 independent premises retain separate private349 cuts;
actual351 passes strict compilation. Broader call shapes remain required.

[Direct ECHO with one named CV argument](coverage/semantics/source-echo-named-cv-call-review.json)
now keeps INIT5 before binding and CV demand. Known second-slot sends use ECHO8;
late-bound names use ECHO7. Defaults, unknown-name priority and fixed-null warnings
retain live handler writes. Returned temporary/reference owners keep bytes after
argument mutation. Seven exact originals and204 independent premises retain private351; actual354
passes strict compilation. Wider call shapes remain required.

[Direct ECHO through an ordinary dynamic callee CV](coverage/semantics/source-echo-dynamic-cv-call-review.json)
now retires the source operand at INIT5 before selecting the live callable.
Undefined-CV handlers retain fixed null; selected invokers survive callee deletion,
and returned temporary/reference owners keep bytes before destruction. Callable
and ECHO lines remain distinct. A returned cast can publish a function and survive
later eval history replay. Nine exact originals retain their private354 cuts;
independent277 premises pass. Actual356 passes strict compilation. Wider callee
and argument producers remain required.
The one-positional-CV increment preserves selected targets across SEND warnings,
with INIT5/call7/SEND-ECHO9 and existing temporary/reference output owners.
Throwing SEND handlers retire the invoker at9; ordinary body throws retire it at7.
Nine fresh exact originals and231 independent premises pass; actual358 passes
strict compilation. One named CV argument now separates SEND/ECHO line9 from the
CV's source line11, preserving the second slot, defaults, unknown-name priority
and captured-null warnings. Eight exact originals and251 independent premises
retain private358; actual358 passes strict compilation. Earlier cuts retain their
inputs; wider callees/arguments remain required.

[Named Stringable `chdir`](coverage/semantics/include-named-current-review.json)
admits `directory:` through computed and owned callable forms. The installed
[configuration unpack increment](coverage/semantics/include-unpacked-current-review.json)
preserves captured array arguments and has separate source and paused-state checks.
[Stringable SET](coverage/semantics/include-set-current-review.json) is installed
with bounded source and callback ownership/cleanup checks.
[Raw/effective INI paths](coverage/semantics/include-ini-prefix-review.json)
preserve full `ini_set` bytes while file requests and SET old returns use the
C-string prefix. The public object invocation union accepts 13 source cases
and thirteen finite fixtures/675 assertions at `6e7ddca894`.
[Stringable Restore](coverage/semantics/include-stringable-restore-review.json)
converts weak options using full-name lookup, restores the initial raw path for
exact names and preserves callback writes on empty, case and NUL-name misses.
Current checks preserve the caller's argument vector across the callback.
[Two-slot INI conversion](coverage/semantics/include-stringable-ini-option-review.json)
converts the option before rejecting array/object values or looking up its full
name, and returns the raw old value after callbacks. Current property and captured
unpack checks pass three source tuples and one finite fixture/83 assertions.
[Raw INI readback](coverage/semantics/include-ini-readback-review.json) returns
full `include_path` bytes, including callback writes. Primitive/null Restore
parsing preserves strict direct refusal and weak explicit `Closure->__invoke` calls. Eligible unary
null deprecations suspend for handlers; normal return, false fallback and throw
preserve raw mutation and caller arguments.
[Unary CONFIG PIPE](coverage/semantics/include-config-pipe-review.json) preserves
the held left value across RHS factory effects and authenticates its compiled
send/callback site. Ordinary Closure PIPE follows caller strictness; normal and
throwing borrowed-warning callbacks preserve raw mutations and caller frames.
Stringable CHDIR PIPE uses post-callback CWD; six source comparisons and 124
directory-provider assertions cover held operands, refusal and throw. Failed CHDIR
warnings now resume eligible handlers: normal return yields false after their
CWD/raw writes, while throw preserves caller arguments and both internal and
wrapper trace operands. [Reporting configuration](coverage/semantics/reporting-ini-review.json)
separates full INI bytes, the live signed32 mask and modified-entry Restore,
including suppression and handler writes. [Diagnostic ingress](coverage/semantics/reporting-diagnostics-review.json)
adds runtime `E_STRICT` deprecations and lossy reporting conversions, retaining
captured values, caller frames and initializer locations through callbacks.
[Compound initializer eval locations](coverage/semantics/compound-eval-location-review.json)
retain authenticated filename owners and child lines through callbacks and later
eval execution, separately from callback scope and compiler exception locations.
[Registered startup inputs](coverage/semantics/startup-ini-review.json) supply
the initial `error_reporting` and `include_path` bytes before compilation.
Getters and Restore retain those facts through setters, silence and callbacks;
null reporting and an explicit empty string have distinct masks. Nine exact
profile comparisons, 99 state premises and 15 transport controls pass.
[Live display errors](coverage/semantics/display-errors-review.json) add nullable
startup bytes, raw get/set/Restore and ordered stdout/stderr/off diagnostics.
Emission captures its destination after callback effects; later writes retain
earlier output. Eleven exact comparisons, 76 state premises and 17 transport
controls pass. The held fatal/shutdown source also matches at the actual231
composition, freezing its destination after rendering and before the queue.
Wider display/startup directives and diagnostic consumers stay open.

[Live precision](coverage/semantics/precision-review.json) preserves raw startup,
get/set/Restore and callback-time float formatting. Parser-folded literals retain
creation precision; later eval compiler operands follow genuine callback resume
epochs. Deferred initializer ASTs convert with the live value. The original
16 source/profile,194 state and12 transport cuts remain separate from later
compiler source/state checks. Wider configuration remains required.

Assertions now distinguish startup modes `-1`, `0` and `1` before compilation,
including eval/include replay. Known direct calls capture normalized descriptions;
dynamic and first-class calls keep ordinary argument evaluation. Twenty-five
retained source/profile comparisons and 64 reached-state premises pass, including
fresh `AssertionError` code 1 and supplied `Throwable` identity. Runtime INI updates
preserve initial/current raw bytes and restore state; quiet quantities, positive
mode 2, negative-boundary refusals and nested/throwing warning handlers match
twelve further source profiles. Deprecated options now retain old-value snapshots,
live callback failure policy and pending exceptions through selected-receiver
cleanup. Constant protection survives parked handlers. The
[options ledger](coverage/semantics/assertion-options-review.json) keeps 20 source
originals and 117/67 reached checks at separate cuts; the excluded Count observer
and valid foreach companion stay distinct. [Bounded quantity warnings](docs/semantics/ASSERTION-QUANTITIES.md)
preserve frozen numeric modes after handler raw writes, throw or restore. Runtime
string carriers retain INI identity while ordinary consumers observe bytes. Four
reentrant request-string lifetime probes remain explicit Unsupported with zero
native agreement. Fresh updates recapture the current original, and warned restore
preserves pending Throwable identity while enabling assertions again. Two new safe
originals and182 source-frontier checks plus one pure trace query pass at57ee.
Retained-entry Stringable SET now preserves once-only conversion, post-conversion
old returns, refusal/shared throws and converted trace arguments. Handler retirement
runs the Option destructor without a ghost owner. Three new originals and236
frontier checks pass at7eaee. Warned Stringable RESTORE retains unary converted
arguments and commits the saved original through handler retirement/shared throw.
Two new originals and211 frontier checks pass at05db. NaN SET now preserves the
pre-conversion old return separately from handler-modified raw state and commits
through an original pending Throwable without a second handler entry. Two originals,
247 source-frontier checks and eight pure companions pass atc2b195. Cleared-original
restore now retains NULL raw separately from its empty getter and parsed mode12.
Two safe originals,323 frontier checks and12 pure exclusion queries pass at242576;
shared throw and later no-op restore preserve the state. Retained-owner Stringable
descriptions convert before truth and finish an entered assertion despite live mode0.
Cast-time traces retain the object; failure traces use the converted string. Three
new originals,265 frontier checks and4 pure ownership queries pass atb4ea. Quiet
weak scalar descriptions now replace the actual call argument before failure handling;
integer17 and named false/NULL controls agree in two fresh originals with217 checks
at088d. NULL and source variables remain unchanged. SET/NaN from NULL, last-owner
entry, description warning conversion and unpack remain required alongside wider forms.
Logical-not generated descriptions now preserve Zend precedence and compound-child
parentheses. Two fresh originals,79 source-frontier checks and2 pure export-context
queries pass atbb485b; wider exporter forms remain open.
Run the [catalogue](tests/semantics/assertion_cases.json)
with `method_runtime.py --catalogue tests/semantics/assertion_cases.json`.

Root-terminal `__halt_compiler()` now discards its payload without an exit event.
Ordinary `__COMPILER_HALT_OFFSET__` reads fold the original file's byte offset,
including plain/global reads inside a namespace; namespace-relative local constants
keep ordinary lookup. Two fresh originals and 104 source-frontier checks plus 20 pure
queries pass at c78beb627. [HALT review](coverage/semantics/halt-compiler-review.json)
records that cut. Selected `defined`/`constant` calls now use the first HALT
registration for their compiled filename across include/eval; fixed literal
`defined` retains PHP's separate false result. Two sources and 375 state premises
pass in the [lookup increment](coverage/semantics/halt-lookup-review.json).
Ambiguous compilation, other direct calls, absent value lookup and wider source
profiles/consumers remain required. The [catalogue](tests/semantics/halt_compiler_cases.json)
uses the existing `method_runtime.py --catalogue tests/semantics/halt_compiler_cases.json`.

[Ordinary string interpolation](docs/semantics/SOURCE-INTERPOLATION.md) follows
effective CAST/FAST_CONCAT/ROPE order, retaining fetched temporaries separately
from live variables through Stringable and warning callbacks. Nine exact source
comparisons and 111 distinct owner/state premises pass at their recorded cuts;
[Legacy dollar-curly compiler notices](coverage/semantics/dollar-curly-review.json)
now preserve syntax/printing, physical pre-child warning locations and main/include
handler delivery. Five profiles and 37 compiler premises pass; early eval delivery
and broader interpolation producers/source contexts remain required.

All required non-system inputs are local and pinned. See
[dependencies/README.md](dependencies/README.md) for prerequisites, provenance,
licenses and offline dependency builds. The PHP source contains matching PHPT
inputs; `corpora/bolaray` contains the pinned application snapshots.

```sh
./scripts/build-deps.sh
./scripts/verify-inputs.py
```

Build the adapter with `make build`. Use `bin/php-syntax check FILE`,
`bin/php-syntax parse FILE` (checked transport), or `bin/php-syntax pretty FILE`.
`--elaborate` additionally checks a typed SpecTec fixture; `--short-tags` enables
short opening tags. Repeat `--ini KEY=VALUE` for source encoding profiles, for
example `--ini zend.multibyte=1 --ini zend.script_encoding=SJIS`.
`print-ast` checks and prints an edited transport file.
[Representation and checking](docs/DESIGN.md) explains the data path.

No application or PHPT helper code is executed to collect syntax. Parsing and
compilation checks are separate; PHP-Parser's version selection is best effort,
so validation compares its raw outcomes with the pinned Zend parser.

`make test` runs extraction, malformed-value, targeted syntax and generated
interaction checks. `make validate` checks all imported source candidates in
four independently checked shards and verifies their complete ordered merge;
`make inventory` regenerates source coverage evidence. See
[validation](docs/VALIDATION.md) for classifications and normalization.

`bin/php-semantics FILE` executes the currently implemented rules through checked
SpecTec values and emits a structured observation. `make test-semantics` runs the
source execution regressions; unfinished behavior returns explicit Unsupported.
Reviewed truth/logical operators and ternary preserve PHP's distinct compiler
and runtime phases; [truth evidence](coverage/semantics/truth-review.json) records
source comparisons, selected-value copying and budget resumption.
Eligible classes and named functions publish in compilation order, so earlier
notices and declarations survive later compiler diagnostics. Parser and modifier
preflight preserve their distinct first errors, while declaration history binds
entry availability, repeated execution and failure. Compile-stop freezes caller
snapshots and preserves completed effects; it retires the active source request
without ordinary unwinding. [Publication evidence](coverage/semantics/compiler-publication-review.json)
links source30, history107, modifier286 and later interaction checks.
Wider startup directives and remaining diagnostic producers stay open.

[Loose and ordered comparisons](docs/semantics/COMPARISONS.md) now cover scalar
and array values, with [independent evidence](coverage/semantics/comparison-review.json).
[Prefix/postfix increment and decrement](docs/semantics/UPDATES.md) execute for
current scalar/array locations, preserving copied results and diagnostic order;
[independent review](coverage/semantics/incdec-review.json) records the source and resumption gates.
[Direct-CV warning callbacks](coverage/semantics/incdec-warning-review.json) now
restore captured bool/null values even after a handler throws; strings restore
only after normal handling. Aliases, fresh handlers and copied results are checked.
[Before-commit restoration](coverage/semantics/incdec-restoration-review.json)
now runs callback-installed object/array destructors while the old slot is visible,
then restores captured scalars before propagating pending throws. Aliases, ordered
cleanup and Previous chains retain their actual owners. Late typed sources,
destructor ownership changes, replacement/destructor exit and wider update
locations remain required.
[Named warning-handler exits](coverage/semantics/incdec-exit-review.json) now
finish handler-local cleanup before restoring captured bool/decrement-null
values; strings retain callback writes. Registry restoration, caller temporaries,
nested handlers, surviving aliases and request exit status are checked through
shutdown. [Handler-local cleanup cancellation](coverage/semantics/incdec-exit-cancellation-review.json)
now restores safe captured values and resumes real caller catch/finally, preserving
Throwable identity, aliases, registry changes and request exit status. Unsafe
restoration targets remain required.
[Caller-temporary cleanup cancellation](coverage/semantics/incdec-parent-exit-cancellation-review.json)
now resumes caller catch/finally after the warning helper finishes: bool/null
restore their capture while strings skip the store. Request status, later destructor
writes and retired operand/finally owners are preserved. Unfinished binary
operands retire in source lifetime order. Wider owning holders and control forms
remain explicit dependencies.
[Owning invokable warning callbacks](coverage/semantics/incdec-callback-exit-review.json)
now release receiver and saved handler before bool/decrement-null restoration;
strings skip the store. Registry replacement/clearing and surviving owners persist;
callback-destructor throws resume caller catch/finally. Seven new and one repaired
source agree, with 568 genuine SL conditions.
[Owning handler-local cleanup cancellation](coverage/semantics/incdec-callback-exit-cancellation-review.json)
now carries the supplied Throwable through both callback releases before safe
bool/null restoration or string store skip, retaining caller catch/finally,
registry/alias effects, secondary Previous and request status 23. Five new
originals agree, with 647 genuine SL conditions.
[Callback-owner destructor exits](coverage/semantics/incdec-callback-destructor-exit-review.json)
now preserve caller operands until safe bool/decrement-null restoration or string
store skip. Integer exit replaces the earlier status; string exit retains it.
Four originals agree, with 553 genuine SL conditions. That first cut refused a
pending user Throwable before caller cleanup with zero agreement credit.
[Destructor exits with a pending Throwable](coverage/semantics/incdec-callback-destructor-exit-pending-review.json)
now retain a suspended Throwable owner through helper completion and caller-temporary cleanup,
then release the retained owner before shutdown. Bool/decrement-null restore
before parent cleanup; strings skip the store, and later destructor writes survive.
Three new and one repaired original agree, with 610 genuine SL conditions. Admission requires
a MAIN caller and a direct destructor scope without local cells, held roots or
owned pending operands. Nested/outer contexts, parent/cause cleanup throws or
exits, unsafe targets and wider callbacks/control remain required.
All twelve [compound assignments](docs/semantics/UPDATES.md) preserve captured
targets, delayed reads and alias ownership; [independent evidence](coverage/semantics/compound-review.json)
records 2,639 exact source comparisons and the corrected diagnostic phases.
Numeric `+=` now retains a captured leading-numeric left operand through named
warning handlers and stores into the selected untyped reference cell. Rebinding
the current variable name does not redirect that store; a supplied throw cancels
it. Three exact originals and 360 focused SL premises cover commit, selected-cell
history, default Warning, throw cleanup and refusal checks in the
[compound ADD warning ledger](coverage/semantics/addassign-warning-review.json).
This direct-CV route requires a quiet numeric RHS at commit; typed/owning/expired
targets, wider operands and callbacks remain partial.
Initially plain CV `+=` destinations now retain their selection through a named
warning handler that creates a late alias. Successful replacement detaches that
alias and writes a new non-reference CV cell; a supplied throw preserves the
alias and callback writes. Three exact originals and 387 focused SL premises
cover capture, default Warning, commit/cancellation and public guards in the
[plain-CV compound ledger](coverage/semantics/addassign-cv-warning-review.json).
The RHS remains defined, plain and quietly numeric; owning/constrained targets,
wider producers and lifecycle paths remain partial.
[Stringable compound concatenation352](coverage/semantics/compound-string-live-rhs-review.json)
reads a defined RHS CV after the left conversion, preserves the non-reference
self-CV fast path, and retains evaluated temporary/reference operands through
the final store. Thirteen exact originals cover live rebinding, aliases, copied
expression results and normal or throwing operand cleanup. The249 independent
reached premises and current-composition gate retain separate records.
[Named static-property Stringable compounds356](coverage/semantics/static-compound-string-review.json)
preserve the initially selected plain slot or reference cell across callbacks,
including typed final results and PHP's retained reference-type history. Twelve
exact originals and368 reached premises cover live RHS reads, inherited slots,
alias rebinding, reference history, temporary cleanup and access-error priority.
The actual344 compiler/init gate retains its separate accepted record.
Direct ordinary-method calls retain `self`, `parent` and `static` selection through
conversion and nested calls. Six further originals and323 reached premises cover
lexical/called scope, private shadows and captured-reference rebinding.
The separate actual347 composition passes compilation and initialization.
Dynamic class expressions now select the class once before RHS evaluation;
callback changes to the selector preserve that destination. Five new exact
originals and241 reached premises cover helper and temporary object selectors,
scalar continuation, captured references and typed expression results.
The separate actual349 composition passes compilation and initialization.
Computed static-property names now read direct name CVs after RHS evaluation
and preserve evaluated name values or reference cells. Six further originals
cover that timing, cold initialization with owned RHS temporaries, selected class
roots, typed results and multiline access-error cleanup. Another295 independent
reached premises validate queued owners, resolved-name authority and resumption.
The separate actual353 composition passes compilation and initialization.
[Stringable computed static-property names371](coverage/semantics/static-compound-string-review.json)
freeze the selected class and converted name, check the property address, then
retire the receiver before reading the live row, reference cell and RHS. Failed conversion plus throwing cleanup
preserves empty-name lookup and the Error-to-destructor-to-cast exception chain.
Eight of nine exact originals pass at separate cuts; the pending-masks original
remains required with an unchanged 60-second CLI timeout and zero agreement.
A separate cold double-throw witness and 155 state premises pass on a 361-module
cut: empty-name lookup leaves defaults deferred and retires the RHS without
stringifying it, preserving Error-to-destructor-to-cast chaining.
Prior 123/private 238 cuts remain separate. A tested cut with 360 modules passes
compilation, 238 affected state premises and 23 constant-export/control premises.
One constant lookup per insertion reduces calls from 689,580 to 229,972 over
a matched prefix of 400 steps while preserving the returned tuple exactly.
A tested 361-module cut passes compilation and 14 ownership controls for an
explicit empty statement-root case. Its same-parent prefix tuple remains equal;
instrumented task dispatch costs fall, while original 7 still hits CLI 60 timeout.
A verbatim access-lookup clause reorder passes 11 direct controls and preserves
the complete same-parent prefix tuple. Its modest instrumented saving does not
close the required original 7 timeout; source and prior state cuts are not renewed.
Inherited static `Closure::fromCallable` calls now retain lexical and called class
selection through Stringable computed NAME retirement and live RHS conversion.
Saved selection evidence survives the callback and final Closure retirement without
adding an owner. Separate ordinary and wrapper originals match native PHP;
213 carrier premises and 359 wrapper selection/authority premises retain their
distinct 363-module cuts. Other Closure families and required original 7 remain open.
An inherited nonstatic `fromCallable` wrapper also retains its exact receiver-bearing
selection through the distinct RHS callback. Explicit Closure release retires the
sole receiver; saved selection evidence remains valid without owning either object.
Separate ordinary and repaired wrapper sources agree with native PHP on 367-module
cuts, with 430 wrapper premises. Required original 7 keeps its separate CLI 60 timeout.
First-class `Closure::fromCallable(...)` can now be invoked as a variable factory.
Calls retain the factory during arguments; the returned method Closure keeps
its receiver after factory retirement. Callback access uses the invoking USER scope.
Eight factory sources and 526 state premises retain separate 367-module cuts.
Literal `->__invoke(callback: ...)` now preserves the selected factory when
arguments clear its caller cell. Invocation USER scope controls private access;
errors retain both the API and Closure invoke frames. A separate variable control
and four explicit sources agree on 368-module cuts, with 552 state premises.
Literal first-class `->__invoke(...)` aliases now reuse the original factory
identity and creation authority. The selected call retains it as original and alias
caller cells retire; the returned Closure owns its receiver independently. A REAL
control and repaired factory source agree on separate 370-module cuts, with 610
factory premises. Wider invoke/factory forms and original 7 remain open.
Captured factories now select finite Throwable getters with a nonowning source
certificate. The getter reads the receiver's live message after factory retirement;
clones retain the same receiver, and equality ignores the creation certificate.
The direct control and two repaired sources agree on separate 371-module cuts,
with 191 state premises. Wider targets and required original 7 remain open.
Captured factories now select static `Fiber::getCurrent`. Frozen callback members
survive name mutation and factory/array retirement; the returned Closure reads
the actual current Fiber across suspension. A direct control and repaired source
agree on distinct 371-module cuts, with 270 state premises. Other captured Fiber
targets and required original 7 remain open.
Captured factories also select bound `Fiber::isSuspended`. The returned Closure
retains only its receiver after factory and callback retirement; frozen selection
survives a referenced-name change through real suspension and termination. Direct
and repaired source agreements remain distinct on the tested 372-module cuts,
with 241 state premises. Other targets and original 7 remain open.
Captured factories now select static `Fiber::suspend` with no bound input.
The parked result marker keeps the selected Closure alive after its caller cell
retires; resume returns the exact value and cleanup releases the last owner.
The direct and repaired sources agree on distinct 372-module cuts, with 299 state
premises. Wider targets and original 7 remain open.
Captured factories additionally select bound `Fiber::resume`. Its saved caller
keeps the Closure and receiver through transfer after argument evaluation clears
the caller cell; last-owner cleanup releases both before final weak reads. Direct
and repaired sources agree on distinct 374-module cuts, with 343 state premises.
Other targets and original 7 remain open.
Captured factories also select bound `Fiber::throw`. The owned argument buffer
injects the same Throwable into the suspended callback while its saved caller
retains the Closure and receiver. Handled termination returns null and releases
all three; direct and repaired sources agree at distinct 374-module cuts, with
439 state premises. The separate 375-module composition passes compilation and
initialized SL439. A new unhandled injection through ordinary child finally
also agrees in direct/captured originals at 204200d1f/375; 542 premises (433
genuine/derived, 109 controls) validate callback/capture retirement and the outer
catch's sole exception owner. Scalar 7 on an INITIAL Fiber raises TypeError before
transfer; two direct/captured originals and 340 premises at 47b318154/375 validate
the generated scalar trace and capture/receiver/callback retirement before catch.
Valid Throwable arguments instead raise FiberError on that INITIAL path; its trace
retains the supplied object until caught-cell null. Two new originals and 456
premises pass at 62405de0a/375, including retirement before the final weak reads.
The existing rules require no change. Wider throw/error paths and original 7 remain open.
Captured factories now select bound `Fiber::getReturn` for a defined ordinary
object result. Direct and repaired sources preserve identity and separate
capture/Fiber retirement from returned-object retirement; 413 state premises
pass at 3a31fc727/375. Original Unsupported and fixture failure retain zero credit.
Captured factory `Fiber::start` also forwards an ordinary named object through
the original API buffer. Direct/repaired sources and 472 state premises preserve
identity, ownership after callback-local null and ordinary buffer/capture cleanup;
the callback's literal return 7 remains distinct from the null API result.
Captured factory `Fiber::__construct` also preserves repeated-constructor
rejection with a valid fresh Closure argument. Direct/repaired sources and 489
state premises verify the error's argument trace and separate callback cleanup.
Explicit `__invoke` agrees in two new originals; 536 state premises distinguish
its copied buffer from two trace argument edges and validate caught-null cleanup.
Captured factories also select bound `Fiber::isStarted`, `isRunning` and
`isTerminated`. Three direct and three repaired captured originals preserve frozen
names across INITIAL, running, suspended and terminated phases. The reduced 1287
state premises check authentic caller/global owners and shared final capture/Fiber
retirement;
original Unsupported and failed admission retain zero credit.
[Ordinary binary operators and casts](docs/semantics/ORDINARY-OPERATORS.md) now pair
source dispatch with scalar/array conversions, delayed variable reads and concat
compile/runtime diagnostics. The admitted catalog adds 1,506 exact source inputs;
seven preserved request-environment boundaries now have separate explicit-input witnesses.
Integer conversion warnings for `%`, shifts and mixed scalar bitwise operations
now suspend through registered handlers for defined CVs, literal/unary/ternary
copies and reference-assignment/named byref-call results. Real temporary owners
preserve reference cells across rebinding; bitwise conversion follows Zend's
compiler slot order. [Direct-CV](coverage/semantics/integer-operator-warning-review.json)
and [copied-operand](coverage/semantics/integer-operator-copy-review.json) evidence
retain separate cuts. Wider producers and object conversion remain open.
Leading-numeric-string `+` now suspends through named warning handlers for two
direct CVs with preexisting untyped reference cells. Both cells are selected before
conversion; cached numbers survive handler writes, while the next conversion reads
its selected referent. Three exact originals and 321 reached state premises cover
return, supplied throw and a second warning with default fallback.
[ADD warning evidence](coverage/semantics/arithmetic-warning-review.json) retains
the original Unsupported baseline; other operand classes and wider arithmetic
callback paths remain partial.
ADD now reports the live selected scalar types when a warning handler makes
the next RHS conversion fail. A completed RHS warning still delivers its cached
number despite later invalid writes. Two exact originals and 159 genuine state
premises check the ordinary TypeError, unchanged destination and warning priority.
[ADD failure evidence](coverage/semantics/arithmetic-failure-review.json) retains
the original Unsupported baseline; wider operand and lifecycle forms remain partial.
Leading-numeric-string `/` now retains selected reference cells and captured
numbers through the same bounded named-handler route. A handler can make the
next divisor zero; a second handler cannot replace an already-captured zero by
writing `7`. Two exact originals and 224 genuine state premises check the default
warning, original-line `DivisionByZeroError`, unchanged assignment destination and
catch/finally continuation. [DIV evidence](coverage/semantics/division-warning-review.json)
retains the original Unsupported baseline; wider operands and lifecycle paths
remain partial.
Unary `+` and `-` now capture leading-numeric strings from defined non-reference
CVs before named warning handlers. Three exact originals and 323 genuine state
premises check callback writes, supplied throws with unchanged destinations,
negative boundary float delivery and a false-handler warning on the operand line.
[Unary evidence](coverage/semantics/unary-warning-review.json) preserves the
original failures; wider operand, callback and lifecycle forms remain partial.
Bitwise NOT now retains the converted long through named deprecation handlers
for finite in-range fractional floats in defined non-reference CVs. Three exact originals
and 324 genuine state premises check live writes, supplied throws, false fallback,
operand lines and public continuation guards. [BITNOT evidence](coverage/semantics/bitnot-warning-review.json)
retains the unchanged Unsupported baseline; wider domains remain partial.
Ordinary `**` now retains both primitive numbers through zero-base/negative-exponent
deprecation handlers. Callback writes cannot change the captured infinity or its
sign; a supplied throw preserves the pending destination. Three exact originals
and 366 focused SL premises pass in the
[power-warning ledger](coverage/semantics/power-warning-review.json).
Numeric-string warnings, wider operands/callbacks and wider `**=` forms remain partial.
Primitive plain-CV `**=` now commits its captured result even when the deprecation
handler throws. A late alias detaches before the same exception continues; the
outer assignment stays unchanged. Three exact originals and 407 focused SL
premises cover signed infinity, target storage and pending ownership in the
[power-assignment ledger](coverage/semantics/powerassign-warning-review.json).
Wider operands, targets, callbacks and lifecycle paths remain partial.
Plain-CV `%=` now keeps the first converted long through a fractional-float
deprecation, then reads the live quiet integer RHS. Normal return stores the
remainder; a supplied throw or live zero leaves the target and late alias intact.
Three exact originals and 362 focused SL premises check capture, cancellation,
default Deprecated, original-line `DivisionByZeroError` and budgets in the
[modulo-assignment ledger](coverage/semantics/modassign-warning-review.json).
Wider operands, targets, callbacks and lifecycle paths remain partial.
With a quiet integer left operand, a fractional RHS now keeps both converted
longs through its deprecation.
Normal `%=` detaches a late target alias; supplied throw or a captured zero divisor
preserves callback writes and aliases even after the live RHS changes.
Three exact originals and 404 focused SL premises pass in the
[RHS modulo ledger](coverage/semantics/modassign-right-warning-review.json).
With two fractional floats, plain-CV `%=` now orders both deprecations: capture
LEFT, run its handler, then capture the live RHS before its handler. A quiet
integer RHS after the first callback skips the second diagnostic. Success detaches
late aliases; either supplied throw or a captured zero preserves them. Five exact
originals and 929 focused SL premises pass in the
[ordered modulo ledger](coverage/semantics/modassign-both-warning-review.json).
An integral float RHS after the first callback also converts quietly: with cached
LEFT `12`, RHS `5.0` stores `2` and detaches alias `99`; signed zero raises
`DivisionByZeroError` before storage.
Three exact originals and 364 focused SL premises pass in the
[quiet float modulo ledger](coverage/semantics/modassign-quiet-float-review.json).
For initially plain variables, `<<=` and `>>=` now retain a fractional left
conversion through deprecation handlers, then read the live quiet integer count.
Success detaches a late target alias; supplied throw or a negative count preserves
callback writes and aliases. Four exact originals and 526 focused SL premises pass
in the [shift-assignment ledger](coverage/semantics/shiftassign-warning-review.json).
With a quiet integer left value, `<<=`/`>>=` also retain both converted longs
through a fractional-count deprecation. Success detaches a late alias; supplied
throw or a captured negative count preserves it. A captured count of `64` keeps
the original signed-right-shift result. Five exact originals and 674 focused SL
premises pass in the [RHS shift ledger](coverage/semantics/shiftassign-right-warning-review.json).
With two fractional floats, plain-CV `<<=`/`>>=` order both conversion
deprecations and retain each long after its own conversion. A quiet integer count
after the first callback skips the second diagnostic. Success detaches late aliases;
either supplied throw or a captured negative count preserves them. Six exact
originals and 1172 focused SL premises pass in the
[ordered shift ledger](coverage/semantics/shiftassign-both-warning-review.json).
An integral float count after the first callback also converts quietly. With
cached LEFT `-12`, `2.0` stores `-48`/`-3`; `64.0` stores right-shift `-1`.
Success detaches late aliases; negative counts error before storage. Five exact
originals and 629 focused SL premises pass in the
[quiet float shift ledger](coverage/semantics/shiftassign-quiet-float-review.json).
For initially plain variables, numeric `&=`, `|=` and `^=` now keep their fractional
left conversion through deprecation handlers, then read the live quiet integer RHS.
Success detaches late aliases; supplied throw preserves callback writes and the
same Exception. Five exact originals and 692 focused SL premises pass in the
[bitwise-assignment ledger](coverage/semantics/bitassign-warning-review.json).
With a quiet integer left value, numeric `&=`, `|=` and `^=` also keep both converted
longs through fractional-RHS deprecation. Success detaches late aliases; supplied
throw preserves callback writes and the same Exception. Negative RHS values remain
ordinary signed masks. Five exact originals and 724 focused SL premises pass in the
[RHS bitwise ledger](coverage/semantics/bitassign-right-warning-review.json).
With two fractional floats, plain-CV numeric `&=`/`|=`/`^=` order both conversion
deprecations and retain each long after its own conversion. A quiet integer RHS
after the first callback skips the second diagnostic. Success detaches late aliases;
either supplied throw preserves them. Negative masks still store signed integers.
Seven exact originals and 1421 focused SL premises pass in the
[ordered bitwise ledger](coverage/semantics/bitassign-both-warning-review.json).
An integral float RHS after the first callback also converts quietly. Cached
LEFT `12` with `5.0` stores `4`/`13`/`9`; negative `-1.0` gives XOR `-13`.
Success detaches late aliases; a supplied first throw preserves them. Five exact
originals and 634 focused SL premises pass in the
[quiet float bitwise ledger](coverage/semantics/bitassign-quiet-float-review.json).
Explicit array-to-string casts now suspend through named warning handlers for
a bounded plain-CV array input. The borrowed array adds no saved owner: replacing
or removing its CV still yields fixed `Array`, while a supplied throw preserves
the destination. Three exact originals and 326 focused SL premises check these
paths in the [array-cast ledger](coverage/semantics/array-string-cast-warning-review.json).
Empty/immutable/nested or owning arrays, wider operands and handlers remain partial.
Ordinary concatenation now stages array warnings for bounded plain-CV inputs.
A left-array warning keeps fixed `Array` before reading the live quiet RHS;
a right-array warning preserves the first converted string across callback writes.
Borrowed arrays gain no saved owner, and supplied throws cancel destination
assignment. Three exact originals and 405 focused SL premises pass in the
[concat-array ledger](coverage/semantics/concat-array-warning-review.json).
Wider arrays/operands and RHS rebinding after a left-array warning remain partial.
Concatenation assignment now stages a right-array warning for two bounded plain CVs.
The first string survives handler writes and RHS removal; normal commit overwrites
the target and detaches a late alias, while a supplied throw preserves it.
Three exact originals and 395 focused SL premises pass in the
[concat-assignment ledger](coverage/semantics/concatassign-array-warning-review.json).
Left-array warnings, wider operands/targets/callbacks and lifecycle paths remain partial.
[Destructuring and retained expression effects](docs/semantics/DESTRUCTURING.md)
now execute current scalar/array list patterns and nonvariable-left coalescing.
[Independent acceptance](coverage/semantics/destructuring-review.json) binds 263
new source cases, effect ordering, aliases and dense resumption.
Object/frame-dependent targets remain unfinished.
[Array unpacking](docs/semantics/ARRAY-UNPACK.md) now preserves key order, copied
values, reference history and compiler/runtime rejection phases. Its
[independent review](coverage/semantics/array-unpack-review.json) audits 155 exact
sources; Traversable objects remain unfinished. Array call arguments are covered by the later call-unpack checkpoint below.
[Iterator foreach](docs/semantics/ITERATORS.md) adds by-value source Iterator
callbacks with effective method selection, retained current values and abrupt
cleanup. Tentative-return declarations use real prototype order and runtime/file
warning delivery after publication. Early eval warnings suspend genuine
compilation at each publication; handler throws or exit preserve later class
publication, while user fatals stop it. Compiler fatal formatting retains the
primary diagnostic through source effects, nested eval/include compilation and
deferred runtime class-link failures.
Aggregate foreach acquires nested Iterator/Generator data, retires returned layers
before initialization and the original operand after initial Iterator valid-result
cleanup or Generator yield. A getter with an independently kept receiver may
rebind the original CV/reference before returning Iterator/Generator data or a
rejected raw value. For a known Aggregate return, the first self comparison reads the live
object-valued source CV/reference; deeper callbacks compare their owned returned
layer. An independently kept original may be the first returned layer before a
deeper getter rebinds the source again. Self returns from immutable inputs and
deeper layers are rejected; a nonobject original at the first comparison remains
Unsupported.
[Source comparison](coverage/semantics/foreach-source-comparison-review.json)
keeps the affected historical control separate from its earlier refusal.
Acquisition and cleanup throws preserve data/input order; reference traversal
accepts reference-yielding Generators and rejects Iterator/nonreference Generator
results. Retained foreach Generator close frames survive Fiber suspension with
one receiver owner. [Focused acceptance](coverage/semantics/foreach-aggregate-review.json)
keeps original source/state cuts separate. [Foreach NaN warnings](coverage/semantics/foreach-valid-nan-review.json)
retain raw valid results through ordinary handlers, reread live references after
handler writes and preserve iterator/input cleanup on suspension or throw.
Eight exact originals and eighteen genuine-source groups/495 ownership and
warning-authority premises pass at retained cuts.
Wider raw payload/operand modes and Aggregate ordinary-call unpack
remain required.
Ordinary source-function calls now unpack direct user Iterators through borrowed
callbacks. Integer and numeric-string keys send positional values; other string
keys bind named arguments. Raw current references survive key callbacks and are
read afterward, while reference-valued keys are unwrapped. Iterator cache, DATA
and raw INPUT owners retire before target entry; errors follow native cleanup
order. Sent copies may keep their values alive. Pending abort cleanup continues
after a destructor throws, preserving the previous exception.
By-reference warnings support null/bool/int/float payloads, including handler
mutation, Fiber suspension and throw; the callee receives a fresh reference cell.
Copied string payloads also preserve their original bytes through key/handler
writes, named variadic binding and Fiber park/throw; see the
[string review](coverage/semantics/iterator-call-unpack-string-review.json).
Authenticated interned-string references and scalar references changed to an
interned string now reread the handler's live value into a fresh private callee
cell, including named variadic binding and Fiber park/throw. See the
[interned reference review](coverage/semantics/iterator-call-unpack-interned-reference-review.json).
Copied object payloads now keep a separate owner before the by-reference warning
before the first send or after earlier fixed-slot arguments. Normal resume
transfers that owner to the fresh callee cell; throw retires the cache and
Iterator/input before fixed argument slots in parameter order, including reversed
named sends and real Fiber park/throw. See the
[object hold review](coverage/semantics/iterator-call-unpack-object-review.json)
and [fixed-slot review](coverage/semantics/iterator-call-unpack-object-sent-review.json).
One direct construction of a statically named Iterator implementation also admits
a failed extra name after fixed or extra named sends, or a failed fixed slot
after an extra named send with a by-value variadic tail. Argument
cleanup visits fixed slots before extra named entries. An authenticated private
object cell in an untyped reference variadic uses a separated logical rest array;
the original named-send owner retains the payload through a rest-item write.
See the [extra-named review](coverage/semantics/iterator-call-unpack-object-extra-named-review.json).
Earlier extra names retain their private cells through a second warning and
retire in insertion order, including real parked throw; see the
[extra-to-extra review](coverage/semantics/iterator-call-unpack-object-extra-extra-review.json).
Later positional copied objects in an untyped by-reference variadic also retain
earlier sent cells at an authenticated direct Iterator construction, with no
prior named extras. Packed rest items alias the original private cells; a rest
write releases the current payload before later body output. See the
[positional variadic review](coverage/semantics/iterator-call-unpack-object-positional-variadic-review.json).
Nullable single-class tails use the same positional ALIAS route, with type
verification after warnings and fresh private-cell sends. A caught TypeError keeps
the dereferenced payloads in its trace through request end. See the
[typed positional review](coverage/semantics/iterator-call-unpack-object-typed-positional-variadic-review.json).
Nullable single-class named tails retain aliases to the private sent cells in
their separately collected rest array. Clearing the current item destroys its
payload before later body output; a rejected class leaves only the earlier rest
item while the TypeError trace retains both named payloads. See the
[typed named review](coverage/semantics/iterator-call-unpack-object-typed-named-variadic-review.json).
Copied arrays at a direct statically named Iterator construction retain their
container through warnings into untyped fixed or positional variadic reference
parameters. The fresh private cell takes that owner; an element write can release
the child before later body output. Earlier fixed sends and reversed named slots
preserve parameter-slot retirement order after Iterator cleanup, including
parked throws.
Packed positional rest items alias the private cells; a nested current-item write
releases its child before later output while the earlier child is released during return.
See the [first-send review](coverage/semantics/iterator-call-unpack-array-review.json),
[fixed-slot review](coverage/semantics/iterator-call-unpack-array-sent-review.json)
and [positional variadic review](coverage/semantics/iterator-call-unpack-array-positional-variadic-review.json).
Nullable-array positional tails preserve the same warnings and packed aliases;
a later scalar is rejected during receive, and its TypeError trace retains the
earlier array and child after private call cells retire. See the
[typed array review](coverage/semantics/iterator-call-unpack-array-typed-positional-variadic-review.json).
Nullable-array named tails retain keyed aliases to the fresh private cells in a
separately collected rest array. A nested current-item write destroys its child
before later output; a rejected scalar leaves only the earlier rest item while
the TypeError trace owns its keyed array snapshot. See the
[typed named array review](coverage/semantics/iterator-call-unpack-array-typed-named-variadic-review.json).
Untyped named tails collect authenticated singleton private array cells as DIRECT
items in a separated logical rest array, retaining the original named-send owner.
A nested current-item write copies its container; both original children survive
through later body output and retire in named insertion order. This abstracts
Zend's shared rest table before the write, without claiming native table identity
or owner counts. See the
[untyped named array review](coverage/semantics/iterator-call-unpack-array-named-variadic-review.json).
An Iterator-owned untyped property returned by reference now retains a detached
object payload across the first positional warning at a direct construction and
untyped fixed reference target. The fresh callee cell is independent of the source
cell: a separate global alias survives its clearing. Warning and parked throws
release Iterator before the held object. A nonowning snapshot authenticates live
callbacks; cleanup receipts remain valid after the source cell retires. See the
[property reference review](coverage/semantics/iterator-call-unpack-reference-object-review.json).
The same stable property-reference route now retains an array container separately
from its raw cell. A nested write in the fresh callee cell copies the container
when a global alias retains the original, leaving its child alive through body
output until that alias is unset. Without the alias, the child retires before
later output. Warning and parked throws release Iterator before the held
container and its child. See the
[reference array review](coverage/semantics/iterator-call-unpack-reference-array-review.json).
The same first send also accepts a key naming the first fixed untyped reference
parameter. It retains the captured payload and fresh callee cell, including source
aliases, array copying, handler throws and Fiber suspension. Named history still
rejects a later positional key before another warning or target entry. See the
[named reference review](coverage/semantics/iterator-call-unpack-named-reference-review.json).
Initial named reference sends can also select later fixed parameters. Earlier
defaults bind before the body, warning numbers and argument count use the selected
slot, and handler writes cannot retarget its captured key. Missing required earlier
arguments raise the real error while its trace retains the supplied payload. See
the [reference-hole review](coverage/semantics/iterator-call-unpack-reference-holes-review.json).
Initial property-reference sends also admit the exact nullable class and array
type shapes at fixed by-reference targets. Types are checked at receive; a later
integer write through the fresh callee cell is allowed and leaves source aliases
intact. Receive failures retain payloads in real TypeError traces until release.
See the [typed reference review](coverage/semantics/iterator-call-unpack-typed-reference-review.json).
Later object property-reference sends now accept free fixed untyped reference
parameters after earlier fixed arguments. Prior private cells and the current
detached payload stay separate, including repeated returns of one raw property.
Reversed named sends release failed arguments in parameter order; duplicate or
positional-after-named keys fail before another warning. See the
[noninitial reference review](coverage/semantics/iterator-call-unpack-noninitial-reference-review.json).
Later array property-reference sends use the same fixed untyped slots. The
detached container becomes a fresh private cell; repeated source arrays stay
independent under nested writes, and source aliases retain their children.
Warning throws and Fiber injection preserve Iterator-before-argument cleanup.
See the [noninitial array reference review](coverage/semantics/iterator-call-unpack-noninitial-array-reference-review.json).
Later fixed reference targets also admit the existing exact nullable class/array
shapes. Types are checked at entry; incompatible later writes use private cells.
Receive errors retain earlier and current payloads in ordinary trace arguments,
while warning throws and Fiber injection precede receive verification. See the
[noninitial typed reference review](coverage/semantics/iterator-call-unpack-noninitial-typed-reference-review.json).
Untyped positional variadics also accept stable property-reference object/array
payloads. Packed rest entries alias distinct private cells; original extra-argument
owners survive `unset($rest)`, and source aliases retain ordinary array COW. See the
[positional variadic reference review](coverage/semantics/iterator-call-unpack-reference-positional-variadic-review.json).
Typed positional reference variadics now admit the exact nullable class/array
shapes. Types are checked on receipt; later incompatible private-cell writes
remain legal. Partial receive errors keep all supplied values in owning trace
arguments. A later warning throw or Fiber injection precedes even an earlier
receive mismatch.
See the [typed variadic reference review](coverage/semantics/iterator-call-unpack-reference-typed-positional-variadic-review.json).
Valid NaN warnings retain the raw return through handler mutation, Fiber parking
and throw. One numeric reread distinguishes copied NaN from a live reference;
the raw return retires before current or iterator teardown.
Plain source-function calls also unpack Generator operands into by-value
parameters. Reference yields become snapshots before resume; named keys use the
ordinary binder. Native iteration adds no method trace frames, and temporary
versus retained Generators preserve their distinct finally/cache lifetimes.
See the [Generator unpack review](coverage/semantics/generator-call-unpack-review.json).
Array `yield from` producers also unpack through their authentic delegated table
and current cache. By-value sends preserve reference snapshots and repeated-row
COW; temporary and retained Generators keep distinct abort/finally cleanup.
See the [delegated-array review](coverage/semantics/generator-call-unpack-array-delegation-review.json).
Shared Generator chains also unpack through the real leaf cache, ending in a
paused value yield or active array delegation. Child returns resume parent tails;
snapshots, real traces and parent/child cleanup retain their existing owners.
See the [Generator-chain review](coverage/semantics/generator-call-unpack-generator-delegation-review.json).
Direct detached roots also unpack when the copied child return owns no heap
nodes. Their object, array and reference caches survive child retirement; key
errors preserve the real return continuation for a later explicit next.
See the [detached-child review](coverage/semantics/generator-call-unpack-detached-child-review.json).
Source Iterator `yield from` leaves also unpack through active Generator chains.
The real raw cache is captured after key callbacks; snapshots preserve reference
mutation, row COW and cache lifetime across next-callback errors.
See the [Iterator-leaf review](coverage/semantics/generator-call-unpack-iterator-delegation-review.json).
Aggregate-acquired Iterator leaves also use the authenticated acquisition receipt.
Acquisition/input owners release before rewind; the saved receipt owns nothing.
Independent Aggregate or Iterator aliases retain their own cleanup lifetimes.
See the [acquired-Iterator review](coverage/semantics/generator-call-unpack-acquired-iterator-review.json).
Aggregate-acquired Generator leaves also unpack through active Generator links.
Their copied raw cache and child owners stay distinct; generic iterator mode
discards child returns, preserves method receivers and orders child close before
parent finally and cached values.
See the [acquired-Generator review](coverage/semantics/generator-call-unpack-acquired-generator-review.json).
Active shared chains may also end in detached roots whose copied return owns no
heap nodes. Their null key raises the real unpack error before argument sending;
retained caches, later next/return/tail execution and cleanup preserve initialization
history. A direct middle next can consume pending initialization without advancing.
See the [nested-detached review](coverage/semantics/generator-call-unpack-nested-detached-review.json).
Aggregate ordinary-call unpack, owning copied returns, other pending-initialization
send/throw, Generator by-reference
call targets and callback methods, nonnumeric raw valid changes, request/plain
reference strings and handler replacements with
those strings, other typed array warnings, broader array/COW interactions,
other reference sources, named variadic reference sends and live
payload replacements,
general shared named buffers and
other type shapes and wider-site variadic object warnings remain
required.
[Generators](docs/semantics/GENERATORS.md) receive arguments eagerly and defer
ordinary bodies in object-owned frames. Value yields, literal iterator methods,
`getReturn`, `send`, `throw` and value `foreach` retain real resumer scope and
traces. Inputs survive initialization; exception injection preserves ordinary
catch/finally execution and exception identity. A pending `send` on a detached root
with a nonowning copied return snapshots its current without advancing. Argument
cleanup precedes receiver release; shared resumes preserve the first-yield history
used by `rewind`. See the [pending-send review](coverage/semantics/generator-pending-init-send-review.json).
Pending `send` through native shared links also buffers a paused child's yield
assigned directly to a simple CV. A direct or forwarded `next` that resumes the
child consumes it; close and overwrite preserve its count until request-store destruction,
independently of caches and Generator owners.
See the [shared-send review](coverage/semantics/generator-pending-shared-send-review.json).
At a bare statement yield, pending `send` instead ignores its argument. The current
snapshot precedes argument destruction, which runs before receiver cleanup even
when it throws. See the [unused-target review](coverage/semantics/generator-pending-unused-send-review.json).
[Delegation](docs/semantics/GENERATOR-DELEGATION.md)
adds arrays, source Iterators and shared Generator graphs with live raw caches
and natural return/unwind. Aggregate yield-from now acquires nested real iterator
data, retires layers and the original operand before rewind, and treats returned
Generators as generic iterators with null results. Raw reference caches stay live;
early cleanup errors retain constructed data until request cleanup, while rewind
errors release it before catch. Seventeen exact originals and 25 genuine-source
groups/720 ownership premises pass at the separate cuts in the
[Aggregate review](coverage/semantics/yield-from-aggregate-review.json).
Acquired Iterator NaN warnings retain raw results through ordinary handlers,
reread live numeric references once, and preserve parent ownership when a handler
parks. False results and thrown handlers release raw retval before iterator data.
Nine exact originals and twenty genuine-source groups/637 ownership and warning
authority premises pass; [warning review](coverage/semantics/yield-from-valid-nan-review.json)
records the separate checks. Wider raw payload changes remain required.
Aggregate getters may also rebind the original CV or reference operand before
returning Iterator/Generator data or a rejected raw value. Six safe originals
agree, and nine genuine-source groups/376 ownership and source-authority premises
pass; at that cut changed operands returning another Aggregate remained Unsupported.
[Rebound review](coverage/semantics/yield-from-rebound-operand-review.json) tracks
the bounded owner and source checks.
Known Aggregate returns now compare the first live object-valued CV/reference
payload, then each owned recursive layer. An independently kept original may
be the first repeated layer without adding a comparator/history owner. Self
returns from immutable inputs and deeper layers retain rejection. Nine selected
originals agree; a first nonobject source with an Aggregate return remains
Unsupported/zero agreement. [Source comparison](coverage/semantics/yield-from-source-comparison-review.json)
records nine source agreements and sixteen genuine-source groups/732 ownership
and source-authority premises at their separate cuts.
[Last-owner close](docs/semantics/GENERATOR-FORCE-CLOSE.md)
runs pending finally bodies with real scopes, graph links and cached owners.
Request 340 adds reverse-global and ascending-store close, handler-before-cache
exception delivery and borrowed zero-owner store buckets. Genuine weak
reacquisition restores ordinary release. [Fresh store teardown349](coverage/semantics/generator-fresh-store-review.json)
releases bound frames without entering body/finally, preserves immediate CV-handler
ordering and releases a closed Generator's Closure before its caches.
[Closed storage355](coverage/semantics/generator-storage-pin-review.json) keeps a
physical pin and readable RETURN through child callbacks, then clears weak lookup.
[Request delegation](coverage/semantics/generator-request-delegation-review.json)
detaches inputs before finally while preserving CV owners, shared store order,
delegated cache lifetime and nested normal handlers. [Request fatal cleanup 363](coverage/semantics/generator-request-abrupt-review.json)
retains Generator/cache owners through normal fatal rendering, releases the reported
exception before bailout, then suppresses later destructors. Normal exception-owned
stdClass/ordinary child cleanup retains full admission and actual storage pins.
A renderer rethrow at request C root reports/releases its builtin inner Throwable
before abandoning the original report and real Generator/cache owners. A returning
renderer-installed handler releases its inner exception before registry restoration;
warning callbacks can refresh the original cached string before fatal reporting.
Three originals and 611 reached premises retain separate cuts. A throwing
renderer-installed handler receives its own fatal report while real outer
handler/report and Generator/cache owners survive. Its reported exception releases
before bailout, even when its destructor changes reporting to zero. Two new
originals and 343 strict premises retain separate cuts. A throwing renderer warning
callback redispatches its new exception through the restored handler, then resumes
the original empty cached fatal report. One exact fatal original and 220 strict
premises retain separate cuts. At the cleared request C root, a property-child
destructor throwing during reported-exception release emits a second fatal.
The Parent free_obj pin keeps Weak lookup null; two Leaf C claims and real
Generator/cache owners survive. Its unfinished fatal frame retains the old
Exception's occupied GC slot through the pending HANDLE job. One exact source
and 549 strict premises retain separate cuts. A declared reference-cell child,
after its last local alias is unset, follows the same second-fatal path. Its
retired cell/STORE value certifies the actual Leaf release without adding an owner;
one new exact source and 677 strict premises retain separate cuts. An array child's
sole owning Leaf entry follows the same path after real array retirement; retired
contents add no owner. An external shared array retains the Leaf and emits only the
first fatal. Two exact sources and 712/77 strict premises retain their private cut.
A sole reference entry follows the same path after genuine array and cell
retirement. Their historical rows certify release without owning the Leaf; an
explicit global reference keeps the cell and Leaf live, emitting only the first
fatal. Two exact sources and 816/113 strict premises retain their private cut.
Wider handlers/rendering,
child lifetimes, reacquisition, parked/escaped storage and generic terminal cleanup
remain required.
[Earlier cuts](coverage/semantics/generator-request-finally-review.json).
[Active Fiber close](docs/semantics/GENERATOR-FIBER-CLOSE.md) preserves current
identity and genuine parked owners throughout ordinary Generator release,
including eager argument and frame cleanup with pending exception chains.
[Arrow Generator311](docs/semantics/ARROW-GENERATORS.md) validates eager
parameters, deferred captures, implicit yield/delegation returns and original
signatures. Value warnings retain the same Throwable, cached key and closed
Closure owner. The current default/Fiber/Stringable-eval composition passes its
source and75 reached cleanup premises; earlier cuts retain their identities.
Final294 preserves the accepted property, collection and source-emission modules.
Integrated [key-CV warnings321](docs/semantics/YIELD-KEY-WARNINGS.md)
copy the value before callbacks, preserve null keys and distinguish genuine child
exception reinjection from direct API close. Its27 normal observations and658
reached premises retain separate cuts; actual305 passes strict compilation after
reviewed receive/source/ARG319/collector compatibility, without source/state renewal.
[Reference yields328](docs/semantics/GENERATOR-REFERENCE-YIELDS.md) preserve live
cache cells, value-API array copies and direct/destructured foreach aliases.
Notice callbacks and retired cache readback retain authentic nonowning carriers;
bounded nonfinalizing global release preserves ordered cache retirement.
Actual321 passes strict compilation over336 and the reviewed39/301 owner factors;
earlier source/state cuts retain their inputs.
Wider IteratorAggregate consumers, call forms and reference producers, request/terminal cleanup
and complete destruction/GC remain required.
[Ordinary array omissions](docs/semantics/ARRAY-OMISSIONS.md) now retain skipped
slots and exact compiler diagnostic context. Object/frame-dependent destructuring and required
broader class-constant contexts remain unfinished.
[Class constants](docs/semantics/CLASS-CONSTANTS.md) preserve owner-scoped lazy
values, strict types, rooted array caches, inheritance priority and global/default
diagnostics. Included units fold only values available at compilation entry;
later fills cannot rewrite earlier images. Current warning-read and static-getter
interactions preserve cache ownership and aliases. Static Closure and fixed
function/static-method callable initializers retain owner/called scope, cached
identity and clone state. The current handler/truth interaction retains the
original null and cached static counter across handler mutation. The catalogue of
93 sources and the 159 + 44 + 63 state checks keep distinct tested revisions.
Named constexpr `::class` preserves namespace spelling and declaring self/parent;
rebound Closure defaults use their current lexical scope without a stale cache,
including inside weak Stringable parameter callbacks.
Wider callable consumers and references into incomplete class tables remain
Unsupported; the family stays partial.
[Foreach syntax and prechecks](docs/semantics/FOREACH-COMPILER.md) preserve reference
and list keys through checked printing and report exact compiler errors;
[independent review](coverage/semantics/foreach-publication-review.json) verifies
the original sources and retired exceptions. [Array foreach execution](docs/semantics/FOREACH-REVIEW.md)
now retains captured values/reference cells, saved copy positions and abrupt-exit
cleanup. [Targeted acceptance](coverage/semantics/foreach-runtime-review.json) binds
155 sources and complementary dense state checks. The historical [full container audit](coverage/semantics/container-campaign-audit.json)
passes 4,997 exact sources and 24 outcome controls; objects, frames and two compiler
contexts remain unfinished.
Current variable/array quiet access, isset/empty, coalescing assignment,
request initialization/GLOBALS and top-level magic constants have a combined
[independent checkpoint](coverage/semantics/quiet-integration-review.json):
5,706 ordinary and 263 explicit-request comparisons, with21 separate outcome
controls on 846/14d17662. All 4,997 historical source bytes and the complete raw
archives are retained. This full runtime checkpoint remains historical after later
call changes and does not close the full-core inventory.
[Named source calls](docs/semantics/SOURCE-CALLS.md) execute declarations,
positional value/reference parameters, recursion, local/global frames, returns
and fatal cleanup. [Reference-parameter acceptance](coverage/semantics/reference-parameter-review.json)
binds 166 exact source replays, 61 independent original agreements, 283 shared
destructuring regressions and eight independent state programs with 1,868 assertions.
[Reference sends and temporary DIM/list behavior](docs/semantics/SOURCE-REFERENCE-PARAMETERS.md)
preserve alias cells, COW, diagnostic phases and checked continuation ownership.
[Ordinary user constants](docs/semantics/SOURCE-USER-CONSTANTS.md) now preserve
ordered activation, namespace/import lookup, initializer diagnostics and array
ownership. [Their independent review](coverage/semantics/user-constant-review.json)
binds source, allocation-class, state/resume and shared quiet/call checks.
Module400 adds scalar global `define`/`defined`, including dynamic string callees,
namespace-prefix normalization and captured request strings after CV mutation.
Rows retain the actual value and string-carrier class. Available positional
literal facts constrain inputs; variable payloads retain the existing structural table
policy. Wider values, conversion/warning paths and namespace fallback remain open.
Scalar `define` names also follow caller strictness with primitive values and an
omitted/already-false flag. Weak registration keeps its received key across later
precision changes and duplicate handlers; strict errors retain raw arguments.
Named sends match their normalized slots without changing captured call authority.
[Four source agreements and 351 state premises](coverage/semantics/define-scalar-name-review.json)
cover registration, returning/throwing warnings and source/budget controls.
Integer/boolean names also accept false scalar flags (`0`, empty/`"0"` strings and
float zero). Weak calls convert the API name while preserving the raw flag;
strict name errors precede flag rejection after argument effects.
[Four source agreements and 595 state premises](coverage/semantics/define-scalar-false-flag-review.json)
cover publication, converted duplicate traces, callback throws and carrier guards.
Finite float names also accept those false flags. Weak calls retain distinct
`"-0"`/`"0"` keys and the received duplicate key across handler precision changes;
strict calls reject the raw float first after argument effects.
[Four source agreements and 603 state premises](coverage/semantics/define-float-false-flag-review.json)
cover captured flags, historical precision, strict errors and throwing cleanup.
Weak null `define` names dispatch the deprecation before conversion and registration.
A returning handler can create the empty-name binding first, causing a separate
duplicate warning with the converted string in its API trace. A throwing first
handler retains raw null and cancels registration; strict calls retain raw
arguments after all argument effects.
[Four source agreements and 396 state premises](coverage/semantics/define-null-name-review.json)
cover source-backed empty-key rows, both warning continuations and budget pauses.
NULL names also accept quiet false scalar flags (`0`, empty/`"0"` strings and
float zero), preserving raw flags through deprecation and converted-name duplicate
traces. Strict name errors win first; conversion-handler throws cancel publication.
[Four source agreements and 755 state premises](coverage/semantics/define-null-name-false-flag-review.json)
cover default diagnostics, callback return/throw and authenticated captures.
Global `constant` queries return primitive values, authenticated string carriers,
validated user array trees, certified completed user instances and certified
Closures. They use the captured query, remove one leading separator and preserve
terminal-name case.
Missing names raise an API `Error`; argument effects precede lookup.
Integer, boolean and float query names follow caller strictness: weak calls convert to
strings, while strict calls raise `TypeError` with the original argument.
Captured originals still authenticate the call; weak missing-name Error traces
contain the converted string. The [scalar-name review](coverage/semantics/global-constant-scalar-name-review.json)
records source and resumption checks.
Null query names raise the weak-call deprecation before conversion or lookup.
A returning handler can publish the empty-name constant; a throwing handler keeps
the raw null API argument. Strict calls raise `TypeError` without that warning.
The [null-name review](coverage/semantics/global-constant-null-name-review.json)
records callback order, trace views and resumption checks.
Array queries retain the stored root and children; existing COW preserves nested
writes, reference acquisition and append history. Immutable and mutable empty
roots retain their provenance. The [array-query review](coverage/semantics/global-constant-array-review.json)
records the focused source and state checks.
Array leaves may also hold certified user instances or Closures: COW separates
containers while object identity, mutable properties and static cells remain shared.
The [object-leaf review](coverage/semantics/global-constant-object-array-review.json)
records physical array-to-object edges and reference-to-bucket replacement checks.
Instance results retain mutable properties; Closure results retain static cells
and callable scope. Both preserve identity and add an ordinary RESULT owner to
the table's owners. The [instance-query review](coverage/semantics/global-constant-instance-review.json)
and [Closure-query review](coverage/semantics/global-constant-closure-review.json)
record the focused source and state checks.
The [global-query ledger](coverage/semantics/global-constant-review.json) preserves
its earlier source/state cuts and historical producer/array refusals.
Ordinary string-valued `const` declarations now authenticate interned and request
carriers while preserving their identity and source allocation classes. The
[string-publication review](coverage/semantics/const-string-review.json) covers
literal, folded and aliased values, recursive array validation and shared defaults.
Primitive duplicate `define` now warns and returns false while retaining the old
binding, including named handlers and retained dynamic selection with callback
appends. [Two exact sources and 207 public premises](coverage/semantics/dynamic-constant-duplicate-review.json)
cover default, false-handler and handled delivery; wider candidates remain partial.
Exact non-NUL names of modeled startup primitives now warn and return false with
primitive candidates and omitted/bool-false flags, preserving the builtin through
strict calls and returning or throwing handlers.
[Four source agreements and 614 state premises](coverage/semantics/define-startup-duplicate-review.json)
cover captured request strings, callback siblings and exact throwing discard;
unknown startup values and wider flag/value forms remain partial.
Non-NUL special `true`/`false`/`null` names now use the same Warning/false path with
primitive candidates and omitted/bool-false flags. Recognition ignores case;
messages and raw API captures keep the supplied spelling through handlers.
[Four source agreements and 645 state premises](coverage/semantics/define-special-duplicate-review.json)
cover preserved special values, strict calls and exact throwing discard.
Boolean `case_insensitive=true` now warns before registration while keeping case
sensitivity. A handler-created binding wins the subsequent duplicate check;
[two exact sources and 221 public premises](coverage/semantics/dynamic-constant-flag-review.json)
cover the retained arguments, callback entry and live-table ordering.
If that boolean-true warning handler throws while the name stays fresh, `define`
still registers the captured primitive before propagating the exception. Strict
calls retain true and request-string candidates across argument and callback effects.
[Two source agreements and 196 state premises](coverage/semantics/define-bool-flag-pending-review.json)
cover this corrected registration tail and the unchanged caller destination.
String-name `define` also receives integer, string and non-NaN float flags with
primitive values. Weak calls preserve the raw flag in warning traces; strict
calls raise `TypeError` after all argument effects. A throwing ignored-warning
handler still permits fresh registration of the captured value before its
exception escapes. [Four source agreements and 462 state premises](coverage/semantics/define-scalar-flag-review.json)
cover both warning phases, this pending registration tail and source/budget guards.
When a binding exists after that first throw, the pending duplicate skips an
eligible PHP handler without fallback. An excluded Warning level uses default
reporting; both paths preserve the original exception,
binding and caller destination.
[Three source agreements and 206 state premises](coverage/semantics/define-pending-duplicate-review.json)
cover live handler masks, raw captures, fatal-trace clearing and quiet reporting.
A NULL third flag instead emits its deprecation before the C body. Normal return
uses false and checks the live table; a first-handler throw cancels registration.
Both warning traces keep raw NULL, and strict calls reject after argument effects.
[Four source agreements and 349 state premises](coverage/semantics/define-null-flag-review.json)
cover default diagnostics, callback-created duplicates, cancellation and raw traces.
A NaN third flag raises its bool-conversion Warning before the ignored-flag
Warning, preserving raw NaN in API traces. A throwing conversion handler cancels
registration; a later ignored-warning throw still reaches the registration tail.
Strict calls reject after argument effects without warnings.
[Four source agreements and 472 state premises](coverage/semantics/define-nan-flag-review.json)
cover these phases, live-table duplicates, captured arguments and budget resumption.
Non-NUL string names containing `::` raise parameter-1 `ValueError` before the
ignored-true Warning. Omitted/bool flags and strict calls retain raw arguments
after their effects.
[Four source agreements and 450 state premises](coverage/semantics/define-class-name-review.json)
cover exact errors, caller traces and preserved state; wider flags/values remain partial.
For the same non-NUL `::` names, weak int/string/non-NaN float flags reach that
ValueError, while strict calls reject the raw flag first with parameter-3 TypeError.
[Four source agreements and 620 state premises](coverage/semantics/define-class-scalar-flag-review.json)
cover both priorities, raw negative-zero/request-string traces and unchanged state.
A NULL flag for these non-NUL `::` names emits its deprecation before the name
ValueError; a throwing handler cancels that body check. Strict calls reject raw
NULL first after argument effects.
[Four source agreements and 429 state premises](coverage/semantics/define-class-null-flag-review.json)
cover default reporting, callback return/throw, raw traces, preserved caller result
and callback effects.
NaN flags for these non-NUL `::` names emit only the bool-conversion Warning before
the name ValueError. First-handler throws cancel the body; strict calls reject raw
float after argument effects without warnings.
[Four source agreements and 441 state premises](coverage/semantics/define-class-nan-flag-review.json)
cover raw captures, false-handler reporting, callback effects and throw cancellation.
NUL/coerced names, owning/wider values and wider NaN producers remain partial.
Fresh two-argument `define` also copies nonempty acyclic scalar-array trees,
dereferencing source cells and rebuilding append history. Request-string leaves,
nested reference snapshots and literal constraints pass
[two exact sources and 219 public premises](coverage/semantics/dynamic-constant-array-review.json).
Top-level empty definitions retain an authenticated immutable table or create a
fresh mutable copy. [Two exact sources and 162 public premises](coverage/semantics/dynamic-constant-empty-review.json)
distinguish allocation classes and rebuilt append history, rejecting a mutable
clone of a fixed literal. Nested empties, wider array warning/flag paths,
uncertified objects and cycles remain Unsupported.
String-name `define` with an omitted/false flag now shares already-certified
stdClass donors. Named/selected calls preserve the captured pointer through later
CV changes, and duplicate handlers keep the old binding and property writes on
normal return or throw. Existing call and Exception-trace cleanup release the
temporary owners. [Certified define review](coverage/semantics/define-stdclass-review.json).
Fresh two-argument definitions also copy nonempty array trees containing certified
stdClass leaves. Copied containers freeze source reference values while object
pointers and property writes remain shared, including selected eval calls
and nested query COW. [Array-object define review](coverage/semantics/define-stdclass-array-review.json).
Duplicate nonempty array definitions retain a private canonical candidate through
the Warning while callbacks and Exception traces keep the original API argument.
Normal false delivery and throwing-handler cleanup retire the candidate, preserving
the old row and callback writes. [Array-duplicate review](coverage/semantics/define-stdclass-array-duplicate-review.json).
Ordinary uncertified objects, other owning leaves, empty-array duplicates, nested
empties and wider flags/names remain partial.
Class-qualified `defined` now checks inherited user constants with lexical visibility
and quiet misses. Named autoload resumes the same captured query once.
[Two exact sources and 288 public premises](coverage/semantics/class-qualified-defined-review.json)
cover the full-query trace and retained selection; at that cut, deferred evaluation and wider class
query domains remain Unsupported.
Class-qualified `constant` returns folded primitive/literal values with lexical
visibility and API Errors. Named autoload retains the captured query across caller
CV changes. [Two exact sources and 384 public premises](coverage/semantics/class-qualified-constant-review.json)
cover value types, string provenance and one-shot resume; at that cut, deferred
evaluation and wider domains remain Unsupported.
[Array-valued qualified `constant` queries](coverage/semantics/class-qualified-constant-array-review.json)
now share source-pooled nonempty literal trees until ordinary COW writes or reference
acquisition separate them. Two exact sources and 326 public premises cover pooled
identity, root/nested separation, reference cells and table history; at that cut,
empty/deferred arrays and wider values remain Unsupported.
[Immutable empty qualified values](coverage/semantics/class-qualified-constant-empty-review.json)
now preserve pooled root/child identity. Emptied copies retain append history,
and a reference to an empty bucket separates its child only on write. Two exact
sources and 244 public premises cover provenance and delayed COW; mutable-empty
query values and deferred/nonliteral arrays remain Unsupported.
[Deferred qualified values](coverage/semantics/class-qualified-constant-deferred-review.json)
now initialize only the requested untyped plain-global-name member. Missing values
leave no cache and can be retried; request-string identity survives later CV writes.
Two exact sources and 314 public premises cover API traces, context restoration,
cache custody and carrier checks. Other deferred initializer/value domains remain open.
[Deferred qualified `defined`](coverage/semantics/class-qualified-defined-deferred-review.json)
now evaluates the same bounded visible initializer before returning true. Quiet
inaccessible members avoid evaluation; actual initializer Errors retain the
`defined` API frame and can be retried. Two exact sources and 415 public premises
cover boolean results, request-string caches and context/resume authority; wider
initializers, class/autoload interactions and fixed namespace fallback remain open.
[Keyword class queries](coverage/semantics/class-keyword-query-review.json) now resolve
`self`/`parent` from lexical scope and `static` from the called class, including eval.
Two exact sources and 368 public premises cover six eval queries, scope Errors and
captured query traces. Keyword `constant` values remain folded primitives/literal
strings; wider initializers, values and internal/bound-Closure scopes remain open.
[Untyped positional defaults](docs/semantics/SOURCE-POSITIONAL-DEFAULTS.md) now preserve
omitted receives, declaration context, observable caches and fresh reference/array
ownership. [Independent acceptance](coverage/semantics/default-parameter-review.json)
binds exact909 source, protocol, state and production checks.
A separate [Closure default-cache guard](coverage/semantics/closure-default-cache-review.json)
authenticates deferred Closure/arrow defaults after object retirement. Installed
checks pass one typed static source and one stage with 27 assertions; earlier
private gates retain separate identities. Scoped class defaults remain open.
[Typed static Stringable assignment197](docs/semantics/TYPED-STATIC-STRING.md)
converts weak object values, then checks the live row and alias constraints while
preserving callback effects and cleanup. The focused INI union accepts two source
tuples and755 finite assertions. Distinct current ARG/callable and nested Restore
witnesses preserve live argument frames, callback order and full property bytes.
Earlier CALLS/SET/property gates keep their own tested identities in the
[ledger](coverage/semantics/typed-static-string-assignment-review.json).
Broader property consumers,186 producers and full core remain open.
[Source strict_types declarations](docs/semantics/SOURCE-STRICT-DECLARATIONS.md) now
execute with source-checked unit/function flags; [independent review](coverage/semantics/strict-declaration-review.json)
binds917 source, protocol, cache/resume and complete weak-state bridges.
Unknown literal `declare` names now emit ordered E_COMPILE_WARNING (128), bypass
registered handlers and continue into the real body. Two fresh originals and
focused notice/body/shared-throw checks pass. At that cut, wider ticks, encoding
and directive values remained required. [Declare review](coverage/semantics/compiler-declare-review.json).
Disabled-multibyte encoding declarations now emit source-derived parser warnings
before compiler warnings, bypass handlers and execute as no-ops. Two originals and
177 SL premises cover eval, once skip/reparse, raw helper stderr and budget resume.
Admission is bounded to root single-line declarations with one string literal, no
body and valid placement; wider shapes/rejected-with-warning inputs remain explicit boundaries.
[Encoding review](coverage/semantics/encoding-declare-review.json).
[Typed positional parameters and value returns](docs/semantics/SOURCE-TYPED-FUNCTIONS.md)
now execute builtin scalar/container checks, sequential receives and uncoerced
default caching while preserving aliases and cleanup. [Independent acceptance](coverage/semantics/typed-function-review.json)
binds926 source/state/protocol gates and the one-test correction bridge.
Remaining callable/type protocols stay pending.
[Callable/string parameter precedence](coverage/semantics/callable-string-current-review.json)
retains admitted public invokable objects before weak string conversion, in either
union order. Independent source and RECEIVE ownership checks pass; two source
regressions and a live-receiver CONFIG fixture/53 also pass on the current INI union.
[Call-result reference assignment](docs/semantics/SOURCE-CALL-REFERENCE-ASSIGNMENT.md)
now preserves target aliases, source diagnostic lines and returned-array ownership;
[its review](coverage/semantics/call-reference-review.json) binds933 source/state/protocol
gates, exact926 state bridges and canonical CLI8.
[Source reference returns](docs/semantics/SOURCE-REFERENCE-RETURNS.md) now preserve
caller demand, alias ownership and shared-cell type coercion; [independent review](coverage/semantics/reference-return-review.json)
binds942 source/state/protocol gates and the one-state-test bridge.
[Exact reference-return checks](coverage/semantics/reference-return-exact-review.json)
now preserve existing cells, property sources and parameter-backing certificates
through forwarded calls and `finally`; real conversions, missing-slot initialization
and ordinary checked writes retain their behavior. Sixteen focused source agreements
and private358 state cuts of 35 plus 483 assertions pass; actual359 passes separate
strict compilation. [Delayed reference-return replay](coverage/semantics/reference-return-replay-review.json)
now follows the protected exception chain once, retaining pending-error ownership,
selected catch eligibility and the continuation after a caught try. Ten replay
originals, 14 current/saved fixtures with 954 assertions and five affected return
controls pass at private360; actual361 passes a separate strict compiler gate.
Source-only [scalar-loop recovery](coverage/semantics/reference-return-scalar-replay-review.json)
preserves initialization and loop steps through caught break/continue/goto in
named, method and closure frames. Fourteen originals and 15 reached fixtures
with 1,102 assertions pass; actual361 compilation has a separate cut.
[CV/compiled-CONST switch recovery](coverage/semantics/reference-return-switch-replay-review.json)
now preserves selected-case remainder, fallthrough and catch scope without
re-evaluating the subject or creating a freeable owner. Seven preserved originals
and 14 current/saved fixtures with 1,339 assertions pass at retained private361
cuts; actual-parent strict compilation remains separate.
[Physical array-owner recovery](coverage/semantics/reference-return-retired-owner-review.json)
preserves the first cleanup and borrows its identity/cursor through current and saved
frames. Capture requires at least three genuine owners before cleanup and two after;
metadata adds none. Four originals agree exactly; nine delayed COW controls intentionally
retain c/d=1 instead of native8, with zero agreement credit. State23/1,873, independent
pending98 and actual-parent carrier71 pass; strict364 is separate. Wider payload domains,
active-finalizer replay and Stringable186 remain open.
[Deferred reference-return Notices](coverage/semantics/reference-return-notice-review.json)
now run after protected finalizers and type rechecks, preserve diagnostic source/line
through callbacks, and retire cancelled or throwing outcomes through ordinary cleanup.
Six focused originals and one preserved protected-unused control agree; eight reached
current/saved fixtures pass 722 assertions. Actual-parent compilation is separate.
[Single-active-finalizer CV replay](coverage/semantics/reference-return-active-finalizer-review.json)
now carries the actual consumed return cursor without keeping its old operand root.
Uncaught errors cross it once; local catches resume the cleared old return, and normal
replacement preserves the new alias. Three originals agree and eight reached
current/saved fixtures pass 602 assertions; actual-parent compilation is separate.
[Consumed string-literal replay](coverage/semantics/reference-return-consumed-literal-review.json) now recovers the original interned
value after a locally caught inner rejection in one already-active finalizer.
The source cursor owns no operand, restores one original-line VALUE Notice and
returns a fresh cell distinct from the globals. Two originals agree and three
reached current/saved fixtures pass 347 assertions; actual-parent compilation is
separate. [Consumed explicit NULL](coverage/semantics/reference-return-consumed-null-review.json) now recovers its special
constant value and original VALUE Notice; two originals agree and three reached
current/saved fixtures pass 367 assertions. A bounded
[computed string VALUE continuation](coverage/semantics/reference-return-consumed-value-review.json) now resumes cleared NULL
without repeating its call. Its pending VALUE Notice survives the public pause;
the nonnullable check rejects before delivery and the next finalizer return selects
the new alias. One original and three reached current/saved fixtures/386
assertions pass. With the checked nullable string mask, the same cleared NULL
passes the repeated check, delivers one original-line Notice and returns a fresh
[caller cell](coverage/semantics/reference-return-consumed-value-nullable-review.json) distinct from x and y, without repeating the call
or outer finalizer. One nullable original and three reached fixtures/381
assertions pass. Two already-active CV finalizers also retain
[ordered non-owning history](coverage/semantics/reference-return-multiple-active-cv-review.json) across inner rejection.
Uncaught replay leaves Z then X; initial success preserves the selected y
alias. Two originals and four reached fixtures/439 assertions pass.
Locally caught inner rejection now resumes the consumed middle CV as cleared NULL,
then replays its finalizer while retaining the outer history. One original agrees
and three reached current/saved fixtures pass 391 assertions at their private cuts;
the earlier state439 caught-Unsupported helper boundary is superseded only here.
An immutable outer string literal also shares the pair with middle Z and inner Y
CV returns. Its source-equal history owns no cell; replacement cancels its VALUE
Notice, and selected Y or error escape retires it. Three exact originals, five
reached fixtures/461 assertions and independent three/187 pass at separate cuts.
A checked catch passage now preserves both histories through Y rejection and
fresh Z NULL rejection. M2 skips Y, D catches Z, and the old literal resumes
with one original-line VALUE Notice and a fresh caller cell. Three exact originals,
five reached fixtures/480 assertions and independent pending63/7 pass at separate
cuts in the same review. Lifecycle capture, other caught layouts and further histories,
other VALUE signatures/layouts, general CONST, other NULL, wider Stringable
consumers, owner domains and broad return verification remain open.
A checked no-argument call can now precede B after D; the observed ping preserves
the old literal through its saved frame, then D;P;B precedes the original Notice.
Three originals, six/514 reached checks and independent saved-ping70/4 pass at
separate cuts; throwing, mutating and reentrant call bodies remain open.
Adjacent ordinary CV histories beyond two now use a source-authenticated ordered
cursor list without owning discarded operands. The observed Z/W/X chain survives
Y rejection and saved ping frames, then retires in order; initial success keeps
the selected y alias. Two originals, five reached fixtures/467 assertions and
independent partial90/7 pass at separate cuts in the same review.
A checked singleton TypeError catch in the selected Y owner now resumes the
consumed Z/W/X chain through root-free cleared NULL. Z raises a fresh TypeError
while the old Y error stays live; W/X survive replay and saved ping restoration.
Rethrow preserves the original Y error. Three originals, six reached fixtures/640
assertions and independent CLEARED75/5 pass at separate cuts. Immediate Y success
is source evidence only; helper leaves remain nonpublic. Other caught/mixed
layouts, lifecycle capture and broad returns_verify remain OPEN.
The ordered chain also accepts an immutable string literal as its last history.
Initial VALUE Notice is canceled; root-free source history survives saved replay
and retires during ordered error escape, while successful Y keeps its alias. Two originals, five
reached fixtures/504 assertions and independent partial96/8 pass at separate cuts.
At that cut, normal mixed clearing/resumption remained Unsupported.
A checked C/IF/E passage now resumes the terminal old literal after a fresh Z-NULL
error, with one original-line Notice and a fresh caller cell; E rethrow retires
that history with the same error. Three originals, eight reached fixtures/811
assertions and independent E-prefix297/5 pass at separate cuts. Other layouts,
lifecycle capture, effectful calls and broad returns verification remain OPEN.
The E catch also admits a checked named noarg call before its literal echo, optionally
followed by same-CV rethrow. Three original sources, three reached fixtures/301 checks
and independent saved-frame80/1 validate the pure `ping()` passage with W/old history,
fresh-Z identity, literal Notice/fresh caller cell, selected alias and abrupt cleanup.
Wider call effects and broad returns verification remain OPEN.
Guarded E-call reentry now preserves a pending source-line VALUE Notice when an
old live literal return survives finalizer retirement. The unused nested call
delivers one Notice before T; the outer call delivers one more. Rethrow cancels
delivery. Two originals, reached3/260 and independent saved-frame59/1 pass at
separate cuts. VALUE restoration excludes NULL-return forms; wider reentry/lifecycle and
broad returns verification remain OPEN. [Notice review](coverage/semantics/reference-return-notice-review.json).
Ordered global string CV histories now coexist with a sole source-checked echo-only
destructor. Capture keeps the selected Y object live; ordinary I2 assignment disposes
it once before the original Y TypeError escapes and histories retire in order.
Two originals, three reached fixtures/306 checks and independent saved-D frame82/1
pass separately. Selected Y keeps its alias without creating the object. Other
lifecycle/caught/mixed layouts and broad returns verification remain OPEN.
[Multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
The checked destructor may also echo then throw a literal TypeError. Its fresh
error has no Previous inside the callback; ordinary finally replacement later
links the original Y TypeError and preserves that same fresh error through ordered
retirement to the caller. Two originals, reached3/335 and independent post-D91/1
pass separately; a native caller observer confirms the late Previous relation.
Other destructor effects and broad returns verification remain OPEN.
A checked destructor can also import W's global string cell and assign a literal
before echoing/throwing. Changed W survives ordered Z/W/X retirement; the selected-Y
bypass retains its alias and skips the write. Two originals, reached3/355 and an
independent post-write saved-frame110/1 pass separately. Reconstructed W after
retirement is a local source certificate; broader mutation/lifecycle and returns
verification remain OPEN.
The checked W write can also use an in-range integer literal. W stays integer17
through public history retirement and caller cleanup; every other history keeps
its string guard. Two originals, reached2/266 and independent saved109/1 pass
separately; wrong W18 and non-W X17 are publicly refused. The selected bypass
skips the write. Other scalar mutations and broader returns remain OPEN.
Checked direct `$GLOBALS` W→X reference rebinding now preserves f's original local
W while global W follows X through the caller's later write. Two originals,
reached2/293 and independent public136/1 pass separately, including wrong global
W/X refusals and selected bypass. Post-retirement W reconstruction remains local;
wider rebinding and returns verification remain OPEN.
Checked direct `unset($GLOBALS["w"])` now preserves f's original local W while
removing its global binding. Two originals, reached2/326 and independent public134/1
pass separately; both caller reads emit their original line6 Warning, with none
during retirement. The bypass stays quiet. Post-W reconstruction remains local;
wider unset/lifecycle and returns verification remain OPEN.
A checked counter-guarded destructor may call the same named f before its literal
tail. Two originals, reached2/324 and independent nested public129/1 pass
separately: nested return precedes T/D, the original Y error reaches the caller,
and selected bypass keeps its alias without object birth. Missing cleanup and a
bool counter payload are publicly refused. Existing active lifecycle rules are
unchanged; wider reentry and returns verification remain OPEN.
The guarded destructor may also bind an ordinary local by reference to nested f
and write a literal through it. Two originals, reached2/332 and independent
public150/1 pass separately: inner aliases Y before the probe, the original outer
error survives T/D and cleanup, and the bypass skips reentry. Shared reference
and lifecycle rules are unchanged; wider demand/returns verification remains OPEN.
The guarded destructor can catch a nested TypeError around the reference binding
and probe. The failed binding and probe are canceled; C/T/D resumes, then the
original outer Y error reaches the caller. Two originals, reached2/350 and
independent early-catch public99/1 pass separately. Shared catch, reference and
lifecycle rules are unchanged; wider catch/reentry and returns remain OPEN.
A separate validation-only escaping nested-throw case passes two originals and
public96/1: the fresh error acquires the old Y as Previous only after leaving the
callback. Its maintained generator and recovery prerequisites are in the
[multiple-history review](coverage/semantics/reference-return-multiple-active-cv-review.json).
The checked local catch may also rethrow its caught TypeError. Two originals,
reached2/353 and independent public132/1 pass separately: the same error retains
its construction line and trace, late cleanup links old Y as Previous, and T/D
and the probe stay canceled. Existing throw/Previous rules are unchanged; wider
catch/rethrow and returns verification remain OPEN.

The guarded catch may instead create a fresh literal-message TypeError. Two
originals, reached2/368 and independent public161/1 pass separately: its own
creation line/trace reach the same caller with old Y as Previous, while the
caught-only nested error retires. T/D and the failed probe stay canceled; budget
continuation and the selected alias pass. Worker120 is a cap-only retry; original
timeouts keep zero credit. Wider replacement/returns verification remains OPEN.

The same guarded catch can explicitly pass its caught error as Previous. Two
originals, reached2/411 and independent public163/1 pass separately: early
replacement→caught becomes replacement→caught→oldY during cleanup, keeping both
trace graphs and the caught error alive through retirement and caller reads.
Caller-cut budgets and selected alias pass; the original fixture parse failure
keeps zero credit. Wider Previous/returns verification remains OPEN.
[Error suppression](docs/semantics/SOURCE-ERROR-SUPPRESSION.md) now preserves folded
effects, deferred reads and frame-owned masks through cleanup; [review](coverage/semantics/error-suppression-review.json)
binds951 gates and its print-only bridge. [Reporting and source error handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md)
now use authenticated callback frames, registration stacks and bounded missing-CV
continuations. Public and lexical private/protected method arrays and class-method
strings keep raw registration values, resolve them at dispatch, and freeze the
entered target through reference
mutation, replacement and throw, with access checked against the genuine emitting
frame. The [scoped-callable ledger](coverage/semantics/scoped-callables-current-review.json)
records selecting-scope and retired-creator checks. The [method-handler ledger](coverage/semantics/handler-callables-current-review.json)
separates original source/state checks from current PIPE warning composition;
the [earlier handler review](coverage/semantics/error-handlers-review.json) retains
its distinct revisions and remaining diagnostic/callable obligations.
Captured-null ASSIGN through a typed alias preserves its value on rejection and
raises a caller TypeError retaining the handler's previous chain. The
[consumer review](coverage/semantics/warning-consumers-review.json) records the
separate source and ownership checks; ordinary missing reference sends stay quiet.

[Missing global reads](docs/semantics/SOURCE-GLOBAL-WARNINGS.md)
capture null before callbacks and skip later writes when a handler throws. Genuine
request snapshots preserve numeric keys, shared reference cells and array COW.
Author8/207, independent8/221 and two current scoped-handler sources retain
separate cutoffs. [Dynamic read keys](docs/semantics/SOURCE-DIMENSION-KEYS.md)
now stage missing key-CV, null/float and global-array-name conversions. Genuine
temporary owners, borrowed CV tables and ordered NaN notices preserve mutation,
COW and throwing cleanup through nested/quiet reads. Author9/246 includes the two
independent NaN originals; independent14/235 and one current constructor
interaction keep separate cuts.
[Writable dimension keys](docs/semantics/SOURCE-DIMENSION-WRITES.md) now stage
bounded CV-array W/RW and direct GLOBALS reference fetches. Callback copies abort
acquisition; real cell aliases, moved sole keepers, delayed RHS reads and named
reference priority retain their native behavior. Author11/340 and independent15
fresh/266 plus two retained originals keep separate cuts; one current typed-caller
interaction passes. [Coalesce assignment and unset keys](docs/semantics/SOURCE-DIMENSION-EDITS.md)
now stage direct CV-array consumers: memoized keys and separate read/write lines,
write-copy abort, unset liveness and shared typed cells survive callbacks.
Author6/255 and independent10/216 share one original, giving15 unique private
agreements; two reduced current trait-handler sources pass.
[Nested unset and append](docs/semantics/SOURCE-DIMENSION-TAILS.md) now preserve
intermediate conversion protection, abort temporaries and late RHS/null-insertion
timing. Author6/247 and independent18/356 share one original, giving23 unique
private agreements; one current private-handler/typed-cell source passes.
[Nested coalesce assignment](docs/semantics/SOURCE-NESTED-COALESCE.md) now owns
quiet row values, walks current write storage and preserves memoized keys,
abort temporaries and late keyed-RHS null/type-error timing. Author9/233 and
independent11/277 share two originals, giving18 unique private agreements;
one current private-handler/typed-cell source passes.
[Global W/RW warnings](docs/semantics/SOURCE-GLOBAL-WRITES.md) now retain selected
names and detach callback-created aliases on returning missing-entry fetches.
Throws preserve callback writes; compound RHS timing and nested real-cell ingress
remain native-grounded. Author9/224 and independent12/273 share four originals,
giving17 unique private agreements; one current private-handler/caller-cell source
passes.
[Container initialization and reference writes](docs/semantics/SOURCE-CONTAINER-WRITES.md)
now stage undefined/null/false CV-rooted W/RW containers and final array-reference
ingress. Real false-conversion protection, distinct FETCH/ASSIGN/DIM_OP paths,
delayed source demand and typed backing through COW survive callbacks. Author12/242
and independent21/275 share three originals, giving30 unique private agreements;
one current private-handler/captured-cell source passes.
[Scalar-container reads](docs/semantics/SOURCE-CONTAINER-READS.md) now stage
missing-base, key-CV and offset warnings, retaining independent null, borrowed
selected pointers and genuine row/key temporaries. Quiet coalesce and terminal
isset/empty preserve their different demands; throws suppress later callbacks.
Author8/212 and independent13/272 share one original (20 unique private programs);
one current private-handler/key-temporary/caller-cell source passes. A separate
stdClass transition agrees; the historical ArrayAccess control retains its earlier
interface-contract Unsupported and no guard-execution credit. Initial string and
ordinary-object reads, wider base and GLOBALS/memoized producers remain required.
[ArrayAccess dimensions](docs/semantics/SOURCE-ARRAYACCESS.md) now admit the builtin
contract, tentative return notices, direct reads, coalesce, isset/empty, Set/Unset and ordinary by-value
compound and writable Get continuations. Compound calls Get then Set with live
key/RHS CV wrappers; nested W/RW/Unset keeps genuine temporary/real-cell owners
through Notice, reentry and throw. Earlier284 retains28 unique programs/492
assertions. Writable292 adds34 normal source agreements and1016 reached premises
across13 recipes; one fresh current-parent source agrees.
Affected GLOBALS reference finish and direct/nested Unset admission are repaired.
Append304 adds intermediate append through returned arrays and final compound
append to returned children, preserving copied reference cells and pending-error
operator order. Its 49 normal sources and eight reached recipes/723 premises pass;
one new parent interaction agrees. Returned-child simple append309 calls Set with
null and preserves the selected child, latched missing RHS and original result
pointer. Eight normal sources and two strict-SL recipes/160 premises pass at one
private cut. The separately accepted eager/weak lifetime composition keeps typed
old-cell readback and genuine callback/provider owners. One new current287
original and64 strict-SL premises also preserve readback across Fiber suspension
and a paused Generator finalizer. The canonical292 GC interaction retains
a cyclic returned child across collection inside Set, reads the old RHS cell
after a collector destructor rebinds its global name, and frees the child on the
next collection. Untyped/mixed reference Get and its named/nested consumers are
implemented; wider memoized/property/GLOBALS consumers and combined
Iterator/ArrayAccess notice ordering remain required.

[Stringable ArrayAccess compounds](coverage/semantics/arrayaccess-stringable-compound-review.json)
convert the left and live RHS through ordinary callbacks before Set, retaining
the raw Get result and exact key/base cleanup order through throws and Fiber
parking. An initially defined key unset by a callback remains a missing C-call
argument, so Set receives its real default or throws before entry. Twenty-three
normal originals agree across retained private cuts; compiler negatives and
independent reached states are recorded separately. Complete
ArrayAccess behavior and the combined offline rebuild remain required.

[Implicit Generator Get](coverage/semantics/arrayaccess-generator-get-review.json)
creates an unstarted Generator for mixed/untyped `offsetGet`, including reference
Generator declarations. Its real frame owns the received key and receiver;
nonowning call-site evidence survives escape, resume and ordinary close.
Finished close cleanup preserves the caller's pending exception through key and
receiver destructors. Seven maintained originals and423 independent premises pass
at separate private cuts. Actual331 compilation and initialization pass separately.

[Source exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md) retain raw
nullable stacks and dispatch an uncaught Throwable with one authentic argument
after `finally`. Nested restore/replacement, callback throws, internal by-reference
warnings and termination preserve selected targets and owners. Module247 stages
keyword/compound registration and terminal re-selection through the shared221 API;
internal deprecations preserve `Unknown:0`, handler stack effects and original
continuations. [Author/composition checks](coverage/semantics/callback-api-consumers-review.json)
cover40 source tuples and140 reached assertions; the
[independent review](coverage/semantics/callback-api-consumer-review.json)
keeps its separate34-source/474-assertion cut.

[Shutdown callbacks](docs/semantics/SOURCE-SHUTDOWN.md) cache selected callables
and copied arguments, then run in order after normal, exit and fatal outcomes.
Keyword/compound selections preserve called/private scope after maker retirement
using a borrowed target and callsite certificate. Callbacks can append entries;
handled throws continue and callback exit stops
the queue. Fatal-render warnings complete before diagnostics freeze and the
queue begins.

[Request-stage destructors](docs/semantics/SOURCE-DESTRUCTORS.md) repeat the
reverse direct-global pass, then scan reusable live object-store handles. Once
marks, nested USER permission, ordered slot/CV cleanup and pending exceptions
preserve native callbacks and owners. Ignored by-value ordinary/constructor returns release
before callee restoration; C callback returns retain their separate destination.
[Author checks](coverage/semantics/destructors-review.json) retain78 source
agreements and303 reached assertions at their actual cuts;
[independent review](coverage/semantics/destructor-review.json) retains64
agreements, two Unsupported controls and548 reached assertions at that original
cut. [Ordinary eager destruction](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md) now
reuses the release loop with native operation order, used/unused result owners
and real MAIN permission. Handler return cleanup precedes restoration; frozen
original Throwable release precedes the queue. Author62 and independent60 exact
source agreements keep their separate cuts; nineteen reached cases pass1,012
assertions. Seven additional fatal sources retain live VM owners through bailout;
two independent logical checkpoints pass198 unique assertions. Introduced runtime
class, autoload, precision and Fiber checks retain separate cuts in the
[author ledger](coverage/semantics/eager-destructors-review.json).
The actual Array operand warning/cleanup interaction now matches the original
lifetime stream and rejects a forged source-marker suffix in reached states.
Active automatic-destruction Fiber transfer, compound Stringable reception, GC,
output buffers and later request cleanup remain required.
Full core and a fresh combined offline rebuild remain required.

[WeakReference 296](docs/semantics/WEAK-REFERENCES.md) memoizes live wrappers without
owning their targets. `get` returns a strong result; resurrection keeps the target
live. Ordinary object free clears weak lookup before property children; Generator
storage notifies after its Closure/cache releases. Twenty-one
exact sources and nine reached cuts (344 physical premises) pass; five Unsupported
controls earn zero agreement. Pending-carrier unwind, deferred construction,
wider consumers and wider WeakMap protocols remain required. Canonical292/304
composition separately passes strict277 initialization and one exact weak lifetime
source; earlier cuts retain their inputs.
Wrappers also satisfy nominal `WeakReference` argument and property types after
their referent retires; diagnostics retain the actual internal class name.

[WeakMap386](docs/semantics/WEAK-REFERENCES.md) supports empty construction and one
first insertion with a `stdClass` leaf key and ordinary leaf value. The map owns
its value; the key stays nonowning. Actual key free transfers the entry to real
destructor release jobs while retaining its storage pin. Early key wrappers become
null before the value callback; a wrapper registered after insertion returns the
pinned key until callback cleanup finishes, including a throwing callback.
Borrowed notification metadata adds no owner; successful reads add ordinary
temporary ownership. Three ordering originals agree with PHP and 393 reached
checks pass at `c1cf6c7`, alongside the separate first-entry cuts. Last-owner map
teardown also releases its single leaf value while retaining the emptied map's
physical pin and live weak identity through normal or throwing callback cleanup.
Two originals agree at `0c9b358`; 467 lifetime checks and 86 freeing-write refusal
checks pass at their separate cuts. Wider map free and wider ephemeron GC stop explicitly;
general multi-map order, wider wrapper creation or mutation during freeing,
additional strong key/map owners retained beyond callback cleanup and wider
entry/read/mutation protocols remain required.

An explicit array cast of a live nonfreeing map now creates a fresh empty array,
even when populated. Results expose no entries and retain neither keys nor private
values. Two originals and 177 premises/6 actual casts cover fresh results, real
function frames, COW/reference history and subsequent key retirement.
[Array-cast review](coverage/semantics/weakmap-array-cast-review.json).

Scalar entries now also retire through eager cleanup while a live leaf key
remains held. The plain 40-byte original already agrees at `b88b45fc`; a held
unrelated destructor object exposes the active path. That 42-byte original and
260 focused checks pass at `f68c6f09`, preserving the key and held object through
map notification and physical retirement. Wider teardown and replacement contexts
remain open.

Two singleton maps can now register the same leaf key on either side of its weak
wrapper. Entry snapshots determine notification order even when map allocation
order is reversed: the first callback sees the key live, then notification clears
before the second callback. Only the current entry transfers its value owner;
the later entry stays intact through the first callback. The normal original
agrees at `e5b19d0`; the throwing original and 405 reached checks pass at `b12f93a`.
General registration order and wider map shapes remain required.

Ordinary object-key dimension reads now copy the stored value into a strong
result, so a held copy survives key removal. A missing key throws Error using its
actual object-store handle and preserves the existing entry. Two originals agree
with PHP at `c4c097e`; 297 reached checks pass. Reference and wider map protocols
remain required.

`isset($map[$key])` and `empty($map[$key])` now test the stored value without
adding a value owner. `isset` distinguishes null from false/zero/empty strings.
Bounded scalar first entries keep their exact string carriers. Two originals agree across
`144597d2`/`b7c1624a`; 377 focused checks cover presence, ownership and literal
source certificates. Wider scalar replacement and teardown protocols remain open.

`$map[$key] ?? $fallback` now copies the stored value directly. Missing keys and
null values select the lazy fallback; false, zero and empty strings are preserved
and skip it. A copied object survives entry removal until that copy is dropped.
Two originals agree at `df2997be`; 279 focused checks pass for copy ownership,
missing keys and fallback routing. Freeing keys, references and wider protocols
remain open.

A callback can also read while a leaf key's unique active storage pin still has
pending notification. The read copies the later entry's value; a missing entry
throws Error with the pin's actual object-store handle. Clearing notification
denies further reads even with a retained key owner. Two originals (111/162 bytes)
and 309 reached checks pass at `2565d378`. Inactive carriers, escaped targets and
wider freeing reads remain required.

Explicit `unset($map[$key])` removes a matching entry before its value destructor
while the map and key stay live. Missing object keys are no-ops; a separately held
value survives entry removal. Throwing cleanup resumes the same pending Exception.
Three originals agree at `0c01e5f`; 418 reached checks pass. Earlier cuts retain
their original evidence.

Occupied same-key replacement publishes the new value before releasing the old
value and preserves key registration. A receiver continuation retains the map
through cleanup; unused results add no owner, and used results copy the selected
RHS value afterward. Owned key temporaries release after the receiver.
Six originals agree across `70bf0c4`/`302b5c9`; 642 reached checks pass with prior
cuts retained.
Supported scalar values now also replace an occupied entry. Replacement publishes
the captured new entry before the old destructor runs; if it changes the RHS variable, the
used assignment result reads that changed variable after cleanup. Two originals
agree and 147 focused checks pass at `5dd834c5`, including scalar-only replacement
without a value release and object result ownership. Wider replacement remains
required.
Wider entries, freeing mutation, reference/iteration and ephemeron protocols remain
open.

`WeakReference::create` now reuses or recreates a wrapper during a live map
teardown callback. Only a unique active empty-map pin with pending notification
is admitted; the callback releases its strong map copy before returning. A fresh
wrapper adds no target owner and becomes null when cleanup notifies it. Two
originals agree at `ac980b0`; 333 reached checks cover reuse, real wrapper
retirement/recreation and notification. Wider freeing contexts and inactive
carriers remain required; earlier evidence and the original refusal stay separate.

A live singleton WeakMap now supports explicit collection of a destructor-free
value-to-key backedge. Ordinary value ownership remains strong; GC traces the
entry only when both map and key are reachable. Holding either key or value
protects the pair; dropping both allows collection while the map survives.
Two originals agree at `0167ec6c`; 439 reached checks validate conditional tracing,
entry disposal and held owners. Wider maps, callbacks and ephemeron graphs remain
required. [Review](coverage/semantics/weak-map-review.json).

That methodless singleton can now coexist with ordinary `stdClass` graphs.
Two originals agree at `fa2e00c6`: an independent self-cycle collects alongside
the pair, or alone while Key is held. The 405 focused checks cover real GC
disposal, indirect Key protection and its then-active destructor/nonleaf refusal.
The collector and physical ownership graph are unchanged.

The same bounded backedge now supports one ordinary public value destructor.
Its first GC pass protects the pair through the callback; retracing then collects
it or preserves it if the callback saves the key. Later collection runs no second
destructor. An independently rooted `stdClass` leaf also survives without keeping
the pair alive; changes outside the admitted shapes fail explicitly. Three
originals agree at
`18a03e08`; 583 reached checks cover destructor entry, retracing and retained
roots. Wider destructor and graph behavior remains required.

Once the value destructor is recorded as called, the singleton ephemeron can
coexist with ordinary outside `stdClass` graphs. A callback-created self-cycle
survives independently, while Other→Key protects the pair until Other is dropped.
Two originals agree and 331 focused checks pass at `c3e844a5`; collector301 is
unchanged.
This supersedes the earlier post-destructor nonleaf negatives; uncalled and wider
shapes remain fenced. [Review](coverage/semantics/weak-map-review.json).

[Ordinary collection301](docs/semantics/CYCLE-COLLECTION.md) implements explicit
object/array cycle collection, ordered destructor callbacks and real weak
retirement. Fiber protection scans reuse one graph within an unchanged state,
preserving lazy empty/nonobject prefixes, eager node order and helper fallbacks.
An evaluated false close predicate now skips total graph owner scans.
Pruning carries that graph through GC selection and destructor dispatch, with
reuse only when destructor preparation leaves the state identical.
Keep and release scans also reuse the carried graph, including detached and
retired buckets; public helpers retain their behavior for modified graphs.
GC and eager-destruction consumers read the same observed state’s edges after
its roots without rebuilding those roots.
The driver carries an already successful original-state owner order into the
following GC pass; failed or skipped destruction branches retain public fallbacks.
Pure graph pruning counts owners once and removes zero-owner cascades through a
worklist, preserving roots and the order and multiplicity of nodes and edges.
GC also reuses pruning's graph edges when pruning leaves the prepared state
identical; changed states recompute their edges.
The retained composed default/Generator/Fiber original agrees with native PHP;
its catalogue is included in the combined semantic and offline checks.
Authenticated specialized call contexts take precedence over ordinary error
handler validation.
Its retained30-source/606-premise and private3/45 cuts remain separate
from the new captured-source/66-premise and readonly-clone/GC compositions.
The earlier 291-module strict compiler/initialization and readonly clone original pass;
the larger nested-Generator source retains a zero-credit 90s timeout.
Module 317 adds actual cached collector Fibers, global parked collection, detached
target/pending guards, replacement batches and authenticated callbackless idle
retirement. Thirteen exact originals and two independent strict-SL groups with
78/68 premises pass at their recorded cuts. The actual318 parent passes strict
298 compilation/initialization and one fresh reporting-Fiber/handler source,
including nested busy GC0 and real count1/weak retirement. The final304 additive
join preserves newer call/source schemas and passes combined compilation.
Collector325 keeps detached zero-owner targets and outgoing children without
adding owners; real weak reacquisition restores ordinary release. Three exact
originals/85 reached premises retain their private cuts. A fresh active
unowned-close original and117 reached premises separately check same-pass count1,
real private-control retirement and saved caller admission. Larger exception-source
60s timeouts remain separate from compact trace/pending controls. Wider internal
graphs, callback reentry during a different active pass, internal takeover, automatic
thresholds and wider freeing remain open. Module332 adds quiescent public idle
resume/throw: supplied values are discarded, new cycles await real collection,
and exceptions reach the caller without terminating or remaining in the worker.
Three new exact originals and two strict-SL groups with169 premises pass at
separate cuts; the final315 current-parent join passes combined compilation.
Module342 admits idle public resume/throw during an active pass after all planned
destructors are marked called: the pass stays busy, masks restore and injected
errors retain identity without remaining in the worker. Two exact originals and
265 independent physical premises retain private323; final327 compilation
preserves337/339/307/334/302. Module345 now scans the retained physical interval
and runs remaining marked destructors without advancing the outer collection.
Zero-owner targets remain borrowed; real weak reacquisition can free them.
Captured APIs retain their genuine caller owners, and protected/private access
uses native `Fiber` scope. Four exact originals and separate274/177 reached
premises pass; one earlier scope assertion is superseded. Final336 compilation
preserves the accepted current parent. Cached callbacks now suspend and reenter
within the same live physical pass, preserving the cache and rebinding the fresh
public API. One normal source and 228 reached physical premises pass; captured
old/new exception priority completes in the state checks while its source CLI
retains a 60s timeout with zero agreement. Final 343 compilation preserves `e1c3d4d61`; publication on `2ed57ca8a`
preserves the static-property change by review.
Quiescent post-pass reentry now authenticates the parked VM and fresh caller
without depending on retired caller metadata or old physical slots. An explicit
no-destructor-tag check lets the retained scan finish safely. One normal source
and 203 independent physical premises pass; the captured source retains its 60s
CLI timeout/zero agreement. Final 345 compilation over `4cd2eab3a` passes.
A new internal collection now resumes the actual parked callback with null and
keeps its retained local interval separate from the new global scan. The unvisited
destructor target survives retracing and runs at request cleanup. One normal source
and 154 independent physical premises pass; original and compact old-error CLI
runs retain 60s timeouts/zero agreement. Final 349 over `63786460e` compiles.
Quiescent public resume/throw now reloads the global physical interval and calls
residual tagged destructors in the cached worker. One compact throw source and
119 independent physical premises pass, including both original continuations
and exact injected-error identity. The larger resume CLI retains its 60s timeout/
zero agreement. Final 351 over `8e513981b` compiles. Fresh internal collection now
scans residual and new tags with its genuine GC caller. Signed −1+2 accounting
returns 1 while both destructors retire. Two original full continuations pass
166 independent physical premises; both whole CLI runs retain 60s timeouts/zero
agreement. Final 353 over `d2bba03b2` compiles. Main-thread residual dispatch372
uses its own physical interval and real caller scope without changing the cached
Fiber cursor. Strict354 compilation/init and 171 independent physical premises
complete both unchanged originals with count1, D/E retirement and exact exception
priority. Final 356 over `a1c5e2626` compiles at `43e793df3`, preserving reviewed
trait, storage, raw Fiber-array and ASSERTIONS additions; both whole CLI 60s
timeouts retain zero agreement. An internal residual callback can now suspend,
detach its actual guarded VM and let a fresh worker scan the remaining physical
suffix. The old worker keeps its own pin/finally error and terminates after later
public completion; replacement errors stay separate. Both original continuations
pass 197 independent physical premises, including count0 before old completion
and later count1. Both whole CLI 60s timeouts retain zero agreement. Final 357 over
`b7419cbe1` compiles at `9ce39cd54`. Last-cache-owner release now closes the
suspended worker before physical replacement, running finally or transferring
its real error into collection pending. Two original full continuations pass
166 independent physical premises, including count1/weak retirement and exact
new/previous exception identity. Both whole CLI 60s timeouts retain zero agreement.
Final 358 over `0059e0a9e` compiles at `0da2cdae7`. Old public callbacks can now
suspend again during internal takeover: replacement uses the advanced reset
cursor while earlier marked targets survive and real FINALLY errors stay
separate. Both original full continuations pass 212 independent physical
premises; both whole CLI 60s timeouts retain zero agreement. Final 358 over
`6ed4873bd` compiles at `0bc957892`. Different-main public reentry now resumes
the actual parked callback while the fresh main plan retains current tags, even
when its target slot has been reused. The completed local scan cannot rewind
onto the fresh destructor. Independent 96/109 physical premises at separate
`93cb1cfd5`/`950c158d5` cuts complete both unchanged originals and preserve
old/new error identity. Actual359 over `0c549de11` passes strict compilation/init;
review preserves GEN176/363 and PROPS207/377 with their shared ownership paths.
The initial compiler stop, first throw-state 120s timeout and both whole CLI
60s timeouts retain zero affected/agreement credit. Overlap, wider active residual
and Fiber-pass reentry, earlier whole CLI completion and broader GC remain required.
Public resume/throw during a live main callback now lets the idle worker consume
snapshot-marked residual targets outside the fresh plan's DTORS. Authentic main
return, cursor and tag checks preserve fresh plan progress and pending errors.
Two native-grounded unset-order companions pass whole CLI60 and 174 independent
physical premises (95/79) at `c5a3e54df`, including count1 and exact replacement/prior
exception identity. Actual361 over `9988f88bf` passes strict compilation/init at
`5d89edb95`; earlier cuts retain their inputs.
Main collection also handles a closed ordinary-object residual/eligible overlap.
Physical nested removal drops old D's tag before fresh E runs; one retrace calls D,
frees E and preserves D's self-cycle, with signed count0 and a live weak probe.
One unchanged source and 247 independent reached premises (165/82) pass at
`85b9d0b73`; black-root, array/reference/proxy and Fiber overlap remain open.
Mixed overlap also admits a separate ordinary residual component outside the
fresh traced graph. Real F selection uses its surviving physical tag without adding F
to fresh DTORS or progress; one signed retrace retires F/E and keeps D weak-live.
One unchanged source and 321 independent premises (215/106) pass at `a2ef8b039`.
Incoming owners, nonordinary components and wider overlap remain explicit boundaries.
The ordinary-Fiber RUN path handles profiles with every residual tag nested-removed.
It preserves the computed physical image while fresh E and retraced D run on the
distinct cached worker. One unchanged source agrees
under CLI60 at `e3d359d01`; five source-reached cuts cover all408 original state
obligations, including caller/guard forgeries, count0, weak liveness and terminal
replay. Nonordinary and later-pass Fiber overlap remain required; earlier cuts
retain their inputs.
Mixed ordinary-Fiber overlap now uses a physical scan when a separate residual F
survives nested removal. It preserves fresh E-only progress and the real saved
caller, initial image and current guard. Three source-reached cuts execute 360
premises, including F→E→D, count 0, F retirement, D weak liveness and terminal
replay. The whole source retains its CLI60 timeout and zero agreement credit.
Wider overlap, throwing callbacks and reentry remain required.

The fresh closed-white component check also permits nonproxy arrays; residual
arrays and references outside the protected component remain excluded. A grounded
ordinary-Fiber E→array→D case has
329 executed state premises covering physical removal, real guard selection,
signed -1+2=1, E/array retirement and D self-owner/weak liveness. Its whole source
CLI60 remains OPEN with zero agreement credit. Main/mixed array layouts,
references/proxy tables and wider overlap remain required.

That fresh component can also traverse genuine unbuffered reference cells without
charging them. Live reference markers and canonical frozen cell edges preserve
admission and guard authority. Three ordinary-Fiber E→array→reference→D cuts
execute 407 premises, including signed count1, E/array/reference retirement and
D self-owner/weak liveness. Whole source38 CLI60 remains OPEN with zero agreement
credit; broader reference, main/mixed and proxy overlap remain required.

Protected residual reach now also permits a genuine unbuffered self-reference.
Three ordinary-Fiber E→D→reference→D cuts execute 375 premises, including
zero reference debit, exact image/guard authority and signed count0.
D and its reference remain live with one owner each; E retires and request cleanup
and replay pass. Whole source39 CLI60 remains OPEN with zero agreement credit;
wider residual-array layouts, outside references and wider overlap remain required.

Protected residual reach also admits nonproxy arrays within fresh-DTORS reach.
Closed white object/array producers remove nested data before parked-worker
continuation and ordinary worker retrace, with separate snapshot and current-image
checks. Six reached cuts execute 559 premises for the ordinary-Fiber D→array→D
case: signed count0, live D/array owners1, E retirement and request cleanup.
Whole source40 CLI60 remains OPEN/zero agreement; wider main/mixed, reference,
outside-array, black/external and proxy layouts remain required.

Disjoint residual reach also admits canonical unbuffered references, with live
markers authenticated through the worker scan and selected guard. Seven reached
cuts execute 326 source/control checks plus nine pure array exclusions for the
ordinary-Fiber F self-reference. Actual PASS1 retrace excludes the reference from
COUNTED and includes it once in FREESET; one terminal continuation retires F and
its reference, leaves D weak-live, clears collector state and matches native END events.
Whole source41 CLI60/180 remains OPEN/zero agreement; broader reference layouts remain
required.

Main-thread residual overlap handles a child held by a live CV with an ordinary
self edge or a canonical unbuffered property reference inside fresh destructor
reach. D's old physical tag is removed while D stays live; collection runs E,
returns −1, and request shutdown calls D after `END`. Both originals agree with native PHP
at separate cuts. The reference variant adds 99 source/control checks plus two
pure array exclusions. The separate held-F original also matches native output
under its recorded 180-second cap, with F weak-live after the callbacks. Its earlier
CLI60 timeout keeps zero credit; source41 remains OPEN/zero agreement. Wider
reference layouts, array components and worker overlap remain required.

Main collection also retires a separate non-destructor `stdClass` self-cycle
reacquired through `WeakReference::get()` during a destructor. Its saved global
CV becomes a nonowning retired slot: weak lookup is null, direct strict-null
comparison and release work, and unsafe reads remain explicit Unsupported.
The original agrees with native PHP; 146 reached source/control checks pass.
Broader retired-object comparisons, container owners and resurrection remain open.

The final main retrace also retains a called ordinary zero-owner leaf in its
existing borrowed root slot, without adding a heap owner. A real WeakReference
temporary promotes that slot; ordinary release clears weak lookup under the
storage cleanup pin. The original agrees with native PHP and 203 reached
source/control checks pass. A fresh `stdClass` child created after the final trace
may be a leaf, have exactly one self-edge, or point to one fresh `stdClass` leaf
with unique incoming owners. Native PHP agrees with all three originals;
199 leaf,212 self-cycle and227 chain checks cover retention, temporary release
and later collection.
Ordinary parent release disposes the acyclic children; the self-cycle waits for
the next collection. Two distinct ordinary parent properties may also share one
fresh `stdClass` leaf. Native agreement and238 reached checks cover borrowed
retention and both property releases, ending at the child's physical cleanup pin
with weak lookup cleared. One marked global CV may also hold the fresh leaf
through parent teardown. Native agreement and281 reached checks cover this
separate owner and its unset release through the child storage pin. Wider graphs,
outside carriers and worker cases remain required.

A fresh ordinary leaf child with a public destructor created after the final
collector trace can also be retained through its borrowed parent. The original
agrees with native PHP: child destruction occurs during the parent's weak
temporary release, before the next output. Another 216 reached checks cover
retention, callback authority and weak retirement under the child's storage pin.
Wider callbacks and graphs remain required.

An own private child destructor is retained through the same borrowed parent;
ordinary teardown raises `Error` before entering its body. Both this caught
access error and a public throwing child agree with native PHP. Another 272
reached checks cover source authority and pending-error cleanup through both
storage pins, where weak identities are null while allocations remain present.

Normal last-owner close335 runs the detached worker's `finally` immediately
and leaves its borrowed target for the next real collection/count1. Two exact
originals and two independent reached groups (216 physical premises) retain their
private cut; final319 compilation preserves331/324. Failed close338 retires its
one remaining private control owner while the real error stays pending in the
caller, including genuine prior-exception identity through a saved caller.
Two exact normal originals and two independent reached groups (247 physical
premises) pass at separate private cuts; tested322 preserves328/336 and publication
preserves the disjoint prior-array foreach guards. Active-pass
failed close and wider close contexts remain required.

[Parameter phase correction](docs/semantics/PARAMETER-PHASE.md) now sends variadic-default
and void-parameter sources through the existing static compiler; [review](coverage/semantics/parameter-phase-review.json)
binds exact PHPT/CLI diagnostics and reproducible parser patches. Positional
variadic execution is now [independently reviewed](coverage/semantics/variadic-review.json).
[Positional tails](docs/semantics/SOURCE-POSITIONAL-VARIADICS.md) preserve ordered
coercion, reference owners and error traces. [Named user-function arguments](docs/semantics/SOURCE-NAMED-ARGUMENTS.md)
are now [independently reviewed](coverage/semantics/named-review.json), including
hole-default preflight, typed/reference aliases and source-bound SEND lines.
[Builtin named compilation](docs/semantics/BUILTIN-NAMED-COMPILER.md) now has
[independent review](coverage/semantics/builtin-named-review.json) of configured
fixed-name lookup and fetch modes. [Array call arguments](docs/semantics/SOURCE-CALL-UNPACK.md)
now preserve insertion order, named holes and reference owners through errors;
[independent review](coverage/semantics/call-unpack-review.json) binds source/state
checks and complete old-state compatibility. Builtin execution and Traversable
remain required. [Dynamic string user calls](docs/semantics/SOURCE-DYNAMIC-CALLS.md)
now preserve callee selection, reference modes and ownership before argument effects;
[review](coverage/semantics/dynamic-call-review.json) binds990 source/state/protocol
gates and complete old-state bridges. The [earlier integration](coverage/semantics/callable-integration-review.json)
retains5706 ordinary comparisons,263 explicit requests,751 callable rows and5751
compiler phases on981 under distinct profiles. [Named-function statics](docs/semantics/SOURCE-FUNCTION-STATICS.md) now retain
persistent reference cells through recursive initialization, local rebinding and
error cleanup; [review](coverage/semantics/function-statics-review.json) binds
source/state/protocol evidence and22 old-state bridges. [Main-script statics](docs/semantics/SOURCE-MAIN-STATICS.md)
now bind persistent cells through the global symbol table; [review](coverage/semantics/main-statics-review.json)
retains source/state/protocol checks and20 complete old-state responses.
Parser-backed eval/file top-level statics now release their source-owned slots
before normal source end or explicit return, preserving callable slots and the
copied return operand. [Review](coverage/semantics/source-static-retirement-review.json)
retains the second-parser-response repair and selected normal lifetime checks;
top-level source slots now also stay separate from a real Closure caller's own
table, preserving each unit's cached cells and escaped references while later
units allocate fresh cells.
[Identity review](coverage/semantics/source-static-identity-review.json) records
the affected and independent source/state cuts. Body throws now retire source
slots before crossing to the caller, retaining the pending Throwable while
destructors run. A normal-end destructor throw still releases remaining source
slots in declaration order; replacement exceptions retain their Previous chain.
[Throw review](coverage/semantics/source-static-throw-review.json) records the
focused source and production-unwind checks. Graceful exit now retires source
tables before shutdown, preserving callee and nested-source release order.
Destructor source reentry keeps the saved exit owner valid; escaped references
retain their objects through shutdown. [Exit review](coverage/semantics/source-static-exit-review.json)
records this separate cut. Throwing source-table destructors now retain user
execution through caller catch and remaining-slot cleanup. Request exit status
survives a caught replacement: integer/default exit updates it, strings preserve
it, and nested resets remain distinct from saved exit control.
[Status review](coverage/semantics/source-static-exit-status-review.json) records
the focused source and public checks. `E_USER_ERROR` now captures the dynamic
source location and retires authenticated execution contexts before shutdown.
Static cells retain their existing roots while shutdown evals and destructors of
new objects run. [Fatal review](coverage/semantics/source-static-fatal-review.json)
records source and public checks. Hard bailout now sets request status255 before
shutdown: a direct string exit preserves it, while integer/default exits replace
it. [Fatal-status review](coverage/semantics/source-static-fatal-status-review.json)
records this separate cut. Frozen fatal completion now reports the request status
after caught shutdown-exit replacement, preserving continued callbacks and
diagnostics. A fresh fatal writes255 even when reporting is suppressed.
[Observer review](coverage/semantics/source-static-fatal-observer-review.json)
records the focused source/public checks. Redeclaration compiler cutoffs now
authenticate fresh shutdown eval/file entries against full current history while
retaining the exact failed prefix and source owner.
[Redeclaration review](coverage/semantics/source-redeclare-fatal-review.json)
records this separate admission repair. File compilation now retains its recorded
hard diagnostic after bailout; a later compiler fatal delivers that message and
location with the current trace. Cutoff receipts authenticate both abandoned
records independently. [Recorded-fatal review](coverage/semantics/source-recorded-fatal-review.json)
records the source and public checks. While that record is retained, nonfatal
runtime diagnostics skip handler/default delivery without interrupting the operation:
`trigger_error` returns true and an undefined-variable read yields null.
[Recorded-warning review](coverage/semantics/source-recorded-warning-review.json)
records three exact sources and two genuine public fronts. A fixed-name
`trigger_error`/`user_error` with `E_USER_ERROR` now drains a retained file fatal
before handler selection, delivering its cached message/location with the current
call trace. Eval-first delivery remains ordinary. [Runtime-drain review](coverage/semantics/source-recorded-runtime-fatal-review.json)
records that fixed-name cut. Selected nonowning calls now preserve their captured
CONFIG/nonce in a separate receipt; prefix replay rejects omitted or retargeted
fatal snapshots. One retained original and 182 public premises pass.
[Selected-drain review](coverage/semantics/source-recorded-dynamic-fatal-review.json)
records the positional string/int slice. Deferred runtime function redeclaration now drains the
same retained fatal using the actual binding trace. Its receipt records the
function site and consumed index; the raw failure is reconstructed from historical
bindings. Captured-prefix replay rejects omitted-entry records while keeping
genuine no-record binding valid. [Function-drain review](coverage/semantics/source-recorded-function-fatal-review.json)
records this separate cut. Deferred named user-class duplicates now deliver the
retained diagnostic with the current binding trace. Their real-statement receipt
and prefix replay reject omitted entries while ordinary class activation remains
unchanged. [Class-drain review](coverage/semantics/source-recorded-class-fatal-review.json)
records the focused source/public checks. Other fatal producers, broader queues, formatter
combinations and destructor/return interactions remain required.
[Real closure instances](docs/semantics/SOURCE-CLOSURES.md) now retain explicit captures,
selected callee owners and per-instance statics through invocation and cleanup.
[Independent review](coverage/semantics/closures-review.json) binds source, object
operation, ownership and compatibility evidence. [Arrow functions](docs/semantics/SOURCE-ARROWS.md)
add implicit undefined snapshots and source-authenticated expression returns; their
[review](coverage/semantics/arrows-review.json) also records the shared suppression
guard correction. Closure rebinding services, cycle collection and dynamic-source
lifetime remain required.
[First-class named function callables](docs/semantics/SOURCE-FIRST-CLASS-CALLABLES.md)
preserve named static roots and existing closure identity through conversion;
[their review](coverage/semantics/first-class-review.json) binds 17 source outcomes
and the separate reference and paused-state gates.
[Pipe arrow grouping](coverage/semantics/pipe-syntax-review.json) survives checked
syntax and printing, so a bare arrow RHS receives the matching compile error
before operand effects. [Pipe execution](docs/semantics/SOURCE-PIPE.md) forces the
left value before selecting a named or closure callable; its
[runtime review](coverage/semantics/pipe-review.json) binds 12 source outcomes
and separate paused-state controls.
[Switch execution](docs/semantics/SOURCE-SWITCH.md) scans cases in source order,
retains the subject through fallthrough, and distinguishes constant-boolean
branching from dynamic equality; its [review](coverage/semantics/switch-review.json)
binds 18 source outcomes and separate compiler and paused-state checks.
[Stringable comparisons](coverage/semantics/stringable-comparison-review.json) now
resume direct instance/string operators and cases after authentic casts, retaining
CV/copy/reference reads, lazy fallthrough and throwing callback control.
[Recursive Stringable comparisons](coverage/semantics/aggregate-stringable-comparison-review.json)
now retain enclosing arrays and declared-property objects across casts, preserving
copy-on-write, live slots/cells, successive casts and active recursion guards.
The preceding six-source/521-check cut remains frozen. [Property-table casts](coverage/semantics/materialized-stringable-comparison-review.json)
now retain stdClass objects and their concrete tables, preserving old dynamic buckets
under copy-on-write. Initialized public declared tables keep live slots and old
reference cells distinct. Six new exact sources and 576 reached premises/28 raw
steps pass; that cut left mixed membership and guarded projection open.
[Fiber comparison transfers](coverage/semantics/fiber-aggregate-stringable-comparison-review.json)
now preserve recursion guards in authentic waiting and suspended VMs. Array COW,
declared live slots versus captured cells, and injected TypeError through caster
and caller finally entry pass three exact sources and 315 reached premises/23 raw
steps. Broader close/destructor lifetimes remain required.
[Mixed ordinary tables](coverage/semantics/mixed-property-stringable-comparison-review.json)
now keep declared slots live in retained tables while copied generations keep their
own values. Dynamic add/unset, shared cells, physical unset buckets and throw cleanup
pass six exact sources and 743 reached premises/37 raw steps. Foreach and array casts
read the current table. Cached cloning and collector traversal remain explicit limits.
[Materialization during direct comparison](coverage/semantics/direct-table-comparison-review.json)
now preserves the original inline-slot walk while nested comparisons use separate
concrete-table guards and pins. Live slots versus retained cells, newly added dynamic
fields and nested throw/finally cleanup pass three exact sources and 383 reached
premises/26 raw steps.
[Fast projections during comparison](coverage/semantics/direct-projection-comparison-review.json)
now copy ordinary declared properties without creating cached tables or replacing
the object guard. Singleton references copy their values; shared references stay
live. Independent projected-array guards and identical TypeError cleanup pass
three exact sources and 503 reached premises/35 raw steps.
[Changed comparison operands](coverage/semantics/stringable-redispatch-comparison-review.json)
now invoke a second ordinary Stringable cast against the saved first string.
Operand order, aggregate pins/guards and selected-case continuation survive the
callback. Live CV/cell mutation, unequal early exit and identical TypeError cleanup
have native-source and reached-state checks; wider object handlers remain open.
[Changed non-Stringable comparison operands](coverage/semantics/nonstringable-redispatch-review.json)
now finish when the comparison's second implicit cast meets a live stdClass or
ordinary source object with no effective `__toString`. That failed cast is quiet;
the object orders after the saved first string and nonzero leaves skip later casts.
CV rebinding, copied text, retained cells, array COW and first-caster throw cleanup
pass three exact sources and 423 Boolean premises/12 raw steps.
[Finite internal changed operands](coverage/semantics/internal-nonstringable-redispatch-review.json)
now admit real/named Closures and Generator/Fiber targets after the first source
cast. The quiet failed second implicit cast preserves signed order, retained cells,
cursor pins and captured children without invoking a callable or resuming a VM.
Three exact sources and 352 Boolean premises/13 raw steps pass; other object-pair
handlers and wider lifetime limits remain partial.
[Weak internal changed operands](coverage/semantics/weak-nonstringable-redispatch-review.json)
also admit WeakMap and WeakReference after the first source cast, including a live
wrapper whose referent has expired. The second implicit cast fails quietly without
reading private entries or referents. Three exact sources and 318 Boolean premises/
12 raw steps preserve signed order, COPY/cell distinctions, COW and throw cleanup;
explicit-cast and existing producer/lifetime domains are unchanged.
[Finite Throwable comparisons](coverage/semantics/throwable-string-comparison-review.json)
now format builtin and inherited internal handlers at reached string leaves, including
a new opposing object after a source cast. Root cache updates, ignored previous
overrides, skipped leaves and saved CV/cell completion pass three exact sources
and 278 reached premises/8 raw steps. Wider formatter callbacks remain open.

Distinct live WeakMap pairs now compare with order zero without reading private
entries or invoking their values. Array and declared-property comparisons continue
to later real casters; COW, private-value ownership and normal/throw cleanup pass
three exact sources and 246 Boolean premises/9 raw steps. Existing entry/lifetime
limits remain separate.
[WeakMap comparison review](coverage/semantics/weakmap-comparison-review.json).
Mixed comparisons with live stdClass, source instances and WeakReference now
return uncomparable +1 in both directions before properties or private entries.
Seven-operator rows include expired referents; aggregate mismatches skip later
Stringable leaves. Wider producer/lifetime forms remain partial.
[Mixed comparison review](coverage/semantics/weakmap-mixed-comparison-review.json).
Mixed WeakMap comparisons also admit normalized real/named Closures, actual
Generator/Fiber tags and finite builtin Throwable kinds. Left-handler fallback and
class mismatch skip captures, VMs, formatter/cache fields and later aggregate casts.
Three exact originals and 468 Boolean premises/16 actual steps preserve owner1 and
complete step states; the old non-map Throwable refusal stays distinct.
Other Closure bodies/internal/custom counterparts and wider lifetimes remain partial.
[Internal counterpart review](coverage/semantics/weakmap-internal-comparison-review.json).

Mixed WeakMap comparisons now also admit normalized direct-method and callable-array
method Closures, without reading receivers, captures, scope rows or private entries.
Three exact sources and 266 Boolean premises/8 actual steps preserve real captured
receiver owners and unchanged aggregate states; later real method/tail bodies remain
quiet until explicitly called. Other Closure representations and wider weak lifetimes
remain partial. [Method-Closure review](coverage/semantics/weakmap-method-comparison-review.json).

Fixed literal method-string Closures now also compare with live WeakMap before
receiver, scope or private-entry traversal. Bound captures and inherited static
captures pass all seven operators in both directions; cloned parent selection,
sole receiver owners and skipped aggregate tails pass two exact sources and
321 Boolean premises/8 actual steps. Stored-string carrier conversion remains a
separate producer gap. [Literal-string review](coverage/semantics/weakmap-string-method-comparison-review.json).

Live WeakMap comparisons also admit supported fromCallable and rebound fake Closures.
They preserve current receiver owners while leaving SOURCE and copied original-scope
history nonowning, even after the seed Closure and old receiver retire. Two exact
sources and 361 Boolean premises/8 actual steps cover all seven operators, cloned
parent-body selection, quiet skipped tails and complete unchanged comparison states.
[Factory/binding review](coverage/semantics/weakmap-factory-comparison-review.json).

Ordinary eligible intrinsic and Fiber API Closures also compare with live WeakMap
before capture, VM or private-entry traversal. Two exact sources and 279 Boolean
premises/8 actual steps preserve GC-enabled observations, a sole cold Fiber owner
and skipped aggregate tails. Later explicit calls expose the flag change and VM
execution. Special intrinsic kinds and wider protocols remain partial.
[Intrinsic/API review](coverage/semantics/weakmap-api-comparison-review.json).

[Numeric object comparison Notices](coverage/semantics/object-numeric-comparison-review.json)
now pause ordinary source-instance/int/float leaves through real error handlers.
Live CV/cell reads remain distinct from copies; a second Notice uses saved 1/1.0,
and aggregate guards and cursors survive callback mutation and throw. Four exact
sources and 482 reached premises/26 raw steps pass. That cut admits a quiet
terminal remainder; wider handlers and lifetimes remain open.
[Builtin stdClass numeric Notices](coverage/semantics/stdclass-numeric-comparison-review.json)
use the same continuation with a fixed builtin class image. Restored second
Notices retain saved 1/1.0 across stdClass/source-instance changes and late live
writes. Three exact sources and 347 reached premises/19 raw steps pass;
property, getter and other internal-handler coverage is unchanged.
[Throwable numeric Notices](coverage/semantics/throwable-numeric-comparison-review.json)
now use builtin nominal kinds and source-subclass names without stringification.
Saved second-Notice targets, copied values, retained cells and original-Exception
throw cleanup pass three exact sources and 340 reached premises/17 raw steps;
string caches and previous links remain intact. Wider limits are unchanged.
[Generator and Fiber pairs](coverage/semantics/generator-fiber-comparison-review.json)
now compare with order zero within the same runtime class, preserving their VM
and capture state. Three exact sources and 409 reached premises/14 raw steps
cover created, suspended and completed values, later aggregate casts and throw cleanup.
[Closure and resumable numeric Notices](coverage/semantics/internal-numeric-comparison-review.json)
now retain fixed class images for real/named Closures, Generators and Fibers.
Three exact sources and 317 reached premises/13 raw steps preserve saved second
numbers, captured children and aggregate cleanup, with no callable invocation or VM
resumption by the numeric cast.
[Weak numeric Notices](coverage/semantics/weak-numeric-comparison-review.json)
now include WeakMap and WeakReference with fixed names and opaque private data,
even after referent expiry. Saved 1/1.0, copied/retained operands, real COW and
pending-Throwable cleanup pass two exact originals and 355 premises/14 raw steps.
Other handler and weak-lifetime forms remain partial.
[Pending comparison remainders](coverage/semantics/pending-exception-comparison-review.json)
now skip later registered callbacks and source string casts while preserving
default numeric Notices and the original thrown object. Three exact sources and
319 premises/10 raw steps cover retained/replaced handlers, array/property scans
and fresh comparison after cleanup. Wider effects remain explicitly bounded.
[Pending Throwable comparison casts](coverage/semantics/pending-throwable-comparison-review.json)
now skip builtin and inherited internal handlers in that authenticated numeric
remainder. Signed nonzero order stops before later Notices without reading fields
or changing cold/warm caches and previous links. Three exact sources and 509
Boolean premises/11 raw steps pass; normal and finally formatting are unchanged.
[Match expressions](docs/semantics/SOURCE-MATCH.md) preserve strict, lazy arm
selection, delayed CV subjects, ordered compiler diagnostics and owned value
results; their [review](coverage/semantics/match-review.json) binds source, compiler
and paused-state checks. [Generated Throwable objects](docs/semantics/THROWABLES.md)
now support ordered no-finally try/catch and throw/rethrow, internal constructors,
getters and structured traces. The distinct `ErrorException` constructor and
`getSeverity` have a separate [bounded review](coverage/semantics/error-exception-review.json).
Ordinary and promoted constructor parameters accept one zero-argument builtin
`#[SensitiveParameter]`. Captured traces store owning `SensitiveParameterValue`
snapshots; `getValue()` and trace strings observe the same wrappers. The
[trace review](coverage/semantics/sensitive-parameter-review.json) records current
fixed CVs, original variadic operands and final wrapper release. The
[promotion review](coverage/semantics/sensitive-promotion-review.json) preserves
value/reference properties separately from later CV snapshots and authenticates
queued promotions. Mixed/repeated/argument attributes, hooks and wider wrapper
protocols remain required.
Direct `SensitiveParameterValue` construction copies a dereferenced mixed value;
readonly re-entry preserves that snapshot, and getter copies retain ordinary
ownership. Seven originals and separate constructor/lifetime checks are recorded
in the [constructor review](coverage/semantics/sensitive-value-constructor-review.json).
First-class `getValue(...)` callables retain their wrapper and captured value;
getter copies, callable clones and final release keep ordinary ownership. Five
originals and separate capture/lifetime checks are recorded in the
[getter review](coverage/semantics/sensitive-value-getter-review.json).
First-class `__construct(...)` callables retain the initialized wrapper through
argument sends and readonly rejection. Aliases, explicit/nullsafe invocation and
clones preserve ownership; the callable's old snapshot and the Error's rejected
replacement retire independently. Five originals and separate genuine checks are
recorded in the [constructor callable review](coverage/semantics/sensitive-value-constructor-callables-review.json).
[Finally continuations](docs/semantics/SOURCE-FINALLY.md) preserve normal,
thrown and transferring outcomes, including value/reference returns, loop jumps
and goto across protected regions. [Source Throwable subclasses](docs/semantics/THROWABLE-SUBCLASSES.md)
inherit owned internal slots, constructors, getters, traces and source override
dispatch; their [bounded review](coverage/semantics/throwable-subclass-review.json)
separates full source, paused-state and later concat checks. Other internal
property access and lifecycle integration remain pending.
[Exit and die](docs/semantics/EXIT.md) support literal, computed, first-class and
pipe invocation, ordered argument binding, internal error traces and a distinct
explicit-exit completion. Ordered shutdown callbacks and request-stage destructors
follow that completion; later request phases remain required. Native checks compare
observable bytes and process status without inferring an exit category.
[Named empty classes](docs/semantics/SOURCE-CLASSES.md) now support early and
conditional activation, allocate owned objects, and support identity, exact class
types and literal `instanceof`; their [review](coverage/semantics/object-classes-review.json)
binds source and paused-state checks.
Ordinary parentless anonymous classes now publish source-authenticated names before
execution and allocate a fresh instance on each visit. Repeated visits create
distinct objects of one class; separate same-line sites have distinct class
identities and methods retain lexical scope. Raw exception traces keep
the full NUL-bearing name; display uses its C-string prefix. Three originals agree
at separate cuts in the [anonymous class review](coverage/semantics/anonymous-classes-review.json).
Dynamic include/eval also preserve the request-wide compiler name sequence:
repeated visits reuse one class with distinct objects, and a fresh compilation
gets the next suffix. A skipped include_once preserves that history. Two exact
originals and 254 SL premises cover direct CV-assignment sites with closed,
completed compilation history and no pre-name diagnostics; wider dynamic source
shapes and failure/reentry contexts remain partial.
[Dynamic-unit review](coverage/semantics/anonymous-dynamic-units-review.json).
Simple global function and static Closure factories also publish their class before
the first call while saving only the restored unit image; two fresh originals
check pre-call lookup, compile-order names and repeated instances. Public noarg
untyped constructors now initialize defaults before the body, ignore automatic
return values and preserve shared Throwable identity through ordinary unwind.
[Four further originals](coverage/semantics/anonymous-constructors-review.json)
also check explicit calls, factory effects and constructor `finally` blocks.
Plain empty named classes can share those units globally and in valid named
namespace sections, including repeated unbracketed sections and bracketed global
bodies. Eligible root/actual-block classes consume no RTD key; deferred classes
consume one even when never published. Qualified names separate same-short-name
and namespace-local internal-looking classes; anonymous sites share the compiler
counter. Methods keep their lexical namespace after caller namespace switches.
The [mixed](coverage/semantics/anonymous-mixed-rtd-review.json),
[block](coverage/semantics/anonymous-block-rtd-review.json),
[bracketed](coverage/semantics/anonymous-namespace-rtd-review.json) and
[unbracketed reviews](coverage/semantics/anonymous-unbracketed-rtd-review.json)
retain distinct native/source/state cuts and original failures. Three new originals
agree at 919bdf8c; author and independent fixtures pass 392 checks with 16 actual steps.
The previous namespace375 join over 4fa216264 passes strict3 at e95aa8ce (5.922s);
private native/source/state cuts retain their original revisions.
Plain empty named declarations also publish from direct root or namespace-body
noarg by-value untyped named functions. Three originals agree at 65c3071c; the
[named-factory review](coverage/semantics/anonymous-named-factory-rtd-review.json)
records 388 checks with ten actual steps for call-order publication, function/callsite
history, saved frames and guarded repeated fresh defaults.
Actual375 over 9ae5ca333 passes strict3 at 684ff104 (5.825s); private
native/source/state cuts retain their original revisions.
Named functions also admit standalone root/namespace-body Block chains: they are
callable before the blocks, and the later function statement preserves state.
The [block-factory review](coverage/semantics/anonymous-block-factory-rtd-review.json)
binds three originals to actual publication, no-op and fresh-allocation checks.
Its 375 join over 0d53475a retains the tested 55dc compiler check after review of
the guarded retired-object paths; no private cuts were replayed.
Exact noarg by-value untyped named functions directly in root or namespace `if`
main, `elseif` or `else` bodies admit plain empty named declarations. Anonymous
fullnames exist before callable publication; executed function statements publish once, and calls
then publish their named classes. The [branch-factory review](coverage/semantics/anonymous-branch-factory-rtd-review.json)
checks skipped branches, reverse calls, fresh defaults and the selected callable
origin when mutually exclusive branches share a case-insensitive function name.
The 375 join over a123a1a5 passes strict3 at 8bde7b9d (5.925s), checking
the shared task datatype. Review preserves the parentless class-link identity;
private cuts retain their original revisions.
The earlier [conditional-factory review](coverage/semantics/anonymous-conditional-factory-rtd-review.json)
retains duplicate executed declaration failure before either body runs.
Its earlier 375 join over 8087545b passes strict3 at 78decf21 (5.875s), covering
the shared task datatype and scalar-echo guard compatibility; private source/state cuts retain
their original revisions.
Static no-capture noarg by-value untyped Closures assigned to ordinary variables
at root/namespace body, through authenticated standalone Block chains or directly
in actual `if`, `elseif` and `else` bodies admit plain empty named declarations.
The [conditional-Closure review](coverage/semantics/anonymous-conditional-closure-rtd-review.json)
checks live anonymous names before creation, skipped assignments, actual capture,
call-order publication and fresh defaults. Its 375 join over 4b13f151 passes strict3
at 7983239b (5.925s), checking the shared task datatype. Review preserves the
parentless class-link identity; private cuts retain their original revisions.
The [block-Closure review](coverage/semantics/anonymous-block-closure-rtd-review.json)
binds three originals and 18 actual steps for Block entry, Closure capture,
call-order publication and fresh defaults. The earlier
[direct-Closure review](coverage/semantics/anonymous-named-closure-rtd-review.json)
retains fatal redeclaration before another allocation.
The earlier Block Closure join of 375 modules over 92f726a3 passes strict3 at
fbacca7a (5.976s); private native/source/state cuts retain their original revisions.
Both factory kinds also admit authentic `while` bodies and `if`, `elseif` or
`else` branches through standalone Block chains and mixed source-authenticated
If/While ancestry at root or a valid namespace body. Selected branches publish functions or create Closures;
skipped branches retain their anonymous identities without either action.
Anonymous names precede publication or Closure creation, including skipped loops.
Two live Closure instances from one compiled template preserve old/current targets,
one guarded class publication, lexical namespace and fresh defaults.
Both exact factory forms also admit `do` bodies through authenticated standalone
Block chains at root or a valid namespace body, including existing conditional
ancestry, direct `while` hosts and nested `do` hosts. Actual Do/While/Block ancestors,
terminals and complete factory guards stay mandatory. Selected hosts publish functions or create
Closures; skipped hosts preserve missing callables while anonymous names already exist.
The [nested-Do review](coverage/semantics/anonymous-nested-do-rtd-review.json)
checks both actual Do ancestors, reverse class publication, retained Closure receivers
and fresh defaults. Three originals agree at 686cb43f /376 (strict3 6.126s), with
702 focused premises and 25 genuine steps at that cut. The
[Do-hosted If review](coverage/semantics/anonymous-do-if-rtd-review.json) adds
authenticated main/elseif/else branches beneath Do and existing Block chains.
Three originals agree at 8ba686a6 /377 (strict3 6.074s), including Do→If→While
selection, reversed publication, retained Closure receivers and fresh defaults.
Author and independent fixtures pass 868 focused checks with 36 genuine steps.
Direct While hosts beneath Do and wider factory guards remain Unsupported.
The earlier [While-hosted Do review](coverage/semantics/anonymous-while-do-rtd-review.json)
retains source3/state683 and its 5ff2413e/d02e5167 strict3 composition; only its
nested-Do exclusion is superseded. The earlier [If-hosted Do review](coverage/semantics/anonymous-conditional-do-rtd-review.json)
retains its original source/state cuts and WeakMap composition; only its direct
While-host exclusion is superseded.
The earlier [Do body-Block review](coverage/semantics/anonymous-do-block-rtd-review.json)
binds three originals at 9d2ca309 /375 (strict3 6.025s) and 690 premises:
648 setup/frontier, 42 pure, with 27 genuine Block, publication, creation/capture,
allocation and eligible no-op steps. Fixtures stop at required allocations; native
observations retain reverse publication, two Closure instances and fresh defaults.
The 375 join over 75c2bdfc passes strict3 at 15c9705e (5.972s), checking
the shared getter task and Iterator snapshot record. Review preserves parentless
class linking and excludes the bool-typed __get/Iterator reception routes; private
cuts keep their original revisions.
The earlier [direct-Do review](coverage/semantics/anonymous-do-rtd-review.json)
retains source3/state653 at 2ee1454b and its 5306defe/75aaa60f composition,
reusing strict3 at tested 2ee1454b (5.974s) with reviewed bind/hook exclusions and
reached parentless linking. No old Do-control/fatal or private evidence replay.
The [While-hosted If review](coverage/semantics/anonymous-while-if-rtd-review.json)
checks genuine If/CHOOSE selection, callable publication, Closure creation/capture
and authentic saved-frame allocations. Unsupported loop placements and nested factories remain required.
The 375 composition at de256ec9 over 07af20a3 reuses strict3 at tested
df0ae18c (6.122s). Review retains parentless class linking and excludes the changed
reference-notice, bind, getter, hook, collector and Iterator routes. No current actor
or private replay is claimed.
The earlier [nested-While review](coverage/semantics/anonymous-nested-while-rtd-review.json)
binds three exact originals to selected/skipped nested hosts, reverse publication
and old/current Closure receivers.
The 375 join over c40c6f57 passes strict3 at fb295c7c (5.976s), checking
the shared task datatype. Review preserves parentless class linking and excludes
the changed bind/getter/hook/collector routes; private cuts retain their revisions.
The earlier [If-hosted While review](coverage/semantics/anonymous-conditional-while-rtd-review.json)
retains its branch selection, callable/Closure ownership and allocation cuts.
The 375 join at aa241bdf over 1867decf reuses strict3 at tested 376de1e1
(6.226s). Review preserves parentless class linking and excludes the changed
hook/finally/bind/collector/Iterator routes; no current actor or private replay is claimed.
The earlier [While body-Block review](coverage/semantics/anonymous-while-block-rtd-review.json)
binds three exact originals and focused Block/publication/creation/allocation
frontiers; state fixtures stop at their required allocation.
The 375 join at ac329f66 over 772760f0 reuses strict3 at tested 35adca9a
(6.125s). Review excludes the changed finally/bind/Iterator routes; no current
actor or private replay is claimed.
The earlier [While review](coverage/semantics/anonymous-while-factory-rtd-review.json)
retains direct loop selection and same-source second-iteration fatal observations,
source4/state1007 at ff82bb60 and the 1c0ffdae/30a22375 strict3 join (5.925s).
The earlier [nested-host review](coverage/semantics/anonymous-nested-branch-rtd-review.json)
retains source3/state882 and its strict reuse over f37653ce, without replay.
The earlier [branch-body Block review](coverage/semantics/anonymous-branch-block-rtd-review.json)
retains its private cuts and ae8b65a9/d3beefe6 strict join without replay.
The earlier [Block-host review](coverage/semantics/anonymous-block-branch-rtd-review.json)
retains its original failures and reused strict3 at 5d91ff5f for the 431dacbd/c35c223e
join, without a current actor or private replay.
Wider Closure targets/placements/signatures, function placement/signatures and RTD/publication contexts,
constructor arguments/types, inheritance, attributes and broader consumers remain required.
[Internal `stdClass` identity](docs/semantics/SOURCE-STDCLASS.md)
now allocates an owned empty object with exact nominal typing and ordinary
empty-object behavior; its [review](coverage/semantics/stdclass-review.json)
binds source and ownership checks. [Non-object casts](docs/semantics/OBJECT-CASTS.md)
add populated stdClass storage, shared-table COW, clone/array round trips and
genuine NaN/key-notice callbacks, with explicit retired-pointer boundaries.
[No-constructor allocation arguments](docs/semantics/SOURCE-NOCTOR-ARGS.md)
evaluate positional, named and unpacked values after class lookup while retaining
sent values through the dummy call; their [review](coverage/semantics/noctor-args-review.json)
binds source, compiler and paused-state checks. [Empty-class inheritance](docs/semantics/SOURCE-INHERITANCE.md)
links eligible source and `stdClass` parents at their required publication time;
`instanceof` and class types follow transitive ancestry. Its [review](coverage/semantics/inheritance-review.json)
binds source, compiler, syntax and paused-state checks. Other internal-class
bodies and method callbacks remain open.
A single builtin `#[AllowDynamicProperties]` permits dynamic slots on named
classes and descendants while ordinary classes retain deprecation. Invalid
trait/interface/readonly targets preserve diagnostic priority and keyword lines;
ten sources and 131 derived/reached checks are recorded in the
[attribute review](coverage/semantics/allow-dynamic-properties-review.json).
Public backed by-value `get` hooks execute their block or expression body on each read,
use the property's return type and retain ordinary writes to the backing slot.
Only the active hook on the same receiver bypasses dispatch; nested calls and
other receivers invoke their hooks. Eight originals and 177 source/state checks
cover exceptions, traces and receiver/result cleanup in the
[hook review](coverage/semantics/backed-get-hooks-review.json). Expression bodies
retain their real source child and compiled implicit-return line; seven additional
originals and 137 return/callback/lifetime checks pass in the
[expression review](coverage/semantics/expression-get-hooks-review.json). Virtual getters
without defaults retain declaration/type metadata and own no backing slot; writes
evaluate the RHS before read-only rejection and returned values have ordinary
result ownership. Eight affected source agreements and 139 derived/reached checks
are recorded in the [virtual review](coverage/semantics/virtual-get-hooks-review.json).
Literal CV/`$this` `isset` and `empty` invoke these getters and test their returned
value, releasing temporary results before branch output while the receiver
remains live. Two originals and 162 premises (143 reached, 19 derived) pass in the
[quiet hook review](coverage/semantics/quiet-get-hooks-review.json).
Literal CV/`$this` hook coalescing retains returned zero, false and object values;
only null selects the fallback. Kept objects survive receiver destruction and
release when their last result owner disappears. Two originals and 249 premises
(224 reached, 25 derived) pass in the
[coalesce review](coverage/semantics/coalesce-get-hooks-review.json).
Literal CV/`$this` hook `??=` retains the getter's actual nonnull value and
writes the original fallback only for null. A CV receiver is refetched after
the RHS, including rebinding; returned objects keep ordinary result ownership.
Three originals and 308 premises (264 reached, 44 derived) pass in the
[coalesce-assignment review](coverage/semantics/coalesce-assignment-get-hooks-review.json).
Direct literal CV/`$this` unset of backed or virtual hooked properties raises
`Error`, including inside the active getter, without reading or changing the slot.
Backing values survive rejection and release with receiver storage. Two originals
and 182 premises (178 reached, 4 derived) pass in the
[unset review](coverage/semantics/hooked-unset-review.json).
Literal CV/`$this` backed get-hook `+=` with an evaluated integer RHS uses the
getter's actual value and stores on the receiver selected after the RHS.
Getter rebinding preserves that selected target. Arithmetic errors keep it live
through returned-value cleanup, then release it before catch. Three originals and
separate scalar/derived and receiver/lifetime state cuts are recorded in the
[addition-assignment review](coverage/semantics/backed-get-hook-addassign-review.json).
Named subclasses can override a public backed by-value getter with another
backed getter of the same normalized property type. The child supplies the
effective slot/default and getter scope; inherited `$this` reads dispatch to it,
while the called class remains the runtime descendant. Returned objects survive
receiver cleanup independently. Two originals and separate scalar/lifetime state
cuts are recorded in the
[override review](coverage/semantics/backed-get-hook-override-review.json).
A child getter without its own backing access or initializer also keeps a
physical slot when its immediate parent's getter body is backed and the property
types match. The child replaces the parent default with uninitialized typed
storage or untyped null; ordinary writes use that slot. Receiver cleanup releases
the backing reference; separately retained return values can survive.
Two originals and separate scalar185/lifetime100 checks are recorded in the
[effective backing review](coverage/semantics/effective-backed-get-hook-review.json).
That storage also propagates through repeated equal-type public getter overrides
without backing access or initializers, including intervening classes without a
redeclaration. Two originals and separate dispatch, write, ancestry and lifetime
checks are recorded in the
[repeated override review](coverage/semantics/repeated-effective-backed-get-hook-review.json).
Virtual getters can override another virtual getter of the same normalized type,
without initializers, when their linked ancestry closes at a genuine virtual root.
They retain no physical slot; reads use the child's lexical scope and runtime
descendant dispatch, and writes raise a read-only error naming that descendant.
Retained return values survive receiver cleanup. Two originals and separate
CV, inherited `$this`, write and lifetime checks are recorded in the
[virtual override review](coverage/semantics/virtual-get-hook-override-review.json).
Public get-only virtual overrides without initializers also accept covariant
property types when both declarations have a type: builtin narrowing and linked
nominal subtypes preserve child scope, empty storage and retained return values.
Incompatible getter signatures fail at the actual hook declaration before
property-type checks;
backed-parent inheritance remains invariant. Three originals and separate CV, inherited
`$this`, lifetime and rejection checks are recorded in the
[covariance review](coverage/semantics/virtual-get-hook-covariance-review.json).
For these virtual getters, removing the inherited property type fails at the
child getter declaration before the property-type check. A typed child overriding
an untyped parent retains the later property diagnostic at the class declaration;
both-untyped overrides retain child scope and inherited `$this` dispatch.
Three originals and separate rejection/dispatch checks are recorded in the
[type-presence review](coverage/semantics/virtual-get-hook-type-presence-review.json).
Public source-body-backed getter pairs with literal defaults follow the same
hook-line priority when an inherited type is removed. Both-untyped reads and
inherited `$this` dispatch preserve one child backing slot; ordinary writes
change that slot. Three originals and separate rejection/read/write checks are
recorded in the
[backed type-presence review](coverage/semantics/backed-get-hook-type-presence-review.json).
A genuinely body-backed child getter can also override a virtual getter of the
same normalized type. The child keeps its own physical slot and default; inherited
reads use child/private scope and runtime descendant dispatch. Receiver cleanup
releases the backing reference independently of a retained return value.
Two originals and separate CV, inherited `$this`, write and lifetime checks are
recorded in the
[virtual-parent review](coverage/semantics/virtual-parent-backed-get-hook-review.json).
With both types present, these backed children also accept builtin and linked
nominal covariant narrowing. Writes enforce the child type; rejected values
preserve its slot. Incompatible getters fail at the child hook declaration.
Three originals and separate CV, inherited `$this`, write, lifetime and rejection
checks are recorded in the
[backed-child covariance review](coverage/semantics/virtual-parent-backed-get-hook-covariance-review.json).
Removing an inherited type from these own-backed children also fails at the
getter declaration. The typed-child/untyped-parent direction retains the later
class-line property error; both-untyped controls keep the child slot and writes.
Three originals and separate rejection/read/write checks are recorded in the
[cross-shape type-presence review](coverage/semantics/virtual-parent-backed-get-hook-type-presence-review.json).
A typed, source-body-backed parent also rejects an untyped, body-unbacked child
without an initializer at the getter declaration. Both-untyped controls retain one
physical child slot with a null default; private and inherited reads still return
13 after an ordinary write stores 300. Three originals and separate
rejection/read/write checks are recorded in the
[inherited-storage type-presence review](coverage/semantics/backed-parent-unbacked-get-hook-type-presence-review.json).
The same getter error priority now applies when a source-unbacked parent inherits
physical backing and a source-unbacked child without an initializer removes its
type. Intervening classes retain the actual declaring getter; reverse type addition
and repeated null-slot reads/writes remain controls. Three originals and five
separate state checks are recorded in the
[effective-storage type-presence review](coverage/semantics/effective-backed-parent-unbacked-get-hook-type-presence-review.json).
This getter error priority also applies when the child has genuine backing access
and its own default. The proof follows the effectively backed parent's declaring
getter across intervening classes. Reverse type addition and both-untyped controls
retain the child's slot 200, inherited/private reads returning 213, and write 300
followed by getter result 313. Three originals and five separate state checks are
recorded in the
[own-backed-child type-presence review](coverage/semantics/effective-backed-parent-backed-get-hook-type-presence-review.json).
Ordinary public parent properties now also admit a genuinely backed child getter
of the same normalized type. The child keeps its own slot and default; inherited
reads use child/private scope and runtime descendant dispatch. Backing references
release independently of retained getter results. Two originals and separate CV,
inherited `$this`, write and lifetime checks are recorded in the
[ordinary-parent review](coverage/semantics/ordinary-parent-backed-get-hook-review.json).
Ordinary parents also preserve physical storage under a child getter without an
initializer or backing read. Typed child slots start uninitialized; untyped slots
start null. Ordinary writes update those slots while getters keep their independent
results. Two originals and separate read, write, untyped and lifetime checks are
recorded in the
[ordinary-storage review](coverage/semantics/ordinary-parent-unbacked-get-hook-review.json).
Repeated getter declarations now carry this ordinary storage through intervening
classes. Typed slots start uninitialized and untyped slots null; reads select the
latest getter and its private scope, while writes update the physical slots.
Distinct backing and retained result references use the existing cleanup rules.
Two originals and nine separate state checks are recorded in the
[repeated ordinary-storage review](coverage/semantics/repeated-ordinary-unbacked-get-hook-review.json).
A typed getter directly backed by an ordinary parent also rejects an untyped,
source-unbacked child at its getter declaration. Across intervening classes, the
error names the actual declaring getter; reverse type addition keeps the property
error. Three originals and focused rejection/plan checks are recorded in the
[ordinary-backing type-presence review](coverage/semantics/ordinary-backed-parent-unbacked-get-hook-type-presence-review.json).
The same priority now covers a genuinely own-body-backed child that removes the
type. Reverse addition and existing backing 200→300/getter 213→313 remain controls;
focused states check rejection before publication and genuine getter entry.
[Own-backed type-presence review](coverage/semantics/ordinary-backed-parent-backed-get-hook-type-presence-review.json).
An equal-type plain child property now inherits a genuine backed parent getter.
The child keeps its own default and storage, while the getter's function, lexical
scope, private helper and trace class remain the parent's; called scope follows
the receiver. One original and four focused states cover child/Grand entry and
write 300/getter 313 in the
[inherited-getter review](coverage/semantics/plain-child-inherited-backed-get-hook-review.json).
Repeated plain redeclarations now retain that original getter through authenticated
inheritance edges. The latest property supplies the slot and default; original
parent function/private scope remains distinct from receiver called scope.
One original and four focused states cover slot 300→400/getter 313→413 in the
[repeated inherited-getter review](coverage/semantics/repeated-plain-child-inherited-backed-get-hook-review.json).
A plain equal-type child also inherits a getter without a source backing read
when an authenticated ordinary ancestor supplies its parent's storage. The typed
parent starts uninitialized; the child owns 200 then 300 while the inherited getter
returns 13 with the parent's function and private scope. One original and three
focused states are recorded in the
[ordinary-backed inherited-getter review](coverage/semantics/ordinary-backed-parent-plain-inherited-getter-review.json).
A genuine hooked backing ancestor now supplies the same positive storage proof.
The nearest source-unbacked parent still supplies the getter and private scope:
Root gets 107, Parent and plain Child get 13, and Child's slot changes 200 to 300.
One original and three focused states distinguish that backing witness from the
selected getter in the
[hook-backed inherited-getter review](coverage/semantics/inherited-backed-parent-plain-inherited-getter-review.json).
A closed virtual get-only parent also passes its getter to a plain public equal-type
child. Parent owns no physical slot; Child owns 200 then 300, while the inherited
getter uses Parent's private method and returns 13. Called scope follows the receiver.
One original and three focused states are recorded in the
[virtual-root inherited-getter review](coverage/semantics/virtual-parent-plain-inherited-getter-review.json).
A virtual `mixed` getter also passes to a plain `int` child. The child keeps its
integer slot 200→300, while the inherited getter keeps Parent's `mixed` return
declaration and returns the string "13". Illegal widening reports the subtype
property error at the child class. Two originals and four focused states are in
[the plain-child covariance review](coverage/semantics/virtual-parent-covariant-plain-inherited-getter-review.json).
A plain public `protected(set) int` child can also inherit the closed virtual
getter. Global writes fail without changing its slot; Child and inherited Parent
methods store 300 and 400 while the getter stays 13. A body-backed parent still
rejects setter narrowing. Two originals and five focused states are in the
[protected setter review](coverage/semantics/virtual-parent-protected-set-plain-inherited-getter-review.json).
Removing a virtual parent's `int` type on a plain child reports the subtype
property error at the child class; adding `int` under an untyped parent reports
that the type must be omitted. Both-untyped inheritance keeps Parent's string "13"
return and the child's physical slot 200→300. Three originals and three focused
states are in the
[plain-child type-presence review](coverage/semantics/virtual-parent-plain-type-presence-review.json).
Repeated plain `protected(set) int` declarations inherit a virtual parent's getter.
First owns 200; Second and Grand start at 300, then Grand's slot becomes 400. The
getter remains 13; later `private(set)` narrowing fails against the immediate parent. Two
originals and four focused states are in the
[repeated protected-setter review](coverage/semantics/repeated-protected-plain-inherited-getter-review.json).
A direct trait’s public body-backed `int` getter also imports into a parentless
using class. Its code and `__METHOD__` spelling remain the trait’s; lexical/private
scope follows the using class and called scope follows the receiver. Slot 100→300
yields 113→313. An identical plain own property still conflicts. Two originals
and four focused states are in the
[trait-getter review](coverage/semantics/trait-imported-backed-getter-review.json).
A direct trait’s virtual get-only `int` getter also imports without physical
storage. Consumer and Grand casts are empty; the getter uses Consumer’s private
method and returns 13, with called scope following the receiver. A Grand write
throws the read-only Error and leaves storage empty. The
[virtual-trait review](coverage/semantics/trait-imported-virtual-getter-review.json)
records one original and three focused states.
A trait’s body-backed expression getter also retains its physical expression
and magic name while executing in Consumer scope. A real backing write 100→300
changes its result 113→313. Physical task lowering and logical imported return
checks are covered by one original and three states in the
[expression-trait review](coverage/semantics/trait-imported-expression-getter-review.json).
Selected virtual expression trait getters also import with no physical slot.
Consumer private13 and Trait magic survive; a Grand write raises the read-only
Error and the getter still returns13. The [virtual-expression review](coverage/semantics/trait-imported-virtual-expression-getter-review.json)
records one original, three new states and the affected earlier controls.
A backed expression trait getter can also import into a class with a real
parent and no same-name parent property. The inherited marker700 survives
Grand’s value100→300 write; Base caller scope and Consumer getter scope stay
distinct. One original and three states are in the [parented-trait review](coverage/semantics/parented-trait-expression-getter-review.json).
Selected public ordinary same-name parents are also admitted: imported int100
replaces Base int10 in the physical slot, while Base string still fails the
existing invariant TYPE check. Base caller scope, Consumer getter/private13 and
Grand300/get313 remain distinct. Two originals and four states are in the
[overlap review](coverage/semantics/inherited-overlap-trait-getter-review.json).
A selected private Base value retains its mangled key beside the imported public
slot: Base reads7 while the Consumer getter returns113; Grand’s public write300
yields313 and preserves private7 and marker700. One original and three states
are in the [private-overlap review](coverage/semantics/private-overlap-trait-getter-review.json).
A selected backed expression getter can also pass through one outer trait.
Both real use edges and the intermediate imported property are authenticated;
Inner magic spelling survives Consumer scope rebasing and Grand100→300/get313.
The intermediate hooked collision remains fatal. [Nested-trait review](coverage/semantics/nested-trait-getter-review.json).
Selected backed set-only class hooks now derive their implicit typed `$value`
and void return from the property declaration. Assignment20 returns20 while the
Parent body stores33; a bad array fails before the body and preserves33.
Ordinary reads keep using the slot. One original and three states/234 checks are
in the [set-only hook review](coverage/semantics/backed-set-only-hook-review.json).
A selected public typed statement pair ordered get then set now keeps two real source
functions. A write inside GET and read inside SET use backing storage without
calling the other hook. Assignment20 returns20, stores33 and later reads46.
One original and two states/210 checks are in the
[paired-hook review](coverage/semantics/paired-backed-get-set-hook-review.json).
Selected sole backed setters now retain a real explicit typed parameter. An
`int|string $incoming` setter receives `"20"` and stores `33`; the assignment
returns the original string. A string-only setter fails at hook line7. Two originals and three states/270
checks cover source identity, receive errors and result restoration in the
[explicit-parameter review](coverage/semantics/explicit-setter-parameter-review.json).
A selected sole backed implicit SET also imports directly from a trait. Consumer
private13 and Grand called scope coexist with Trait magic; assignment20 returns20
while storage becomes33. One original and two states/231 checks are in the
[trait-setter review](coverage/semantics/trait-imported-backed-set-hook-review.json).
Selected direct trait setters also retain an actual `int|string $incoming`
parameter. The assignment returns its original `"20"` string after storage33;
Trait magic, Consumer private13 and Grand called scope remain distinct. A
string-only parameter fails at the physical Trait hook line7. Two originals and
two states/281 checks are in the [explicit trait-setter review](coverage/semantics/trait-imported-explicit-set-hook-review.json).
A selected direct Trait GET/implicit-SET statement pair imports both hooks
together. Trait code/magic and Consumer private scope remain distinct; crossed
accesses skip both hooks, and assignment20 returns20 after storage33/get46.
One original and two states/333 checks are in the
[paired trait-hook review](coverage/semantics/trait-imported-paired-hooks-review.json).
A selected sole implicit class setter can also be virtual: `$value` has no slot,
while its body changes a separate stored10 to33. Assignment20 still returns20;
reads raise the receiver’s write-only Error and bad arrays fail before the body.
One original and two states/252 checks are in the
[virtual setter review](coverage/semantics/virtual-set-only-hook-review.json).
An active virtual SET writing through a same-object alias now raises the receiver’s
Must-not-write Error for input from a defined local variable. No second SET runs;
stored10 and the outer result7 remain unchanged. One original and one state/116
checks are in the [alias-write review](coverage/semantics/active-virtual-set-alias-review.json).
A public `protected(set)` backed implicit setter now permits an inherited Child
writer while denying a global write before parameter reception. Assignment of20 returns20
after storage becomes33; an array reaches TypeError only through the permitted
Child call. One original and two states/266 checks are in the
[protected setter review](coverage/semantics/protected-set-backed-hook-review.json).
A selected public `private(set)` backed implicit setter permits the declaring
Parent writer on a Child receiver. Child/global writes fail access before reception;
a permitted Parent array call reaches TypeError. Assignment20 returns20 after
storage33, and a plain Child redeclaration fails against the implicitly final property.
Two originals and two states/305 checks are in the
[private setter review](coverage/semantics/private-set-backed-hook-review.json).
A selected inherited public `__unset(string $name): void` now handles a direct
external unset of a declared private property. Accessible initialized public unset
skips the callback; the callback retains Parent lexical scope and Child called
scope, removes Parent's private slot and sets `seen=13`.
One original and one state/212 checks cover selection, reception and receiver
cleanup; [magic unset review](coverage/semantics/magic-unset-review.json).
A selected inherited `__isset(string $name): bool` now handles terminal `isset`
of a direct CV/literal private property. Initialized public and typed-uninitialized
slots bypass it; actual true/false results preserve short circuiting and storage.
One original and one state/215 checks cover typed name reception, lexical scope
and receiver cleanup; [magic isset review](coverage/semantics/magic-isset-review.json).
Without `__get`, terminal `empty` now returns true after either inherited
`__isset` boolean, retaining the receiver through callback CV rebinding or throw.
Three originals and focused242 checks cover delivery, cleanup and catch;
[isset-only empty review](coverage/semantics/magic-empty-isset-only-review.json).
With an untyped by-value `__get`, terminal `empty` chains it after the inherited
`__isset`: false skips the getter, while true tests its null, bool, int, float
or byte-string result. Only empty bytes or exactly ASCII `0` make a string
empty; NUL and `0` plus NUL do not. The original integer/call state208 remains historical; one further
original and state155 cover primitive results and authenticated string metadata.
[Magic empty review](coverage/semantics/magic-empty-review.json),
[primitive result review](coverage/semantics/magic-empty-scalars-review.json).
Both signed float zeros are empty; other finite/subnormal values and infinities
are not. One further original and state145 check the actual float bits and bounds;
[float result review](coverage/semantics/magic-empty-floats-review.json).
NaN getter results now warn after Get returns, keeping the receiver through a
returning or throwing handler. Three originals and two state cuts totaling242
checks cover the default Warning, caller-CV rebinding and destruction before
result/catch; [NaN warning review](coverage/semantics/magic-empty-nan-review.json).
Ordinary user-object getter RVs now dispose while the isset guard and receiver
remain, before receiver release and false result/catch. Two originals and focused247
checks cover actual RV/receiver destructors, rebinding, the same Exception and
budgets; [object RV review](coverage/semantics/magic-empty-object-rv-review.json).
stdClass RVs now retain that phase through storage and owned-child disposal.
Two originals and focused222 checks cover the real storage pin, child throw,
receiver release and catch; [stdClass RV review](coverage/semantics/magic-empty-std-rv-review.json).
Nonempty array RVs now retain the phase through owned-element disposal; immutable
empty literals yield true directly. Three originals and focused255 checks cover
normal/throw cleanup, shared owners and budgets; [array RV review](coverage/semantics/magic-empty-array-rv-review.json).
Other signatures, receivers, mutable-empty arrays/other internal-object RVs and
wider recursive/coalesce magic combinations remain unsupported.
Hooked iteration, defaulted virtual hooks, other paired or virtual setters, wider trait
setters, other explicit setter parameter forms, references, other inherited/trait
and wider receiver, quiet or indirect-access families and wider `__unset` consumers remain required.
[Source interfaces](docs/semantics/SOURCE-INTERFACES.md) link ordered `extends`
and `implements` declarations, enforce method prototypes and abstract
obligations, and add finite `Stringable`/`Throwable` nominal ancestry. The installed
[finite internal-method increment](coverage/semantics/interface-internal-renewed-review.json)
adds inherited contracts and source `__wakeup` linking checks. Other internal
interface tables, broader constant linking and hooked properties remain open.
[Public object properties](docs/semantics/SOURCE-PROPERTIES.md) now have typed
and uninitialized slots, source-backed defaults, inherited public overrides,
dynamic names, direct access, live foreach, casts and comparison. The
[property review](coverage/semantics/properties-review.json) binds source,
compiler and paused-task checks. [Constructor promotion](coverage/semantics/constructor-promotion-review.json)
retains source parameter declarations, separate property defaults and ordered
value/reference writes after all receives, including explicit constructor re-entry
and inherited/trait scopes. Source9 and genuine Weak48/byref47 preserve the
original failure and separate acceptance cuts. One zero-argument builtin
`#[Override]` on promoted properties now resolves real imports and checks the
effective parent declaration, including deferred trait links. Thirteen originals
and 110 genuine source/trait/rollback assertions have separate reviewed cuts in
[the Override review](coverage/semantics/promoted-override-review.json).
The same builtin on ordinary parameters now produces its native target Fatal
after constant-default compilation and before type checks, preserving spelling,
compiler lines and prior eval notices. Sixteen originals and 109 derived/reached
checks retain separate cuts in [the parameter-target review](coverage/semantics/parameter-override-review.json).
Other parameter attributes/hooks remain required.
[Public property references](docs/semantics/SOURCE-PROPERTY-REFERENCES.md)
now attach ordered typed sources to shared cells, check writes atomically, and
preserve aliases across unset and object traversal. Their
[review](coverage/semantics/property-references-review.json) records exact source,
compiler and paused-state gates. [Instance property visibility](docs/semantics/SOURCE-PROPERTY-VISIBILITY.md) adds lexical
visibility, mangled storage keys and consistent access across aliases, traversal,
casts and clone updates. Private declaring slots preserve ancestor lexical selection,
same-name shadows and inherited-private dynamic fallback.
The [class static property contract](docs/semantics/SOURCE-CLASS-STATICS.md)
models declaration-owned cells, inherited sharing, typed aliases and captured
class identity for computed selectors. Its [bounded review](coverage/semantics/class-static-properties.json)
records installed source and paused controls alongside historical matrices.
Backed static final/asymmetric setters distinguish lexical permission from called
scope, preserve delayed RHS/receiver ordering and typed escaped aliases, and
check raw object slots before writable interior access. The
[setter review](coverage/semantics/static-setter-access-review.json) separates
declaration/source/state checks from the fresh inherited method-array interaction.
Static-method reference assignment with untyped return signatures now retains
lexical/called scope, inherited typed static cells and returned-cell cleanup. Its
[review](coverage/semantics/static-method-reference-review.json) separates original
getter/alias checks from current raw-getter and nullsafe rejection controls.
Typed fetch flags preserve initial-slot error priority and nullable aliases;
handled borrowed reads and a Stringable CONFIG PIPE restore the inherited
getter's scope and arguments while retaining full raw INI bytes.
Discarded genuine reference getters also wrap initialized typed slots; ordinary
by-value getters leave them unchanged. Post-return checks retain only the static
cell owner and its property type source. A focused current-constants check
completes a forward constant table before fetching the reference and preserves
the typed alias. Deferred scalar/array static defaults now evaluate in declaring
scope with strict binding, preserving successful prefixes across later failure.
The [deferred-default review](coverage/semantics/deferred-static-defaults-review.json)
separates eighteen earlier source agreements and five state programs/152 premises
from thirteen new reentry comparisons and one inherited67 ownership/history fixture.
Same-default reentry replaces the live row while escaped typed aliases retain
their ordered constraints; failure preserves the reentrant value. Cold
static reference targets now complete cold tables while keeping the captured RHS
cell alive through callbacks. Dynamic and ordinary method keyword selectors keep
their selected class/name; seven source comparisons and an 84-premise fixture
cover failure/retry, replacement and ownership. Captured/rebound Closure keyword
references now retain authentic scope/binding and nested creator evidence after
collection, including unrelated called classes and handler ingress. Nine new
sources and 162 state premises pass separately. Temporary `Closure::call` children
retain the authentic receiver scope after their maker retires, with genuine
receiver ownership for nonstatic children and nonowning evidence for static
children. Six new sources and 193 state premises pass at separate cutoffs.
Deferred scalar/array instance defaults now use class-owned templates, copying
the parent's actual state when a child links and filling constants, instance
defaults and statics in order before allocating an object. Eight new source
agreements and three programs/172 state premises check private shadows, strict
failure/retry, reentry, link-time copies and template ownership after collection.
Deferred static/no-use Closure and function/method callable defaults now retain
shared template object identities through arrays, constant aliases, retry and
reentry. Nine new source agreements and six programs/335 premises retain their
separate cuts. One actual trait-import source and 98 premises distinguish the
first cached target from each fresh called class/publication prefix, including
retired source objects and namespace fallback. Other object producers and wider
property/callable consumers remain open. Children created by cached property
method callables retain lexical and called scope after wrapped or cloned makers
retire, including private `new self` defaults. Two sources and 170 state premises
retain separate accepted cutoffs.
Shared trait-constant callable targets retain their first lookup while later
method imports use fresh called classes and named/method receipts use current
publication prefixes. Three new source
agreements and112 AL/122 SL premises check partial failure, copied children and
actual constant-cache ownership. Compiled/named keyword NEW now retains exact
constant METHOD receipt authority through plain-clone retirement; one source and
38 reached premises retain their separate [cut](coverage/semantics/named-keyword-new-review.json).
Global `const` Closure and function/method callable values now evaluate before
registration, retaining the genuine main/include/eval entry scope and shared
constant ownership. Duplicate-warning callbacks hold their discarded candidate
and captured lookup prefix; raw-trait notices precede allocation. Nine new source
agreements and seven AL programs/341 premises retain their distinct cuts.
Per-child alias receipts now preserve reads before and after callback namespace
shadows; three further source agreements and two AL programs/184 premises verify
first registration, mixed selections and throwing retry. Global `const new` now
retains the allocated identity through argument evaluation and constructor return,
including ignored no-constructor arguments, access errors, inherited include/eval
scope and escaped failure/retry. Three new source agreements and 274 AL premises
retain separate cuts. Two further cold no-constructor sources and 80/81 AL premises
check table completion before allocation/arguments and fresh retry after failure.
Eager destructor cleanup and wider object producers remain required.
[Zero-argument global `new stdClass()`](coverage/semantics/global-constant-stdclass-review.json)
now preserves ordinary-read identity and property sharing. Duplicate registration
holds the fresh candidate through its Warning handler and discards it afterward,
retaining the original object and callback mutation. Two exact sources and 225 SL
premises cover birth/completion, live/dead authority, alias release and budget
resume. Certified global `constant()` queries now return that same live stdClass
through literal and retained selected calls, preserving shared writes and adding
only the ordinary result owner. [The query review](coverage/semantics/global-constant-stdclass-query-review.json)
keeps two source comparisons and 384 SL premises separate from producer evidence.
Other internal/Throwable producers, arguments, defaults and wider query forms
remain partial.
Certified stdClass aliases now also pass through global constant array trees,
including eval declarations and whole-tree donation. Array queries share the
stored containers until ordinary COW, while embedded object identity and property
writes remain shared. Three exact originals and 648 SL premises retain their
[reviewed cut](coverage/semantics/global-constant-stdclass-array-review.json).
Zero-argument stdClass NEW can now appear directly in nested global constant
arrays, including selected full/shorthand ternary leaves and eval declarations.
Earlier facts retain their source guards; birth receipts preserve distinct leaf
identities, shared property writes and duplicate-candidate cleanup.
The [nested-birth review](coverage/semantics/global-constant-stdclass-new-review.json)
records four source agreements and 1,107 reached-state premises. Whole-array conditional
transfer and wider object producers remain partial.
Newborn stdClass leaves also transfer through `??`, including nested operand
chains, eval units and quiet literal-array dimension reads. A nonnull left keeps
its identity and skips the right; a NULL constant selects a fresh fallback leaf.
The [coalescing review](coverage/semantics/global-constant-stdclass-coalesce-review.json)
records the focused source and state cuts. Conditional aliases, whole-array
coalescing and defaults remain partial.
Global stdClass constant-AST NEW now evaluates and drops ordinary positional and
uniquely named arguments, preserving donated identities, real value destructors
and fresh eval retry after an argument Error. The
[argument review](coverage/semantics/global-constant-stdclass-arguments-review.json)
records the initial duplicate-name lifetime counterexample. Bounded duplicate
argument names now retain the rejected current value, including its nested array
containers, while earlier values and the unfinished target retire. Existing
shutdown callbacks observe that same value after normal output, including writes
through an escaped leaf and a fresh eval retry.
[Duplicate-argument review](coverage/semantics/global-constant-stdclass-duplicate-arguments-review.json).
References, unpacking, defaults and wider lifecycle forms remain partial.
Legal untyped static-slot getters leave ignored object/scalar/null values raw;
used references share the real static cell across inherited scopes. Escaped aliases
can attach to a typed target, then lose only that target's constraint when it is
rebound. Ordinary StaticCall results also retain their reference kind in direct
by-reference sends; value results emit the existing Notice and use a fresh cell,
while first-class callable results reject. Focused ownership checks cover parameter
retirement and allocation release, without claiming destructor/GC callbacks.
Backed asymmetric instance setters288 enforce lexical permission across direct,
compound, reference, dimension and unset operations, while diagnostics retain
called scope. Raw object interiors and object foreach references preserve their
native exceptions. Stringable `.=` retains the selected destination and restores
the writer scope after callbacks. Private34 normal/eight compiler/350 reached
checks retain their [cuts](coverage/semantics/instance-set-access-review.json);
one actual Fiber source preserves the captured property across suspension.
Readonly follow-ons/hooks, wider borrowed destination lifetime and static
Stringable compounds with wider selectors
and broader temporary-return/callable/typed-reference consumers remain open.
The ordinary [readonly slice294](docs/semantics/SOURCE-READONLY.md) adds first
initialization, initialized write priority, detached object references and genuine
first Stringable reentry. Its 39 normal/18 declaration controls, separate Fiber1,
243 reached conditions and SL275 keep distinct cuts. Genuine clone300 callbacks
add object-owned readonly allowances through return/throw/exit and Fiber parking,
preserving borrowed versus actual temporary/intrinsic input owners. Its separate
20 normals/five declarations/exit1 and 264 reached controls pass with SL276.
[Nonempty readonly clone updates](docs/semantics/READONLY-CLONE-UPDATES.md) add a
second window, captured conversions and write revisions. A separate dynamic/FCC
selection follow-on has 20 distinct source agreements, 665 clauses across seven
reached-state groups and a passing compiler gate at recorded cuts. Pending-candidate
identity admission remains open. The earlier290 composition separately passes
two exact originals and79 reached premises for private clone makers and live
clone windows during Generator/Fiber close. Last-owner destination
release, Deprecated method dispatch and promotion remain required. The new reference controls supersede one historical288 internal assertion
without renewing the other accepted gates.

Ordinary literal dynamic-property creation in module 318 resumes eligible warning handlers,
including throws with a surviving receiver, live CV/reference RHS selection and
same-key reentry. Physical duplicate buckets retain native lookup and foreach
order. Receiver retirement stays latched across destructor resurrection; unused
and used assignment results retain different cleanup lifetimes. Its
[review](coverage/semantics/dynamic-property-warning-review.json) keeps the private
source/state cuts and current 297-module GC/cleanup interaction separate. Handler exit,
array casts over duplicate buckets and expired or undefined RHS pointers remain
explicit Unsupported boundaries; computed names and wider writes remain required.

[Physical property references324](coverage/semantics/duplicate-property-reference-review.json)
select each duplicate bucket independently while preserving declared readonly/type
checks and latest named access. Reference foreach retains the actual shared receiver
cell across replacement, unset and object/array/scalar changes. Previous plain-CV
own-destructor object cleanup reads the old value while the object remains live;
normal and throwing cleanup preserve the selected reference. Late scalar warnings retain
the iterator owner through callbacks and remove it on normal or abrupt completion.
A fresh original and 92 reached premises cover explicit GC while the saved binding
continuation retains its selected cell; the318 composition retains Fiber API captures.
Previous plain-CV arrays now release ordinary and nested child destructors in
order before installing the selected reference, including after a child throws.
Six new originals and 284 reached premises check shared owners, selected-property
mutation/deletion and exception chaining. Ordinary previous objects without their
own destructor now release dynamic children before declared children; four new
originals and 313 reached premises cover shared owners, retirement and throwing
cleanup. Module346 now detaches typed reference sources at each declared slot's
release visit, preserving constraints through earlier child callbacks and genuine
Fiber suspension. Each queued marker owns only the existing slot cell. Six exact
source agreements, including the two unchanged prior controls, and 151/84 reached
premises retain separate cuts; the actual332 composition passes strict compilation.
Private Generator cleanup now preserves the same per-slot timing in actual cleanup
queues and parked Fiber VMs. Four further exact originals and 134/71 reached
premises cover reversed slot order, two constraints on one cell, exception
chaining, owner transfer and rejection of stale snapshots or duplicate queues.
The336 composition passes strict compilation.
Last-owner previous reference wrappers now retire through the actual cleanup
queue before binding. A separate raw CV adds no payload owner; the original
wrapper has zero owners during callbacks. Safe live-object reads remain available,
and selected-reference installation
remains atomic after throws. Five exact originals and 136/139 reached premises
cover shared wrappers, typed descendants, exception chaining and expired-pointer
refusals at separate cuts; the actual341 composition passes strict compilation.
Whole `$GLOBALS` snapshots during wrapper retirement
remain Unsupported.
Ordinary INSTANCE storage359 now keeps one physical parent pin through ordered
property release. WeakReference already returns null during child callbacks, while
safe class metadata remains readable; each slot transfers its owner and detaches
its type source exactly once. Five new originals and 164/57/67 reached premises
cover pending exceptions, the Generator RETURN-child interaction and genuine
Fiber suspension, with distinct source and repair cuts in the review. The composition of 347 modules
adds one exact Iterator-child original and 113 reached premises; future
destructor-tail validation applies the real result discard before owner checks.
Consumed property storage and escaped reacquisition remain required.
The same physical pin now covers ordinary stdClass storage. A materialized
property table transfers its one HARRAY owner before bucket cleanup; shared tables
keep their children after the parent retires. Five new exact originals and
150/91/51 reached premises cover deletion/reinsertion order, exception chaining,
early Weak notification and the Generator RETURN-child interaction at separate cuts.
The actual349 composition passes strict compilation.
Initialized declared scalar properties that cleanup has not yet visited now read
through the actual parent carrier and current slot, with ordinary visibility checks.
Three exact originals and104/89 reached premises cover live typed aliases,
consumed-slot refusal and genuine owner/slot boundaries; wider quiet and
mutating accesses remain required. The actual351 composition passes strict initialization.
Future initialized declared object and array reads now acquire the copied payload owner, dereferencing
property aliases without retaining their wrapper. Three further originals and
136/134 reached premises cover alias rebinding, array copy-on-write and kept
children surviving parent retirement until explicit release. The actual353
composition passes strict initialization.
Unvisited uninitialized typed properties now raise ordinary Error after visibility
resolution, using the declaring class and source line. Three exact originals and
123/141 reached premises cover inherited declarations, private denial, pending
Error ownership, continued child cleanup and atomic selected-reference binding.
Consumed slots remain a separate boundary.
The actual355 composition passes strict initialization.
Future explicitly unset typed slots now raise the same Error when no getter is
present. Three exact originals and 142/147 reached premises distinguish actual
dynamic-first cleanup order from physical slot indexes, retain visibility and
alias detachment, and verify pending cleanup and atomic selected binding.
The later undefined-property cut below extends untyped unset reads; consumed
slots and wider getter accesses remain required.
The actual356 composition passes strict initialization.
Future initialized declared values and typed INITIAL/UNSET slots now support
quiet `isset`, `empty` and `??` without magic consumers. Terminal probes borrow
their payload; coalescing copies the live referent. Three originals cover private,
null and typed INITIAL/UNSET results; 157/138 reached premises prove unchanged
heap owners, alias rebinding/type detach and kept-child survival.
The actual358 composition passes strict initialization.
Consumed/missing storage and wider magic accesses remain required.
Literal undefined property reads now run real warning handlers with fixed null
after their writes or receiver retirement. CV/`$this` receivers borrow their
owner; temporaries hold the receiver until completion. Future untyped UNSET slots
retain their physical storage carrier through quiet reads and handler throws.
Six original comparisons and two distinct false-return comparisons retain
separate cuts; 132/154/166 reached premises and strict initialization pass.
The reviewed current359 composition over `f5c4eed1f` passes strict compilation
at `e77c3eff0`, preserving current source and Generator interfaces.
[The review](coverage/semantics/undefined-property-review.json) preserves the
original fallback/fixture failures and the weaker bound-Closure witness.
Literal calls to named reference-return functions with no arguments, one CV
argument supplied positionally or by name, two positional CVs, or two CVs with
distinct named labels, or a positional CV followed by a named CV retain the
actual returned cell through undefined-property warnings. The captured target remains borrowed, so
handler rebinding may retire it while the cell keeps the replacement alive until
fetch cleanup. Ten exact originals and separate 237/207/225 reached cuts cover
callee/finally rebinding, normal and throwing last-owner cleanup, saved callers
and stdClass child retirement. [The reference-receiver review](coverage/semantics/reference-property-receiver-review.json)
records the pinned8.5 wrapper behavior and the refuted8.6 snapshot prediction.
The actual361 join over `7c18fccada` passes strict compilation at `0b6054930`,
preserving accepted return replay, CALLS and exception interfaces.
Six further originals and five reached groups cover argument destruction before
lookup, shared argument/receiver cells, a surviving separate argument alias and
normal/pending fetch cleanup. The actual361 composition over `43a3fed4f` passes
strict at `827c12ebf`, preserving current compiler and class-promotion interfaces.
Named arguments preserve skipped defaults, unknown-label priority and distinct
known/deferred SEND diagnostic lines. Five original per-case agreements and one
affected deferred comparison retain separate cuts; five new reached groups
validate shared cells, captured null, callee cleanup and pending exceptions.
The actual361 join over `b82bd2425` passes strict at `432084968`, preserving
current call, return-replay and class interfaces.
Two positional CVs now preserve left-to-right live sends: a first Warning fixes
null while its handler can change or unset the second CV before that later read.
Deferred SEND2 uses its emitted line while retaining the documentary CV operand
and captured prefix. Six source agreements and 1207 setup-inclusive reached
premises cover shared reference formals, parameter cleanup before lookup and
throwing prefix/replacement cleanup. The original `is_null` observers retain
their builtin boundary; distinct core-only companions provide the first two
agreements.
The actual361 join over `430face8d` passes strict at `4b39fa53c`, preserving
current CALLS, class attributes, return replay and lifecycle interfaces.
Two distinct named CVs preserve source SEND order while binding captured values
to formal slots. Deferred warnings retain documentary CV operands and emitted
argument-list lines at both ordinals. Seven per-case source agreements and 1245
setup-inclusive reached premises cover skipped defaults, shared cells, formal
cleanup order and label-error priority before later CV demand. Earlier whole
source and fixture failures retain zero credit.
The actual364 join over `e26e3fb2d` passes strict at `2383140e3`; one affected
pending300 gate also passes with exact Throwable message bytes under current
string carriers. Earlier source/state cuts remain separate.
A positional CV followed by one named CV now preserves the captured prefix,
skipped defaults and the emitted deferred second-SEND line. Six exact originals
and five reached groups pass 1235 setup-inclusive premises, including shared
cell owners, parameter cleanup before lookup and label-error/property cleanup.
Earlier source/state cuts retain their original credit.
The actual367 join over `4d7ef44ee` passes strict at `87aca689f` (5.179s),
preserving accepted Notice, GEN and ARG interfaces without renewing those cuts.
Literal CV-base reads now invoke a first public `__get` family for missing or
explicitly unset public properties. Accessible never-initialized typed properties
raise Error without invoking the getter. One real receiver hold survives the
borrowed getter call; exact property verification precedes receiver release,
and a reference result is copied afterward from its current cell. Eight source
agreements and eight reached groups pass 1293 setup-inclusive premises, covering
value/reference differences, discarded reads and H/B/C exception cleanup.
[The getter review](coverage/semantics/magic-property-get-review.json) retains
distinct native, source, strict and state cuts plus the original failures.
The actual369 composition over `b9f0b1ae9` passes strict at `bae438b0f`
(5.181s), preserving current class, Generator, return and callable interfaces.
Source/state evidence retains its original cuts.
Denied private/protected reads and inherited-private literal fallback now invoke
the getter without applying the hidden property's type. Allowed lexical reads
use the physical backing key or raise its initialization Error. The original
caller scope remains valid through privileged getter/destructor callbacks.
[Six new source agreements and six reached groups](coverage/semantics/magic-property-denied-review.json)
pass 1094 setup-inclusive premises; earlier public-getter evidence is unchanged.
The actual370 join over `e2ef06143` passes strict at `2fc127185` (5.422s),
preserving current callable, class, Generator, collector and assertion interfaces.
Private source/state cuts retain their original credit.
Literal reads on a statically named ordinary noarg by-value function result now
invoke the same public getter for missing/public UNSET properties. The original
receiver temporary survives the getter hold: reception copies the returned
payload and releases the raw return's cell owner before releasing that temporary;
surviving aliases can keep the cell alive. The copied payload stays alive through
receiver cleanup. Readonly verification,
discarded and by-value results, surviving aliases and H/B/C cleanup pass
[seven source agreements and seven reached groups](coverage/semantics/magic-property-owned-review.json)
with 1266 setup-inclusive premises. Native6 plus a separate by-value native1,
the original Unsupported baseline and failed gates keep their distinct cuts;
earlier CV/denied getter evidence is unchanged.
The actual371 join over `675a2e1b5` passes strict at `d54c66076` (5.417s),
preserving current compiler warning routing and getter interfaces. Private
source/state cuts retain their original credit.
Weak getter verification now accepts numeric strings parsed as an in-range
integer. Unconstrained reference returns convert the actual cell; value returns convert only
the returned value. The getter declaration determines strictness, and readonly
backing remains UNSET without a new type source. CV reception can observe later
receiver-destructor changes, while an owned receiver copies the converted value
before releasing its original temporary. [Six source agreements and six reached
groups](coverage/semantics/magic-property-integer-review.json) pass 909
setup-inclusive premises; the original Unsupported and fixture failure keep
zero credit, and earlier getter evidence is unchanged.
The actual372 join over `e11f0f06c` passes strict at `5f96624c8` (5.554s),
preserving current hook/getter and cleanup interfaces. Private cuts retain their credit.
Typed-property-backed getter references now support exact int/object targets
without changing the cell or attaching the getter target type. Weak integer
strings can instead raise a source/target conflict; strict and nonnumeric
mismatches retain the ordinary getter TypeError. The first actual source selects
the conflict label, and pending errors survive later source detachment/repair.
[Six source agreements and six reached groups](coverage/semantics/magic-property-reference-review.json)
pass 829 setup-inclusive premises; owned copied payloads survive source/cell removal.
The actual374 join over `bed352b5a` passes strict at `e0d62e7ed` (5.399s),
preserving current anonymous-class and hook interfaces; private cuts remain unchanged.
Getter verification now widens an actual unconstrained integer return to builtin
float, including strict getters. Reference returns update the real cell; value
returns change only the returned value. Exact floats with real typed-property
sources remain unchanged, while integer widening raises a source conflict without
converting that cell. Readonly backing stays UNSET without a new type source.
[Six source agreements and six reached groups](coverage/semantics/magic-property-float-review.json)
pass 904 setup-inclusive premises, including binary64 rounding and CV versus owned
receiver cleanup. That cut leaves numeric strings, booleans and wider float
conversions open; earlier getter evidence is unchanged.
The actual374 join over `2c0d9531c` passes strict at `076606980` (5.481s),
preserving current virtual-hook interfaces; private cuts retain their original credit.
Weak float getter verification now also accepts full numeric strings classified
NFLOAT, converting the actual unconstrained reference cell or only the by-value RV.
[Six source agreements and six reached groups](coverage/semantics/magic-property-decimal-review.json)
pass 877 setup-inclusive premises, covering exact 7.5/0.1 bits, prefix/getter-strict
rejection, real string|float source conflicts and CV versus owned cleanup.
The actual375 join over `22adef5d5` passes strict at `cab88a623` (5.527s);
private source/state cuts retain their original inputs.
Weak float getters also convert NINT-classified full strings using the parsed
integer's binary64 cast, including rounding beyond 2^53 and positive zero for `-0`.
[Six source agreements and six reached groups](coverage/semantics/magic-property-integer-float-review.json)
pass 899 setup-inclusive premises at `498b2281d`, covering signed limits,
strict rejection, real source conflicts and CV versus owned cleanup.
The actual375 join over `2d0146317` passes strict at `50ba5293a` (5.512s);
private source/state cuts retain their original inputs.
The two older constructed NINT controls now expect conversion; their earlier
reports retain their original cuts.
Weak float getters now convert false to positive zero and true to one on the
actual unconstrained reference cell or only the by-value RV. Strict getters and
null reject; real float|bool sources select a conflict without converting the cell.
[Six source agreements and six reached groups](coverage/semantics/magic-property-boolean-float-review.json)
pass 911 setup-inclusive premises at `cf9bcd566`, including CV/owned cleanup and
pending errors. Getter diagnostics use `bool`; other type-check contexts are unchanged.
Three older constructed boolean controls are maintained only in the new kept group.
The actual375 join over `78cd4d6e8` passes strict at `f44398f38` (5.646s);
private source/state cuts retain their original inputs.
Weak int getters now convert original false to zero and true to one on the actual
unconstrained reference cell or only the by-value RV. Strict getters and null reject;
real int|bool sources conflict without converting the cell.
[Six source agreements and six reached groups](coverage/semantics/magic-property-boolean-integer-review.json)
pass 915 setup-inclusive premises across `03ed0aa16`/`90fad5bed`, covering CV/owned
cleanup and pending errors. Two maintained constructed controls contribute five
selected clauses; prior cuts are unchanged and three fixture/preparation failures retain zero credit.
The actual375 join over `036035583` passes strict at `9c0bce310` (5.582s);
private source/state cuts retain their original inputs.
Weak string getters now convert original false to interned empty and true to ASCII
`1` on the actual unconstrained reference cell or only the by-value RV. Strict
getters and null reject; real string|bool sources preserve an exact first read and
select a later boolean conflict without converting the cell.
[Six source agreements and six reached groups](coverage/semantics/magic-property-boolean-string-review.json)
pass 997 setup-inclusive premises at `cdbd762a1`, covering CV/owned cleanup and
pending errors. Source credit retains four passes at `eaaf00ba0` and two at `cdbd762a1`.
At the phase36 cut the original concatenated-echo source leaves scratch BASE that blocks
getter entry; its failure and diagnostic retain zero agreement credit.
The actual375 join over `619170565` passes strict at `828bad179` (5.769s);
private source/state cuts retain their original inputs.
Successful scalar echo now consumes the current-frame concat scratch BASE after output.
[Five exact originals and five whole reached groups](coverage/semantics/concat-emit-review.json)
pass 570 setup-inclusive premises at `a7ca4b349`, preserving inner getter output,
saved outer concat continuations, delayed CV reads and pending-error cleanup.
At the phase37 cut the separate temporary Stringable direct-echo control destroys
its receiver before output; that frozen whole-source observation keeps zero agreement.
The actual375 join over `f8ad4d4a4` passes strict at `3876bc706` (5.671s);
private source/state/control cuts retain their original inputs.
Direct Stringable echo now holds an authenticated named noarg NEW input through
output separately from its cast pin. Borrowed CV self-drop still destroys during
cast release, then writes a successful string before a pending destructor exception.
[Six exact originals and six reached groups](coverage/semantics/stringable-echo-review.json)
pass 787 setup-inclusive premises across `caf0f56ab`/`e6ff87e95`; strict375 and
source6 retain `b0a90ed31`. Throwing cleanup/previous links and concat timing agree;
plain strings remain admitted. Two fixture seek failures retain zero credit.
The actual375 join over `3d54ec25a` passes strict at `b0d807f94` (5.774s);
private source6/state787 and original failures retain their recorded cuts.
Weak string getters now convert original integers on the actual unconstrained
reference cell or only the by-value RV. Digits retain interned strings; signed and
limit values retain newly allocated request strings through cleanup.
[Six source agreements and six reached groups](coverage/semantics/magic-property-integer-string-review.json)
pass 1,188 setup-inclusive premises at `7556c579f`; strict375/source6 retain
`0f910ddb4`. Genuine string|int conflicts and strict/null rejection preserve raw
values until cleanup; the original kept fixture failure retains zero credit.
The actual375 join over `753f960e2` at `90da67734` preserves disjoint parent paths.
Existing parent/private strict cuts and private source6/state1188 are reused;
this join adds no numeric execution.
Weak string getters also convert non-NaN floats at the current post-getter precision.
Every result retains a fresh request string, including digits, signed zero and infinities.
[Seven source agreements and seven reached groups](coverage/semantics/magic-property-float-string-review.json)
pass 1,351 setup-inclusive premises at `d8030561f`; strict375 retains `1923d7939`.
REF/BYVAL/owned cleanup, genuine string|float conflicts and strict/null rejection agree.
The original eight-read composite retains timeout/zero agreement; two smaller originals
fit the same caps. At the phase40 cut, a native NaN control observes both conversion
warnings and keeps zero model agreement.
The actual375 join over `ca764836f` at `35f7dc33f` preserves disjoint parent paths.
Accepted parent/private compiler cuts and private source7/state1351 are reused; no new numeric execution.
Weak string MAGIC_GET now retains the allocated `NAN` request string before warning
dispatch. Scalar handler mutation is overwritten only on an unconstrained returned
reference; BYVAL preserves the changed global. A real source conflict instead reads
the post-handler value, and handler throws commit before receiver cleanup.
[Six source agreements and six reached groups](coverage/semantics/magic-property-nan-string-review.json)
pass 1,014 premises at `3f19892d8`; strict375 retains `00902286f`.
Strict getter rejection emits no warning. Original observer/preparation failures stay0;
object/array callback replacements and changed source constraints remain required.
The actual375 join over `6f2a0d742` at `925c3b1bd` preserves disjoint parent paths.
Private and parent compiler cuts are reused; fresh strict/source/state/native credit remains0.
Weak int MAGIC_GET now accepts integral floats quietly, including negative zero,
and captures fractional truncation before precision-loss deprecation handlers.
Normal return commits the saved int on an unconstrained RV; throwing handlers
preserve their scalar writes before getter cleanup. Real source conflicts diagnose the live value.
[Six exact sources and seven reached groups](coverage/semantics/magic-property-float-integer-review.json)
pass 1,338 premises; strict375 retains `6674a8cdb`. The original whole425 fixture
timeout stays0 after a fixture-only split. Range controls are constructed;
object/array callback replacements and changed source constraints remain required.
The join over `2b482deaa` at `751f6f917` preserves reviewed parent routes with 375 modules.
Private and parent compiler cuts are reused; fresh strict/source/state/native counts remain 0.
Weak int MAGIC_GET also converts full NFLOAT numeric strings, preserving the original
spelling in precision-loss deprecations. Quiet `7.0`/`-0.0` convert without warning;
normal handlers commit captured truncation, while throwing handlers preserve their writes.
Real source conflicts diagnose the current value without committing the captured int.
[Six source agreements and eleven reached checks](coverage/semantics/magic-property-numeric-string-integer-review.json)
pass 1,469 premises, including compact authentic warning/return/error stages.
Four original timeouts and a transient cleanup-validator fixture failure stay0.
Scalar/string callbacks and unchanged source/tail authority remain bounded;
wider object/array replacements remain required.
The join over `69333905f` at `0de05afcb` preserves reviewed parent routes with 375 modules.
Retained private and parent-family compiler cuts are reused; fresh strict/source/state/native counts remain 0.
Weak bool MAGIC_GET now converts original non-NaN scalar results with PHP byte-string
truth: `"0"` is false while `"0.0"` and nonnumeric strings are true. Unconstrained
references update their cell; BYVAL changes only RV, and owned reception detaches
before receiver cleanup. Real bool|string sources preserve exact reads and diagnose
later conversion conflicts without writing the referent; strict getters and null reject.
[Seven source agreements and seven reached groups](coverage/semantics/magic-property-scalar-boolean-review.json)
pass 1,053 premises at `a303833a8`, including signed zero/INF, aliases and full budgets.
The fixture preparation failure stays0. At the phase44 cut, NaN warning/control
observations retain zero model/state/agreement; later numeric-payload handling is recorded below.
The `ffc9103a` composition preserves disjoint CLASS42 hooks; accepted private and
parent-family compiler cuts are reused with zero fresh executions.
NaN bool MAGIC_GET now resumes its warning before reading live numeric reference
payloads: handler-written LONG_MIN and negative zero yield false. BYVAL retains
saved NaN true; real sources diagnose the current type without conversion, and
throwing handlers skip the bool write before receiver cleanup and exception chaining.
[Seven source agreements and ten compact reached stages](coverage/semantics/magic-property-nan-boolean-review.json)
pass 1,014 premises at `a3f383502`, including whole states and full driver budgets.
The original preparation failure stays0. Normal bool/string payload history remains
Unsupported with a separate native-only control0; wider object/array/source/PARAM scope stays open.
The `58d5c5fe` join preserves disjoint parent paths and reuses retained compiler cuts.
Private observations retain their revisions; fresh strict/source/state/native evaluations stay0.
Weak string MAGIC_GET now converts ordinary Stringable results while retaining the
returned argument and getter receiver. The cast owner releases first, then the
original argument or copied temporary owner before the saved string write. A successful cast still
writes its string when that release throws; a throwing callback performs no conversion.
Real typed sources diagnose the current referent, and a conflict TypeError retains
an object-release exception as previous. REF/BYVAL/owned reception preserves native
cleanup order; declaration-strict getters call no cast.
[Nine source agreements and twelve compact reached checks](coverage/semantics/magic-property-stringable-string-review.json)
bind 899 premises across retained cuts. Original failures remain0; unconstrained input
changes during callbacks/precommit cleanup and wider replacement/getter/PARAM scope remain required.
The `fd7eae1` composition preserves the newer storage/lifecycle rules and 376 modules.
Private cuts and the retained parent compiler are reused; fresh executions remain0.
PARAMETERBACKINGS and wider conversions remain required.
Wider coercions, other constrained returned cells, wider getter signatures, quiet/write
access, lexically accessible nonpublic UNSET, changed Closure scopes for nonpublic access, guarded
recursion, computed names, hooks and wider reference-call receivers remain required.
Released-CV mutation, raw retired-container reads, wider wrapper-pointer consumers
and internal Generator/Fiber retirement, binding-time exit
and expired notice buckets remain explicit boundaries;
full foreach coverage remains required.

Simple typed property assignment converts its declaration
before shared alias checks; compound alias updates keep the generic reference
route. Typed object conversion remains a separate consumer.
[Nullsafe property access](docs/semantics/SOURCE-NULLSAFE-PROPERTIES.md)
short-circuits only the active property/dimension chain, skips later names and
keys, and preserves quiet probes and by-reference argument error ordering. Its
[review](coverage/semantics/nullsafe-properties-review.json) binds source,
compiler and paused-state controls. [Source methods and constructors](docs/semantics/SOURCE-METHODS.md)
execute ordinary/nullsafe, inherited, nonpublic and static/scoped dispatch,
bound closures and `Closure->__invoke` trampolines.
Ordinary abstract scoped calls reject before arguments, and inaccessible concrete
nonstatic methods report access errors before missing-receiver errors. Literal
constructor calls retain separate opcode dispatch: private denial precedes
receiver compatibility, and inherited private constructor errors name the requested
class. A missing constructor reports `Cannot call constructor` for literal/folded method
names and the ordinary undefined-method Error for computed names; both suppress
argument evaluation. [The focused review](coverage/semantics/missing-constructor-review.json)
records two exact originals and distinct17+17 reached SL checks.
Deferred trait parameter constructors preserve selected scope through class-table
work and retain valid initialization history after an ordinary capture is released.
A fresh original and38 reached checks pass independently; unpublished-FCC work
remains separate.
[Source traits](docs/semantics/SOURCE-TRAITS.md) compose nested uses, conflicts
and adaptations with using-class scope, original body provenance and distinct
class/alias static cells. Property/constant composition preserves invariant source
types, pure evaluated compatibility, per-import identities and static sharing.
Imported deferred instance defaults use owning class templates. Raw trait-property
warnings retain selected cells and operand ownership through handlers and abrupt
opcode completion. Deferred collision operands compare before type conversion;
operation diagnostics are recorded with runtime operand order and AST lines,
then delivered after class publication. Private-final compile warnings retain
their phase order and handler-ineligible severity. Compiler delivery of those diagnostics also
preserves level 128 versus eligible warnings at levels 2 and 8192 under live
reporting masks;
[two new originals and focused state checks](coverage/semantics/compiler-warning-severity-review.json)
cover returning and shared-throw eval paths. Successful collision dependency
fills retain real typed caches and distinct import scopes. Collision expression
errors stop the comparison, flush earlier diagnostics without handlers and render
the pending Error before the composition fatal. Cyclic lookups retain full imported
constant identities and release transient failure allocations. Failed class links,
including an initializer Error before the composition fatal, retain caches for
published owners and release unpublished import caches. Raw trait composition uses
the same source-kind proof; direct trait constants still fail before evaluation.
Published Closure/FCC dependencies retain their real initializer scope, callable
receipts and cache owners through successful and failed composition; array keys
and duplicate-key selection keep source-derived proofs. Errors inside those
initializers preserve actual Throwable fields and demand traces, retire failed
temporary owners and keep completed nested caches. Cross-file typed constant
demand retains the composing file, physical fetch line and expression frame.
Static, capture-free REAL Closure dependencies can also be created before the
using class is published, with an exact collision receipt and cache owner. Failed
imports retain dead receipts while retiring live owners; fatal trait links reserve
their name before later binding, without publishing the failed class. First-target
method FCCs also retain source-checked dead receipts after failed composition,
reconstructing the exact trait method-copy plan and declaration prefix. Immutable
parameter TYPE views retain the callable's birth scope and canonical code, defaults,
return contract and statics. Receipt access uses the unfixed exporting-trait scope;
68 supplied private/protected forgery checks pass, with12 setup clauses separate.
Focused
source2 and87 supplied strict-SL conditions cover retirement and equal lexical/called
FCC scope, with12 setup clauses separate. The reviewed322 composition passes strict
compilation and a genuine active default/TYPE checkpoint with26 supplied conditions
plus6 setup clauses; that checkpoint ends at the old-U constructor Error.
Live concrete aliases and visibility adaptations preserve the exact selected body,
default and alias static cells. Three normal source comparisons and44 supplied
birth/default/static conditions pass, with6 setup clauses separate.
Later failed imports preserve a published first owner's cached method even when
their own method differs; one PHP-error source comparison and68 supplied retirement
conditions pass, with6 setup clauses separate.
Failed first-owner targets also remain callable through later imports, without
publishing the failed class or reviving its retired Closure. Three shutdown
originals cover imported, own/private and missing-alias targets, literal defaults
and clone-shared statics;115 supplied checkpoint conditions pass, with12 setup
clauses separate.
A later failed import also retains a dead receipt when the first owner failed;
one shutdown original and59 supplied rollback conditions pass, with6 setup
clauses separate.
If data binding succeeds before abstract verification fails, later cached calls
use the fixed class scope while an imported first birth keeps its trait scope.
One shutdown original and59 supplied phase/scope/static conditions pass, with6
setup clauses separate; the failed class stays unpublished.
Retained `new self` rejects abstract construction before arguments or instance
allocation. Implicit requirements need completed data binding; explicit abstractness
uses the declaration flags, including after an earlier data failure. Three shutdown
originals and122 supplied conditions plus18 setup clauses pass at separate cuts.
Parent/interface construction contracts remain open.
Retained trait-scoped `new self` rejects the published trait before arguments,
with a valid pending NEW certificate. One shutdown original and37 supplied
conditions plus6 setup clauses pass.
Retained `new static` constructs the published called class from failed-class or
published-trait scope, entering arguments after allocation. Two shutdown originals
and80 supplied conditions plus12 setup clauses pass at separate cuts, including
durable selected-NEW static-fill history.
An authenticated retained `self::n(argument())` rejects the exact abstract method before
arguments, using completed data binding and copied requirements. One shutdown
original and41 supplied conditions plus6 setup clauses pass, including all four
global validators; unknown phases stay Unsupported.
Three full parameter-view originals now agree with PHP at the original45/55 limits:
constructor/default rejection, error-handler reception and positional/named variadic
Stringable conversion preserve old, later and cloned scopes. Exact ASCII lookup and
disjoint property/header guards reduce repeated source replay work without changing
authority. Broader mixed parameter-view contexts, differing-owner later births
and wider failed-owner member/construction behavior remain open. Wider
initializer contexts, held/open failed links and readonly
storage remain
required. The current313 join passes strict compilation, one fresh REAL/constructor
source agreement and46 source-reached conditions plus6 setup clauses, including
actual capture retirement with live REAL cache authority. Earlier source/state
cuts stay separate. A bounded
[selector repair](coverage/semantics/method-class-selector-review.json) preserves
static class identity after object retirement. Its installed author and independent
gates each pass two sources and one finite CONFIG stage/26 assertions. Rebound
capture, called-class and receiver-creation116 repairs are
[installed](coverage/semantics/method-capture-current-review.json) at **c536d1f74**.
Author and independent gates each accept nine sources and seventeen finite
stages/541 maintained assertions; the reviewer also accepts creator2/89.
The earlier source35/finite40-stage projection retains its own identity. Their
[authority contract](docs/semantics/METHOD-CAPTURE-AUTHORITY.md) keeps retired-history limits explicit.
The [public object `__invoke` union](coverage/semantics/source-invoke-current-review.json)
adds runtime-class dispatch, first-class capture and ordinary `callable` typing.
Installed **18a1383d7/b3a02ebc/1304** accepts 21 author sources and
20 finite stages/537 maintained assertions. Independent checks accept 37 sources
and 29 stages/997 assertions, including FIRST7/331 then SET79/finally50.
Nonstatic private/protected `__invoke` now uses the effective runtime method table
for bare calls, callable admission and object capture/clone. Publication emits the
visibility warning after compiling parameters/body; static `__invoke` rejects at
that point, before that warning. Explicit calls keep ordinary lexical access.
The [publication review](coverage/semantics/invoke-publication-current-review.json)
separates source, runtime/compiler and strict warning-handler observations.
Dynamic include/eval warning delivery, transformed weak wrappers and other magic
protocols remain open. Public concrete source method arrays now share callable
admission, dynamic dispatch and first-class capture/clone. Selected receivers
and method choices survive referenced-member mutation and array retirement;
static selections retain called class without an object root. The
[array review](coverage/semantics/array-callables-current-review.json) separates
the private source/state gates from current publication/Restore/property/ARG
and two-slot INI interactions. Ordinary lexical private/protected array selectors
now retain genuine access through selection and capture; object parent-private
redirection stays distinct from concrete-class lookup. Module221 stages deprecated
keyword class selectors and qualified array methods in fixed callable reception
and error-handler registration/dispatch. Warnings preserve the chosen class and
string split while rereading referenced method bytes; actual receiving/emitting
frames authenticate selection, including compound foreign-`$this` API calls.
The [keyword/compound review](coverage/semantics/keyword-compound-callables-current-review.json)
keeps failures and later consumers visible. Magic/autoload/internal consumers remain open.
Public concrete class-method strings now distinguish
computed static dispatch from fixed calls using a compatible active receiver.
Immutable string captures/clone retain selected descriptors, called scope and
receiver ownership; callable admission uses the receiving frame independently.
The [class-method string review](coverage/semantics/class-method-strings-current-review.json)
records selected source/state evidence and separate Unsupported controls.
Lexical private/protected class-method strings retain selecting scope through
capture and saved calls. Protected checks use the root prototype; API handlers
resolve raw values using the emitting frame. The
[scoped-callable review](coverage/semantics/scoped-callables-current-review.json)
keeps these observations separate from earlier public-route evidence.
[`Closure::fromCallable`](docs/semantics/FROM-CALLABLE.md) now invokes the factory
over existing core callable forms, freezing selection across raw mutation and
maker retirement. Genuine USER permission, internal getter scope, foreign called
classes, defaults and shared method statics remain distinct. Existing Closure
inputs preserve identity; factory errors wrap lookup warnings after full unwinding.
Created source Closures retain authentic method/import scope after captures retire;
static children add no receiver owner and nonstatic children own their receiver.
[Default and variadic callable reception](docs/semantics/CALLABLE-RECEIVES.md)
preserves named-hole order, live reference operands and borrowed method receipts.
Failed lookup stages slow scalar warnings and forced Stringable conversion.
Other internal and user-return keyword warning consumers remain required;
magic/autoload and complete binding remain open.
[Current Closure and fake binding](docs/semantics/CLOSURE-CURRENT-BINDING.md)
returns the exact immediate ordinary Closure and preserves `__invoke` capture
identity. Transformed fake bindings keep source statics and own only their new
receiver; returned source Closures retain the genuine internal scope after makers
retire. [REAL binding](docs/semantics/CLOSURE-BINDING.md) now stages ordered
static/internal warnings and uses the function's compiled `$this` flag when
removing a receiver. Valid unbinding copies REAL statics, preserves reference
captures and resets called scope; explicit null scope removes class permission.
Literal named-static `Closure::getCurrent(...)` capture now preserves the immediate
ordinary caller; selected API and returned body retire independently. A named
helper still errors under an outer Closure. Three native originals, one direct and
two repaired source comparisons and two separate state cuts totaling 447 premises
pass. Simple class-CV `$class::getCurrent(...)` also prepares Closure and freezes
selection before the class cell changes; one affected source and 166 focused state
premises pass. Named-class evaluated CURRENT members also freeze selection;
one concat original and 242 focused state premises validate the request carrier,
two operand writes and the same immediate body result. Evaluated class expressions
with a literal CURRENT member also freeze selection; one concat-class original and
240 focused state premises validate canonical preparation before later writes.
Combined evaluated class and member CURRENT captures also freeze selection;
one both-concat original and 353 focused state premises validate distinct request
indexes, source authority, four operand writes and the same immediate body result.
Ordinary object-form literal CURRENT capture creates the same receiver-free API;
one selector-CV original and 200 focused premises validate selector retirement
before its weak read and the distinct immediate body result.
Ordinary object-form evaluated CURRENT members also use that receiver-free mint;
one get+Current/selector-CV original and 315 premises bind the actual name carrier,
two member writes and selector release before the distinct current-body result.
Literal `Closure::bind(...)` capture also reaches the existing binding handler;
its copied receipt survives original API/body retirement while the bound Closure
and returned value retain the receiver separately. A captured BIND call now pins
its API when a third-argument helper clears the selected cell; static authority
remains borrowed. Simple class-CV `$class::bind(...)` capture also freezes the
resolved Closure before the class cell changes. Literal-class `Closure::$method(...)`
also freezes a simple method CV after resolving its string bytes. Combined simple
class/member-CV capture now authenticates internal Closure task authority and
keeps that selection after both cells change. Evaluated class expressions with a
literal bind member also freeze selection. Named-class computed members also
freeze selection after their expression evaluates; a concat witness retains the
API after both operands change. Both class and member expressions now share
internal Closure task authority and freeze selection before later operand writes. Wider API
captures, argument forms and temporary current escape remain required.
The FCC compiler clears the callee result fold before recording the capture;
literal-array captures produce Closure objects while preserving child constants.
Current named-handler checks retain the selected caller and its argument vector.
Wider readonly lifecycle, hooks and user magic methods remain open.
[`Closure::call`](docs/semantics/CLOSURE-CALL.md) invokes ordinary and fake method
captures with temporary receiver/scope, shared source statics and original wrapper
values. Binding warnings precede inner-name errors; forwarding reference warnings
precede fresh cell allocation and preserve the captured value through callbacks.
Finite getters and created children retain their selected scope and owners.
The [new review](coverage/semantics/temporary-fake-call-review.json) preserves
source/state cuts; unpacking and REAL temporary-current lifetime remain required.
[Print expressions](docs/semantics/SOURCE-PRINT.md) preserve output effects while
returning constant integer 1, including folded expressions and reference demand.
Source, compiler and paused ownership checks cover admitted conversions;
user-object `__toString` now runs callbacks for echo, print and string casts,
with other string contexts still open.
[Eval operand conversion](coverage/semantics/user-string-eval-author.json)
extends that callback to checked eval source requests. Its source catalogue
passed on the file-trace base; installed focused, paused and included-file
callback bridge checks also pass.
[Concat conversion](coverage/semantics/user-string-concat-author.json)
preserves both expression effects before left-to-right string conversion and
keeps a right-side variable live across the left callback. Source and paused
checks pass on the eval-conversion base; installed focused and null-resolver
include bridge checks also agree.
[Weak typed-return conversion](coverage/semantics/user-string-typed-author.json)
is installed. It resumes checked `__toString` callbacks for
by-value returns, including nested weak returns and throwable `previous`
chains. An installed 90-second interface-method bridge and paused marker check
pass; the generic 45-second runner times out on that source.
[By-reference Stringable conversion](coverage/semantics/reference-return-typed-cv-review.json)
now preserves selected live unconstrained aliased CV cells through callback GLOBALS
rebind/unset. Successful conversion writes the selected cell; failure reports its live
value and retains the previous callback Exception. Thirteen exact originals and eight
current/saved fixtures with 843 assertions pass. The separate
[local CV lifetime increment](coverage/semantics/reference-return-local-cv-lifetime-review.json)
borrows a sole nonreference local CV or preserves its protected owning temporary.
It runs the old receiver's destructor before copying a successful string into the
captured cell; callback failure retains the object through finally and chains the
callback Exception. Five exact originals and eight reached fixtures/871 assertions
pass. Genuinely released targets, destructor throw/reentry, real suspension and
wider typed consumers remain open.
Separate validation at `b55942bc` checks an ordinary local `unset` and its control:
the original selected cell remains in the protected return carrier during `ping`,
then reaches the caller's `r/a` aliases and write. The owning temporary persists;
physical collection and released borrowed-cell conversion remain open.
An untyped `finally` return override cancels the earlier reference carrier;
its destructor runs before caller output, while the control delivers the old cell.
Scoped descriptor checks now require every registered destructor operation's exact
exit marker in current or saved tasks, including parked Fibers. Focused source,
carrier/caller and public refusal checks pass; physical cell collection and broader
returns remain open. Details are in the local CV lifetime review above.
A separate Fiber validation keeps a protected string-return carrier live after
local unset and suspension, then delivers that cell to the resumed worker's r/a
aliases and write. Source2, parked58/two refusals and late2/230 pass at `cb498f92`;
these are separate executions, with no runtime change or physical collection claim.
Suspended untyped `finally` cancellation also validates at `cbc57fdb`: the old
object carrier survives parking, then an override triggers its destructor before
delivery of the new y cell to worker aliases. Source2, early92/two controls and
separate late214 pass; abstract cell retirement is not physical Zend collection.
Dropping an orphaned suspended Fiber also validates without a runtime change at
`27a92e4b`: early D precedes L; delayed drop keeps the carrier through GC and emits
D between G/E. Source2, early98/two refusals and separate late270 pass, including
canceled worker R, drained close controls and caller-budget continuation.
A selected O destructor may instead raise an Exception during orphan close.
Source2, early102/one refusal and separate late260 validate catch delivery with
null Previous, preserved modeled trace at the live caller and failed Fiber
retirement. Native outputs establish messages, without identity or trace claims.
Pending reference-return temporaries now keep a suspended Fiber/object cycle live
across explicit GC. A bounded normal request-store path later force-closes that
Fiber with a temporary receiver hold. Two source comparisons and separate 122/262
state checks cover collector roots, shutdown provenance, D after E and cleanup;
broader shutdown layouts and physical collection remain open.
A destructor error during that request-store close now reports an uncaught fatal
with the original creation line and source-derived destructor trace site. An
ordered private-control release remains valid when execution pauses before the
fatal cleanup. Source2/early139 at `0ec20831` and separate late262/paused123 at
`d16a062b` cover fatal output, normal null control, cleanup and budget resumption;
the latter revision adds only storage admission. Wider layouts remain open.
Typed by-reference Fiber returns also validate without a runtime change at
`ee915d44`/388. An external bad write reaches the same selected global cell;
the first resume parks again with a TypeError, and the second delivers it to the
worker catch. The integer control delivers that cell to r/a and writes through
to global x. Source2, early79/one replay-line refusal and separate late144+146
pass, including live error/trace preservation, cleanup and caller-cut budget.
The global cell remains owned; wider typed/suspended return layouts remain open.

Suspension inside `__toString` during a selected by-reference string return
also validates without a runtime change at `ee915d44`/388. Moving one external
write across resume preserves the selected global cell and parked cast receiver;
early64/one wrong-destination refusal and separate late54+54 worker alias,
completion and budget checks pass. The negative may also fail REFCELLS validity;
old-receiver destructor suspension and broader return layouts remain open.
[Weak Stringable parameters](coverage/semantics/weak-string-parameters-review.json)
now convert supplied fixed parameters in receive order, preserving caller
strictness, nominal/callable precedence and the entered formal cell. Existing
property constraints reject a by-reference conversion before its callback;
free references write back through their captured cell even when the callback
attaches property constraints. Later writes and binds still enforce the live
sources. Reentrant receives retain distinct formal cells, and callback throws
keep the original exception without authorizing a backing-value exception.
Cached constant Closures and nonpublic invokable objects preserve these rules.
Six focused sources, 299 state checks and two independent instance-property
controls cover the new backing behavior.
[Variadic and default reception](coverage/semantics/variadic-default-string-review.json)
converts positional then named Stringable elements and fresh constructor-free
defaults, retaining declaring method scope and captured cells.
[Source constructor defaults](coverage/semantics/default-constructors-review.json)
finish class tables before allocation and evaluate all argument values before
constructor access and name mapping. Declaration strictness, API reference warnings
and fresh default objects retain their real owners.
[Internal default constructors](coverage/semantics/internal-default-constructors-review.json)
map prepared values with declaration strictness, named-hole filling and exact
string-mutated traces. [Suspended reception240](coverage/semantics/internal-default-reception-review.json)
retains real warning and Stringable callbacks, raw integer trace slots and each
reentrant constructor owner. Current trait/display fallback preserves a filename
argument after its global root retires.
[Anonymous keyword defaults](coverage/semantics/anonymous-default-new-review.json)
resolve self/parent from the live receiving Closure lexical scope, including
rebinding, arrows and temporary calls. Private constructors and saved recursive
defaults retain that scope independently of called class and receiver.
[Ordinary Throwable constructors](coverage/semantics/ordinary-throwable-reception-review.json)
suspend null/lossy warnings and Stringable parsing for NEW and explicit inherited
or scoped calls. Fields commit only after all parameters pass; successful string
casts replace sent slots and retire their old temporary owners. Callback traces
and recursive conversion consumers retain their own constructor.
[Dynamic object `::class`](coverage/semantics/object-class-name-review.json) returns
the real class name without a cast, preserving child effects, compiled lines and
captured missing-CV reads through handlers. Broader constrained conversion remains open.
[Ordinary dynamic NEW](coverage/semantics/dynamic-new-review.json) captures a string or object
class selector before arguments and releases selector temporaries before class work.
Compiled keyword scopes survive recursive constructors and retired receiving Closures;
cached property method callables retain lexical and called class separately.
[Ordinary named keyword NEW](coverage/semantics/named-keyword-new-review.json)
uses lexical self/parent and called static scope through inherited constructors,
rebound Closures and eval. Known invalid function scopes reject at compilation;
deferred scopes fail before arguments.
[Autoload registration and dispatch](coverage/semantics/autoload-review.json)
now capture real callable targets and preserve live queue mutations, including
HashTable compaction. Ordinary named/dynamic NEW and class-parent lookup suspend
before argument demand; explicit dispatch keeps its weak internal context.
Callbacks retain genuine ownership and declaration authority after unregistering.
Thirty-six private source agreements and one current global-constant loader
interaction retain separate cuts. The 263 original finite premises pass with
seven typing bindings and eight repeated compaction setup premises; the split
compaction groups use the existing strict SL runner at the unchanged120s cap.
[Declaration-interface autoload](coverage/semantics/interface-dependency-autoload-review.json)
now loads a sole missing user interface before a parentless class or interface is
linked and published. Two exact originals and 324 SL premises distinguish cached
descriptors from live names, retained prototypes and genuine loader continuations,
including eval and budget resume. Trait-bearing and parented targets, wider missing
lists and callback/failure interactions remain partial.
[Trait-dependency autoload](coverage/semantics/trait-dependency-autoload-review.json)
also loads a sole missing user trait before a parentless class or trait imports
methods. Raw Trait code and magic remain distinct from logical Consumer ownership
through a nested import. Two exact originals and 380 SL premises cover publication,
source/history guards, parent/trait/interface priority and budget resume. Wider
dependency lists, parents, adaptations and loading/failure interactions remain partial.
[Parameter-default NEW autoload](coverage/semantics/default-new-autoload-review.json)
now completes lookup before allocation and nested arguments, then reselects the
loaded constructor under the receiving declaration scope. Nine private sources
and 174 reached premises pass at separate cuts; one actual generator interaction
preserves eager default creation before suspension. A bounded
[global-constant AST NEW follow-up](coverage/semantics/global-constant-new-autoload-review.json)
now runs lookup before allocation/arguments and restores declaration context for
same-text eval retry. Two exact sources and 326 SL premises retain the successful
141-premise front and 185 retry premises; earlier binder/fixture failures remain
zero credit. Direct roots with no earlier facts and supported positional arguments
are covered; nested autoload and wider consumers remain required. Default
`spl_autoload` filesystem search stays excluded.
[Private parameter callable defaults286](docs/semantics/SOURCE-POSITIONAL-DEFAULTS.md)
create fresh static Closures/FCCs using the authentic receive scope and cached
physical FCC target. Nonowning receipts survive maker retirement and ordinary
clone/static writes. Eleven normal sources, two compiler rejections and 504
state premises retain separate cuts; one body-autoload interaction preserves
ordinary private-constructor argument suppression.
Private parameter aliases295 preserve borrowed global/cached class-constant
identity, statics and donor permission through direct mixed arrays and selected
compiled ternaries. Eight normal sources and640 reached checks retain separate
AL367/SL273 cuts. Global aliases require callback-free initializers and quiet
values/facts; its historical six Unsupported boundaries earn zero agreement. Broader effectful read/registration causality, transformed producers and full
core remain required; canonical integration is pending.
Private parameter alias causality306 preserves callback reads and registrations
through genuine receive generations, nested reentry, retries and deprecated-value
capture. Ten normal originals,15 genuine state groups/1170 premises and37 existing
reporting checks pass at distinct cuts. At the306 cut five controls rejected
unsupported routes with zero native agreement;312 adds bounded multiple frontiers.
Wider effectful producers remain required.
Current295 dispatch retains eight quiet originals/two object controls;306 replaces
its four former causal Unsupported fixtures without changing archival checks.
Private multiple-frontier defaults312 preserve intermediate reads across distinct
callbacks, partial cache retry, nested cache warming and deprecated pre-shadowing.
Eight exact normal originals and eight genuine state groups/761 premises pass;
the strict compiler277 gate retains its separate cut. Current306 dispatch delegates
its former two-frontier control to312. Parked Fibers, object/null-key/outside-eval
producers and wider initializer forms remain required; integration is pending.
Scoped collector scan refinements pass affected state/source controls; the full
default retry still exceeds the 55-second host cap.
[Object and closure cloning](docs/semantics/SOURCE-CLONE.md) preserves shallow
copying, live aliases and closure receiver/static ownership. Callable cloning
binds named/unpacked arguments and applies weak property updates in order.
Genuine clone callbacks and nonempty readonly update windows have separate cuts;
Generator callbacks, hooks and wider lifecycle
integration remain open.
[`get_class` testing support](docs/semantics/GET-CLASS.md) observes finite live
object names and executing lexical scope through direct and callable invocation.
[Labels and goto](docs/semantics/SOURCE-GOTO.md) now resolve within each callable,
enter nested branches without evaluating skipped guards, and preserve or release
active loop, foreach and switch owners; their [review](coverage/semantics/goto-review.json)
binds static, source and paused-state checks. Legal entry into no-finally
try/catch and source-authenticated jumps requiring finally execution are supported.
Historical first-call and full quiet/request campaigns retain their own identities.
[Reference-wrapper history](docs/semantics/REFERENCE-WRAPPERS.md) now preserves
the distinct warnings from intermediate fetching and final dimension mutation;
[independent review](coverage/semantics/reference-wrapper-review.json) retains the
original disagreements and their source-level resolution. Ordinary computed-name
writes preserve existing history without creating a reference;
[corrective review](coverage/semantics/wrapper-dynamic-write-review.json) retains
the later diagnostic regression and resolution.
See [semantic design](docs/semantics/DESIGN.md) and
[numeric reference](docs/semantics/NUMERICS.md) and
[static checks](docs/semantics/STATIC.md) for interfaces and helper checks.
[Source occurrences](docs/semantics/SOURCE-CONTEXT.md) define retained checked
units and structural identities. [Declaration continuation](docs/semantics/LINKING-HANDOFF.md) records the compiler
context and linking work that remains before source activation.
Intentional departures are recorded in [engine discrepancies](docs/semantics/DISCREPANCIES.md).

[Ordinary argument introspection](docs/semantics/ARGUMENT-INTROSPECTION.md)
reads live fixed parameters and retained positional extras, with fresh result
arrays and native receive/context priorities. Bounded private checks cover
inherited source object invocation and Stringable SET ownership; broader
Generator and unfinished callback interactions remain open. Live
[Fiber transfers](docs/semantics/FIBERS.md) now retain separate VM continuations,
shared globals and handlers, cached callbacks and original C argument buffers.
Ordinary force-close and callback retirement preserve captured destructor stacks,
pending exceptions and already stored returns. Protected cleanup after an actual
return retains the earlier real exception and restored reporting/handler behavior.
Internal `error_reporting` callbacks retain weak C receives, owned arguments,
warning producers and real resumer/destructor traces through handler suspension.
Scoped constructor selectors (`self`, `parent`, `static` and compound method
arrays) now use the effectful callable resolver. Warning callbacks can mutate,
throw or suspend before the repeated-constructor check. Cached scope and maker
receipts survive reference changes and maker retirement without extra heap owners.
The [constructor ledger](coverage/semantics/fiber-callable-constructors-review.json)
keeps distinct source cuts and independently accepted state checks, including
a callback made by a GC destructor whose receiver has already retired.
The [callback ledger](coverage/semantics/fiber-core-callbacks-review.json) separates
bounded state checks from unconfirmed rich whole-source execution.
Static `getCurrent`/`suspend` first-class Closures retain immutable source and
method selection without owning an object-style static input. Direct calls,
explicit `__invoke` and Fiber C-root callbacks preserve their distinct Closure
and argument owners through normal resume and injected throw. The
[static-callable ledger](coverage/semantics/fiber-static-api-callables-review.json)
retains the private source/state cuts and remaining API/lifecycle boundaries.
Bound first-class `resume`, `throw`, `getReturn` and status methods retain their
selected Fiber. Calls borrow its receiver from the Closure and preserve distinct
direct and `__invoke` buffers through nested transfers and retirement. The
[bound-callable ledger](coverage/semantics/fiber-bound-api-callables-review.json)
records the new originals and reached checks, including saved calls to the idle
collector Fiber. Fixed bound API captures also execute as Fiber C-root callbacks:
the [C-root ledger](coverage/semantics/fiber-bound-core-callables-review.json)
records borrowed receivers and callback retirement before original start arguments.
Bound `start` captures forward the original positional/named buffer through
direct and explicit `__invoke` entry, retaining the selected receiver through
argument effects and cleanup. The
[start-capture ledger](coverage/semantics/fiber-start-callables-review.json)
records their separate checks. Captured `start` also runs as a Fiber C-root
callback, preserving the original outer buffer and its separate handler copy.
The [start C-root ledger](coverage/semantics/fiber-start-core-callables-review.json)
records genuine caller chains, source-free inner traces and callback retirement
before the original argument destructor. Bound `__construct` captures now retain
their immutable receiver through direct, explicit `__invoke` and C-root calls.
Callable parsing, including deprecated selectors and suspended warning handlers,
precedes repeated-constructor rejection. Known registered callbacks reach that
rejection without executing their body. The
[constructor-capture ledger](coverage/semantics/fiber-constructor-callables-review.json)
records source/error traces, parser ownership and last-RAW retirement.
`Closure::fromCallable` now selects Fiber APIs from simple method arrays and
static class-method strings. Frozen callback members and completed factory
arguments authenticate the capture after arrays or the factory owner retire;
bound captures own their receiver, while static object selectors add no owner.
Direct, explicit `__invoke` and C-root consumers reuse the selected API protocol.
Successful waiting calls retain their real API callsite in exception traces.
The [factory ledger](coverage/semantics/fiber-from-callable-review.json) keeps
distinct source and state cuts.
Ordinary callable arrays with simple method names now select fixed bound and
static Fiber APIs before argument evaluation. Frozen dereferenced members survive
selector mutation or retirement; the pending call owns its bound receiver once,
while static object selectors own none. Constructor callable parsing retains its
real warning continuation and validation-before-status order.
Ordinary array-selected `start` also freezes its receiver before arguments and
forwards the original positional or named buffer. Nonowning receipts authenticate
source and saved callers; completed selection stays valid after receiver retirement.
Throwing arguments release
positional values, the receiver, then extra named values in Zend order; recursive
argument frames and body exceptions keep their real callsites.
The [array-start ledger](coverage/semantics/fiber-array-start-review.json) records
six exact originals and 427 reached premises at their separate cuts.
Simple Fiber API arrays also convert to first-class Closures. A distinct source
witness freezes the selected members; the temporary bound receiver owner moves
into the Closure, while static selectors add none. Clone/equality and direct,
explicit `__invoke` or C-root calls reuse the existing API protocols, including
start and constructor captures. Simple raw Fiber API arrays also run as C-root
callbacks, including start and constructor methods. RAW owns its current array
members; the frozen receiver cache and C result tails add no receiver owner.
Copied C arguments remain separate from the original outer start buffer. Saved
Fiber states and actual callers authenticate nested, parked static and idle
collector continuations. Inner API trace frames have no file or line site. The
[raw-array ledger](coverage/semantics/fiber-array-core-callbacks-review.json)
records these distinct checks. Array unpacking now forwards copied, dereferenced
values through ordinary, array-selected and captured `start` calls. Each pack
resets named-key ordering; completed pack history authenticates the original
buffer after its arrays retire. C-root forwarding separately authenticates the
genuine outer API.
Abrupt cleanup preserves positional/receiver/named order and the distinct direct
Closure versus explicit `__invoke` owner order. The
[start-unpack ledger](coverage/semantics/fiber-start-unpack-review.json) records
these checks. Generator and Iterator packs now use real native resume operations
and iterator callbacks, preserving references through `key()` before copying
arguments; the [Traversable ledger](coverage/semantics/fiber-start-traversable-review.json)
records their source and reached-state checks. NaN `valid()` warnings retain the
raw return through mutating, parked and throwing handlers: live references are
reread, while copied NaN remains true. The [NaN ledger](coverage/semantics/fiber-start-nan-review.json)
records these separate cuts. IteratorAggregate START packs now call the real
`getIterator()` contract and retain the original operand separately from the
returned Iterator or Generator. The `getIterator()` receiver is borrowed; a saved
Generator frame acquires its own receiver. Rejected raw returns survive until
authenticated unwind. Iterator data retires before a temporary aggregate
operand. The [Aggregate ledger](coverage/semantics/fiber-start-aggregate-review.json)
tracks these bounded checks. Nested START acquisition retains each returned
Aggregate until recursive acquisition finishes, then retires layers inside-out
before rewind. Repeated ancestor identities remain distinct retval owners;
throwing-layer cleanup preserves remaining retirement before data and input.
Pending Generator startup executes a literal-output/scalar-yield prefix with a
frame with no owned roots, then closes without finally. Other pending startup routes remain
required. The [nested ledger](coverage/semantics/fiber-start-nested-aggregate-review.json)
records eleven normal agreements, two zero-credit Unsupported controls and twenty
independent reached groups/544 physical premises.
Ordinary-call unpacking, wider raw payload changes and compound selectors remain required.
The undefined-result protocol, request/fatal cleanup and wider Fiber consumers
remain required.

[Called-class introspection](docs/semantics/CALLED-CLASS.md) now implements
`get_called_class()` through inherited/forwarded methods, source Closure binding,
captures and handlers. Real stopping frames and explicit builtin Closure wrappers
preserve their distinct scope, argument priorities and error traces.
