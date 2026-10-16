# Source reference returns

Compiler98/runtime99 connect reference-returning named positional functions on
pinned PHP 8.5.10 CLI NTS64. The paired input is942/3c331e74; the independent
acceptance report records its exact code, evidence and one-test bridge. This
increment does not close the callable family or PHP core.

A returned reference owns its cell before the callee frame releases its locals.
Reference assignments and reference parameters preserve that identity; value
consumers read the value with the existing array ownership/COW rules. Temporary
call-array leaves can be returned by reference and survive their container's
release. The parameter-send restriction on temporary bases does not apply here.

Return source designation remains independent of the resulting operand. Ordinary
variables and actual reference calls avoid the return Notice. Literal/value
expressions, including an assignment-by-reference expression with a REFERENCE
result, emit `Only variable references should be returned by reference`. Calls
returning ordinary values also emit it. Bare and implicit returns emit the Notice
at their own instruction/end line after applicable static/fallthrough checks.
Whole `$GLOBALS` is a variable-designated copied value, not an alias to the global
table; its reference return does not emit that Notice.

An emitted type verifier reads an ordinary CV before the quiet return write fetch.
Missing untyped or mixed CVs stay quiet; a nullable typed missing CV warns and can
succeed, while an int CV warns before TypeError. Computed variables and dimensions
perform their writable fetch before verification, initializing missing slots
quietly. Successful coercion writes the shared source location/cell before frame
cleanup, including when the caller discards the result. Existing value-return
coercion remains detached from external aliases.

Exact reference-return verification and acquisition now avoid assigning the
unchanged cell. This preserves genuine parameter-backing certificates and
property type sources, including forwarded reference calls and the repeated
check after `finally`. Writers compare the checked value with the captured
pre-check input; real scalar conversions and quiet missing-slot initialization
still write, and ordinary later assignments/binds still enforce property types.
The [focused review](../../coverage/semantics/reference-return-exact-review.json)
records 16 focused source agreements and private358 state cuts of 35 independent
plus 483 reviewed assertions across 13 fixtures. Actual359 over6536a8339
passes separate strict SL compilation at37b08adeb, with zero runtime evaluations.
That ledger retains the original delayed-TypeError failure and disproved
`F|R|SHARED` prediction. The same original now matches PHP's `F|F|R|SHARED` in the
[replay increment](../../coverage/semantics/reference-return-replay-review.json):
ten replay originals and 14 current/saved fixtures with 954 assertions pass at
private360. Four preserved affected return controls and one core-only terminal
weak-conversion control also agree; actual361 compilation retains a distinct cut.
The [scalar continuation increment](../../coverage/semantics/reference-return-scalar-replay-review.json)
also recovers while/do/for tails and caught break/continue/goto through source
contexts: 14 originals and 15 reached fixtures with 1,102 assertions pass at
separate private361 cuts; actual361 strict compilation has a distinct cut.
The [no-FREE switch increment](../../coverage/semantics/reference-return-switch-replay-review.json)
recovers selected-case remainder and fallthrough for CV/compiled-CONST subjects
without repeating their evaluation. Adjacent END/PHASE metadata owns no payload
and retires together on end, jump or incoming transfer. Seven preserved originals
and 14 current/saved fixtures with 1,339 assertions pass at retained private361
cuts; actual-parent compilation is separate. Runtime VAR/TMP array owners,
active-finalizer replay, protected temporary/NULL Notice timing and by-reference
Stringable conversion remain required.

Module 379 defers the designated Notice until finalizers and repeated type checks
complete. Source occurrence, designation and emitted line remain captured through
current/saved handlers; the raw operand retains its existing payload owner until
ordinary materialization and frame cleanup. A throwing handler leaves this function
and propagates in the caller; a replacing variable return cancels the old Notice.
Six focused originals plus one protected-unused control agree, and eight reached
fixtures pass 722 assertions. Actual-parent compilation keeps a distinct cut in the
[Notice review](../../coverage/semantics/reference-return-notice-review.json).
Runtime156 now retains the actual consumed ordinary CV reference-return cursor for one
already-active finalizer, with no discarded operand root. Inner rejection preserves
its pending error during replay; uncaught escape consumes the cursor once. A local
catch resumes the cleared old return with NULL, while normal replacement and final
return preserve the selected new reference cell. Three exact originals and eight
reached current/saved fixtures/602 assertions pass; actual-parent compilation has a
separate cut in the [active-finalizer review](../../coverage/semantics/reference-return-active-finalizer-review.json).
Wider consumed VALUE/CONST/NULL and multiple-active histories, wider Stringable CV
layouts and owner protocols remain required.

For one old immutable string literal compiled as CONST with exact declared-type
acceptance, runtime156 recovers its original interned value from the authenticated
source after a caught inner rejection. The cursor owns no operand nodes. Normal
resumption restores one VALUE Notice at the original line before materializing a
fresh returned cell; the caller write preserves the globals. Two exact originals
and three reached current/saved fixtures/347 assertions pass at distinct cuts in
the [consumed-literal review](../../coverage/semantics/reference-return-consumed-literal-review.json). Actual-parent compilation is
separate. Effectful VALUE, other CONST/NULL and multiple histories remain required.

An old explicit `return null` with exact declared-type acceptance now recovers
PNULL only from its checked special-constant source. The consumed cursor owns
no operand, and normal resumption restores one original-line VALUE Notice before
a fresh returned cell. It remains distinct from bare/implicit NULL designations
and cleared CV recovery. Two originals and three reached current/saved fixtures/367
assertions pass at separate cuts in the [consumed-NULL review](../../coverage/semantics/reference-return-consumed-null-review.json).
General CONST, other effectful VALUE signatures/layouts, other NULL and multiple
histories remain open.

For a named zero-argument call concatenated with an empty string, runtime156
captures only root-free source history of the consumed computed VALUE. Normal
resumption uses cleared PNULL and one original-line VALUE Notice at the public
pause. Nonnullable string rejects NULL before Notice delivery, reenters the
outer finalizer and later selects the new reference cell (source1/state3-386
in the [computed-VALUE review](../../coverage/semantics/reference-return-consumed-value-review.json)).
The checked ordered string|null mask accepts NULL and delivers one Notice
before returning a fresh caller cell distinct from x and y. Neither path
repeats the call or restores its old payload; the nullable path enters no
second outer finalizer. One nullable original and three reached fixtures/381
assertions pass at separate cuts in the [nullable computed-VALUE review](../../coverage/semantics/reference-return-consumed-value-nullable-review.json).
Other VALUE signatures/layouts, owning payloads and wider histories remain open.

For exactly two already-active ordinary CV finalizers, runtime156 captures
the actual ordered Z/X return, phase3 and restore triples in separate steps.
The pair certificates own no old operands and survive genuine saved frames.
Uncaught inner rejection replays its finalizer, then leaves Z and X in order;
initial successful replacement retires the pair and returns the selected y
alias with x/z unchanged. Capture requires the exact named-function string
signature and no destructor operation. Two originals and four reached
current/saved fixtures/439 assertions pass at separate cuts in the
[two-history CV review](../../coverage/semantics/reference-return-multiple-active-cv-review.json).
After a locally caught inner rejection, the consumed middle CV resumes as cleared
NULL. Atomic Z/X restoration adds no payload root; the fresh NULL TypeError uses
Z's original line and replays its finalizer with the outer history retained.
The selected y alias later returns. One original at `478eb1e4` and three reached
current/saved fixtures/391 assertions at `0068f567` pass; private strict374 is
separate. Only the complete pair and CLEARED endpoints are public frontiers:
the first Z leave is helper-internal, and missing CLEARED is helper refusal.
The earlier state439 caught-Unsupported helper boundary is superseded only for
this slice.

The outer history may also be a source-equal immutable string literal; middle Z
and inner Y remain ordinary distinct CV returns. The literal owns no cell or
operand root, and its canceled VALUE Notice stays absent through caught Y
replay, cleared-Z replay and saved ping frames. Y has two source replay contexts
but one finalizer owner. Successful Y or error escape retires both histories.
Three exact originals, five reached fixtures/461 assertions and independent
three/187 pass at separate cuts in the same review.

A literal-only catch passage authenticates the intervening D catch and following
echo from checked source. Pending suffixes 3/2 retain D's actual origin; 1/0 use
the outer-finally origin after its real restore. Y has three replay contexts and
Z has two. Caught Y rejection retains the histories; M2 skips Y, fresh Z NULL
rejection reaches D, and B precedes literal resumption with one original-line
VALUE Notice and a fresh caller cell. Expanded pair admission projects scope
only for the intact authenticated tail; the first-Z helper remains nonpublic.
Three exact originals, five reached fixtures/480 assertions and independent
pending63/7 pass at separate cuts in the same review. Other passages/layouts,
lifecycle capture, wider signatures/operands, further histories and broad returns
verification remain open.

A checked named zero-argument call may precede that echo. Five reached pending
suffixes preserve D/outer-finally scope; the saved post-D ping restores f with
the root-free old literal and canceled Notice. D;P;B precedes the original Notice
and fresh caller cell. Three originals, six/514 reached checks and independent
saved-ping70/4 pass at separate cuts in the same review; throwing, mutating and
reentrant call bodies remain open.

For more than two adjacent ordinary CV histories, an ordered cursor list
authenticates each source return, phase3/restore triple and complete protected
path. Capture requires distinct live CVs, the exact named-function string
signature and inactive destruction. Each old operand loses its task root once;
partial markers validate the actual next-finalizer origin before virtual task
traversal. The observed Z/W/X chain survives Y-error replay and saved ping scope,
then leaves Z, W and X in order; initial success returns the selected y alias.
Two exact originals, five reached fixtures/467 assertions and independent
partial90/7 pass at `5a9fd5ba` in the same review.

A checked singleton TypeError catch in the selected Y owner now resumes the
consumed Z/W/X chain atomically as root-free cleared NULL, retaining first-Z
source/line/recheck. Its fresh NULL TypeError remains distinct from the live Y
error; W/X survive replay and authentic saved ping restoration. An optional
rethrow of the catch CV preserves the original Y error. Three exact originals,
six reached fixtures/640 assertions and independent CLEARED75/5 pass at separate
`cc93bbac` cuts. Immediate Y success is source3 evidence only; internal partial
leaves remain nonpublic, and source reauthentication does not exclude coherent
history rewrites. Other caught layouts retain explicit Unsupported boundaries;
mixed histories, lifecycle capture and broad returns_verify remain OPEN.

An immutable string literal may be the final history in this ordered list. Its
source-equal interned value and original line reconstruct the root-free live
triple; inner Z/W/Y remain distinct ordinary CVs. Initial VALUE return designates
one pending Notice, canceled by replacement before capture. Saved Y-error replay
retains the literal; escape leaves Z, W and literal in order, while immediate Y
success returns its alias. Two exact originals, five reached fixtures/504
assertions and independent partial96/8 pass at separate `d28f2a0c` cuts in the
same review. At that cut, normal mixed clearing/resumption remained Unsupported;
the all-CV cleared route is unchanged.

A checked C/IF/E passage now admits Z/W/old replay with Y3/Z2/W2/old1 contexts.
The root-free pending E suffix authenticates actual restores before projected
task traversal; full consumed tails and throw-only standalone old markers have
separate public scope guards. C clears Z to NULL, whose fresh error stays distinct
from the live Y error through saved M2 restoration. E/B resumes old once with its
original-line Notice and a fresh caller cell; E rethrow retires W/old with the
same fresh error. Source3 and affected old643 compatibility pass at `4336`; eight
reached fixtures/811 assertions retain first7/705 there and final106 at validator-only
`3abc`. Independent E-prefix297/5 is separate. Internal partial leaves remain
nonpublic; local source certificates do not exclude coherent history rewrites.
Adjacent mixed clearing, other layouts, lifecycle and broad returns remain OPEN.

The E-catch body additionally admits a checked named zero-argument call followed by
literal echo, optionally rethrowing that same catch CV. In the measured pure `ping()`
passage, the saved frame authenticates the complete statement/catch restores, Z replay
and W/old consumed tail under its restored f scope. The fresh Z-NULL TypeError remains
in f.e; no Notice is emitted during the call. Returning reaches E/B and old once,
yielding its original-line Notice and a fresh caller cell. E rethrow preserves the
identical fresh error and retires W/old; selected Y cancels the call and keeps its alias.
Source3, reached3/301 and independent saved80/1 pass separately at `e18e338a`; deleting
the pre-W finalizer restore is publicly refused. A late normalized budget comparison
passes. Shared selected-owner syntax admits named noarg calls, but arbitrary effects,
reentry, suspension, other catch layouts and broad returns verification remain OPEN.

When legacy throw retirement exposes a surviving live literal return, module379
restores its missing source-authenticated VALUE Notice without emitting it. Existing
markers and restores remain intact; NULL-return forms and access-reference VALUE paths are
excluded. In the guarded E-call reentry witness, unused nested `f()` delivers one
original-line Notice before T, then the outer return delivers one more. E rethrow
preserves its error identity and cancels delivery. Source2, reached3/260 and a
genuine saved nested frame59/1 pass at `23cde2d9`; a wrong Notice line is publicly
refused. The helper is wider than this string-literal witness; other reentry,
lifecycle and NULL-form restoration remain OPEN. See the [Notice review](../../coverage/semantics/reference-return-notice-review.json).

Module156 also admits idle lifecycle for distinct globally aliased ordinary string
CV histories under a sole source-checked plain echo-only destructor class. The
selected Y object remains live during capture; ordinary I2 assignment invokes its
destructor once, preserving the original SelectedY-return TypeError through Z/W/X
retirement. Selected Y succeeds with its alias and no object birth. Source2,
reached3/306 and independent saved-D82/1 pass at `c121e080`. The saved frame's full
registered result/release/operation-exit prefix validates before existing projection
reaches idle scope; deleting the exit is publicly refused. Direct active consumed
validation and other lifecycle/caught/mixed domains remain OPEN.

The checked destructor body also admits literal echo then literal-message
`throw new TypeError`. This only extends body admission; class, global string-CV,
distinctness, idle metadata and full registered-prefix guards remain intact.
Ordinary eager disposal and finally replacement preserve a distinct fresh error:
Previous is empty inside the callback and becomes the original Y TypeError after
Y-finally replacement. Source2, reached3/335 and independent post-D91/1 pass at
`df2d4e0b`; the native caller observer supports the late link. Public post-callback
admission requires the operation exit. Other destructor effects remain OPEN.

The lifecycle certificate also admits an exact global CV import and string-literal
write before the checked echo/TypeError throw. Names agree with reconstructed W's
return source and its live ordinary ENV/GLOBALTABLE cell; W is recovered beneath
the last outer X so public consumed validation remains linked at suffix X.
Source2, reached3/355 and independent post-write saved-frame110/1 pass at `a8110086`.
Changed W reaches the caller through ordered retirement; bypass skips the write.
Existing registered prefix validation remains authoritative. Reconstruction after
W retirement is local source evidence, not a physical predecessor-history seal;
other mutation/lifecycle layouts and broad returns verification remain OPEN.

An additive integer-literal write route separates checked W source reconstruction
from payload validation. W may hold a string or exactly the checked
in-range integer; all other supplied cursors retain the original string guards.
Source2, reached2/266 and independent saved109/1 pass at `b38a164b`: actual W=PINT17
survives public WX/X retirement and caller cleanup; W18 and non-W X17 refuse.
The old string mutation helper still rejects integer W. Existing assignment and
registered-prefix validation supply the effects; local reconstruction after W
retirement and the integer17 witness do not close wider mutation/returns scope.

An additive direct GLOBALS reference-rebinding route preserves distinct f-local W
and X string cells while global W may equal original W or exactly X. Only the
checked source-linked W gets that exception; every other history keeps the old
global/string guards. W's same checked relation remains required after its marker
retires. Source2,
reached2/293 and independent public136/1 pass at `a850a5df`: global W follows X,
local W stays unchanged, full registered prefixes admit and wrong global targets
refuse. Existing rebinding/destructor rules supply the effects. The retained W
relation is a local source certificate; wider rebinding and returns remain OPEN.

An additive checked singleton GLOBALS-W unset route admits either the original
global W binding or its absence, retaining a present global table and f's original
live local W string cell. Non-W histories keep the old global/string guards, and
W is reconstructed even at reduced [X]. Source2, reached2/326 and independent
public134/1 pass at `cec65d21`: actual unset keeps saved W, complete registered
prefixes admit, wrong global W/X targets refuse, and both caller reads warn on
line6 only after retirement. Existing unset/destructor rules supply all effects;
local reconstruction and the bounded witness leave wider unset/returns OPEN.

An additive checked destructor route links a GLOBALS counter guard to the selected
Y finalizer's first increment and resolves its noarg call to the current named f.
All histories retain their ordinary string/global/source guards, and common idle
admission is unchanged. Source2, reached2/324 and independent public129/1 pass at
`7ab32609`: actual nested f and the full registered saved-frame stack admit,
unused return resumes the destructor before T/D, and the original outer Y error
survives ordered retirement/caller cleanup. Missing outer operation exit and
counter-only PBOOL payload refuse. The selected bypass retains its alias without
object birth/reentry. Existing active machinery supplies all callback effects;
source reconstruction after reduced history remains local, and the exact linked
shape exceeds this n2/Q/T/D witness. Wider reentry/returns remain OPEN.

An additive guarded reference-demand route checks a noarg call on the RHS of an
AssignRef and a following literal write to the same decoded ordinary local,
excluding environment names. M35's bare-call route and common idle/string/prefix
checks are unchanged. Source2, reached2/332 and independent public150/1 pass at
`30e2fdbc`: cleanup first carries the returned reference in DESTRUCTOR_FRAME_EXIT.VALUE,
then actual inner/global/saved Y share it before the probe. The write changes Y,
while the original outer TypeError survives T/D, history retirement and caller
catch. Full public prefixes, missing operation exit and counter-PBOOL controls,
late budget equality and quiet selected bypass are checked separately. Existing
call/reference/eager rules supply all effects; local source certificates and
reached alias evidence do not authenticate arbitrary historical alias rewrites.
Wider demand/returns remain OPEN.

A separate exact caught-call certificate admits a TypeError catch around guarded
AssignRef/probe, with ordinary inner/caught names and a matching getMessage
receiver. Source2, reached2/350 and independent public99/1 pass at `8a125248`.
Nested failure cancels both binding and probe; y stays fixed and no inner alias is
created. The caught fresh error has empty Previous, while the original Y error
remains in the outer FINALLY_RESUME and reaches the caller after C/T/D and ordered
retirement. Full saved cleanup/public refusal and late budget continuation pass.
M35/M36 and common idle/string/prefix rules remain exact; no generic active/catch
admission or historical-certificate claim is added. Wider catch/returns stay OPEN.
Validation-only M37 source2/public96/1 at `2f15e222` separately cover escaping
nested failure: the fresh error reaches the caller with old Y as Previous only
after callback unwind. Its verbatim producer requires the retained checked query
in an ignored recovery directory; the ledger keeps this older cut separate.

An additive exact caught-rethrow class certificate links catch echo receiver and
throw variable to the same ordinary local. Source2, reached2/353 and independent
public132/1 pass at `64d33559`: failed reference binding/probe stays canceled,
the same caught TypeError survives late replacement/caller with its creation
origin, line4 and all reached trace-array payloads preserved. Previous is empty
at callback rethrow and old Y at later cuts; T/D never executes. Full registered
prefix/public refusal, ordered WX/X retirement, counter control, selected alias
and budget continuation are separate checks. M38/M36/common idle guards and
throw/Previous rules remain exact. These trace/identity assertions are modeled
state evidence with engine corroboration, not native trace comparison. Local
source reconstruction and broader catch/rethrow/returns remain OPEN.

A separate exact certificate admits the guarded catch echo followed by a
one-literal New TypeError. Source2, reached2/368 and independent public161/1 pass
at `98aacd7d`: failed inner binding/probe stays canceled; the new replacement
retains its own source New, line3 and captured trace-array graph through ordered
retirement and the same caller. Caught nested is distinct with line4/its own trace
and retires after callback unwind. Early Previous is empty; late replacement
Previous is old Y. Full saved-prefix/public refusal, counter control, selected
alias and budget continuation are separate checks. Old class/call/throw/idle
rules remain exact; Worker120 changes only the source cap. No native trace or
identity comparison or physical predecessor-history proof is added. Broader
replacement, explicit Previous and returns remain OPEN.

The next exact certificate permits positional New TypeError(literal,0,caught).
Source2, reached2/411 and independent public163/1 pass at `aed60b2e`. The fresh
replacement directly retains the caught nested error; old Y is appended to that
error's tail during finally unwind. All three objects remain distinct; caught
and replacement keep their own creation origins/lines/trace-array payloads
through Z/W/X/empty and caller e/p/q reads. T/D/probe are canceled. Budget
resumption starts at the genuine caller before R, and selected alias remains
quiet. Counter and missing-operation-exit refusals are separate. Original parse
failure0 and syntax-only elab retain their cuts. No native identity/trace or
physical predecessor-history proof is inferred; wider Previous/returns OPEN.

Module 186 captures the physical cell of an ordinary live unconstrained aliased CV
before weak Stringable conversion. Its retained current/saved f-local binding
authenticates that selection independently of later GLOBALS rebind/unset. Success
writes the captured cell and uses ordinary reference-return demand/unwinding; callback
failure reads its live value for TypeError and preserves the callback Exception as
previous. Certificates own nothing; existing STRINGIFY_RESULT retains the cast receiver.
The [typed CV review](../../coverage/semantics/reference-return-typed-cv-review.json)
binds 13 exact originals and eight reached fixtures/843 assertions at separate cuts,
plus actual-parent compilation. Admission checks source, line, receiver, matching
copies and retained local identity, not a fully coherent rewritten private history.
Module 381 separately admits a sole ordinary nonreference local CV. Plain conversion
borrows the f-local cell; a protected return first creates the real owning temporary.
FETCH/THROW certificates own nothing. COPY retains the converted text and masks only
the captured cell's released old-object edge while the real destructor runs, before
raw copying into that cell. Current/saved f-local scope authenticates this stage even
after the old object is collected. Callback failure retains the live object through
finally and preserves its previous Exception. The
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json)
records five exact originals and eight reached fixtures/871 assertions, separately
from the aliased-CV cut. Matching source/cell/task copies do not reconstruct a fully
coherently rewritten history; parked-VM checks are helper-only. Genuinely released
targets, destructor throw/reentry, real suspension and wider typed consumers remain open.

Validation-only M42 at `b55942bc`/385 follows a protected ordinary string return
through local `unset($x)` and a retained-binding control. Independent107/2 ties
the pre-unset cell to the saved FINALLY_REF_RETURN carrier and checks whole-state
public admission plus phase deletion refusal. Late2/176 follows the same carrier
to returned REFERENCE, caller r/a aliases, writes and caller-cut budget equality.
The return temporary stays live; physical cell collection and released borrowed
Stringable targets are outside this validation.

M43 follows an untyped by-reference return whose `finally` removes x, then either
returns y or preserves the pending x carrier. Source2 and late2/230 at `43df347e`
distinguish the delivered cell, D/R order, caller aliases and caller-cut budget.
At active cancellation the old HCELL leaves modeled allocations/roots while the
old HOBJECT remains rooted by its destructor; stale STORE data is not collection.
Deleting only a saved operation EXIT exposed a real public integrity gap. The
scoped84/270 guard at `b6805e2` requires at least one exact EXIT per registered
operation in current or saved tasks. Active68 and genuine parked23 plus two
refusals pass with strict/source2. Synthetic fatal history views retain their old
checks. No physical Zend collection or wider returns coverage is claimed.

Validation-only M44 at `cb498f92`/385 checks protected string return through local
unset and a genuine Fiber suspension. Early58/two refusals binds pre-unset x to
the parked VM carrier and a Fiber-to-cell heap edge; phase and allocation controls
remain distinct. Separate late124+106 executions capture the parked/resumed or
direct carrier, then authenticate its returned REFERENCE and worker Closure
source/target, r/a aliases, writes, main E and budget from the worker alias state.
Source2 agrees with native2. This is an owning temporary, with no released borrowed
Stringable, physical collection or cross-fixture identity claim.

M45 validation at `cbc57fdb`/386 combines suspension with untyped finally return-y
cancellation. Source/native2 agrees. Early92/two controls authenticates original
x/O to parked carrier, then resumed active O destruction while new y owns the
queued return; phase and saved EXIT-only deletion are separately heap-valid and
refused. Separate late107+107 executions follow their own source-qualified y to
worker returned REFERENCE/r/a/write, main E and worker alias-state budget. Old
HCELL allocation/root retirement leaves stale STORE while the active object stays
rooted; this does not claim physical Zend collection or broader returns coverage.

Caller demand comes from the original checked callsite's immediate source
consumers. Expression statements and discarded for clauses have unused results;
casts to void, ternary/coalesce expressions and value/reference consumers retain
used results. Variable promotion occurs only for a used result. Nineteen separate
pre-optimizer opcode observations constrain this projection. Two suppression
sources are projection-only controls: runtime error suppression remains required
work, and their Unsupported outcomes are not agreements.

`RETURN_REF_FETCH`, `RETURN_REF_VALUE` and `RETURN_REF_NULL` bind the owning BYREF
function, actual return source class and emitted line, or the permitted implicit
function/end line. Legacy value/null stages cannot replace them in BYREF frames.
Each call context's CALLSITE equals its immediate saved caller frame's ORIGIN,
including the saved context chain. An active RETURN_REF_VALUE stage accepts owning
KNOWN/REFERENCE results through leading AT/ORIGIN_RETURN wrappers; queued stages
do not inspect an unrelated current RESULT. Arbitrary consistent owning values
and references remain valid. The original forged lines, missing origins, legacy
stage substitutions and used/unused callsite swap are retained before repair.

Author gates cover31 source profiles,56 exact compiler phases plus2 suppression
boundaries/49 projections,19 demand projections/38 assertions, typed38 and
acquisition17 regressions, and2 dense cases/777 assertions. Independent gates
cover12 profiles,26 protocol controls/378 assertions,4 dense cases/1282 assertions
and2 complete933 state comparisons at seven cuts. Sets overlap. Final942 changes
only the repaired author state-test producer from semantic gate942/7951; all941
other files and modes agree. Three failed fixture preparations remain retained.

Authority is pinned `vendor/php-src` commit
`34308a6666b2d489c509541ea9befea9e2b42348`: `zend_compile_return`, return type
verification and `ZEND_RETURN_BY_REF`, with existing variable/dimension and frame
ownership machinery. Suppression, named/unpacked/variadic calls, closures/callables,
objects, exceptions/finally, dynamic sources, generators/Fibers, lifecycle and
intrinsics remain required, followed by callable integration and final complete
source/syntax/fresh offline checks. No intentional engine departure is introduced.

M46 at `27a92e4b`/386 validates external destruction of a suspended Fiber
with an object-valued owning reference-return carrier. Early98/two heap-valid
refusals binds original x/O to parking and drop-triggered destruction; parked
phase and close-caller VM operation EXIT remain separate controls. Source/native2
agrees for early/delayed drop. Separate late135+135 executions follow their own
pre-drop carrier through active D to graceful, non-returning Fiber retirement,
main L/G/E, canceled worker R and budget from the restored caller cut. Modeled
allocation/root retirement is not physical Zend collection; wider returns stay OPEN.

M47 at `0df6172`/387 validates an Exception raised by the selected O destructor
during orphan close. Source/native2 agrees. Early102/one saved-f operation EXIT refusal
binds original x/O through parking to fresh ordinary error versus private close
control. Separate late130+130 executions source-bind ExprThrow versus creation
New, then preserve the same error/line2/pure trace and null Previous at main
catch/caller. Failed, non-graceful Fiber termination cancels worker R; caller-cut
budget and final request error retirement are separate checks. Native messages
add no identity/trace claim; physical collection and wider returns remain OPEN.

M48 at `059bc886`/387 distinguishes owning edges from collector visibility for
selected reference-return temporaries in suspended Fiber VMs. Their effective
collector roots keep the Fiber/cell/O cycle out of white candidates, without
admitting general internal cycles. A normal idle request-store selection can
then close an empty-local pending-REF Fiber with an actual USER=false receiver
hold and advanced physical handle. Source/native2, independent122/two controls
and separate late163+99 pass: the same post-G carrier survives second GC/E,
then its O destructor runs during shutdown, followed by retirement and caller
budget checks. Native evidence is output timing; broader layouts and physical
collection remain OPEN.

M49 adds a bounded request-store error consumer: with genuine root-scope
USER=false Fiber hold and physical INDEX provenance, a live ordinary Throwable
becomes UNCAUGHT directly, matching `zend_fiber_object_destroy` when there is no
executing PHP frame. The existing shutdown formatter renders the fatal; the null
control still delivers the same error to the source catch. A direct-finally
source/operation guard derives the destructor trace line from the suspended
callsite for both USER origins, preserving the creation line and pure trace.
Source2/early139 retain `0ec20831`; late262/paused123 at `d16a062b` additionally
admit only the actual ordered private-control retirement state. The explicit
storage-admission bridge preserves original source evidence. Raw PhpStep UNCAUGHT
is an internal transient; public resumption is checked after driver postprocessing.
Split/full budget equality, exact fatal stderr/255 and normal null continuation
pass. See pending_carrier_cycle_throw in the local-CV ledger. Broader layouts,
physical collection and complete returns remain OPEN.

M50 at `ee915d44`/388 validates the existing typed by-reference Fiber recheck.
An external bad write changes the same selected global cell before resume;
the recheck raises TypeError and re-enters finally, parking a second time before
the worker catches that same error. An integer control instead returns the same
reference to worker r/a, whose write updates global x. Source/native2, early79
with one coordinated replay-line refusal and separate late144+146 pass. Late
checks preserve the live error's f-declaration origin/line2/null Previous/pure
trace and actual catch/alias-cut budget, then check normal cleanup separately.
The selected global cell stays owned. No runtime edit, native trace equivalence,
cross-fixture identity or broader typed/suspended return completeness is claimed.

M51 at `ee915d44`/388 validates a by-reference `:string` return whose selected
global cell contains a Stringable object. The cast receiver remains captured
while `__toString` suspends; an external write before resume changes that same
cell, then resume emits D and delivers the converted string through worker r/a.
The moved-write control resumes before the external write. Two native-exact
sources, early64/one allocated wrong-destination refusal and separate late54+54
pass. The mutant can also fail REFCELLS membership, so it is not an isolated
local-binding proof. No native identity, physical collection or wider-layout
completeness is inferred; see `stringable_suspended_selected_reference_validation`
in the local-CV ledger.

M54 repairs one computed owning VALUE return canceled inside nested `finally`.
An authenticated source-only cursor survives the old object's eager release;
after the inner return-y fails its repeated `?object` check and is caught, replay
returns detached NULL with one Notice at the original return line. A saved f
cleanup-prefix guard admits the real paused destructor state while still checking
the cursor's source and line. Source/native2 passes at `7d843e3b`; public80/one
LINE refusal and a separate caller54+40 pair pass at `ff7768cb`/388 through the
descriptor-only bridge. The treatment's split budget crosses the destructor
pause, and its returned r/a cell stays separate from bad y;
the control returns the live y object cell and writes through it. Modeled object
retirement does not establish physical collection. Other computed VALUE forms,
CONST/NULL, multiple active histories and broad returns remain open. See the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M56 extends that authenticated computed-call cursor to one owning array
`[new O]` selected by a by-reference `?array` return. The cursor owns no old
value: ordinary release retires the table, then invokes its child destructor;
caught recheck resumes a detached NULL and one Notice at the original return.
Native2/source2 agree at private `ec9c395a`/391. Public95 proves the same
HARRAY-to-HOBJECT edge and release order, real pre-destructor budget
composition, and whole-state refusal of a saved cursor with only its source
LINE changed. The original treatment Unsupported and a parse-only diagnostic
remain separate. This covers one direct array entry and modeled retirement,
not physical collection or other aggregate layouts; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M57 adds a computed-call string to the same source-only cursor rule. Although
`old_value()` returns an interned `"old"` payload, its computed return slot is
consumed during replacement; the caught `?string` recheck then restores NULL.
A literal `"old"` source instead restores that immutable value. Native2/source2
agree at private `dfa3632d`/391.
Paired public88 follows both sources to null versus old restoration with one
Notice each, rejects a heap-identical cursor LINE forgery through the driver,
and checks split budget at active replay. This adds no heap-owner rule and does
not cover other computed scalars or general CONST sources; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M58 handles two nested computed owning object returns when a deepest selected
`?object` return fails recheck and the error is caught. The replacement records
two nonowning source cursors; ordinary destruction still retires the B and A
objects in order. Both saved destructor callback views pass public admission.
Pair replay restores detached NULL with one Notice from the inner B return,
while the retained-y control delivers its alias. Native2/source2 and a
source-linked public123 pass at private `86109c30`/394, including a saved inner
cursor LINE refusal and B-callback split budget. This proves modeled retirement
for the reached pair, not physical collection or other nested layouts; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M59 records a node-free retired switch-subject history before a computed
`[new O]` table is discarded by a by-reference return from the selected case.
Ordinary cleanup retires the table and invokes O's destructor; the saved caller
keeps the source and line needed to resume the switch after both allocations
are gone. The distinct history reconstructs the remaining case without reading
the retired array and is removed by normal switch exit. Native2/source2 agree
at private `646a9e5b`/394. Public102 admits the real destructor pause and
replay, rejects a FIRSTLINE-only saved-row forgery through the driver, and
checks split budget and final row removal. The compiled constant-array control
does not need this history. This covers one sole-owned direct-object table,
not borrowed tables, other array layouts or physical collection; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M61 admits a nonempty compiled literal-array source in the caught by-reference
`?array` finalizer replay. Its source-only cursor restores the pooled `['old']`
table and one original-line Notice; an otherwise equal computed call clears
its return slot and resumes with NULL. Native2/source2 agree at private
`46af5bbc`/394. Public104 binds the compiled read, live pooled table and
one-owner replay, verifies a heap-identical cursor LINE refusal through the
driver, and checks split budget. The returned r/a reference is detached from
bad y; appending `"q"` creates a distinct table with `['old','q']` while the
pooled table remains `['old']`. This is modeled copy-on-write for the reached
literal, not a claim about GC immutability or general CONST arrays; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M62 admits a source-qualified simple local-array DIM return `$a[0]` as an old
by-reference operand during a caught `?object` finalizer recheck. Treatment
unsets the sole local array before a replacement return; control retains it.
Ordinary cleanup retires the treatment's table and selected bucket and invokes
the old object's destructor, while a node-free cursor keeps only the source
needed for replay. The saved destructor frame passes its exact cleanup-prefix
check. For a used nullable result, the consumed step installs a fresh detached
NULL reference before delivery; neither case emits a by-reference Notice.
Native2/source2 agree at private `3ea78c33`/394 with their distinct destructor
order. Public172 follows both owner states, the saved cursor and caller alias,
rejects a heap-equal cursor LINE forgery through the driver, and checks split
budget from the callback. This covers the reached local-variable/literal-int
DIM source and modeled retirement, not other DIM shapes, unused or nonnullable
returns, or physical collection; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M63 admits a source-qualified simple typed-property return `$box->slot` as
an old by-reference operand during a caught `?object` finalizer recheck.
Treatment unsets the sole local Box before the replacing return; control
retains it. Ordinary cleanup removes the old property cell and typed source,
and invokes O's destructor at different points in the two cases. The saved
source-only cursor owns no property or old object. For a used nullable result,
the consumed step creates a fresh detached NULL reference without an old
PROPREFS constraint or by-reference Notice. Native2/source2 agree at private
`39e5223b`/394. Public216 follows the typed slot and both owner states,
admits the saved callback cursor, checks the fresh reference, rejects a
heap-identical cursor LINE forgery through the driver, and checks split budget.
This covers a variable base and literal property name, not effectful or dynamic
property expressions, unused or nonnullable returns, or physical collection;
see the [local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M65 restores `REF_NOTICE_NULL` when a caught inner-finalizer throw exposes an
older bare `return;` in a by-reference function. The same source and line
remain pending after the catch; only its Notice marker had been lost. The
restoration checks the actual bare-return source and NULL operand, and uses
the existing tail placement. The explicit `return null;` control retains its
separate `REF_NOTICE_VALUE` route. Native2/source2 agree at private
`797abaa7`/394, including the original return-line Notice. Paired public74+68
admits both pending states, rejects a heap-identical NULL-to-VALUE marker
forgery through the driver, and checks caller alias and split budget. This
does not cover implicit fallthrough or other NULL-return histories; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M66 covers a caught `?object` recheck after an outer computed owning object
return and an inner global-CV reference return are both pending. The actual
replacement records two nonowning source cursors; ordinary cleanup invokes the
old object's destructor while external `$z` remains live. Pair resumption leaves
the two nonowning restoration slots and, for the reached used nullable result,
creates a fresh detached NULL reference without a by-reference Notice. The
retained-y control delivers its alias. Native2/source2 agree at private
`17fa485a`/394. Public157
admits the saved destructor pair, binds the TypeError replay and fresh caller
cell, rejects a heap-identical saved inner cursor LINE forgery through the
driver, and checks split budget from the callback. This covers one mixed
computed-object/global-CV layout, not unused or nonnullable returns, other
payloads, physical collection or complete returns verification; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M67 admits the same mixed computed-object/global-CV pair when `&f(): object`
has a used nonnullable return. The first caught `$y` recheck error leaves a
consumed source-only pair; resuming the middle `$z` return checks NULL and raises
a new TypeError at its own source line, with Previous NULL. Its error survives
reentry through the inner finalizer and reaches the caller catch. The ordinary
old-object cleanup and live global `$z` are unchanged, and this route creates
no fresh returned cell or by-reference Notice. Source2 at private `836b7845`/394
matches retained native2. Public120 binds the distinct old and new errors, node-free
cleared marker, reentered finally owner and caller catch, rejects a heap-equal
inner cursor LINE mutation through the driver, and checks split budget from the
cleared cut. This covers the reached used nonnullable source shape, not unused
returns, other mixed layouts or complete returns verification; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M68 reverses the old sources for a used `?object` return: the outer return
holds global `$z`'s reference and the inner return holds a computed owning
object. An authenticated pair of nonowning source cursors survives ordinary
object cleanup and the destructor callback; it does not restore the old object
or reread `$z`. After the caught `$y` recheck, the reached pair resumption
produces NULL and one inner computed-source VALUE Notice marker. Source2 at
private `d49392a2`/394 matches retained native2, including the emitted Notice
and the retained-y control alias. Public155 authenticates the saved pending
pair and original VALUE release, the old object's retirement with `$z` live,
then detached caller delivery. A saved inner cursor LINE mutation keeps the
heap equal but fails descriptor and actual-driver admission; callback budget
composition also passes. This covers one reversed used nullable mixed layout,
not unused or nonnullable returns, other layouts or complete returns
verification; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M69 admits a used `?array` pair with an outer global `$z` reference and an
inner array source that is either a no-argument computed call or an authenticated
compiled `["old"]` literal. The pending array carrier is consumed during
replacement; the pair records only source cursors. Both old tables remain
allocated through their pools, so allocation survival does not choose the
restored value: the computed call yields NULL and the literal rereads its exact
compiled PARRAY. Each raw resumption installs one inner-source VALUE Notice
marker. Source2 at private `952bc3db`/394 matches retained native2, including
the emitted callee Notice and different post-append arrays. Paired public
checks bind the real capture and pool owner drop, caller detachment and new
append table while the old table stays unchanged. A heap-equal literal cursor
LINE mutation fails descriptor and actual-driver admission; both pair-cut
budget compositions pass. This covers the reached used nullable source pair,
not other array layouts, unused or nonnullable returns, or complete returns
verification; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M70 admits an ordinary no-argument instance-method call with a literal method
name as an old computed return source for used `&f():?object`. The receiver is
evaluated and cleaned up by the existing call machinery; the source cursor
does not retain or reconstruct it. A temporary Factory emits its destructor
marker before the selected finally return; publishing the same Factory to a
global slot retains it through the caller cut. In both cases, ordinary cleanup
releases the old O method result and enters its destructor before replay. The
saved f frame carries a nonowning source cursor, and the caught `$y` recheck
resumes the old method return as NULL with one VALUE Notice marker. Source2 at
private `6e4e1115`/395 matches native2, including the exact callee Notice and
receiver destructor ordering. Paired public checks bind the authentic saved
cursor and original VALUE release, raw NULL/Notice marker, caller detachment
and retained Factory root; a heap-equal cursor LINE mutation fails descriptor
and actual-driver admission, and both callback budget compositions pass.
Temporary Factory node identity is only printed by the output-only frontier,
not claimed by the public proof. This covers the reached no-argument,
literal-name method result, not arguments, dynamic names, nullsafe calls,
reference-returning methods or complete returns verification; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M71 extends that computed source to an ordinary literal-name method call with
one positional argument. The Factory receiver remains globally live in both
cases. A temporary Arg runs its destructor before F; assigning the Arg to a
global slot retains it through the caller cut. Existing argument cleanup
determines this timing; the return cursor records only the old method source
and line. Ordinary replacement cleanup invokes the returned O destructor,
and the saved f frame carries the nonowning cursor. After the caught `$y`
recheck, raw cursor resumption installs NULL and one method-source VALUE
Notice marker. Source2 at private `031881ee`/395 matches retained native2,
including the exact callee line5 Notice and both destructor orders. Paired
public checks authenticate the old one-argument source, saved O release,
retained Arg global root, detached caller alias, one delivered diagnostic,
heap-identical cursor LINE refusal and both callback budget laws. The
temporary Arg node identity is printed by the diagnostic, not asserted by
the public proof. This covers the reached single ordinary positional
argument, not named/unpacked/by-reference arguments, dynamic method names,
nullsafe or reference-returning methods, or complete returns verification;
see the [local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M72 admits the evaluated REFERENCE carrier of an ordinary no-argument,
literal-name instance method on a variable receiver as an old return source.
The source test uses a by-reference `?object` method returning Factory's slot;
the outer finally unsets that slot before a caught `$y` recheck. The original
old cell is live at capture and retires during ordinary replacement cleanup,
which invokes O's destructor. The saved f frame holds a nonowning source
cursor, so it neither rereads the unset property nor retains the dead cell.
Raw resumption installs NULL and one method-source VALUE Notice marker; the
caller receives a detached r/b NULL alias. Source2 at private `e1cff5d3`/395
matches retained native2 in both reference and value-method cases, including
exact stdout, stderr and the callee line4 Notice. The reference-only public
proof binds the old cell, unset slot, original VALUE-O release, retired cell
and O, one delivered diagnostic, heap-equal cursor LINE refusal and callback
budget law. The initial state fixture's compile failure and the first public
fixture's unrun binder version contribute no state credit. This covers the
reached used nullable simple-variable/no-argument/literal-name method source,
not argument or dynamic-name or nullsafe method forms, unused or nonnullable outer returns, or complete
returns verification; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M73 admits the discarded-result `object` form of the mixed old computed-O
and global-CV return history. The caller uses a plain `f();`; after the first
caught `$y` recheck, the genuine pair resumes as a node-free cleared NULL
without allocating a returned reference at that step. Its type check creates
a distinct line-9 TypeError with no Previous exception, then the middle
finalizer runs again and the same error reaches the caller catch. The shared
`?object` control completes normally. Source2 at private `7806bdc2`/395
matches retained native2 in both cases, including exact PHP output and quiet
stderr. Public125 binds the old and new errors, unchanged allocations at raw
clearing, zero Notice, one heap-identical cursor LINE driver refusal and split
budget. The prior Unsupported baseline and output-only guard query retain
zero repair credit. This covers one discarded nonnullable mixed source layout,
not other unused histories or complete returns verification; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M74 distinguishes an evaluated integer call result from a compiler-folded
integer expression as the old source of a used `&f():?int` return. Both original
sources carry node-free `KNOWN PINT 41` into F, but `old_value()` has no compiled
read at the old expression, while `40 + 1` has an authenticated compiled `41`.
After the selected `$y` recheck fails and is caught, the genuine active cursor
resumes the computed source as NULL and the folded source as `41`. One raw
consumed step installs the corresponding return operand and one old-source
VALUE Notice marker; the diagnostic is delivered before the caller's r/b
observation. Source2 at private `04a21f96`/396 matches retained native2 for
both opposite caller values and exact callee line-3 Notice text and stderr.
Paired public checks bind the original carrier, active cursor, raw restoration,
caller alias and final write. A folded cursor LINE-only mutation preserves the
heap but fails descriptor and actual-driver admission; both active-cut budget
compositions pass. The proof does not claim a direct capture step or general
scalar/CONST recovery. The unchanged Unsupported baseline and output-only
category query retain zero repair credit. Other scalar expressions and return
layouts remain open; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M75 admits a used `&f():?int` old return of `($x = old_value())` while one
finalizer is active. The named call runs once and leaves a root-free integer 41;
the finalizer observes `$x === 41` before writing 99. After a selected `$y`
return fails and its error is caught, replay restores NULL with one old-line
VALUE Notice. It does not repeat the assignment or undo `$x = 99`. The direct
`return old_value()` control observes `$x === 0` at the same finalizer and
retains its existing result. Both original sources match exact stdout, stderr
and exit at private `8afe016f`/397. One source-reached fixture binds the old
carrier, active cursor, raw NULL/Notice marker, detached caller alias, bad
cursor-line refusal and split-budget equality. The initial rule-name parse
failure has zero semantic credit. This covers only the reached nullable,
simple-variable assignment of a named no-argument integer call; other return
signatures, layouts and complete returns verification remain open in the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M76 admits the same used nullable return when its named call has one ordinary
positional argument, `($x = old_value($x = 17))`. The callee receives 17 once;
its return then stores 41 in `$x`, which the finalizer observes before writing
99. The selected `$y` return consumes the old carrier and cancels its initial
Notice. After its reference recheck fails and is caught, a surviving nonowning
source cursor restores detached NULL with one
new old-line VALUE Notice, without repeating either assignment. The matching
no-finalizer control returns 41 and keeps `$x === 41` after the caller writes
through its detached alias. Both originals agree exactly with PHP at private
`8beef331`/397. One reached fixture starts in the callee with `n=17` and
global `x=17`, then binds the old 41, cursor, raw restoration, caller aliases,
bad cursor-line refusal and budget resumption across that early call state.
This admits only one same-variable nested integer assignment argument, not
other argument or return layouts; see the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M77 distinguishes a compiled integer RHS from the outer assignment result.
With the same x-observing, caught-`$y` finalizer, direct `return 40 + 1`
restores `41`, while `return ($x = 40 + 1)` observes `$x === 41` in the
finalizer but restores detached NULL. The RHS retains compiled `41`; the
assignment itself has no compiled read, and its cleared temporary cannot use
the RHS constant to recover. Both original sources match PHP exactly at
private `86a52f19`/398, including one old-line Notice each. One assigned
source-reached fixture proves the compiled-read distinction, old carrier,
consumed cursor, raw NULL/new Notice, detached caller, cursor-line refusal
and budget resumption. The direct source agrees independently; M74 examined
the direct-folded source category in a separate state fixture, which was not rerun.
Two-literal integer addition and this nullable used-return layout bound the
new rule; see the [local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M78 admits one flat owning array from a named no-argument call in a used
`&f():?array` assigned return. Before the finalizer, the pending old `[41]`
array and global `$x` share a table; appending 99 leaves `$x` with a distinct
`[41,99]` table. A direct `return old_value()` control leaves `$x` as `[99]`.
After the selected `$y` recheck fails and is caught, the assigned source's
root-free cursor restores detached NULL and one new old-line VALUE Notice.
Both originals agree exactly with PHP at private `90e931fe`/399. One assigned
reached fixture binds the table split, root-free consumed marker, raw restore,
caller alias, cursor-line refusal and budget equality. The compiler pool may
retain the old literal table after its pending root is consumed; no physical
collection or independent pending-root COW causality is claimed. The first
fixture's compiler binding error has zero state credit. This covers only a
live, single direct-integer array at key 0 from the no-argument assignment
shape; see the [local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M79 admits an ordinary object from a named no-argument call in a used
`&f():?C` assigned return. The pending old C instance and global `$x`
initially share the object; the finalizer sets `$x` to NULL. The selected
`$y` return then consumes the old carrier and cancels its first Notice,
running C's `__destruct` once between the two `I` markers. After the
selected reference's recheck fails and is caught, the nonowning cursor
restores detached NULL and one new old-line VALUE Notice. The direct-call
control observes `F:0`, while the assignment observes `F:1`; both exact
original sources agree with PHP at private `02ffe678`/399. One assigned
source-reached fixture validates the saved `f` frame's destructor-result,
release, operation and cursor prefix inside `D`, then proves modeled old
object retirement after release, raw restoration, detached caller aliases,
saved-cursor line refusal and budget resumption. Its first stage-search
failure has zero state credit. This covers one normal destructor and the
nullable, no-argument assignment shape; it does not establish physical
Zend collection or throwing/reentrant destructor behavior. See the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M80 admits the no-argument integer assignment source under a nonnullable
`&f():int` declaration. The finalizer's selected `$y` return fails its int
recheck and is caught; the consumed old assignment cursor then restores NULL
with a new pending old-line VALUE Notice. NULL fails the declared int check
before that Notice can be delivered. The resulting TypeError survives a
second outer-finalizer passage and reaches the caller catch with `$r` still
7. A direct-call control observes `F:0` on the first passage; the assignment
observes `F:1`. Both call `old_value()` once, emit `F:0` on the second
passage, and deliver no Notice. Native observations at `e90b3a74`/399 are
matched by strict compilation and both original-source agreements at private
`8b7c539a`/399; the unchanged model admitted only the direct control.
One assigned source-reached fixture distinguishes the
selected-array and restored-NULL TypeErrors, pending versus delivered Notice,
the surviving NULL error at the caller, a cursor-line refusal and budget
resumption. This extension applies only to the exact builtin-int signature
in the no-argument assigned-integer source guard; effectful arguments and
other nonnullable source/value shapes remain open. See the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M81 covers a throwing destructor during the selected-reference replacement of
a used `&f():?C` old return. The old source is a named no-argument call,
directly returned or assigned to a simple variable before return. Releasing
the old C object runs `D` and leaves its Exception pending at the selected
return operation exit. The bounded pending-finish rule restores the source
replay owners and single nonowning cursor, so the same Exception reaches the
local `CE` catch; the consumed old return then restores detached NULL and
one new old-line VALUE Notice. Native observations and unchanged mismatching
baseline are pinned at `e70950fcb`/399; strict compilation and both exact
original-source agreements pass at `7bc06612d`/399. One assigned reached
fixture passes 120 Boolean checks and two raw steps. It binds the retired old
HOBJECT and pending Exception, public descriptor admission at the operation
exit, local catch identity, caller `rNULL/b7`, a LINE-only public refusal and
whole/split budget equality. The first public state failure at `75c47721a`
has zero full-state credit; it exposed the missing operation-exit descriptor
case. This proves one echoing C destructor throwing an ordinary Exception,
not other exception types, reentry or physical Zend collection. See the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M82 admits the modeled built-in subclasses of Exception at that same bounded
selected-return destructor exit. A new direct/assigned pair makes C's
destructor throw `RuntimeException("boom82")`; the local `catch (Exception)`
observes its subclass and message as `CE:1/1`, then consumed replay restores
detached NULL and one old-line VALUE Notice. Native2 and the unchanged
two-mismatch baseline are pinned at `108b026fe`/399; strict compilation and
both exact original-source agreements pass at `345244d14`/399. One assigned
reached fixture passes 124 Boolean checks and two raw steps. It binds the
pending subclass and message at the actual operation exit, the same object in
the local superclass catch, retired old HOBJECT, public descriptor and
LINE-only refusal, caller `rNULL/b7` and budget equality. The guard reuses the
existing Exception parent relation; Error siblings remained excluded at M82. This
fixture proves one RuntimeException history, with M81's exact Exception proof
separate. Other admitted built-in Exception descendants lack focused validation;
user-defined throwable subclasses, Error siblings and reentrant destructors
remain open. See the [local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M83 admits public resumption at a normal pending-free destructor operation
exit in the same bounded nullable-class old-return family. After `D`, the
old modeled HOBJECT is retired; the operation exit still precedes the
selected reference return and carries one nonowning old-return cursor.
The unchanged model rejected this source-reached exit before its valid
normal finish step. A narrow saved-descriptor clause now validates the
queued return and cursor, leaving finish and return-value behavior intact.
Strict compilation passes at private `cb2f199bf`/399. One assigned reached
fixture passes 90 Boolean checks and one raw step: public admission, raw
normal finish, the historical M79 caller `r=bNULL` then `42` and one Notice,
a heap-equal LINE-only public refusal, and equal split/whole budgets. M79's
native/source agreements remain separate; no old actor was rerun. This proof
covers one normal C destructor and named no-argument nullable-class source;
wider histories and broad returns remain open. See the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M84 admits finite modeled built-in Throwable kinds at the same authenticated
pending destructor exit. In new direct/assigned `&f():?C` originals, C's
destructor throws `TypeError("dtor84")`; local `catch (TypeError)` checks that
message and prints `CT:1`. Native2 at `ee63167a`/399 has
`F:0/1;I;D;I;CT:1;A;S`, detached `rNULL/b7` and one old-line VALUE Notice;
strict compilation and both exact original-source agreements pass at
`913c8747`/399. The unchanged model wrongly
routes both to outer `OT`, with r7 and no Notice. One assigned reached fixture
passes 131 Boolean checks and two raw steps: its pending TypeError originates
at the destructor's `new TypeError`, distinct from the selected-y return, and
the same object and message reach local `CT`. It also proves retired old
HOBJECT, consumed NULL/new Notice, public descriptor and LINE-only refusal,
caller state and exit-cut budget equality. The two changed guards retain their
source, operation, owner, liveness and single-cursor checks. This is one
TypeError history; M81 Exception, M82 RuntimeException and M83 normal-exit
proofs remain separate. Other built-in kinds and wider destructor histories
need focused validation. See the [local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).

M85 admits an ordinary no-argument, literal-name method call on a variable
receiver as the old source at that pending destructor-throw exit. The paired
`?O` sources differ only in whether `Factory::old_ref()` returns by reference.
After `f` unsets the retained Factory's slot, O's destructor throws
`TypeError("dtor85")`. Native2 and repaired source2 both reach the local
`CT:1` catch, resume the old return as detached NULL, and emit one old-line
VALUE Notice; the unchanged model wrongly reaches outer `OT` without a Notice.
The reference-only reached proof binds the old property HCELL to O before
unset, their separate modeled retirement while Factory remains live, the same
destructor TypeError at the local catch, and the root-free cursor's NULL/new
Notice continuation. It also passes actual exit admission, a heap-equal
LINE-only public refusal and budget equality. The initial fixture's false
assumption of an early Notice has zero state credit; the genuine reference has
no marker at that pre-finalizer cut. Only pending-throw admission changed;
normal pending-free method admission is unchanged, and wider method forms remain
open. See the
[local CV lifetime review](../../coverage/semantics/reference-return-local-cv-lifetime-review.json).
