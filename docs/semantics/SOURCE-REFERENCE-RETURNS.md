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
