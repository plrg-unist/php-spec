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
and valid foreach companion stay distinct. Parsing warnings, Stringable-option INI
refusal, Stringable descriptions and wider expression/callback forms remain required.
Run the [catalogue](tests/semantics/assertion_cases.json)
with `method_runtime.py --catalogue tests/semantics/assertion_cases.json`.

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
All twelve [compound assignments](docs/semantics/UPDATES.md) preserve captured
targets, delayed reads and alias ownership; [independent evidence](coverage/semantics/compound-review.json)
records 2,639 exact source comparisons and the corrected diagnostic phases.
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
Prior 123/private 238 cuts remain separate. A tested cut with 360 modules passes
compilation, 238 affected state premises and 23 constant-export/control premises.
One constant lookup per insertion reduces calls from 689,580 to 229,972 over
a matched prefix of 400 steps while preserving the returned tuple exactly.
[Ordinary binary operators and casts](docs/semantics/ORDINARY-OPERATORS.md) now pair
source dispatch with scalar/array conversions, delayed variable reads and concat
compile/runtime diagnostics. The admitted catalog adds 1,506 exact source inputs;
seven preserved request-environment boundaries now have separate explicit-input witnesses.
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
IteratorAggregate and other Traversable consumers remain required.
[Generators](docs/semantics/GENERATORS.md) receive arguments eagerly and defer
ordinary bodies in object-owned frames. Value yields, literal iterator methods,
`getReturn`, `send`, `throw` and value `foreach` retain real resumer scope and
traces. Inputs survive initialization; exception injection preserves ordinary
catch/finally execution and exception identity. [Delegation](docs/semantics/GENERATOR-DELEGATION.md)
adds arrays, source Iterators and shared Generator graphs with live raw caches
and natural return/unwind. [Last-owner close](docs/semantics/GENERATOR-FORCE-CLOSE.md)
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
premises retain separate cuts. Absent or throwing restored handlers, deeper
rendering, abrupt child cleanup, parked/escaped storage and generic terminal cleanup
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
IteratorAggregate, wider call forms and reference producers, request/terminal cleanup
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
Scalar-loop/CV-CONST continuation and physical-array owner recovery, active-finalizer
replay, protected temporary/NULL Notice timing and Stringable conversion remain open.
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
wider consumers and WeakMap remain required. Canonical292/304
composition separately passes strict277 initialization and one exact weak lifetime
source; earlier cuts retain their inputs.
Wrappers also satisfy nominal `WeakReference` argument and property types after
their referent retires; diagnostics retain the actual internal class name.

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
[Match expressions](docs/semantics/SOURCE-MATCH.md) preserve strict, lazy arm
selection, delayed CV subjects, ordered compiler diagnostics and owned value
results; their [review](coverage/semantics/match-review.json) binds source, compiler
and paused-state checks. [Generated Throwable objects](docs/semantics/THROWABLES.md)
now support ordered no-finally try/catch and throw/rethrow, internal constructors,
getters and structured traces. The distinct `ErrorException` constructor and
`getSeverity` have a separate [bounded review](coverage/semantics/error-exception-review.json).
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
binds source and paused-state checks. [Internal `stdClass` identity](docs/semantics/SOURCE-STDCLASS.md)
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
[the Override review](coverage/semantics/promoted-override-review.json); other
parameter attributes/hooks remain required.
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
Literal named noarg reference-return calls now retain the actual returned cell
through undefined-property warnings. The captured target remains borrowed, so
handler rebinding may retire it while the cell keeps the replacement alive until
fetch cleanup. Ten exact originals and separate 237/207/225 reached cuts cover
callee/finally rebinding, normal and throwing last-owner cleanup, saved callers
and stdClass child retirement. [The reference-receiver review](coverage/semantics/reference-property-receiver-review.json)
records the pinned8.5 wrapper behavior and the refuted8.6 snapshot prediction.
The actual361 join over `7c18fccada` passes strict compilation at `0b6054930`,
preserving accepted return replay, CALLS and exception interfaces.
Computed names, getters/hooks and wider reference-call receivers remain required.
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
their phase order and handler-ineligible severity. Successful collision dependency
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
Temporary-current and internal API capture consumers remain required.
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
pass; the generic 45-second runner times out on that source. By-reference returns
and wider typed consumers remain open.
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
[Parameter-default NEW autoload](coverage/semantics/default-new-autoload-review.json)
now completes lookup before allocation and nested arguments, then reselects the
loaded constructor under the receiving declaration scope. Nine private sources
and 174 reached premises pass at separate cuts; one actual generator interaction
preserves eager default creation before suspension. Global-constant AST NEW
autoload and wider class-link consumers remain required. Default `spl_autoload`
filesystem search stays excluded.
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
records these separate cuts. IteratorAggregate acquisition, wider raw payload
changes and compound selectors remain required.
The undefined-result protocol, request/fatal cleanup and wider Fiber consumers
remain required.

[Called-class introspection](docs/semantics/CALLED-CLASS.md) now implements
`get_called_class()` through inherited/forwarded methods, source Closure binding,
captures and handlers. Real stopping frames and explicit builtin Closure wrappers
preserve their distinct scope, argument priorities and error traces.
