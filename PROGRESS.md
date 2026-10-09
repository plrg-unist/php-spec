# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
agreement does not establish complete semantics. Large evidence stays outside
Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

Root-terminal HALT compilation now folds original-file byte offsets and treats
the authenticated final statement as a no-op, preserving pools, events and the
remaining continuation. Two fresh originals agree at c78beb627/371, including
namespace/global379 versus local17 and UTF-8 byte positioning. Strict3 passes 5.272s;
104 checks at real source frontiers plus 20 pure queries pass in 66/58 groups.
A separate pure payload decoder2 passes; the compile-stage baseline and two
fixture failures retain zero credit. Encoded profiles, broader constant/default/class
contexts and include/eval registration remain required.
Actual 371 over 8f1b22aad passes strict3 at 72e1a9d58 (5.321s), preserving attributed
class lines, property/factory/collector and foreach acquisition guards. Private
source2/104+20 checks and both fixture failures retain their original cuts.
[HALT ledger](coverage/semantics/halt-compiler-review.json).

Aggregate yield-from380 recursively acquires real Iterator/Generator data through
borrowed getter calls, retires raw layers and the original operand before rewind,
and keeps returned Generators in generic iterator mode: null result, no send/throw
forwarding and live raw reference cache. Copied getter frames own This once;
parked acquisition keeps the real parent resumer/source receipt. Early pending
cleanup retains constructed data until request cleanup; real rewind errors drop
it before catch. Seventeen unchanged originals agree across the retained source16
and owning-reference source1 cuts; strict368 passes at `b1164af45`. Independent
25/720 physical owner and source-authority premises pass at separate cuts.
Original compiler/source/fixture failures remain zero. At that acquisition cut,
Iterator NaN warnings and changed original operands remained required.
Ordinary-call Aggregate unpack remains required.
Actual368 over `7b449476` passes strict compilation at `f4567b30`; private
source/state cuts retain their inputs. [Yield-from review](coverage/semantics/yield-from-aggregate-review.json).

Acquired Iterator `valid()` NaN warnings now retain their raw retval and acquisition
receipt through ordinary handler invoke, result and cleanup. One post-handler
decision rereads numeric references; copied NaN remains true. Real parked handlers
preserve the parent resumer and delegation claim in the Fiber VM. False or thrown
warnings retire raw retval before iterator data, without request retention.
Nine exact native-grounded originals and strict368 pass at `c52ae1d16`.
Twenty independent genuine-source groups/637 physical ownership and warning
authority premises pass at `d825e3fc0`. Wider raw payload changes stay explicit Unsupported. Actual370 over `d827dc635` passes strict SL at `4723282ff`;
private source/state cuts retain their own inputs.
[Warning review](coverage/semantics/yield-from-valid-nan-review.json).

Aggregate yield-from getters may rebind an original CV or reference operand when
the raw result is a terminal Iterator/Generator or a rejected non-Aggregate value.
The original class still names rejection; borrowed CV and owning-cell cleanup
retain their existing owners. Six safe unchanged originals agree at `f82e9b3ed`;
strict370 passes at that cut. Changed operands returning another Aggregate stay
explicit Unsupported/zero agreement. Nine genuine-source groups/376 physical
owner and source-authority premises pass at separate cuts; the two fixture
failures retain zero credit.
Actual370 over `288dc800` passes strict SL at `50367af16`; private source/state
cuts retain their own inputs.
[Rebound review](coverage/semantics/yield-from-rebound-operand-review.json).

Foreach Aggregate getters now permit terminal Iterator/Generator or rejected
non-Aggregate returns after rebinding an independently protected original CV or
reference. Borrowed CVs and owning cells retain their modes through initial
Iterator valid-result cleanup or Generator yield; input retirement then precedes
current/body with data protected.
Six unchanged originals agree at `4e9dd1014`;
strict370 passes there. The changed-Aggregate control passes its zero-agreement
assertions at `1cf220b69`; its original event-encoding failure stays zero.
Nine genuine-source groups/361 physical ownership and authority premises pass
at `5a811c3d5`; no state fixture correction was needed.
Actual371 over `557e8c817` passes strict SL at `ab0808dff`; private source/state
cuts retain their own inputs.
[Foreach rebound review](coverage/semantics/foreach-rebound-operand-review.json).

Bounded assertion quantity warnings retain frozen parsed modes and old returns
through nested raw writes, throw and restore. Immutable string carriers preserve
INI identity while ordinary consumers use bytes. Seventeen safe originals retain
the separate 5ec/4141/1a8 cuts; actual phase234 at93be contains208 well-defined and26
reached lifetime-boundary checks. A replaced modified request raw stops with explicit
Unsupported; four native lifetime probes have zero agreement, with no allocator model.
Affected Throwable source3, genuine trace47 and retained Generator source1/report52
pass at1a8; template2 passes at6cb. Strict361 compiler3 passes at1a8 (4.623s).
The [quantity ledger](coverage/semantics/assertion-quantity-review.json) preserves
failures and the separate diagnostic46. Per-round original recapture and warned
restore now pass two fresh safe originals and182 source-frontier checks plus one
pure NULL trace query at57ee/363; strict3 passes5.024s. Pending shared Throwable
identity and real restore commits remain intact. Retained-entry Stringable SET
now snapshots the converted option before the old return, warning/refusal and trace
arguments. The original conversion is borrowed evidence; actual calls own only the
converted string, so handler retirement runs the Option destructor immediately.
Three fresh safe originals and236 checks at real frontiers, including a projected
ownership query, pass at7eaee/363; strict3 passes4.921s. Warned Stringable RESTORE
now retains a unary converted call and commits the saved original despite handler
retirement/shared throw. Two fresh safe originals and211 frontier checks, including
a projected owner query, pass at05db/365; strict3 passes5.024s. NaN SET now freezes
the old return and formatted input before conversion warning dispatch, then captures
live raw/original after the callback. Two fresh safe originals and247 source-frontier
checks plus eight pure trace-clear companions pass atc2b195/367; strict3 passes5.021s.
The shared Throwable survives committed NAN/mode0 without a second handler entry;
the baseline and original entry-certificate failure retain zero credit. Reentrant
restore now represents a cleared live original as raw NULL with modified=false.
The getter returns canonical empty bytes; parsed mode12 and safe no-op restores
remain intact through the shared Throwable. Two fresh originals and323 checks at
real frontiers plus12 pure exclusion queries pass at242576/367; strict3 passes5.074s.
New or active SET/NaN continuations encountering NULL stop explicitly; no source
executes NULL parsing. Retained-owner Stringable descriptions now convert once before
truth and resume the entered assertion despite a callback changing live mode to0.
Cast-time traces retain the original object; a failed assertion stores the converted
argument/message. Original cast Throwable identity and untouched assignment survive.
Three fresh originals,265 checks at source frontiers and4 pure owner-exclusion queries
pass atb4ea/367; strict3 passes5.174s. The original raw-descriptor timing failure retains
zero credit; the corrected fixture checks admission after actual driver publication to
THROW_SEARCH. Quiet weak scalar descriptions now apply TYPESTRING and replace only
the actual second call argument before failure policy and trace capture. Integer17
gets a fresh authenticated carrier; false gets canonical empty bytes and NULL stays
NULL, while source variables and assignment sentinels stay unchanged. Two fresh
originals and217 checks at source-derived frontiers, including helper counterexamples,
pass at088d14878/370; strict3 passes5.224s. The prior TypeError diagnostic carries
zero agreement. Description warning conversion/unpack and last-owner entry/handoff
remain required. [Description checkpoints](coverage/semantics/assertion-quantity-review.json).
Logical-not generated descriptions now use Zend prefix precedence240/child241,
retaining compound-child parentheses. Two fresh originals and79 checks at a genuine
compound pool/default-message/trace/true-control frontier pass atbb485b301/370, plus
two pure export-context queries; strict3 passes5.223s. The compile-stage exporter
Unsupported baseline retains zero agreement/reached credit; wider exporter forms
remain required. [Exporter checkpoint](coverage/semantics/assertion-quantity-review.json).
Actual370 over2ffab90c passes strict3 at461e012e (5.274s), preserving factory
invocation, denied-getter scope and yield-from Aggregate acquisition guards.
Private logical-not source2/79+2 checks and all prior cuts retain their identities.
Actual370 over1963b152 passes strict3 atb74fe28fb (5.775s), preserving current
factory/GEN/SensitiveParameter, implicit-getter, typed-reference and EX worker guards.
Private description source3/265+4 checks and all previous cuts remain unchanged.
Actual367 over78f866bb passes strict3 at7a2095bf (5.071s), preserving
SensitiveParameterValue reception and by-reference finalizer cursor/replay guards.
Private nullable source2/335 and all earlier cuts remain unchanged.
Actual367 overdb808 passes strict3 atfac7c8 (5.121s), preserving ARG
receiver/argument/foreach continuations and EX parked-public lookup/collector guards.
Private source2/255 cuts and prior unsafe boundaries remain unchanged.
Actual367 over288c passes strict3 ate6c5 (5.224s), preserving Aggregate foreach,
deferred return Notices, live concat and mixed-CV property ingress; private
source2/211 cuts are unchanged.
Actual365 over7377 passes strict3 at6b2a (5.020s), retaining current GEN/PROPS,
retired-owner and SensitiveParameter guards; private source3/236 cuts are unchanged.
Actual363 over1b33 passes strict3 at1ad9 (4.975s), preserving canonical GEN release
evidence and carrier-aware ARG/GEN fixtures; the private source/state cuts are unchanged.
Actual363 over75dade passes final strict3 atb0d8 (4.921s), preserving current
CALLS/CLASS/PROPS guards. Source-backed static70, Fiber54 plus4 pure key queries
and three retained incoming originals keep their0506/2ae cuts. Static356/371 and
key376 preserve carriers; the ledger retains separate failed source/VERIFY/fixture cuts.

Constructor property promotion retains source Param flags/origins, compiles separate
property defaults and performs ordered value/reference writes after all receives.
Explicit re-entry, private/inherited/trait scope, readonly checks and supported method
attributes reuse ordinary property protocols. Exact original9b85 now gives
`B|Y|F|D1||Z|1|1`; eight focused originals add seven normals and one ordered
CompileError. Private359 at00c passes strict compilation, source9 and genuine
Weak48/byref47. Historical Unsupported, strict/fixture stops and wrong-status row
retain zero affected credit. Actual361 over6e09 passes strict compilation
at8335 (4.840s); private source/state cuts retain their inputs. Other parameter
attributes/hooks and complete core remain required. [Promotion review](coverage/semantics/constructor-promotion-review.json).

Promoted properties accept one zero-argument builtin `#[Override]` through the
actual namespace/import scope. Exact nonprivate parent properties satisfy it;
simple root errors occur during compilation, while parent/trait links check after
ordinary compatibility and roll back failed publication. Trait collisions retain
the effective declaration's source. Two originals plus eleven focused sources
agree at `373f804e` (361 modules);
the namespaced user attribute stays Unsupported with zero agreement. Strict
compilation and 110 genuine assertions (own 63, trait 26, rollback 21) pass at
`456ebb0b`; the source cut and four earlier compiler stops retain their identities.
The actual 361-module composition over `61e7b80ff` passes strict compilation at
`6c098ce8` (4.979 s), preserving current EX/CALLS interfaces without renewing
the private checks. [Override review](coverage/semantics/promoted-override-review.json).

One zero-argument builtin `#[Override]` on an ordinary parameter now raises the
native target Fatal in methods, functions, Closures and arrows. Name/variadic
guards and constant-default compilation precede it; type/default compatibility
follows it. Resolved spelling and surviving compiler lines are retained. Eval
preserves earlier output/notices and stops before catch, body or publication.
Sixteen originals agree across the bad18/94a/929/ba904 cuts. Strict compilation
of 361 modules and one SL gate with 109 checks (68 derived request checks,
41 reached eval checks) pass at `4f6a47d6`. Earlier line/nondeterminism
discrepancies, fixture stops and the failed state run retain zero credit. Other
parameter attributes/hooks remain required. The actual 361-module composition
over `786137a55` passes strict compilation at `f5eb9399b` (4.954 s), preserving
current runtime/owner/GC/replay paths without renewing the private checks.
[Parameter-target review](coverage/semantics/parameter-override-review.json).

Ordinary parameters accept one zero-argument builtin `#[SensitiveParameter]`.
Fixed trace slots snapshot current CVs; positional/named variadic slots retain
their original operands, with no invented omitted defaults. Real owning wrappers
are allocated before callback/retirement and shared by getters and trace rendering.
Ten originals agree at `e27ceb30c` (362 modules); the namespaced user attribute
remains explicit Unsupported with zero agreement. Strict compilation and SL112
(34 derived source checks, 78 reached lifetime checks) pass at the same cut.
The original false105 fixture and both diagnostics retain zero state credit.
Actual 365-module composition over `88ddc64c5` passes strict compilation at
`78453102d` (5.083 s), preserving current retirement, string, GEN and PROPS paths
without renewing the private checks. Mixed/repeated/argument attributes, hooks and
wider wrapper protocols remain required. [Sensitive review](coverage/semantics/sensitive-parameter-review.json).

Promoted constructor parameters also accept the single builtin SensitiveParameter.
Value/reference property writes retain ordinary semantics; trace wrappers capture
later live CVs without creating a property Override obligation. Source8 passes at
separate bf6/688 cuts, including readonly/private/trait and ordered promotion
errors. Strict 365-module compilation and SL176 (74 derived, 102 reached checks)
pass at `75c4aba82`, including authentic queued-promotion admission. Earlier
Unsupported, method-continuation failure, fixture stops, false states and diagnostics
retain zero affected credit. Actual 367-module composition over `235a74c84`
passes strict initialization at `5448b4ba` (5.214 s), preserving current owner,
GC, GEN, PROPS, CALLS and returns paths without renewing private checks.
[Sensitive promotion review](coverage/semantics/sensitive-promotion-review.json).

Direct SensitiveParameterValue construction uses ordinary ordered argument sends
and stores an owning dereferenced snapshot. Arity precedes readonly re-entry;
named arguments, array COW, getter copies and final object release retain ordinary
semantics. Seven originals, strict compilation of 367 modules and SL121 (20
constructed, 101 reached checks) pass at `a50f9bc5`. Both checked baselines retain
Unsupported with zero agreement; the earlier raw-completion fixture preparation
was corrected before execution. Actual 367-module composition over `24c1b9e4`
passes strict initialization at `0e5152643` (5.351 s), preserving current assertion
fields and sibling constructor arms without renewing private source/state checks.
Uninitialized getter, debug/property and wider wrapper protocols
remain required. [Constructor review](coverage/semantics/sensitive-value-constructor-review.json).

First-class SensitiveParameterValue `getValue(...)` callables own their receiver
and snapshot through the existing getter-closure protocol. Five originals agree
at `db70c7a5`: array COW, argument priority, computed capture/alias and clone
ownership. Strict initialization of 367 modules and separate SL76 (15 derived,
61 reached checks) pass; four real steps verify capture, getter-copy ownership
and final destructor/weak-null release. Both checked baselines retain Unsupported
with zero agreement. Actual 368-module composition over `47accb555` passes strict
initialization at `f4ca5840` (5.209 s), retaining parent owner/runtime paths and
existing getter-closure ownership without renewing private checks.
[Getter review](coverage/semantics/sensitive-value-getter-review.json).

First-class wrapper constructors retain their initialized receiver through ordered
sends, arity checks and readonly rejection. Computed capture names stay fixed;
aliases, explicit/nullsafe invocation and clones preserve ownership. Five originals
agree across `420f47247`/`9602dbc4f`. Strict compilation of 368 modules and SL129
(27 derived, 102 reached checks) pass at `a9228bdd8`: real capture/SEND/Error steps
and final releases distinguish the callable's old value from the Error's rejected
replacement; saved caller queues authenticate nested argument calls. Both original
Unsupported baselines, the initial trace mismatch and fixture AL stop retain zero
affected credit. Binding/Closure::call and wider wrapper protocols remain partial.
Actual 370-module composition over `36b0c6948` passes strict initialization at
`b39a2a2b0` (5.284 s), preserving current factory/carrier and sibling runtime paths
without renewing the private source/state checks.
[Constructor callable review](coverage/semantics/sensitive-value-constructor-callables-review.json).

One zero-argument builtin `#[AllowDynamicProperties]` on a named nonreadonly
class resolves real namespace/import scope and permits inherited dynamic slots.
Allowed writes/reference creation and unset/recreation stay silent; ordinary
classes retain first-creation deprecation. Trait/interface/readonly targets fail
before body/interface checks, using the actual declaration keyword line.
Ten originals agree at separate `2945e171`/`8c37b2c6` cuts; a namespaced user
attribute remains Unsupported with zero agreement. Strict compilation of 370
modules and SL131 (37 derived, 94 reached checks) pass at `8c37b2c6`, including
real writes, inherited links and rejection of substituted compiled-name evidence.
The earlier trait-line mismatch and both pre-main fixture stops retain zero
affected credit. Mixed/repeated/argument attributes, anonymous/enum targets and
wider attribute protocols remain required. Actual 371-module composition over
`55c9c98a9` passes strict initialization at `9f2ed249d` (5.553 s), preserving
current GC/PROPS/ARG interfaces without renewing private source/state checks.
[Dynamic-property attribute review](coverage/semantics/allow-dynamic-properties-review.json).

Exact reference returns99 avoid unchanged checked writes during verification,
acquisition and156 repeated finalizer checks. Genuine backing certificates,
selected cells and property sources survive; conversions, quiet initialization
and later ordinary writes remain checked. Sixteen of17 focused originals agree,
with private358 independent35 and13 source-reached fixtures/483 assertions passing.
Actual359 over6536a8339 passes strict SL compilation at37b08adeb (4.679s);
those source/state cuts and the original seventeenth failure retain their identities.
[Exact-return review](coverage/semantics/reference-return-exact-review.json).

Delayed reference-return TypeError now re-enters the protected exception chain
once, preserving pending-error ownership, selected catch eligibility and code
after a caught try. Ten replay originals agree at `247446c` (360 modules), including
the former `F|F|R|SHARED` mismatch; 14 source-reached current/saved fixtures pass
954 assertions.
Four preserved affected return controls and one core-only terminal weak-conversion
control agree. The 361-module composition over `5b7452edd` passes separate strict
compilation at `2c3dbf30`.
The old prediction, pre-evaluation declaration failure and Unsupported `gettype`
observer remain zero-credit at their original cuts. Physical-array owners,
active-finalizer replay,
protected temporary/NULL Notice timing and Stringable reference conversion remain
required. [Replay review](coverage/semantics/reference-return-replay-review.json).

Source-authenticated while/do/for tails now recover after caught delayed reference
rejection without repeating initialization. Break/continue depth, goto labels and
try/catch origin survive named, method and closure frames. Fourteen originals
agree at retained private361 cuts; 15 reached current/saved fixtures pass 1,102
assertions (13/973 at51eb, corrected label/direct2/129 at89e). The actual361
composition over `cf9411d` passes strict compilation at `c5579f5d` (4.878s).
Fixture elaboration and label-finder failures retain zero affected credit.
Physical-array owners, active-finalizer replay and protected temporary/NULL
Notice/Stringable paths remain required.
[Scalar replay review](coverage/semantics/reference-return-scalar-replay-review.json).

Source-authenticated CV/compiled-CONST switch tails now recover selected-case
remainder and fallthrough without repeating subject or case evaluation. Paired
END/PHASE metadata adds no payload roots or freeable owner and preserves catch
scope through current/saved frames, goto and abrupt transfer. Seven preserved
originals and 14 reached fixtures/1,339 assertions pass at retained private361
cuts; actual361 over `dd6478b` passes strict compilation at `3c06eba5` (4.880s).
The selected-catch admission failure keeps zero affected credit at its original cut. Runtime VAR/TMP
array owners, active-finalizer replay and protected NULL/186 paths remain open.
[Switch replay review](coverage/semantics/reference-return-switch-replay-review.json).

Protected reference returns now preserve the first cleanup of mutable, refcounted
switch temporaries and dense value-foreach owners. Non-owning rows retain physical
identity/cursor through current and saved frames, authenticated replacement and replay.
Capture conservatively requires at least three genuine owning edges before cleanup
and two after; aliases sharing a cell count once. Later one-owner reads remain live;
collected switch END reads nothing, while collected foreach fetch stops explicitly.
Thirteen originals pass at private362 cuts: four exact native tuples and nine deliberate
c/d=8(native) to1(spec) differences, with zero agreement for those nine. State23/1,873
and independent pending98 pass across retained cuts. Actual364 over `2c1283f04` passes
strict at `31838d5ad` (5.033s) and one genuine carrier bridge/71 assertions. Original
failures/timeouts remain zero-credit. Wider payloads, active-finalizer replay and
Stringable186 remain required. [Owner review](coverage/semantics/reference-return-retired-owner-review.json).

By-reference VALUE, bare/null and implicit-return Notices now dispatch after protected
finalizers and repeated type checks. Captured source and line survive saved handlers;
throwing handlers leave through ordinary cleanup, and replacing variable returns cancel
the old Notice. Six focused originals and one protected-unused control agree at retained
private cuts with 365 modules. Eight reached current/saved fixtures pass 722 assertions (315+407);
Actual 367-module composition over `d23ed96e6` passes strict compilation at `8d7fad70e` (5.082 s), with zero application evaluations. Stringable186
and wider owner domains remain required.
[Notice review](coverage/semantics/reference-return-notice-review.json).

Delayed rejection inside one already-active finalizer now preserves its consumed
ordinary CV reference-return cursor without retaining the discarded operand root.
Uncaught errors cross that consumed continuation once; a local catch resumes the
cleared old return, whose NULL recheck can re-enter the outer finalizer. Successful
replacement keeps the selected new alias. Three originals agree at `d12494664`;
eight source-reached current/saved fixtures pass 602 assertions (277+325).
Actual367 over `99f3432e` passes strict compilation at `5b40480dc` (5.173s, zero
application evaluations); its cut stays separate in the
[active-finalizer review](coverage/semantics/reference-return-active-finalizer-review.json).
Wider consumed VALUE/CONST/NULL and multiple-active-finalizer histories,
wider Stringable CV layouts and owner domains remain required.

One consumed string literal compiled as CONST now resumes its original interned
value after an inner delayed TypeError is caught in an already-active finalizer.
Its non-owning source cursor restores one VALUE Notice at the original return
line after the catch and finalizer tail. A fresh returned cell keeps the caller
write separate from the globals. Two exact originals agree at `bdb0f010` and
`1341b27f`; three reached current/saved fixtures pass 347 assertions at `9b98849d`.
Actual 371 over `88d7e5d4c` passes strict at `682126ff1` (5.413s, zero application evaluations).
The [consumed-literal review](coverage/semantics/reference-return-consumed-literal-review.json) keeps these cuts distinct.

Weak by-reference Stringable returns now preserve the selected live, unconstrained
aliased CV cell through callbacks. Current/saved f-local bindings authenticate that
cell while GLOBALS may rebind or disappear; conversion writes the old cell atomically.
Failed callbacks report the live selected value and chain the callback Exception.
The certificates add no roots; existing STRINGIFY_RESULT retains the cast receiver.
Thirteen exact originals agree at `010545`/368; eight reached fixtures pass 843 assertions
(95 at `34607` plus 748 at `436014`). Actual 370 over `6f096ef1` passes strict at
`cfd5f87d` (5.280s, zero application evaluations); the
[typed CV review](coverage/semantics/reference-return-typed-cv-review.json) keeps each cut separate.
Sole nonreference local CV string returns now borrow their selected cell, while
protected returns first create the real owning reference temporary. Successful
conversion releases the old receiver before raw copying into that cell, so its
destructor precedes finally; callback failure retains the object through finally
and reports its live value with the previous callback Exception. Five originals
agree at `18ab1ad5`/371; eight reached fixtures pass 871 assertions (488 at `dfb45`
plus 383 at `fbb5d0a`). Actual 371 over `3d99674e` passes strict at `cf1094`
(5.293s, zero application evaluations). The
[local CV lifetime review](coverage/semantics/reference-return-local-cv-lifetime-review.json)
keeps these cuts separate from the earlier aliased-CV evidence. Genuinely released
targets, destructor throw/reentry, real suspension and wider typed consumers remain open.

Deprecated assertion options preserve raw flags, old-value snapshots, callback
arguments and live warning/exception/bail policy after callback/retval retirement.
Per-constant protection survives namespace publication and parked handlers.
Earlier 17 accepted originals retain their cuts; parked constant at 6fcb and selected
receiver plus independent RAW-array cleanup at ca196 add three, giving 20 distinct
options originals. State 117 stays at d7; original pending state 52 plus 15 real/history
and frozen-wrapper counterexamples pass at ca196 (67 total), with strict 356 compilation.
Pending exceptions validate on the real heap; the historical target view owns none.
The [ledger](coverage/semantics/assertion-options-review.json) keeps original failures,
the Count Unsupported/foreach distinction and bailout status-only correction.
Actual 359 over dfca passes strict compilation at 14ae4, preserving current property
warning/base roots and collector/storage fields. Earlier 358/f5 compilation retains
its own cut. Wider callback/description producers and INI warning paths remain required.

Module 374 unpacks arrays into ordinary method/array and captured START buffers.
Per-pack named ordering, dereferenced value copies and nonowning completed history
survive selector/pack retirement; copied C-root buffers authenticate their genuine
outer API. Ordered unwind preserves active-pack, positional/EX(This)/named and
direct Closure versus explicit invoke cleanup. Strict356, ten exact normals at
9+1 cuts and 345 independent plus 296 author premises pass. Constant packs retain
their genuine pool owner; a distinct dynamic-pack companion proves retired history.
Initial elaboration/matching failures and pooled fixture assumptions retain zero
affected credit. Compound/lifecycle gaps and paused returns remain open.
[Start-unpack ledger](coverage/semantics/fiber-start-unpack-review.json).

Module 376 uses native Generator resumes and real Iterator callbacks for START
packs. Borrowed CVs, iterator data and retained `current()` references have
distinct owners; arguments copy after `key()`, before `next()`. Exact unpack
lines authenticate implicit calls and saved frames. The 374 quiet-unwind fix
prunes consumed owners without creating inactive release jobs. Strict359 and
thirteen exact normals at 11+1+1 cuts and 752 independent plus 308 author physical
premises pass. Source-identical cuts preserve every original assertion within
existing caps; earlier failures and timeouts retain zero affected credit.
At that cut, IteratorAggregate acquisition was Unsupported/zero agreement;
wider raw payload changes and compound selectors remained required.
Actual361 over `401bfb516` passes strict SL compilation at `a54204745`, preserving
the current ARG Stringable/static, exact-return, property and abrupt-cleanup paths;
private13/1060 source/state cuts retain their original inputs.
[Traversable ledger](coverage/semantics/fiber-start-traversable-review.json).

NaN Iterator `valid()` warnings retain the original raw retval through ordinary
handler mutation, suspension and throw. Live references reread the changed float;
copied NaN stays true. Warning wrappers preserve one authentic START pack through
retval cleanup, and thrown handlers retire raw result/data/temporary before the
unfinished buffer. Strict361 and four unchanged native-profile normals pass at
`d2852e8bf`; eight independent source-reached groups/269 physical premises pass.
The original Unsupported baseline and thrown-tail fixture failure retain zero
affected credit; selected-handler cleanup precedes exact raw/data/temp release.
Prior376 cuts are not renewed. Actual361 over `169dd2f3f` passes strict SL
compilation at `f8d591f24`; EX32 and fatal-render interactions preserve their own paths.
[NaN ledger](coverage/semantics/fiber-start-nan-review.json).

IteratorAggregate START acquisition preserves original borrowed/owning input and
distinct returned Iterator/Generator data. Real prototype/inheritance, tentative
return notices and builtin covariance are checked; raw reference/scalar/self
returns raise the native Exception and survive until authenticated unwind.
The `getIterator()` receiver is borrowed, while Generator creation adds one
receiver to its saved frame. Successful cleanup retires
inner data before temporary input. Thirteen exact normals and five native255
declaration failures pass; four explicit consumer controls have zero agreement.
The affected historical Aggregate original now agrees, with its earlier
Unsupported record preserved. Strict361 and fourteen independent source-reached
groups/425 physical premises pass at their separate cuts. Live interface-link
admission and rejected raw-return retention are corrected; original failures stay
at zero credit. At this single-acquisition cut, nested acquisition and
foreach/yield-from/ordinary-call unpack consumers remained required. Actual361 over `5ec31e145` passes strict SL at
`35d7e73f1`, preserving current promotion, reference-recheck and EX33 collector
paths; private source/state cuts retain their original inputs.
[Aggregate ledger](coverage/semantics/fiber-start-aggregate-review.json).

Recursive Aggregate START acquisition owns each returned layer, including
nonadjacent repeated identities, and retires layers inside-out before rewind.
Terminal data stays protected while a throwing retval destructor preserves the
pending Throwable through remaining layer retirement. Eleven exact normal
originals and strict361 pass privately. Literal-output/scalar-yield startup with
a pending error runs the real Generator body, then closes a frame with no owned roots
without finally; two explicit controls keep pre-yield calls and owned roots at zero
agreement. Twenty independent reached groups/544 physical premises pass, including genuine
borrowed/raw owners, retained Generator receipts and pending-error startup/close.
Original model, strict-binding and cleanup-fixture failures retain zero credit.
Actual361 over `fbc87ced3` passes strict SL at `53396820d`, preserving current
switch replay, promotion and shutdown fatal cleanup; private source/state cuts
retain their inputs. Other Aggregate consumers and broader pending Generator
startup remain required.
[Nested ledger](coverage/semantics/fiber-start-nested-aggregate-review.json).

Aggregate foreach378 acquires nested real Iterator/Generator data with borrowed
getter receivers and one raw owner per returned layer. Layers retire before
initialization; raw valid retval cleanup precedes original input retirement and
the loop body. Acquisition/layer throws prevent startup, while retval/input throws
keep exact data-before-input unwind. Persistent reference-mode CVs stay borrowed;
reference-valued inputs retain their HCELL, and reference-yielding Generators keep
ordinary live aliases. Retained foreach Generator close runs real finally throw
and Fiber suspension, with source-authenticated receipts and unique operation
ownership across saved VMs. Earlier cuts retain twenty normal sources, strict362
and the later-valid NaN Unsupported control/zero agreement. Twenty-six independent reached
groups/719 physical premises pass at separate retained cuts; genuine getter
creation readiness and one initializer cursor claim are checked. Original admission/source failures stay
zero; prior Aggregate/START evidence is not renewed. Changed original CV/reference
operands, wider byref locations and remaining Aggregate
consumers stay required. Actual366 over `c07eac043` passes strict SL at
`646095932`, preserving current retired-owner replay, sensitive trace wrappers
and assertion conversion; private source/state cuts retain their inputs.
[Foreach ledger](coverage/semantics/foreach-aggregate-review.json).

Foreach valid NaN warnings retain the raw return through ordinary handler invoke,
result and cleanup, then reread live numeric references once. Copied NaN stays
true; first-valid input retirement follows raw-result cleanup, and thrown handlers
retire raw retval before data/input. Seven new originals and the affected unchanged
late-valid original agree with preserved native tuples; strict366 passes at
`6ce4b1524`. Eighteen independent genuine-source groups/495 physical premises
pass at retained cuts, including saved-frame forgeries and exact raw retirement. Wider raw
payload changes remain explicit Unsupported; previous foreach/START evidence is
not renewed. Actual367 over `88f132db8` passes strict at `0b37a8334`,
preserving the parent reference-return Notice protocol.
[NaN ledger](coverage/semantics/foreach-valid-nan-review.json).

Actual358 over `0f28f9d62` passes strict compilation at `8b1b71064`, preserving
current physical collector, source-line, assertion and retained-method fields;
private source/state cuts retain their inputs.

Runtime assertion INI preserves raw initial/current bytes, modified/restore timing
and the live numeric mode. Quiet quantities permit nonnegative updates; changes
involving a negative mode warn before a frozen false completion on the handler's state.
At `1593cd3ca` (354 modules), strict compilation, 12 new native-profile source
tuples, 54 typed quantity/state premises and 96 authentic state premises pass.
Nested writes and original thrown identity survive; altered refusal bytes/options
are rejected. Raw output is under
`.tools/compiler-assertion-ini-368-19/.tools/{assertion-ini-gate-v1,method-runtime-9j809l_h,assertion-ini-state-v1}`.
The later bounded warning/overflow/carrier cut is recorded above; original recapture,
warned restore and authenticated Stringable-option refusal remain required. Explicit
startup transport still admits exactly `-1`/`0`/`1`.
The actual 356-module composition over `4563a5bf9` passes strict initialization
at `06409ee08` (4.471 seconds); raw output is in
`.tools/compiler-assertion-ini-current-19/.tools/assertion-ini-current-gate-v1`.
Earlier 354-module runtime cuts retain their identities.

Module 370 executes simple RAW Fiber API array C-root callbacks, including start
and constructor. RAW owns current members; frozen caches and C handlers borrow
the receiver, with separate original/copied buffers. Saved states and actual
callers authenticate parked static, nested, collector and warning continuations.
Strict 353, twelve exact normals at 6+6 cuts and 293 independent plus 241 author
reached premises pass. A narrow 296 fix admits nominal WeakReference argument/property
types and names their diagnostics. The historical promoted-parameter original, initial
compiler stop, typed-companion failure and fixture parse stop retain zero credit;
the explicit-property companion is distinct. Compound selectors, start unpacking,
broader lifecycle work remain required; paused returns stay excluded.
Constructor promotion has its separate accepted cut above.
Actual 355 over `aa8ebb4d1` passes strict compilation at `cb42ba678`, preserving
current startup/source/collector and retained-method guards; private source/state
cuts retain their inputs. [Raw-array ledger](coverage/semantics/fiber-array-core-callbacks-review.json).

Assertions368 supplies early startup `-1`/`0`/`1` selection for main/eval/include
and replay, resolved direct-call elision, pre-argument immutable descriptions,
dynamic/FCC evaluation and description validation before truth. At `02f0d61c4`
(350 modules), strict compilation, 25 exact native-profile source tuples and 64
authentic state premises pass; fresh errors have code 1 and supplied Throwables
retain identity. Independent quote7 at `45cdd2f92`, export17 at `85f098d5f` and
startup18 retain separate cuts. Raw results are under
`.tools/compiler-assertions-368-19/.tools/{method-runtime-itg9mwvs,assertion-state-v3,assertion-gate-v13,assertion-gate-v10,assertion-gate-v8,assertion-startup-v1}`;
startup rejection classification is derived from unchanged recorded streams.
Original compiler/receive failures remain preserved. Assertion options/callbacks,
Stringable descriptions and wider export/producer shapes remain
required. Combined/offline catalogue wiring is prepared; its fresh run is pending.
The actual 354-module composition over `fa0180918` passes strict initialization
at `c24807fcd` (4.370 seconds); raw output is in
`.tools/compiler-assertions-368-current-19/.tools/assertion-current-gate-v1`.
Earlier private 350-module source/state/helper cuts retain their own identities.

367 ordinary simple array START retains six exact normals and 267/160 reached
premises at their own cuts, with ordered positional/receiver/named unwind and
real start exception sites. Actual 352 over `262ab0c38` passes strict compilation
at `c757a7e25`; no earlier evidence is renewed. [Ledger](coverage/semantics/fiber-array-start-review.json).

Generator 363 handles uncaught request-finally and throwing-handler fatal cleanup.
Actual close/cache owners survive normal rendering and handler-registry mutation;
the reported exception releases after frozen emission and before bailout suppresses
later destructors. Internal C-root trace rows preserve real function arguments.
Seven exact php_error255 originals and 493 strict premises pass at separate cuts.
Normal post-report stdClass and ordinary child storage add one exact fatal original
and 161 premises, preserving real pins and excluding consumed prefixes only from
the future validation view. Earlier seven/493 cuts retain their own inputs.
The current 353-module composition over `a210cd253` passes strict compilation at
`b7b693fa3`; earlier validation retains its own inputs and current fields remain intact.
Original refusals, preparation stops and corrected trace/admission failures stay at zero.
Request C-root renderer rethrows with no current handler add three exact fatal
originals and 527 reached premises. The real receiver decrement preserves owners;
the builtin inner Throwable reports/releases before the original report and
Generator/cache/EHR carriers are abandoned. Structural future projections avoid
heap-query recursion; full admission and malformed producer rejection remain intact.
Actual 356 over `2b98ff468` passes strict compilation at `72d5f7353`;
private source/state cuts retain their own inputs.
A renderer-installed handler returning normally adds three exact fatal originals
and 611 reached premises: inner release precedes handler restoration, warning callbacks
receive Unknown/line0, and fatal reporting reads the original live cached string.
Real pins/transient Weak owners, actual-head refusal and budget replay pass.
Actual 358 over `b721887ce` passes strict compilation at `00536106a`, preserving
current source/argument/storage fields; private 3/611 retain their own inputs.
A throwing renderer-installed handler adds two exact fatal originals and 163/180
strict premises at separate cuts. Genuine EHR/renderer-return/outer-report carriers
retain prior exceptions and Generator/cache owners while the new renderer holds
three roots; frozen reporting precedes its release and reporting-zero destructor.
The release replay starts from its already authenticated bailout; all 180 premises
remain. Earlier nondeterminism, wrong renderer-owner and 120-second AL/SL timeouts
retain zero affected credit. Final 358 over `ea04fbbe4` passes strict compilation
at `ff3d3278b`, preserving named-SEND warning shapes; the earlier 2aa/646 compiler
and private source/state cuts retain their revisions. A throwing renderer warning
callback redispatches through the restored handler before warning cleanup resumes
the original empty cached fatal report. Exact source1 and strict compiler358 retain
`558e53a9c`; 220 reached SL premises retain `80be20cde`. Genuine warning/handler/report
owners and malformed source/site/line/origin rejection pass; initial binding stops
and the incorrect fixed-argument phase retain zero credit. Actual361 over `59c163ef4`
passes strict compilation at `7983c825f` (6.128 seconds), preserving current ARG/CALLS
fields; private source/state cuts retain their inputs. A ROOT/nonuser ordinary
child destructor throwing during reported-exception release, with no live handler,
emits a second fatal while retaining the unfinished release tail. The Parent pin
keeps Weak lookup null; two Leaf C claims and real Generator/cache owners survive.
Actual unreleased fatal frames retain both INSTANCE pins and nonowning retired
HANDLE jobs; borrowed history is not another carrier. Source1 retains `7d3574e75`;
549 SL premises and complete compiler361 retain `47c8c3c1c` (6.459 seconds).
Original refusal, diagnostic/binding stops, cache/retirement fixture failures and
Weak/GC admission gaps stay at zero. Final361 over `e889a1592` passes strict
compilation at `77e534575` (6.488 seconds), preserving EX34's301/372 collector
guards; this source has no collector task. Private source/state cuts retain their
inputs. A declared property ALIAS whose last local alias is unset transfers its
HCELL then Leaf through the actual release chain and emits the same second fatal.
Stable retired-cell markers and STORE evidence certify the consumed child without
owning it; Parent Weak-null and both Leaf C claims survive. Source1/compiler361
retain `c5b8de418` (6.315 seconds); 677 strict SL premises retain `4870a1a8c`.
The original Unsupported, reached discriminator and pre-evaluation bounds syntax
stop retain zero credit. Actual363 over `d54dd9fa8` passes strict compilation
and the affected 677 SL group at `a2847abb8` (compiler 6.438 seconds). Three shared
message predicates observe bytes across the parent's immutable carriers;
private source/compilerc5 and state487 retain their cuts. A declared array child's
sole owning Leaf entry transfers through genuine HARRAY retirement and emits the
same second fatal; retired contents add no array pin, GC slot or child edge.
The real shared-array control keeps its live owner and Leaf silent through the
first fatal. Source2, strict712/77 and complete compiler363 retain `5da367130`
(6.312 seconds). The original primary Unsupported and 118-premise reached
discriminator retain zero credit at `4c410b607`; the exact shared baseline is a
separate control. Actual364 over `70c5ff9fc` passes strict compilation at
`3aeb34484` (6.399 seconds). The parent's retired-owner carriers remain empty on
both sources; current frame/fatal-history fields survive. Private source2/789
retain their `5da367130` inputs. A sole reference entry retires HARRAY then HCELL
before the authentic Leaf release; stable cell markers and historical rows add
no owner, edge or GC pin. An explicit global reference instead retains the cell
and Leaf through the first fatal. Source2, strict816/113 and complete compiler364
retain `9faf09e39` (6.536 seconds). The initial helper-load stop, failed local-CV
alias control, primary Unsupported and 172-premise reached diagnostic remain zero.
Final366 over `87752f2a0` passes strict compilation at `807fa6013`
(6.471 seconds). Empty parameter attributes/plain traces add no sensitive wrapper
or owner; Aggregate/Fiber, quantity and undefined-read hooks are inactive.
Private source2/929 retain their `9faf09e39` inputs. Wider
handlers/rendering, child lifetimes, reacquisition, message warnings,
parked/escaped storage and generic terminal cleanup remain required.
Actual 351 over `7c4a13bc1` passes strict
compilation at `ba1c17c07`, preserving current schema, storage and collector/source
guards; private source/state cuts retain their own revisions.
[Ledger](coverage/semantics/generator-request-abrupt-review.json).

Module 364 converts simple Fiber API arrays to first-class Closures, including
start and constructor methods. An independent ARRAY witness freezes selected
members; the temporary bound receiver owner moves into the Closure, while static
object inputs stay nonowning after retirement. Existing consumers retain named
buffers, traces and last-RAW cleanup; duplicate conversion tasks fail admission.
Strict compilation of 349 modules, nine exact normal originals at 1+8 cuts and
261 independent plus 121 author premises pass. The live-static helper overlap is
corrected with a disjoint bound guard and a fresh ordinary-static counterexample;
the static-source failure and compiler/preparation/fixture stops retain zero
affected credit. Ordinary array-selected start, raw array C-root callbacks,
compound selectors and Fiber-start unpacking remain required.
Actual350 over `f0ab3bcaa` passes strict compilation at `3ef6eb4e9`, preserving
current collector/source/static and storage-table guards; private source/state
cuts retain their inputs, with no earlier362/358 renewal.
[Array-capture ledger](coverage/semantics/fiber-array-captures-review.json).

362 selects ordinary callable arrays with simple Fiber API method names before
argument evaluation. Frozen members survive selector retirement and REF mutation;
one bound receiver owner transfers from CONFIG to its waiting API, while static
object selectors own none. Local receipts preserve recursive argument frames,
real saved callers and constructor warning/validation order. Strict346,
thirteen exact normal originals at12+1 cuts and independent259/author206 reached
premises pass. Three required array-start/FCC/C-root Unsupported controls earn
zero agreement. The compiler stop and original static fixture failure remain
zero; the corrected fixture pins V in its genuine cleanup carrier and queued
receiver retirement. Compound selectors, Fiber-start unpacking, broader adapters
and lifecycle/library behavior remain required.
Actual348 over `b03c0d918` passes strict compilation at `e109fec8a`, preserving
current storage pins, compound/SELF, Generator and generic ownership paths;
private source/state cuts retain their inputs.
[Array-consumer ledger](coverage/semantics/fiber-array-consumers-review.json).

Module 360 closes normal request delegations, detaching real input owners before
finally while retaining independent CV owners and shared store order. Delegated
CURRENT is the physical value slot; consumed-cell history is tied to the object's
own storage stage. Nested normal handlers retain inner cache/close pins and admit
the authenticated queued outer source frame. Eight exact normals and 553 new
strict premises pass at separate cuts; malformed actual handlers remain rejected.
Composition with 346 modules over `9cacdbf51` passes strict compilation at
`4d867f6b0`, preserving current ownership/source/Fiber/collector semantics;
earlier source/state cuts retain their inputs.
Original Unsupported/failed cuts stay zero. Abrupt terminal cleanup, parked/escaped
storage and broader lifecycle work remain required.
[Ledger](coverage/semantics/generator-request-delegation-review.json).

358 selects simple Fiber API method arrays and static class-method strings
through `Closure::fromCallable`, including named and unpacked factory arguments.
Frozen members and completed factory history survive callback-array mutation,
array retirement and factory-owner retirement without new metadata roots.
Bound receivers and static object selectors keep their distinct ownership;
direct, explicit `__invoke` and C-root calls reuse the existing API protocols.
Successful waiting resume/throw traces retain their actual API callsite.
Strict342 initialization, ten exact normal originals at7+3 cuts and independent288
plus author114 reached premises pass. The original trace mismatch and two fixture
stops retain zero affected credit; native recorder preparation stopped before
launch and is separate from the accepted ten-original native cut.
The actual345 composition over `d5e07cef2` passes strict initialization, preserving
current Generator/source/property/collector and trait target-reuse guards; earlier
source/state cuts retain their inputs.
Fiber-start argument unpacking, ordinary API callable arrays, effectful compound
factory selectors and wider lifecycle/library consumers remain required.
[Fiber factory ledger](coverage/semantics/fiber-from-callable-review.json).

Direct ECHO now admits an ordinary CV dynamic callee with no arguments.
The source certificate selects INIT5 independently of call7 and ECHO5, before
operand retirement, live selection and warning demand. Undefined handlers resume
captured null; invoker/array selection and existing TMPVAR/HCELL output ownership
preserve mutation and retirement order. Dynamic and implicit-string declaration
history alternatives now have disjoint domains, allowing a returned cast to
publish a function before later eval. Nine exact originals retain seven rows at
`50f11389e`, late installation at `dc8943d37` and cast publication at `f01375e6f`,
all private354. Independent239 premises retain `dc8943d37`, with38 fresh history premises at
`f01375e6f` (277 total,193 bindings/84 checks). Actual356 over `5107cc589`
passes strict compilation with reviewed Generator/collector/scoped-method and
assertion-state compatibility. Original
baseline mismatches and nondeterministic replay failures retain zero agreement.
No module, task or owner schema is added; wider callee/argument forms remain open.
The one-positional-CV increment now preserves independent INIT5/call7/SEND-ECHO9,
selected targets across returning/throwing argument warnings, silent missing
by-reference cells and existing returned TMPVAR/HCELL output ownership. A narrow
nonowning discard source keeps SEND9 destruction distinct from ordinary body
throw7. Nine fresh exact originals retain two rows at20cd and seven at491e;
independent231 premises (153 bindings/78 checks) pass at491e/private356.
Actual358 over478710ea passes strict compilation with reviewed Fiber/collector
and storage seams. Earlier9/277 retain their cuts; wider call shapes remain open.
The named-CV increment additionally separates SEND/ECHO line9 from operand
metadata line11. Its source-selected warning shape rejects forged operand metadata
before fallback; the existing nonowning discard source preserves throwing-handlerD9.
Second-slot/default binding, unknown-name priority and independent returned
reference cells keep their runtime protocols. Eight exact originals and251 independent
premises (entry101/warning72/result78;170 bindings/81 checks) retain `db5c0f0f3`/358.
Actual358 over `2aa14083a` passes strict compilation at `a2dcb99e3` with reviewed
current seams. Prior9/231 remain unchanged; wider call shapes remain required.
[Ledger](coverage/semantics/source-echo-dynamic-cv-call-review.json).

Direct ECHO now admits one named ordinary CV argument through361's existing
certificate and owning output protocol. INIT5 precedes live SEND; known second-slot
binding uses ECHO8, while late-bound names use7. Default holes, unknown-name errors
before CV demand and fixed-null returning warnings retain their native order.
Returned TMPVAR/HCELL values survive post-SEND argument mutation. Seven exact
originals and204 independent premises (142 bindings/62 checks) retain `5baec287b`/351.
Actual354 over `1c4c8f283` passes strict compilation with reviewed current-parent
compatibility. The unchanged baseline's parent/cast lines and early destruction
retain zero agreement. No new module or owner schema is added.
[Ledger](coverage/semantics/source-echo-named-cv-call-review.json).

SOURCE365 extends361 through a shared certificate for one ordinary positional
CV argument. INIT5 precedes live SEND8; operand retirement can install the callee
or replace the CV, while returning warnings send fixed null and earlier throws
abort later work. Returned TMPVAR/HCELL values retain bytes after argument deletion;
conversion and final release use ECHO8 independently of call initialization.
Public pending/active cast admission authenticates that separate line.
Nine exact originals retain seven rows at `21fc1ae04`, eval at `3493d49bd` and the
new line discriminator at `3c9cc065f`, all private349. The two unchanged baselines
and intermediate final-destructor line mismatch retain zero affected agreement.
Independent236 premises (150 bindings/86 checks) retain three groups at `f5f4ac0c1`
and the affected result group at `3c9cc065f`. Actual351 over `760771d9d` passes
strict compilation with reviewed Generator/Fiber, trait and storage-read compatibility.
No new module or owner schema is added.
[Ledger](coverage/semantics/source-echo-cv-call-review.json).

Source361 selects first INIT for a direct ECHO of a resolved named noarg
nonbuiltin call without namespace fallback. Owned include/eval operands retire
before invocation, allowing late function installation. A returned Stringable
TMPVAR or REFERENCE keeps its original owner beside the cast pin until output;
mutable references preserve returned bytes through an old-referent destructor
exception before later referent cleanup and Throwable replacement. Borrowed CV
release stays distinct. Ten exact originals retain eight rows at `4ea22120a` and
two affected rows at `e51d0e343`, both private344;247 independent premises pass
at the latter cut. Actual349 over CALLS362 `d46556cb0` passes strict compilation
at `eb0ce479d` with reviewed ownership and source-history compatibility.
Original early-free and admission failures and the corrected
pre-call owner fixture retain zero affected credit. Wider calls and output producers
remain required. [Ledger](coverage/semantics/source-direct-call-emission-review.json).

Source357 selects INIT for a named noarg nonbuiltin key call in an ordinary
CV-base DIM, directly under ECHO or before a literal property. Owned include/eval
operands retire before the call; existing runtime keeps the base borrowed and the
returned key fixed before live lookup. Six exact originals and128 independent
premises pass at `d198116d0`/341. Actual343 over `36ccc4520` passes strict compilation
at `3bfd78e2d` with reviewed Generator storage/ordinary destructor compatibility.
Earlier source/state cuts retain their inputs; dynamic/builtin/argument/fallback
calls and wider emissions remain required.
[Ledger](coverage/semantics/source-call-key-emission-review.json).

Generator355 keeps one physical closed-storage pin through Closure/value/key/return
release. Child callbacks retain weak Generator liveness and readable RETURN;
consumed Closure/reference metadata adds no repeated owner. Existing257/303
parents retain pending Throwable priority, with sole-pin retirement before handle
reuse. Six exact normals and 784 new strict premises pass at `b62f360d7`; the two
actually affected maintained storage queues separately pass 209 at `d67773039`.
Actual342 over `dc68616a3` passes strict compilation at `f78a1a06b`;
reviewed current-parent composition preserves the separate source/state cuts.
Original failures remain zero; the earlier349 11/663 retains its own cuts. Abrupt
terminal cleanup, parked/escaped storage and nested ordinary-object RETURN reads
remain required. [Ledger](coverage/semantics/generator-storage-pin-review.json).

354 executes bound `__construct` captures directly, through explicit `__invoke`
and as Fiber C-root callbacks. Immutable receivers and real parser/warning
continuations preserve validation-before-status ordering, handler suspension and
last-RAW retirement. Known valid registered callbacks reach repeated-constructor
rejection without executing their bodies. Strict339 initialization, eleven exact
normal originals at separate cuts and independent210/author112 reached premises
pass. The original registered-builtin Unsupported failure retains zero agreement;
pre-entry names and entered constructor traces retain native frames and arguments.
The actual341 composition over `500a2cedc` passes strict initialization with
reviewed current source353, compound-string352, property-warning and generic
ownership guards; earlier source/state cuts retain their inputs. Outer unpacking,
broader callable adapters and lifecycle consumers remain required.
[Constructor-capture ledger](coverage/semantics/fiber-constructor-callables-review.json).


Source353 selects the first ordinary CV-base DIM read before ECHO or a literal
property, using the key compiler line before live base/key lookup. The affected
writable array-property receiver now separates its table; the later literal
null-property warning has an authenticated fixed-null resume. Seven exact originals
and245 independent premises retain separate private336 cuts. Actual340 over
`ea7cf0a34` passes strict compilation at `7ff6d34c3`; current ARG/GEN/Fiber/collector
interactions are independently reviewed. Original source failures, fixture stops
and the receiver frontier false/vector retain zero affected credit. Wider emission
and receiver forms remain required.
[Ledger](coverage/semantics/source-dimension-emission-review.json).

351 executes captured `start` as a Fiber C-root callback. Immutable RAW selection
and genuine outer caller chains preserve separate original/copied argument
buffers, RAW/result Closure owners and borrowed API receivers. Inner traces have
no file or line site; actual outer callsites, body exception identity and
last-callback retirement retain their native order. Strict334 initialization,
ten normal originals and independent228/author107 reached premises pass at the
recorded private cuts. The original compiler/source stops, diagnostic prefixes
and author fixture elaboration stop retain zero agreement or state-group credit.
The affected348 C-root control gains agreement only at351; outer unpacking,
constructor captures, broader adapters and lifecycle consumers remain required.
The actual338 composition over `b2fb07e1d` passes strict initialization with
reviewed Generator349, collector345, source350, trait347 and property/ownership
interactions; earlier source/state cuts retain their inputs.
[Start C-root ledger](coverage/semantics/fiber-start-core-callables-review.json).

Collector345 preserves cached callbacks across suspension and genuine reentry
within the same live physical pass. The parked VM authenticates its real suspend
and saved-frame projections; reentry binds the fresh public API without detaching
or adding an owner. One normal source and 228 independent physical premises pass
at separate cuts, including captured old/new exception priority and exact full
continuations. Both captured source variants retain 60s CLI timeouts/zero agreement;
fixture stops remain zero affected credit. Final 343 over `e1c3d4d61` compiles at
`bb74145c7`, preserving reviewed Generator storage, call-key source and eager
owner-order changes; the earlier 341 compiler cut remains separate.
Publication 344 over `2ed57ca8a` preserves the static-property change by review.
Quiescent post-pass reentry separately admits the actual parked VM and fresh
caller after collection completes, requiring no destructor tags and no retired
caller/old-slot authority. One normal source and 203 independent physical premises
pass at separate b28/95fd+9765 cuts; captured source CLI 60s timeouts retain zero
agreement. Final 345 over `4cd2eab3a` compiles at `0c23223f3`, preserving reviewed
Fiber-factory/trait additions. One obsolete maintained post-pass refusal premise
is superseded; earlier cuts are not renewed.
A new internal collection now resumes the same parked callback with null and a
real GC_WAIT caller. Frozen PLAN.SCAN preserves its old local suffix independently
of the reset global scan; UNVISITED gives no DONE credit. Residual tags remain
physical but do not seed retracing. One normal source at 9bc and 154 independent
physical premises at 0f007+9c8246 pass, including original old-error identity,
owner 2→1 and full request cleanup. Original/compact old-error CLI 60s timeouts retain
zero agreement. Final 349 over `63786460e` compiles at `f1b0dea7a`, preserving
reviewed SOURCE361, exact-state pruning graph reuse and dynamic ARG356.
Quiescent public resume/throw now scans residual physical tags in the current
global interval. A persistent mode keeps normalized callback slots under physical
authority; BIRTH owns nothing and supplies no access scope. One compact throw
source and 119 independent physical premises (66/53) pass at separate ed30 fixture
cuts, including both original full continuations and error owner 3→2. The larger
resume CLI retains its 60s timeout/zero agreement. Final 351 over `8e513981b`
compiles at `3f2ff607d`, preserving reviewed GEN363/364/TRAIT/PROPS fields.
Fresh internal entry now scans residual and new destructor tags through the real
GC_WAIT caller and physical interval. Signed accounting preserves the residual
debit: first-pass −1 plus retrace 2 returns 1 while D/E both retire. Independent
91/75 physical premises at separate 6132 fixture cuts complete both originals,
including prior-error identity; both whole CLI runs retain 60s timeouts/zero
agreement. Final 353 over `d2bba03b2` compiles at `3f2016024`.
372 now scans main-thread residual/fresh tags with a local physical interval,
leaving the cached Fiber cursor unchanged. Exact frozen slots and called flags
authenticate callbacks without adding residual D to fresh DTORS; E protects D’s
error before ordinary finally chaining. At `7e5ff7198`/354, strict compilation/init
and 93/78 independent physical premises complete both unchanged originals,
including signed count1, D/E retirement and exact new/previous identities. Final
356 over `a1c5e2626` compiles at `43e793df3`, preserving reviewed abstract-method,
typed freeing-read, raw Fiber-array tasks and ASSERTIONS additions. Both whole
CLI 60s timeouts retain zero agreement.
375 now detaches an internally suspended residual callback and starts a real
replacement worker on the remaining physical suffix. The old guard pin and
finally error stay in its actual saved VM; replacement pending is separate, and
fresh-plan progress is unchanged until callbacks finish. Independent 92/105
physical premises at separate `be1099c26` fixture cuts, finalized as `7e72ff341`,
complete both unchanged originals, including count0 followed by later count1,
distinct old/new errors and old-worker termination. Both whole CLI 60s timeouts
retain zero agreement; the first error-state 120s cap retains zero affected credit.
Final 357 over `b7419cbe1` compiles at `9ce39cd54`, preserving current assertions,
private-constructor, storage, source and Generator cleanup changes.
Last-cache-owner physical replacement now closes the actual suspended worker
before starting its replacement. Normal close runs finally; failed close moves
the real error into plan pending while the caller's outer error stays in FINALLY.
Only the actual normal/failed private-control release tail gains storage/scoped
admission. Independent 77/89 physical premises at separate `4227d8609` fixture
cuts, finalized as `292b27847`, complete both unchanged originals, count1/weak
retirement and exact new/previous identities. Both whole CLI 60s timeouts retain
zero agreement; the first failed-state root-order premise has zero affected credit.
Final 358 over `0059e0a9e` compiles at `0da2cdae7`, preserving both empty-PACKS API
constructors and reviewed inherited-constructor/quiet-read behavior.
Old public callbacks can now suspend again during internal takeover. Detachment
captures the reset global cursor's advanced suffix, preserving earlier marked
targets without DONE credit and keeping the two real FINALLY errors separate.
At separate `88daee39b` fixture cuts, finalized as `27e65e46e`, 114/98 independent
physical premises complete both unchanged originals. The affected error fixture
now checks request-final retirement of the new error; its obsolete lookup has
zero affected credit. Both whole CLI 60s timeouts retain zero agreement. Final
358 over `6ed4873bd` compiles at `0bc957892`, preserving reviewed Generator render
and dynamic-source hooks.
Different-main public reentry345 now authenticates the actual parked VM/fresh API
while preserving fresh main tags after the old target slot is reused. Old guard
INDEX equals the global cursor; the completed local scan must be INDEX+1, so a
rewind cannot consume the fresh E callback. Independent normal96 at `93cb1cfd5`
and throw109 at `950c158d5` complete both unchanged originals with exact error
identity, heap-identical forgeries and budget replay. Actual359 over `0c549de11`
passes strict compilation/init at `280feeb2a`, preserving GEN176/363 and the
PROPS207/377 warning and ownership interfaces. The printable-metadata helper is the concrete
changed cost dependency for the one throw-only retry; no general speedup is inferred.
The initial undefined-helper compiler stop, first throw-state 120s timeout and
both whole CLI 60s timeouts retain zero affected/agreement credit. Overlap, wider
active residual/Fiber-pass reentry, earlier whole CLI completion and broader GC
remain required; earlier cuts are unchanged.

During a live main callback, public resume/throw of the idle worker now scans
snapshot-marked residual targets outside the fresh plan's DTORS. The authentic
main return, physical cursor and tags govern admission without changing fresh
plan progress. Two native-grounded unset-order companions pass whole CLI60 and
174 independent physical premises (95/79) at `c5a3e54df`, preserving count1 and
exact replacement/prior exception identity. Actual361 over `9988f88bf` passes
strict compilation/init at `5d89edb95`; reviewed Traversable, Generator and
computed-static paths preserve this lane. Four earlier native observations and
the first failed diagnostic remain preserved; corrected41 only localizes refusal.
[Ledger](coverage/semantics/cycle-collection-review.json).

Residual/eligible overlap301 now admits a closed white ordinary-object component
on main PASS0. Physical nested removal clears D's old tag before fresh E runs; the
single retrace calls D, frees E and leaves D's self-cycle/weak probe live, with
signed count -1+1=0. The exact current RETURN pin authenticates preselection SITE
before CALLED; executable return and future-tag/cursor checks retain authority.
One unchanged whole CLI60 source and 247 independent premises (165/82) pass at
`85b9d0b73`. Baseline38 and image110 localize distinct boundaries; earlier compiler,
source/133 and obsolete79 fixture failures retain zero aggregate credit.
Black-root/array/reference/proxy/Fiber overlap and wider GC remain required.
Actual361 over `8ac503030` passes strict compilation/init at `d77cd6d9a`, with
independently reviewed call, ownership and scalar-return interfaces; earlier
source/state cuts are unchanged.

Mixed overlap301/372 now permits separate ordinary residual components outside
the eligible graph, with an incoming-owner closure and surviving-tag authority.
In the grounded original, nested removal drops D's tag while F survives for selection
before E; signed -2+2 returns0, F/E retire and D retains its self-owner/weak liveness.
Source1 and 321 independent premises (215/106) pass at `a2ef8b039`; role-bound
physical slots preserve exact removal, cached-W reuse, retrace order and replay.
Baseline66 localizes the old301 refusal. The first195 ordering fixture fails with
zero aggregate credit; corrected controls change no code/source. Broader
black/external/nonordinary/Fiber/later-pass overlap remains required; prior cuts
and whole CLI timeouts are unchanged.
Actual361 over `be0cfaa7f` passes strict compilation/init at `9391ce28e`, preserving
reviewed call/ownership/property interfaces; source1/state321 retain their inputs.

Closed white ordinary-object overlap317 now runs on a genuine ordinary Fiber
through its distinct idle cached worker when every residual tag is removed.
Exact nested images, saved caller/API and real guards preserve physical cursor,
ordinal and CALLED authority. Source1 agrees under CLI60 at `e3d359d01`; five
source-reached cuts155/134/172/54/130 cover all408 original obligations
(645 executed premises include repeated setup), with count0, E retirement and
D self-owner/weak-live. Pure lookup/source-site factors preserve all validators.
Earlier compiler stops, source failures and timeouts retain zero credit;
nonordinary/later-pass overlap and wider GC remain required.
Actual367 over `6e709da74` passes compiler/init at `020f95d30`; reviewed carrier,
fatal, reference-return and promotion interfaces preserve the unchanged e3 cuts.
[Ledger](coverage/semantics/cycle-collection-review.json).

Mixed ordinary-Fiber overlap301/345 now scans surviving physical tags after
nested removal through the actual U caller and cached worker W. Exact initial BUFFER/FREE,
surviving F/E tags and the selected physical guard retain authority without adding
F to fresh DTORS/progress. Three independent source-reached cuts 147/95/118 at
`fb872a74e` execute 360 premises: F→E→D, signed -2+2=0, F/E retirement, D self-owner 1
and weak-live, request cleanup and replay. Compiler/init pass; baseline 97 and
projection 66 localize ingress and first selection. The first 146-premise fixture clears an
owner-bearing caller and fails with zero credit; its corrected LINE-only forgery
preserves the heap. The whole source CLI60 timeout remains OPEN with zero source
agreement, and only that source is excluded from the default whole-CLI campaign.
Wider overlap/throw/reentry, nonordinary/non-idle and later-pass lanes remain required;
prior cuts are unchanged. Actual370 over `71cf292aa` passes compiler/init at
`aecdcb088`; reviewed typed-return, caller and retained-root interfaces preserve
the fb872 cuts and whole-source CLI60 OPEN/zero agreement limit.
[Ledger](coverage/semantics/cycle-collection-review.json).

Array-mediated overlap301 now permits nonproxy HARRAY alongside HOBJECT in the
fresh closed-white component, retaining the object-only residual-reach fence.
Three source-reached cuts 118/107/corrected104 at `f184ac959` execute 329 premises:
real ordinary-Fiber E→array→D, nested D/array removal with debit4, exact E guard,
signed -1+2=1, E/array retirement, D self-owner1/weak-live and terminal replay.
Native grounding and compiler/init pass; baseline91 localizes the old301 refusal.
The first104 fixture expects a marked E after real selection normalized it and
fails with zero credit; its separate correction changes no code/source.
Whole source37 CLI60 remains OPEN/zero agreement and only that source is newly
excluded from the default whole-CLI campaign; all three state groups remain enabled.
Main/mixed array layouts, references/proxy tables, black/external components,
non-idle caches and later-pass overlap remain required; prior cuts are unchanged.
Actual371 over `d80c97b3c` passes compiler/init at `9233da4ca`; reviewed local-CV
return, property/caller and captured-constructor interfaces preserve state329 at
f184 and the whole-source CLI60 OPEN/zero agreement limit.
[Ledger](coverage/semantics/cycle-collection-review.json).

Reference-mediated overlap301 transparently follows genuine unbuffered HCELL
edges without reference debit. Fresh-component reach, live reference markers and
canonical frozen cell shapes preserve count/image and current worker authority;
residual reach remains object-only. Three source-reached cuts corrected159/130/118
at `b5fc0476e` execute 407 premises: direct/duplicate reference walks, real E guard
and marker/shape counterfeits, signed -1+2=1, E/array/reference retirement,
D self-owner1/weak-live, request cleanup and replay. Native grounding and compiler/init
pass; baseline101 localizes the old refusal. The original159 stops on literal-record
syntax before semantic checks with zero credit; its separate correction is syntax only.
Whole source38 CLI60 remains OPEN/zero agreement; only its default whole-CLI
selection is newly excluded, with all state groups enabled. Broader reference,
main/mixed, proxy/black/external and later-pass overlap remain required; prior cuts
are unchanged. Actual371 over `8ea50de70` passes compiler/init at `711bedcfd`;
reviewed shared compiler/property/return interfaces preserve state407 at b5fc and
the whole-source CLI60 OPEN/zero agreement limit.
[Ledger](coverage/semantics/cycle-collection-review.json).

Source350 admits array-valued ordinary computed-name CVs. Its nonowning warning
resume fixes `Array` before live target lookup; handler/child exceptions abort FETCH.
Seven exact originals and117 independent premises retain `c2a1051db`/331. Actual335
over `94e3593e6` passes strict compilation at `4832f2226` with reviewed current-parent
compatibility. The fixture elaboration stop has zero application/acceptance credit.
[Ledger](coverage/semantics/source-array-name-review.json).

348 executes bound `start` first-class captures directly and through explicit
`__invoke`. Immutable receiver selection and original positional/named buffers
survive argument effects, nested same-Closure calls, weak callback receives and
cleanup. Waiting calls borrow the receiver from the Closure; explicit invocation
keeps its extra Closure owner and copied buffer. Status and entry errors retain
actual start callsites. Strict329 initialization, ten normal originals and
independent186/author96 reached premises pass at the recorded private cuts.
Two C-root-start/outer-unpack controls and the separate original `is_int` builtin
dependency failure have zero agreement. That builtin remains required core work;
a distinct fresh comparison original checks the same weak int receive.
At348, C-root `start`, constructor captures and broader adapters remained open.
The actual333 composition over `05ef7bb9f` passes strict initialization with
reviewed Generator/property/Throwable/ownership interactions; earlier source and
state cuts retain their inputs.
[Start-capture ledger](coverage/semantics/fiber-start-callables-review.json).

Source343 adds Stringable ordinary computed-name CVs with a separate cast owner.
Returned bytes survive receiver retirement before live target lookup; a pending
destructor exception permits the default missing-target warning but suppresses
an eligible registered handler. Eight exact originals and134 independent premises
retain private `fdb6e4577`/325. Actual329 over `fe9ad60a9d` passes strict compilation
at `890496dec`, with reviewed callable/trait/collector compatibility. Original
fixture failures and diagnostic cuts retain zero affected credit.
[Ledger](coverage/semantics/source-stringable-name-review.json).

341 executes fixed bound API captures as Fiber C-root callbacks. Immutable RAW
selection preserves the receiver, borrowed API ownership and genuine nested or
idle collector caller chains. Last callback retirement can close its receiver
before the original `start` argument destructor; C-root API traces have no file
or line. Strict324 initialization, ten new normal originals plus one affected337
former boundary, independent255 and author93 reached premises pass at separate
recorded cuts. The narrow saved-root helper correction is covered by full-drive
nested108 and collector93 checks; original failures retain zero credit.
The actual328 composition over `175a197e9` passes strict initialization while
preserving current collector342, method307, source339 and ownership factors;
earlier source/state cuts retain their inputs.
At341, C-root `start`, constructor captures and broader adapters remained open;
paused undefined-result verification is excluded. Earlier331/337 cuts are unchanged.
[C-root ledger](coverage/semantics/fiber-bound-core-callables-review.json).

Collector342 admits public idle resume/throw during an active pass once every
planned destructor is marked called. The real parked collector consumer remains
busy; worker cache/mask and transient error ownership follow332. Two exact normal
originals and two independent strict-SL groups with127/138 physical premises pass
at private323. Final327 over `5f478ea6a` passes combined compilation at `f9dbe3205`,
preserving337/339/307/334 and the pointwise302 factor. Module345 separately handles
remaining-dtor stale intervals; these earlier cuts are unchanged.
[Ledger](coverage/semantics/cycle-collection-review.json).

Source339 adds the missing ordinary name-CV warning before computed FETCH.
Returning handlers change the live caller CV used for conversion; absent/unset
CVs quietly become null, while a later missing-target warning keeps fixed null.
Seven exact originals and171 independent premises pass at private `bf7bcb3da`/321,
including local/global isolation, fallback, throw priority and authentic include
retirement/FETCH6. The actual324 composition over `6b51f811c` passes strict
compilation at `e3d6a7c85` with reviewed bound-Fiber/Generator/collector/array
compatibility. Original fixture failures and diagnostic vectors retain zero
affected credit. [Ledger](coverage/semantics/source-missing-name-cv-review.json).

337 adds bound first-class `resume`/`throw`/defined `getReturn` and status methods.
The Closure owns its selected Fiber; direct and explicit `__invoke` calls borrow
that receiver while retaining their actual argument buffers and saved operation
provenance. Strict318 initialization, nine normal originals and author65/independent403
reached premises pass at the recorded private cuts. Two explicit start/C-root
Unsupported controls earn zero agreement at that cut; earlier331 evidence is unchanged. A
separate actual322 composition passes strict initialization, one collector
original and115 independent premises: captured public resume/throw authenticate
the genuine saved caller, preserve borrowed receiver roots and retire the idle
cache on request completion. The
[bound-callable ledger](coverage/semantics/fiber-bound-api-callables-review.json)
retains these checks and required follow-ons.

Collector338 admits failed last-owner close of a detached worker after collection.
A throwing `finally` retires the one remaining private control owner while the
real error stays in the caller's pending operation; a genuine prior exception
keeps its identity. Two exact normal originals and two independent strict-SL
groups with117/130 physical premises pass at separate private320 cuts. The
322-module composition over `f89fbee745` passes combined compilation at
`9277e334d`, preserving Generator328, source336 and reviewed ownership factors.
Publication over `0bb453754` preserves the disjoint prior-array foreach guards;
the tested compiler/source/state cuts remain unchanged.
Active-pass failed close and wider close contexts remain required; earlier
collector cuts retain their inputs. [Ledger](coverage/semantics/cycle-collection-review.json).

Generator 340 closes paused frames at normal request end through real reverse
globals and ascending store handles. Registered normal handlers run before cache
release; borrowed zero-owner buckets survive bare store decrements until genuine
weak reacquisition restores ordinary release. 19 normal originals and 692 physical
strict-SL premises retain separate private cuts; 85 premises assert required abrupt
controls with zero observation agreement. Actual330 over `7a0f8044f` passes strict
compilation at `1399d8a7e`, preserving source343, bound C-root and collector342
behavior without renewing source/state cuts. The original observer mismatch stays
zero credit. Delegating request close and wider terminal/free-storage paths
remain required. [Scope and cuts](coverage/semantics/generator-request-finally-review.json).

Generator349 closes fresh store frames without entering body/finally, releases
actual parameter/receiver owners, and transfers the single Closure owner.
Root CV-destructor handlers precede later parameter release; closed storage
releases the Closure before caches. Ten distinct normal originals and 584 strict-SL
premises retain separate cuts and original failures. The composition with 337 modules
over `ed1c8c6a2` passes strict compilation at `5dc524df4`; its fresh typed-slot
interaction adds one exact normal source and 79 strict premises. A real free-storage
pin, late WeakReference notification and readable caches during child destructors remain
required. [Bounded evidence](coverage/semantics/generator-fresh-store-review.json).

Generator328 reference caches, value snapshots and effective destructuring aliases
retain their original source/state cuts and actual321 compiler. 340 promotes the
identical active-finally original; its old refusal40 remains zero agreement.
[Reference-yield scope](docs/semantics/GENERATOR-REFERENCE-YIELDS.md).

Source336 adds one named ordinary CV argument to computed-name emission: INIT6
precedes known FETCH8/property11, and unknown `Sent` binds Error7 before CV demand.
Six exact originals and325 independent premises retain private317. The final320
composition over `89c1019cc` passes strict compilation at `29f5f402b` with reviewed
331/324/335 compatibility. The original deferred-operand fixture false and diagnostic
earn zero affected credit. [Ledger](coverage/semantics/source-named-argument-emission-review.json).

Collector335 admits normal last-owner close of a detached worker after collection.
Assigning null to its shared cell runs `finally` immediately; the worker retires
and its borrowed zero-owner target waits for the next real collection/count1.
Two exact normal originals and two independent strict-SL groups with100/116
physical premises pass at the private317 cut. The final319 composition over
`6fac6d270` preserves static Fiber331 and property324 fields/tasks/owners and
passes combined compilation at `e12be6f67`. Failed-finally close338 has separate cuts;
earlier collector cuts keep their inputs. [Ledger](coverage/semantics/cycle-collection-review.json).

331 adds source-authenticated static `getCurrent`/`suspend` first-class Closures
with receiver-free capture, alias/clone history and distinct direct, `__invoke`
and Fiber C-root owners through resume/throw cleanup. Independent sources and
reached-state guards retain their private cuts. The actual317 composition over
`e91fc6d6` passes strict compilation; newer collector/source/GC guards remain
intact. [Scope and retained cuts](coverage/semantics/fiber-static-api-callables-review.json).

Collector332 adds quiescent public resume/throw into the cached collector Fiber.
Its real caller transfer preserves the worker mask and idle cache without a
stored exception or supplied-value worker owner. Strict compilation/initialization
and three exact source controls pass at `084aebce1`; two explicit strict-SL groups
with169 premises pass separately at `0649fd604`. The final315 composition over
`79546523e` passes combined compilation at `f3d62ee7b` without renewing earlier
cuts. Module342 separately admits active transfer after destructor exhaustion;
remaining-dtor transfer stays Unsupported. Complete GC and the fresh
combined offline rebuild remain required.

Collector325 retains a detached zero-owner target and its outgoing graph through
a borrowed buffer tag, without adding an owner. Real weak reacquisition restores
ordinary last-owner release and parent retirement before child destruction.
Three exact originals and85 reached premises pass at separate private cuts.
An actual305-parent unowned-close original collects the target in the same active
pass;117 reached premises validate its real two-owner private-control retirement
and saved caller VM. The narrow scoped admission repair passes changed compilation.
The final309 join over callable Fibers322 passes its sole combined compiler
at `b4cfe4a14`; earlier source/state cuts retain their identities.
[Scope and retained cuts](docs/semantics/CYCLE-COLLECTION.md).

Integrated321 copies a known YIELD value before an ordinary missing
key-CV warning, authenticates one object-specific partial-cache carrier and keeps
null key/index/opcode-line behavior through callbacks. Actual child-resume markers
select child catch/finally reinjection for KEY and311 VALUE warnings; direct API
resumers preserve closed-cache ownership. A narrow303 release-only handoff moves
cached destructor owners once and preserves replacement exception priority.
Strict compiler295,27 exact normal observations and eight genuine reached groups
with658 physical premises pass at their separate c102/7edf cuts. Actual
`642659405`/304 composition passes strict compiler305 at `309c9b25f`, preserving
accepted receive/source/ARG319/collector fields. Independent seam review requires
no source/state renewal. Original failures and the older required close Unsupported
retain zero credit.
[Scope and results](docs/semantics/YIELD-KEY-WARNINGS.md).

Arrow Generator311 is integrated; its frozen310/276 cut retains44 normal source
agreements, nine compiler rejections and10 genuine strict-SL groups with987
setup-inclusive premises retain separate cuts; two required Unsupported controls
earn zero agreement. Eager receives, deferred captures, implicit sent/delegated
returns and original signatures use accepted280/95/118. Value warnings freeze
null before delayed keys; throwing handlers install the closed Closure owner
before eager frame retirement. The frozen286 parent is privately composed
with exact311 and maintained fixtures at287 modules. One fresh original combines
an eager NEW default, active Fiber, temporary Stringable eval CV ECHO entry and
last-owner child close. Its scoped source/Fiber validator repair passes strict
compiler287, one native/model agreement and148 independent reached premises;
earlier cuts retain their identities. Exact311 also composes over the actual
`2a2e1af7c` property/collection parent at292: strict compilation, the same original
and75 independent source-HANDLE/Arrow-close/gc/clone premises pass without
renewing148. Final294 preserves accepted ARG309/316 and passes strict compilation;
their introduced seams are independently reviewed as compatible, with no source/state
renewal. Earlier cuts retain their own tested parents.
[Scope and retained cuts](docs/semantics/ARROW-GENERATORS.md).

The current source includes accepted ArrayAccess292/304/309/319/326/329, eager destruction270,
WeakReference296, ordinary cycle collection301 and collector Fibers317/325/332/335/338/342/345,
Fiber291/302/308/313/322/341, Generator289/303/310/311/321/328/340 and source operands293/298,
plus instance/readonly properties288/294, clone300/305 with cached maker selection
and ordinary dynamic-property creation318, physical references324 and defaults286/295/306/312,
with 336 modules composed over
`6e107993a`, retaining static/bound Fiber API captures331/337/341/348, property references324/346, Generator344 and collector335/338/342/345.
The ordered integration preserves
the final Generator eager-release bridge, Fiber cleanup guards and source-emission314/316/320/323/327/330/333/336/339/343/350.
The property/clone composition passes strict SL290/compiler application0 at
f6b2cad34, two new exact normal originals and79 independent strict-SL premises at
4767e8ea6. Transfer onto68393 retains the same semantic inputs. Earlier private
cuts below retain their original inputs.
The preceding 284-module cut passes strict compilation, one exact source original and
49 reached premises during active nested Generator delegation. Earlier accepted
cuts retain their original inputs. Accepted290/297/299 add composing-owner REAL
births, dead failure receipts and fatal trait class-name reservation. Their actual313
join passes strict compilation and one fresh REAL/constructor/capture-retirement
source with46 supplied reached conditions; earlier cuts retain their identities.
Nonconstant source-emission314 is installed after Fiber308; literal auto-global316
is integrated after reviewed current-parent composition.
Held 279 and user-paused return verification stay set aside. Complete core and the
final combined, fresh offline rebuild remain required.

Default composition adds286/295/306/312 over actual canonical296,
preserving ARG309/316, property, clone, GC301 and shared source hooks (300 modules).
Exact `279839ac4` passes strict initialization and one fresh native/public original:
two default warning frontiers retain GLOBALS snapshots and storage/readback,
with exact `ArrayArrayg:g:l2:A:B` in29.546s at unchanged45/55 caps. Its omitted-request
Unsupported remains zero; the corrected gate uses matched explicit CLI facts.
Raw records are under `.tools/compiler-defaults-publication-18/.tools/defaults-publication/compact-gate-v{1,2}`.
The genuine current107 prefix/source-origin/refusal/retirement predicates pass
on `b50d4062e` in33.911s; their original request parse and nat-cast elaboration
stops keep zero runtime credit (`compact-controls-v{1,2,3}` in the same directory).
The later812 terminal-seek harness correction changes no tested semantic input.
The final301 join over `ff1b7a888` preserves accepted property warnings318 and
passes strict initialization on `3b6a92f2f` in3.769s. Independent review found no
introduced runtime overlap; earlier source/state cuts retain their own inputs.
Current296 eval31/saved42 plus persistent wrong-id/valid/replay controls and
Stringable/Fiber chdir with73 owner/log/marker predicates keep their distinct cuts.
Earlier old290/v5 Generator/Fiber default227 remain accepted; new231 remain UNRUN.
The full retry original still times out at host55 with zero agreement. A bounded
trace completes throw/catch/new receive/bind before GC:293 completed GC transitions
take27.843s versus294 execution steps5.491s. The separate39 compute-once candidate
preserves pruning guards and partiality and passes strict301 initialization plus
GC42/Generator47/Fiber34 lifecycle predicates on `1060496af1`. Inputs stay stable
and all groups are reaped; raw records are under
`.tools/compiler-defaults-pruning-18/.tools/pruning-current-v1`.
Its unchanged full retry again times out at host55 with empty streams and zero
agreement. No speedup, whole-retry agreement or offline rebuild is claimed.
The actual305 join preserves collector317 and Generator321 and passes strict
initialization on `ad5acdc4d` in3.821s; earlier lifecycle/source cuts stay distinct.
The current301 diagnostic measures297 completed GC bodies27.988s, with pruning
alone26.283s (93.9%), then times out at host55 with zero agreement.
The private retained-node factor passes strict305 initialization, GC42/GEN63/Fiber34
and one parent-child WeakReference original on `67fa589eb`; exact public output
`P:live|C:null|N|END` completes in9.078s. Its full retry still times out at host55
with empty streams and zero agreement; this adds no demonstrated speedup.
The separate destructor preparation/waiting factor passes strict305 initialization,
110 source-reached/controlled branch and original-state fallback predicates plus
GEN63 on `5559f2c00`; the WeakReference original again agrees in9.078s. The selected
RHS Unmatch fallback is statically preserved. Its full retry still times out at
host55.066 with empty streams and zero agreement. The maintained
`destruction_prune_protocol.py` reproduces the corrected110 fixture; its original
relation-premise elaboration stop earns no runtime credit.
Both factors now join actual `bf1c0053a`/309, preserving current325/322/326/327
root and caller hooks. Strict initialization passes on `13bc4e931` in3.769s.
The earlier139/173/WeakReference cuts retain their own inputs; no source renewal
or speedup is claimed.
The nonempty zero-owner scan now computes its unchanged GC keep list once.
Private `7d0ed7543`/309 passes strict initialization, processed-DONE43 and
active-bare75 direct keep/retirement predicates, and the exact WeakReference
original in9.279s. Empty-scan and Unmatch/Runtime domains are statically reviewed.
Its full retry still times out at55.046 with empty streams and zero agreement;
inputs are stable and groups reaped, with no demonstrated speedup or231 credit.
The actual314 join preserves TRAIT290/297/299, CV330 and ARG329 handoff fields;
strict initialization passes on `1a148ff63` in3.871s. The309 cuts stay distinct.
The separate release-walk keep reuse passes strict314, DONE44/ACTIVE77 direct
walk predicates and the WeakReference original on `cd2f2a355`; its full retry
still hits55.065 with empty streams and zero agreement. Empty/HANDLE and fallback
domains are statically preserved, with no demonstrated speedup or231 credit.
The actual316 join retains332/333 roots/source fields and passes strict
initialization on `1e95f04a8` in3.870s; earlier314 runtime cuts stay distinct.
The per-node zero-scan factor binds each owner count once in the unchanged heap.
Private `8bbe41e3d`/316 passes strict initialization, DONE44/ACTIVE77, independent
35 graph premises and the exact WeakReference original in9.175s. The graph
fixture's initial parse stop keeps zero runtime credit. The full 1697-byte retry
still hits55.065 with empty streams and zero agreement; inputs stay stable and
groups are reaped. No speedup or231 credit follows. Raw records are under
`.tools/compiler-gc-zero-owners-18/.tools/gc-zero-owners-gate-v1/run-v{1,2}`.
The actual335-parent319 composition passes strict initialization on `3e56ab759`
in4.019s; earlier316 runtime cuts retain their identities.
Private `2582d7008`/319 partitions edge targets before source-membership scans,
passing strict initialization and 48 graph premises. Both factors compose over
SOURCE336/320 by static review. Actual `c38af3cf7`/320 full retry still hits 55.065
with empty streams and zero agreement; inputs stay stable and groups are reaped.
No speedup or 231 credit is claimed. Raw checks/retry stay under
`.tools/compiler-edge-owners-19/.tools/edge-owner-gate-v1` and
`.tools/compiler-gc-zero-owners-current-parent-19/.tools/full-default-retry-edge-v1`.
A zero-credit `c38af3cf7`/320 diagnostic identifies Fiber protection as the main
completed pruning cost. Module 302 now builds its graph at the first object and
reuses it within the unchanged state, preserving lazy empty/nonobject prefixes,
eager scan order and Unmatch fallbacks. Exact `181931c20`/321 passes strict
initialization, 22 controlled partiality premises and 65 source-reached
protected-result/lifecycle premises. Its original
full retry still times out at 55.066 with empty streams and zero agreement.
The first compiler stop and two malformed Runtime expectations (actual false)
remain preserved; Runtime propagation and eager evaluation of later nodes remain
statically reviewed.
Composition over `b7ed1bea1`/326 preserves SOURCE339, TRAIT307 and ARG334
by static review, without runtime renewal.
Raw records: `.tools/compiler-fiber-protection-graph-19/.tools`
(`fiber-protection-gate-v{1,2,3,4}` and `full-default-retry-protection-v1`).
Pruning now carries its graph through GC selection, Fiber protection and
destructor dispatch, retaining active and idle bare-root guards. Destructor
preparation reuses the graph only for identical states; changed states take the
original prepared-state path. Exact `74a8a11ca`/326 passes strict initialization
and 41 independent fixture premises. Its first destructor78 check exposed an existing
207 ordinary-handler/destructor validation overlap. The one-line fallback repair
at `039abc623`/326 passes changed initialization and four fixtures with 78 destructor,
69 protected Fiber, 40 active GC and 37 ordinary-handler domain premises.
The original full source still times out at host 55.066 with empty streams and
zero agreement; inputs are stable and groups reaped. No speedup or 231 credit follows.
Final 330-module composition at `5ca56cf55` mirrors the new idle retired-bucket guard
and passes changed initialization plus a genuine retirement fixture with 73 body /
190 physical premises. Earlier 326 cuts stay separate. Raw failures and checks remain
under `.tools/compiler-fiber-protection-current-19/.tools` (`prune-graph-controls-v{1,2,3}`
and `full-default-retry-prune-graph-v1`) and `.tools/compiler-prune-graph-publication-19/.tools/prune-graph-gen330-controls-v1`.
Known-current graph reuse now covers keep, zero and release scans, avoiding
rebuilding the graph inside bare/retired retention. Exact `c09806280`/330 passes
strict initialization, 52 independent premises and reached DONE51, bare62,
destructor82 and retired193 physical premises (38/50/76 body premises for
DONE/bare/retired). Public modified-graph helpers and changed-preparation paths
stay intact. Raw checks: `.tools/compiler-prune-graph-publication-19/.tools/prune-graph-keep-controls-v1`.
Final 334-module composition at `989e6bb09` passes changed initialization in
4.222s; its earlier 330 fixture identities stay separate. Raw final check:
`.tools/compiler-prune-keep-current-19/.tools/prune-keep-current-controls-v1`.
The unchanged 1697-byte original on `94e3593e6`/334 matches native output, while
the public model still reaches host55.045 with empty streams and zero agreement.
Inputs stay stable and the group is reaped; no speedup or 231 credit follows.
Raw retry: `.tools/compiler-prune-keep-current-19/.tools/full-default-retry-graph-keep-v1/run-v1`.
Module302 skips total graph owner scans only after evaluating a false close
predicate, retaining per-node fallback and eager recursive tail. Exact `7b02a1d39`/334
passes changed initialization, 44 independent physical/43 main helper premises
and a genuine suspended-ready Fiber frontier with 54 physical/41 main premises.
True branches are typed helper controls only; the source frontier proves false.
Raw checks: `.tools/compiler-fiber-blocked-scan-19/.tools/fiber-blocked-controls-v1`.
Final 336-module composition at `3f19f2278` passes changed initialization in4.122s.
Raw final check: `.tools/compiler-fiber-blocked-current-19/.tools/fiber-blocked-current-controls-v1`.
Its standalone original retry remains UNRUN; the combined result follows below.
Module301's removed-owner consumer now reads the same observed state's edges
after its first roots call, preserving owner order and fallback. Exact `c0cbdd69b`/336
passes initialization, 51 typed physical/44 main and 56 reached physical/39 main
premises, with explicit admission of the changed branch. Raw checks:
`.tools/compiler-gc-transition-edges-19/.tools/gc-observed-edges-controls-v1`.
Final 339-module composition at `a164f0f9e` passes changed initialization in4.171s.
Raw final check: `.tools/compiler-gc-transition-edges-current-19/.tools/gc-observed-edges-current-controls-v1`.
One combined302/301 original retry at `ea7cf0a34`/339 still reaches host55.045625
with empty streams and zero agreement. Inputs stay stable and the group is reaped;
no speedup or231 credit follows. Raw retry:
`.tools/compiler-gc-transition-edges-current-19/.tools/full-default-retry-gc-observed-edges-v1/run-v1`.
Module270's eager-slot consumer now reads same-state allocation edges after
its first roots call, preserving owner/live-slot/property-pending order and fallback.
Exact `6f16a3f11`/339 passes initialization, 68 typed physical/54 main premises
and a genuine main UNSET frontier with 52 physical/32 main premises, explicitly
admitting a nonempty CV-cell release. Raw checks:
`.tools/compiler-eager-observed-edges-19/.tools/eager-observed-edges-controls-v1`.
Final 340-module composition at `6c1a89b38` passes changed initialization in 4.270s.
Raw final check: `.tools/compiler-eager-observed-edges-current-19/.tools/eager-observed-edges-current-controls-v1`.
The `500a2cedc`/340 original retry matches native output but the public model
still reaches host 55.045470 with empty streams and zero agreement; inputs stay
stable and the group is reaped, with no speedup or 231 credit. Raw retry:
`.tools/compiler-eager-observed-edges-current-19/.tools/full-default-retry-eager-observed-edges-v1/run-v1`.
The driver now carries the successfully evaluated original-state eager owner
order into the following GC. Exact `8c889199c`/340 passes initialization, 66 typed
physical/52 main and 102 reached physical/82 main premises. The real empty-slot
STMT and later nonempty UNSET have an authenticated origin-entry step between them.
The declaration stop and original 98-premise task-assumption failure remain preserved failures.
Raw checks: `.tools/compiler-owner-order-carry-19/.tools/owner-order-carry-controls-v{1,2,3}`.
Final 343-module composition at `4a96bad9a` passes changed initialization in 4.320s.
Raw final check: `.tools/compiler-owner-order-carry-current-19/.tools/owner-order-carry-current-controls-v1`.
The `e1c3d4d61`/343 original retry matches native output but reaches host 55.043267
with empty streams and zero agreement. Inputs stay stable and the group is reaped;
no speedup or 231 credit follows. Raw retry:
`.tools/compiler-owner-order-carry-current-19/.tools/full-default-retry-owner-order-carry-v1/run-v1`.
Pure graph pruning now counts distinct node identities, root/edge multiplicities
and removes zero-owner cascades through a worklist. Final filtering preserves
roots and original node/edge order and duplicates, including arbitrary finite typed
graphs with dead sources or absent targets. Exact `a39876cbe`/343 passes strict
initialization in 4.273s, independent 54 physical/33 main premises comparing 512
graph variants in 4.472s, and 54 reached physical/44 main premises in 4.973s.
The real post-UNSET cell/object cascade requires successive old pruning rounds
and matches the new graph and public pruning results. Raw checks:
`.tools/compiler-heap-prune-worklist-19/.tools/heap-prune-worklist-controls-v1`.
Final 345-module composition at `8ed6d5bcb` passes changed initialization in 4.272s.
Raw final check: `.tools/compiler-heap-prune-worklist-current-19/.tools/heap-prune-worklist-current-controls-v1`.
The `9cacdbf51`/345 original retry matches native output but reaches host 55.044761
with empty streams and zero agreement; inputs stay stable and the group is reaped.
Raw retry: `.tools/compiler-heap-prune-worklist-current-19/.tools/full-default-retry-heap-prune-worklist-v1/run-v1`.
One current-public-path hook diagnostic reaches normal active-Fiber execution
with output through `H1|H2|X|H3|same:same:` before host 55.046281. Completed outer
allocation-edge calls total 17.202s; `heap_prune` totals 1.025s. These nested
observations include hook overhead and establish no speedup or source agreement.
Raw diagnostic: `.tools/compiler-heap-prune-worklist-current-19/.tools/current-public-phase-v1`.
GC now reuses pruning's already-built edges only when the full prepared/pruned
states are equal; changed states recompute, preserving owner/root order and fallback.
Exact `738d2a3b1`/345 passes initialization and 60 typed physical/47 main premises
in 4.222s each, plus 65 reached physical/57 main premises in 4.971s. The latter
admits real unchanged STMT GC and changed raw post-UNSET pruning. Its initial
blank-separator parse stop remains preserved, with zero runtime credit.
Raw checks: `.tools/compiler-pruned-edges-19/.tools/pruned-edges-controls-v{1,2}`.
Final 349-module composition at `9b69ebb2e` passes changed initialization in 4.323s.
Raw final check: `.tools/compiler-pruned-edges-current-19/.tools/pruned-edges-current-controls-v1`.
The exact 1697-byte original at `ea58ac361`/349 now agrees with native PHP in
54.832s at unchanged 45/55-second caps: normal, exit 0, exact 46-byte output and
empty stderr, with stable inputs and reaped groups. Earlier timeouts stay preserved.
Raw retry: `.tools/compiler-pruned-edges-current-19/.tools/full-default-retry-pruned-edges-v1/run-v1`.
The source and tuple are retained in `compiler_composed_retry_cases.json`, wired
through the existing runner into combined and offline checks; those runs remain pending.

Ordinary collection301 preserves potential-root order, discarded-temporary
decrements, parked handle authority, weak retirement, destructor guards and
frozen per-pass counts. Its original30/606 and private285-parent3/45 retain their
recorded cuts. The actual286-parent composition passes strict compilation and
initialization, one exact captured-source retirement original and66 independent
strict-SL premises for genuine child6/main26 context, guard ownership, forged
plans/consumers and live-state resumption. The larger nested-Generator original
retains its90s timeout with zero agreement. Actual290-parent composition passes
strict291 compilation/initialization and one new exact readonly self-clone/GC
original: both real cycles are weakly observable until two destructors/count2,
then both retire and a second collection returns0. The
[ledger](coverage/semantics/cycle-collection-review.json) retains each distinct
cut. Module 317 adds the actual collector-Fiber cache,
global parked collection, detached target/pending guards, replacement batches,
source-less traces/scope and callbackless idle retirement. Thirteen exact normals
and two strict-SL groups with 78/68 premises pass at separate cuts with 292 modules.
The actual318 parent passes strict298 compilation/initialization and one fresh
reporting-Fiber/handler original, preserving global busy0 through nested callbacks,
mask restoration and real count1/weak retirement. The final304 additive join
preserves newer default-receive, Get/reference and literal-this source schemas
and passes the required combined compiler without source/state renewal.
The fresh explicit-INI source discriminates
cached mask reuse. The two larger 60s model timeouts retain zero agreement.
Module325 adds separately tested detached zero-owner retention, real reacquisition
and active unowned-close retirement. Wider internal graphs, callback reentry during
a different active pass, internal takeover, automatic thresholds, resurrection and final
request freeing remain required.

Undefined source operands293 resume genuine warnings with fixed null after
handler writes, preserving direct empty-path errors and earlier computed-name
fetch timing. Borrowed/captured Stringable sources298 keep converted bytes and
real owners through cast destruction, compiler notices and parser/provider work.
Separate reviewed cuts cover compiler fast returns, delayed error-API checkpoints,
empty/once/failed helper results and authentic child/main retirement traces.
[Undefined](coverage/semantics/source-undefined-review.json),
[lifetime](coverage/semantics/source-stringable-review.json),
[ordering](coverage/semantics/source-stringable-ordering-review.json),
[helper](coverage/semantics/source-stringable-helper-review.json) and
[retirement](coverage/semantics/source-stringable-retirement-review.json) ledgers
preserve every original cut and failure. The separate
[first-work extension](coverage/semantics/source-stringable-first-work-review.json)
adds constant ECHO and assignment to a literal variable name opcode lines: three original
source agreements and 46 reached entry premises retain their accepted private cut.
[Nonconstant emission314](coverage/semantics/source-expression-emission-review.json) adds ordinary CV ECHO, literal property FETCH and no-argument named-call INIT lines. Its private277 source3/entry57/guards72 retain their original inputs and two zero-credit fixture stops. Actual286 passes strict compilation, one fresh nested-Generator captured-source original and independent70 entry/retirement/public/heap/image premises. The relocated maintained case prepares70 with zero applications. Broader producers, first emissions, checkpoints and providers remain required.
The [composition ledger](coverage/semantics/include-source-composition-review.json)
records genuine child line5/main keyword21, retained captured input after alias
clearing, the saved Generator caller and public/heap owner/suffix controls. The
maintained relocated fixture prepares 49 premises with zero runtime applications.

[Auto-global emission316](coverage/semantics/source-autoglobal-emission-review.json)
selects literal FETCH_R5 before ECHO or property6. Its isolated278 cut passes
strict compilation, two exact explicit-request originals, independent79 MAIN
entry/first-destructor/source/image premises, computed-name11 and new maintained72
classification premises. The omitted-request Unsupported, request-literal fixture
stop and copied Generator-owner false fixture retain zero accepted credit.
A separate cc397-parent291 join passes strict compilation, one genuine readonly
clone-owned include original and independent64 entry/first-destructor premises,
including maker-site and receiver-line counterexamples. Its two maintained
relocations gain no refreshed execution credit. The actual292-parent join passes
strict293 initialization, the same exact original and independent47 source/GC/public
premises, including a heap-identical forged NOGC receipt. Earlier cuts retain
their own inputs; wider emissions remain required.

[Literal GLOBALS emission320](coverage/semantics/source-globals-emission-review.json)
is integrated: FETCH5 precedes later direct Array Warning5 or property-on-array
Warning6; parenthesized entry retains FETCH6/property8 and snapshot timing.
Private294 source4/67 premises retain their inputs. Actual296 passes strict
compilation with reviewed Arrow/Fiber compatibility and no renewed source/state
credit. Relocations add no execution credit; broader first emissions remain required.

[Literal this emission323](coverage/semantics/source-this-emission-review.json)
is integrated: FETCH5 precedes child work or the later
missing-instance Error5, while a method include retains its receiver/private scope.
Private297 retains four exact originals,70 independent premises and9 affected guard
checks; the initial INSTANCE fixture false has zero accepted credit. Actual303
passes strict compilation with reviewed property/default/argument compatibility.
Relocations and the actual join add no source/state credit; broader emissions remain required.

[Computed-name emission327](coverage/semantics/source-computed-emission-review.json)
is integrated: an owned operand retires at INIT6 before
the resolved no-argument helper and later FETCH6/property8 execute. Three exact originals
retain their first cut; the corrected missing-name original passes separately.
The new warning producer resumes with null after handler writes, with188 independent
entry/admission/pending-handler premises. Original Unsupported and two fixture
stops retain zero affected credit. Actual307 passes strict compilation with reviewed
collector/Generator/ArrayAccess compatibility; broader names remain required.

[CV-computed name emission330](coverage/semantics/source-cv-name-emission-review.json)
is integrated: compiling the ordinary name CV emits no opcode,
and outer FETCH6 precedes property8 after operand retirement. Four exact originals
show the live name changes before lookup; a missing target resumes null after handler
name/target writes. Genuine entry/warning/identity controls pass174 premises.
Actual310 passes strict compilation with reviewed Fiber/collector/constructor compatibility.
Earlier cuts and relocations gain no renewed credit; broader names remain required.

[One-argument computed-name emission333](coverage/semantics/source-call-argument-emission-review.json)
is integrated: operand retirement uses INIT6 before argument lookup,
and outer FETCH7 precedes property10. Five exact originals and275 independent
entry/warning/identity/admission premises retain live CV reads and handler writes
with fixed-null argument/target resumes. The parser stop and incorrect CODEARG
origin mismatch have zero affected credit. Actual316 passes strict compilation
with reviewed trait/ArrayAccess/collector compatibility; earlier noarg/CV cuts
and relocations gain no renewed credit.

Generator289 now delegates arrays, source Iterators and shared/nested Generators,
preserving raw caches, input forwarding, actual callback demand and return transfer.
The accepted private52 normal/four compiler agreements and618 reached premises,
plus the distinct actual274 source/87-premise cut, retain their original inputs.
Canonical integration preserves newer ArrayAccess/Fiber/call fields; introduced
composition checks pass with303/310. IteratorAggregate, wider reference-yield forms and
wider lifecycle/API behavior remain required. [Scope and retained evidence](docs/semantics/GENERATOR-DELEGATION.md).

Generator303 now runs ordinary last-owner finalizers, releasing delegation links
before finally and retaining authentic frame, scope, cursor and cached owners
through ordered storage cleanup. Its private 40 normal/two compiler agreements
and 569 reached premises across eight programs/eleven groups retain separate
original cuts. Canonical integration preserves the installed eager-destruction
and Fiber clauses. The actual eager-release bridge retains pending exceptions
and remaining slots through authentic closing-frame restoration. Request-end,
terminal, GC and user-destructor paths remain required.
[Scope and retained evidence](docs/semantics/GENERATOR-FORCE-CLOSE.md).

Generator310 permits ordinary paused-Generator last-owner close inside an active
Fiber, preserving current identity, parked callers and genuine frame/cache owners.
Its accepted private 26 normal sources and eight strict-SL programs/groups with
669 reached physical premises retain their original cuts; four precise required
Unsupported controls earn zero agreement. The actual282 composition passes a
strict compiler cut, five distinct new normal sources, two promoted close sources
and one precise request-end control. One new strict-SL program/group passes189
reached premises for pending frame release, remaining owners, the previous chain
and live-state budget resumption. Private cuts retain their original identities;
the two source discrepancies and stale fixture elaboration failure retain zero
credit in the existing ledger. Parked running Generators, switching
finalizers, request/terminal cleanup, GC and general user destructors remain open.
[Scope and retained evidence](docs/semantics/GENERATOR-FIBER-CLOSE.md).

Integrated module 308 extends force-close of captured cleanup
after an actual callback return: private previous ownership, source-less deprecation, restored reporting
and shared handler registration. With its captured producer payload unchanged,
a nonowning protected pair rejects another older Throwable substituted as the child. The fixed 277 module cut passes AL,
fourteen distinct normal source comparisons and two precise Unsupported controls
with zero agreement. Three authored groups/227 conditions and eleven independent
groups/860 conditions pass, along with two affected existing schema groups.
Composition over the integrated 291/302 parent `9dd9ca8b3` passes strict-SL 280
initialization, one exact defined-result original and two reached strict-SL
groups/113 premises. The final GEN/include parent `ed7f23c67` composition passes
strict-SL 285 initialization, the same exact original and two groups/113 premises
on tested transfer `68b9ec4c4`. Earlier cuts retain their own evidence.
The original verbose-source timeout retains zero agreement. CALLS308's dynamic
property warning retains Unsupported at its original cut; no result is renewed.
Undefined-result engine verification remains held.

Ordinary eager destruction270 releases consumed slots in native order, retaining
pending owners through callbacks, throws and resurrection. MAIN preserves source
permission and catch/trace behavior; used results, borrowed CV receivers and
cold/warm property RHS temporaries retain their native lifetimes. Handler returns
and the original Throwable release before handler restoration and queue entry;
fatal diagnostics freeze before release, while bailout retains real VM and C
owners. Author62 and independent60 exact sources, nineteen reached cases/1,012
assertions and the separate fatal/actual-parent cuts retain their recorded inputs
in the [ledger](coverage/semantics/eager-destructors-review.json). The actual Array
warning/cleanup original now agrees and rejects a forged source-marker suffix.
The [contract](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md) keeps compound
Stringable reception, GC, wider weak protocols, output buffers
and later freeing open. Actual 292/304 composition passes strict-SL initialization
and one new exact returned-object lifetime source at276, with stable inputs;
earlier cuts gain no renewed execution credit. The separately reviewed shared
cleanup bridge authenticates helper producers in the saved caller and binds the
internal destructor frame site. One strict-SL reached277 cut passes19 physical
premises for authentic entry, a heap-identical site/line forgery and zero/one-step
resumption; the oversized62/41 cuts timed out and remain unconfirmed.

WeakReference296 memoizes allocated wrappers using nonowning immutable semantic
target IDs. `get` copies a live target into a genuine strong result; destructor
resurrection stays live, while actual free clears weak lookup before child
retirement. Forbidden direct NEW preserves genuine pre-argument candidates and
validated parked stacks. Twenty-one exact originals and nine reached cuts/344
physical premises retain their private275 inputs in the
[ledger](coverage/semantics/weak-reference-review.json); five Unsupported controls
earn zero agreement. The [contract](docs/semantics/WEAK-REFERENCES.md) keeps
pending-carrier unwind, deferred construction, wider consumers, GC and WeakMap
open. Actual292/304/270 composition passes strict277 initialization and one new
exact weak lifetime original, with stable inputs and separate recorded cuts.

ArrayAccess304 reconstructs intermediate `[]` after ordinary by-value Get and
supports final compound append, including null-key Get/Set on returned children.
Returned temporary arrays extract selected rows before retirement; copied real
cells detach or remain shared according to their actual owners. False-conversion
throws preserve the same-opcode append/write/operator priority, conversion
checkpoints, callback eligibility and complete previous chain. Dimension records
require a real key expression, keeping `[]` distinct from `[null]` at public
admission. Forty-nine normal sources agree across retained cuts; eight genuine
strict-SL recipes with 723 premises pass. One fresh interaction at
actual 38f + accepted 292 + 304 / 275 agrees through include conversion,
private Owner/Child selection, GLOBALS
reference rebinding and a retained-cell append. The
[append ledger](coverage/semantics/arrayaccess-append-review.json) keeps cuts and
original failures separate. Final simple returned-child append309 is installed;
its private276 and actual278 cuts remain independently accepted. The current287 composition keeps
the canonical Generator/Fiber/source fields; clean718b passes full compilation,
one new exact Fiber Set/paused-Generator finalizer original and64 strict-SL
premises. The actual291 bridge overcc397 keeps PROP call/cleanup schemas and
also matches the same original;64 retains its287 cut. Independent review accepts
these separate gates. Canonical292 over2a2 preserves HANDLE/TEMP/NOGC
and301 and passes full compilation plus one new exact cyclic-child original:
Set collects an unrelated cycle, readback returns old CELL25 after global
rebinding to31, and later collection frees the returned child/count1.
The [returned-child ledger](coverage/semantics/arrayaccess-returned-append-review.json)
preserves eight sources/160 premises, separate lifetime/provider/compiler/warning
cuts and zero-credit original failures. Wider producers, remaining reference-Get consumers and
complete core remain open; paused return verification stays separate.

ArrayAccess319 adds accepted untyped/mixed by-reference Get: implicit
callbacks demand their real result, R/IS dereference it, writable shared cells
stay shared, and a genuine sole wrapper moves before receiver release. Direct
DIM_OP owns the raw reference through Set without retaining its old referent.
Final nested reference acquisition and borrowed Unset source prefixes preserve
parent release and callback retirement. Fourteen normal originals agree across
explicit cuts; six strict-SL recipes/375 premises cover demand, wrapper move,
sharing, raw compound/throw cleanup, captured rows and retired-parent Unset.
The [reference-Get ledger](coverage/semantics/arrayaccess-reference-get-review.json)
keeps source, reached, compiler and original failures separate. Actual298 over
ff1b passes full compilation, strict initialization and one new exact original:
a genuine Fiber reporting warning handler suspends inside Get, then resumes
the shared property CELL write while restoring main reporting. Parent318 fields
are preserved; this source makes no dynamic-property runtime claim. Final302
over b135 preserves new default receive fields and passes full algorithmic and
structuring compilation. Module326 adds named sends and nested captured-row
updates below;329 adds VALUE-return Notice callbacks. Wider producers remain required;
typed non-mixed return verification stays user-paused.

Integrated ArrayAccess326 admits captured live ELEMENT rows for named reference
sends and nested pre/post updates. Exact source/writer/RHS/temp guards preserve
name-check priority and existing finishing dispatch. Six new exact normal
originals and three genuine strict-SL groups/246 premises cover named promotion,
duplicate rejection before promotion, copy/shared-cell behavior and resumption.
The [consumer ledger](coverage/semantics/arrayaccess-reference-consumers-review.json)
keeps this303 cut separate. Final306 over `40e3c4fcc` passes full algorithmic
and structuring compilation at `46c624e89`; independent seam review requires no
source/state renewal. Module329 adds VALUE-return Notice callbacks below;
wider Get behavior remains open. Typed non-mixed
return verification stays user-paused.

ArrayAccess329 stages the RETURN_REF_VALUE Notice for genuine untyped/mixed
reference Get. The computed operand survives ordinary handler return, throw or
Fiber suspension without a pre-Notice cell write or saved referent owner. Throw
materialization bypasses Get's inner catch, retains the real RV through local
release, then transfers its owner after the caller's access owner so the receiver
retires before the returned value. Nine new exact normal originals and four
genuine strict-SL groups/401 premises pass at `13e29b78d`/307. The
[producer ledger](coverage/semantics/arrayaccess-reference-value-review.json)
preserves both compiler-only failures and the corrected native rebind forecast.
Final314 over `2a2f69a71` passes full algorithmic/structuring compilation at
`e87987ebc`, preserving current trait, constructor and pruning fields. The
earlier307 source/reached cut remains separate. Finally-sensitive Notice ingress,
bare/fall-through NULL, handler exit and wider producers remain open; typed
non-mixed return verification stays user-paused.

ArrayAccess334 stages real Get, left Stringable conversion, live RHS conversion
and Set while retaining the raw RV/CELL and each genuine cast/key/base owner.
An initially defined key unset by a conversion retains its absent C-call slot:
required and variadic Set reject before entry, while scalar and NEW defaults use
real receives and argument introspection. Twenty-three normal originals agree
across `1a9577fbc`, `e24bc593f`, `44e1bf990` and `e79ff62bd`; three compiler
rejections pass separately at `1a659fe82`. The
[compound ledger](coverage/semantics/arrayaccess-stringable-compound-review.json)
keeps 341 earlier and 248 missing-key reached premises at their separate cuts.
The composition of 325 modules over SOURCE339 `3691db3dd` passes full
algorithmic/structuring compilation and six strict initialization checks at
`7a7dd4faf`, without source/state renewal.
The final composition of 326 modules over TRAIT307 `55c2eab0c` preserves its
TYPE/default/FCC source guards by independent pointwise review; the 325-module
compiler cut remains separate.
The ordinary helper-base compiler repair preserves special builtin temporary
rejection. The deferred Generator Get control at this334 cut remains zero-credit;
module344 below records the later repair. Bare/fall-through NULL, finally-sensitive
Notice ingress and wider
producers remain open; non-mixed typed return verification remains user-paused.

ArrayAccess344 creates mixed/untyped implicit Generator Get results without
starting their body, including reference-yield declarations. A nonowning
TARGET/SITE/LINE certificate preserves exact Get scope after its emitter returns;
actual frames and received arguments retain every heap owner. Ordinary last-owner
close reaches the real caller carrier through an authenticated finished marker,
including destructor replacement of a pending finally exception. Seven maintained
normal originals pass across `dc27aa3e1`, `09ec7db36` and `3ff67878e`; the unchanged
334 Unsupported original has a separate new positive cut. Full327 compilation and
six initialization premises pass at `09ec7db36`. Independent423 reached premises
pass at `4e3062ac4`; actual331 algo/struct and initialization over `d811717a0`
pass separately at `f2d3c6d29`, with reviewed request/name/graph-carry interactions.
No earlier334 evidence is renewed.
Typed non-mixed producers and the other paused return lanes remain unchanged.

ArrayAccess292 now handles ordinary by-value compound Get/operator/Set and
writable Get temporaries through nested W/RW/Unset, pre/post updates and by-value
reference consumers. Defined key/RHS CVs remain live across compound Get;
computed RHS precedes queued Get/Notice and delayed CV demand follows Notice.
Returning arrays preserve real-cell edges while ordinary copies stay detached;
returned objects skip Notice, and thrown Notice suppresses later work. Direct compound Get throws
retain the replacement Error's opcode line and original previous chain. The
exposed276 direct GLOBALS reference finish preserves selected names/global
routing/owners;249 direct Unset admission now excludes255 nested paths.
Thirty-four distinct normal sources agree across retained cuts. Author 223 and
independent 793 premises pass across 13 recipes (1016 total), with 634 in AL and
382 in strict SL.
The [writable ledger](coverage/semantics/arrayaccess-write-review.json) records
actual revision/diffs, original failures and excluded count-observer0; its
core-language companion agrees. Remaining reference-Get consumers,
wider memoized/property/GLOBALS producers and combined interface notice ordering
remain required. Paused return validation remains separate. One fresh source at
actual 38f + 292 / 274 agrees through array-include conversion287, private
Owner/Child warning selection and live GLOBALS RHS rebinding; algorithmic,
structuring and loader checks pass. The original missing-provider input failure
retains zero agreement.
Private multiple-frontier defaults312 retain genuine handler/eval cuts for each
source effect, exact intermediate read prefixes, partial FCC-cache retry and
nested warming. Eight exact normals pass across retained cold v1 and seven v3
sources; native seven preliminary plus minimized warm v3 preserve exact tuples.
Strict277 at v2 and all eight genuine state groups/761 premises at v3 pass.
The two original warm host55 timeouts and actual all-true bind diagnostic retain
zero agreement credit. Catalogue133 preserves prior125. Current306 dispatch
delegates only its old two-frontier boundary to312; archival data stays unchanged.
The [ledger](coverage/semantics/deferred-static-defaults-review.json) records cuts.
Independent review accepts the bounded milestone; canonical integration is pending.
No actor or canonical writer is held.
Parked Fibers, object/null-key/outside-eval and wider producers remain required.

Private parameter alias causality306 preserves callback reads, retries, nested
reentry and captured deprecated values through dense nonowning receive births
and source-derived parent/frontier/eval cuts. Ten exact normal originals pass
across v9/v10. Strict SL276, all15 genuine state groups/1170 premises and the
37-check reporting interface pass on distinct cuts: prefix134 at v10, five555
at v11 and nine481 at v13. At that cut five controls rejected multiemitter,
parked Fiber, object/null-key and outside-eval routes with zero native agreement;
312 above supplies the bounded multiemitter paths. Catalogue125 preserves prior115.
The [ledger](coverage/semantics/deferred-static-defaults-review.json) retains
original failures, runtime identities and concise recovery. Independent review
accepts this bounded increment; canonical integration is pending. No numeric
actor or writer lease is held.

Private parameter aliases295 preserve borrowed global/cached class-constant
Closure identity, statics and donor body permission without adding owners.
Direct mixed-array defaults and selected compiled ternaries now have genuine
source/state witnesses. Eight normal originals and640 reached checks over14
originals pass on the dirty d39d cut:367 AL plus273 strict SL at identical120s
caps. Six historical effectful/object boundaries rejected explicitly and earned
zero native agreement. The unchanged private42 passes SL after its retained AL timeout.
[The ledger](coverage/semantics/deferred-static-defaults-review.json) binds actual
module/runtime hashes and distinct failed/corrected cuts. Global alias admission
is bounded to callback-free initializers and quiet values/facts. The306 slice
above adds bounded effectful read/registration causality;312 adds bounded multiple
emitters. Suspended Fibers and wider producers remain open. Historical
catalogue115 and protocol sources retain exact native bytes. Canonical
integration is pending.

Private parameter callable defaults286 allocate fresh static/no-use Closures and
fixed FCCs from genuine deferred `NParam` receives. REAL scope follows the
receiving lexical class; physical FCC targets stay cached while called classes
remain fresh. Immutable nonowning unscoped evidence survives maker retirement;
plain clones retain earlier permission without acquiring receipts. Nine normal
and two compiler originals pass at0f90; two new originals and one affected replay
pass atd39d. Earlier mixed342 and affected/new162 state premises retain distinct
cuts, including retired rebound-maker and coherent wrapper-erasure controls.
The separate actual285 Closure-body autoload source passes atd39d: private
constructor access rejects before nested argument effects. All274 production
modules pass the public SL path. The [ledger](coverage/semantics/deferred-static-defaults-review.json)
preserves original failures and the wider producer obligations beyond295.
Independent review accepts these gates; Canonical integration is pending.

The integrated dynamic/FCC clone maker follow-on was validated from frozen305
commit367e581df. Live clone calls capture the selected name before arguments;
cached makers retain only their own site, selected name or immutable intrinsic
Closure identity. An immediate genuine callback marker admits computed selectors;
the source-selection alternatives remain disjoint. Nonowning consumer birth keys
distinguish later activations through real Fiber identity, shutdown position and
autoload candidate identity.
Independent autoload bucket and selected-call stamps survive registry movement
and removal, including retained declaration history. Scoped autoload callbacks
use their retained producer source rather than replaying ordinary invocation.
Independent review, production SL277/application0, 20 distinct lifetime/manual,
pipe, argument mutation, autoload and shutdown originals, and 665 clauses across
seven reached-state groups pass at recorded cuts; three affected source repeats
are separate. Maintained builders recreate nine checked programs with exact
accepted clause/prefix parity; preparation adds no model credit. Coherent
pending-candidate identity rewrites remain an admission boundary. The
[selection ledger](coverage/semantics/readonly-clone-selection-review.json)
preserves original failures, scoped repairs and regeneration commands.
Accepted305 semantic inputs and all earlier cuts remain unchanged. Its directly
affected private shutdown companion now agrees exactly at367e581df and is
published at a2cab39d0. Its preserved CALLS308 warning original retains its
historical Unsupported cut with zero agreement.

Ordinary dynamic-property creation318 now resumes eligible callbacks for literal
simple assignments. The real warning owner protects the destination, then its
retirement decision survives destructor resurrection. Late plain CVs, old
reference payloads and owned RHS temporaries retain distinct behavior; same-key
reentry appends physical buckets with latest lookup and ordered value foreach.
Unused results release before receiver cleanup, while used results retain a copy.
Fifteen private exact normals retain separate cuts; initial 297, changed 498 and
cleanup 98 reached premises are not one campaign. The 297-module composition at
`078ecb2f8` passes strict initialization, one new exact GC/resurrection source and 69/98
GC/cleanup premises. At that cut, four explicit Unsupported boundaries cover handler exit,
duplicate casts/reference foreach and expired or undefined RHS pointers.
Computed names, wider writes and full-family closure remain required. The
[review](coverage/semantics/dynamic-property-warning-review.json) retains original
failures, commands and cuts; no historical clone campaign is renewed.

Physical duplicate-property reference foreach324 now selects and promotes the
actual bucket, preserving latest named access and declared readonly/type checks.
Staged own-destructor previous-CV cleanup keeps its raw value readable while live,
masks its released edge and installs the selected reference before normal/throw continuation. The
real shared receiver cell survives unset/recreate and follows alias writes, table
replacement and object/array/scalar dispatch; late scalar warnings retain that
owner until normal or abrupt iterator removal. Initial12 normals and288 reached
premises retain their earlier cuts. The shared-receiver extension has12 additional
exact normals at separate cuts, strict SL298 initialization and491 affected
premises at87f9b399a. The actual318 join at `f643ed070` passes strict
initialization and 92 fresh GC/saved-COMMIT premises; one separately tested
original collects during the previous CV destructor with exact normal output.
The331 schema/FCC seam is independently reviewed; earlier cuts keep their inputs.
HOBJECT-owner forgeries fail public reference-foreach admission. Previous plain-CV
array retirement now stages ordinary child destructors in physical order,
including nested arrays and continuation after
a child throws. Six new exact normals at `ccafc5d65` and 139/145 reached premises
at fixture-corrected `368bed28a` cover surviving array/reference owners, selected
property mutation/deletion and B/previous=A exception chaining; strict318 initialization
and the actual321 join at `be7edc9e2` pass. Ordinary prior-CV objects without their
own destructor now release dynamic children before declared children. Four exact
originals and 152/161 reached premises at `531145bb4` cover shared owners, retired
OLD masking and atomic binding with B/previous=A. At `95899634d`, strict initialization
and 19 fresh guard premises pass; two native observations retain explicit Unsupported
and zero agreement for direct/nested retiring typed sources at that cut.
Module346 now keeps each typed source until its actual declared-slot release visit,
including parked Fiber queues, without retaining the retired parent. Six normal
originals at `77a17756c`, 151 reached premises at `cc326bf43` and 84 Fiber premises
at `7573d02bb` retain separate cuts. They cover declaration order, two sources on
one cell, pending exception chaining, exact detach ownership and resumed scoped
Throwable validation against the actual live heap. The actual332 join at
`108d07bb5` passes strict initialization. Private Generator-close queues now
retain the same per-slot constraints without retaining the retired parent. Four
exact normal originals and strict332 initialization pass at `5b26e3526`; 134/71
reached premises at `edf7e7ec1` cover exact detach, ordinary cell-release transfer,
pending A/B chains and genuine parked/restored Fiber ownership. The actual336
join at `0d233dde9` passes strict initialization; earlier behavioral cuts remain
separate. Borrowed plan snapshots and duplicate queues provide no authority.
Last-owner previous reference wrappers now retire on the actual eager cleanup
queue. A separate nonowning raw CV preserves safe own-destructor reads while the
original wrapper reaches zero owners; normal/throw binding installs the selected
reference atomically. Five exact originals pass at `329ec8e38`; independent
native-first observations retain `f84fdab9d`. At `d3688fdf9`, 136/139 reached
premises cover genuine wrapper release, masked raw storage, pending A/B chaining
and refusal of whole `$GLOBALS` snapshots or expired borrowed-reference reads.
Shared wrappers and surviving payloads decline this staged path. Earlier source,
compiler and state cuts remain separate. The actual341 join over `6848742a2`
passes strict initialization at `ecd8e8745`.
Ordinary INSTANCE free_obj now retains one physical parent pin while visiting
property slots in release order; this supersedes immediate physical retirement
in the ordinary descendant path. WeakReference is already null during children,
while safe class metadata remains readable. Five exact originals pass at
`56b323d89`; separate Weak/get repairs pass affected2 at `99e3902c6`, and physical
GC-slot occupancy passes affected1 plus strict346 at `d91ef1ea4`. Three fresh
groups pass 164/57/67 premises at that latter cut, covering exact typed detach,
A/B chaining, actual355 RETURN-child ownership and genuine parked Fiber pins.
Adapted earlier ordinary fixtures carry no new credit; direct private303 physical
storage pins and wider raw-payload/escape behavior remain required.
The 347-module join over `cd7d74529` passes strict initialization and one exact
Iterator-child original at `5916e0e0b`. Its 113 shared premises at `9d007c3d4`
preserve live Weak-result ownership of 2 and future-tail ownership of 1 after genuine
destructor-result discard; added owners still reject queued close. The original
shared failure/timeouts remain uncredited; prior359/360 campaigns are unchanged.
Ordinary stdClass storage now uses the physical parent pin. Materialized tables
transfer one HARRAY edge before real bucket cleanup; shared-table children survive
parent retirement. Five exact originals pass at `c7e984676`; the disjoint dynamic
tombstone validator repair passes affected2 and strict347 at `f064fd2c6`.
New reached groups pass150/91/51 premises at `f064fd2c6`/`56d3b070b`/`2282b68da`,
covering table ownership, B-before-A throws, early Weak and actual355 RETURN storage.
Original baseline/fixture failures retain zero credit; prior campaigns are unchanged.
The actual349 join over `013ca6d2b` passes strict initialization at `e7e74c6c9`.
Unvisited initialized declared scalar reads now preserve ordinary visibility and
use the current DIRECT/ALIAS value under the actual unique storage carrier.
Native3 at `8488dbc53` establish safe reads; the unchanged scalar model baseline
stops explicitly Unsupported with zero agreement. Source3 and strict349 pass at
`b89e7e66d`; fresh104/89 premises at that same cut prove frame ownership, live9
with its typed source, real NEXT advancement/detach and consumed-slot refusal.
The old typed fixture is adapted statically with no renewed credit. Quiet reads,
consumed storage, mutation and escape remain required.
The actual351 join over `9782fbb4e` passes strict initialization at `4fbcf845e`.
Future initialized declared object/array reads now copy the live payload owner; ALIAS reads
retain the referent without acquiring its wrapper. Native3 at `8bd90af79` precede
an explicit unchanged-model Unsupported control with zero agreement. Strict351,
source3 and fresh136/134 premises pass at `756c4673b`, covering actual captured
VALUE/result transfer, nullable alias rebinding/type detach and array COW/child
survival through parent retirement. Earlier fixtures are adapted statically only.
The actual353 join over `26134d7a0` passes strict initialization at `8469aa86e`.
Unvisited typed PROP_INITIAL reads now raise ordinary Error after visibility
resolution, retaining declaring-class identity and actual source metadata.
Native3 at `e9dd1a554` precede the unchanged inherited-model Unsupported baseline
with zero agreement. Strict354, source3 and fresh123/141 premises pass at
`3418d8268`, proving Error ownership during receiver release, continued cleanup,
B/previousError chaining and atomic selected-reference binding. No earlier
campaign is renewed; consumed slots remain required.
The actual355 join over `64b2fabca` passes strict initialization at `08dfc81ef`.
Future explicitly unset typed properties now raise ordinary Error without a
getter, using the actual dynamic-first release prefix to exclude consumed slots
whose original/current UNSET images match. Native3 and the unchanged dynamic
Unsupported baseline at `0824519ef` are separate from changed strict/source3 at
`f43b28b47` and 142/147 reached premises at `bad93efed`. The resolved-default
fixture correction preserves its original uncredited failure; no earlier
campaign is renewed. The later377 cut below extends untyped unset reads;
wider getter access remains required.
The actual356 join over `976a55232` passes strict initialization at `4b31fc1cc`.
Future initialized declared values and typed INITIAL/UNSET slots now support
quiet `isset`/`empty` and coalescing with ordinary visibility and no magic consumers. Terminal booleans add no payload owner;
coalescing copies the dereferenced value. Native3 and the unchanged scalar
Unsupported baseline at `ad8135241` remain separate from strict356/source3 and
157/138 reached premises at `310e0fac6`. Actual receiver-release queues, unchanged
borrowed owners, alias rebinding/type detach and kept-child survival pass without
corrections. Earlier quiet assertions are adapted statically only; no campaign
is renewed. The actual358 join over `77d86df730` passes strict initialization
at `36df1d531` (4.663s); source3/295 retain their original changed cut.
Consumed/missing slots and wider magic access remain required.
Module377 resumes literal undefined-property warnings with fixed null after
handler writes, throws or borrowed CV/`$this` receiver retirement. Real temporary
owners and future359 untyped UNSET carriers retain their separate cleanup paths.
Strict359/source6 retain `bd419da30`; the false-only207 repair passes strict359
at `cb1c19466`. Borrowed132, owned154 and pending166 pass at separate cuts;
two distinct false sources pass at `192e33452`, including static handler replacement
and default emission before its destructor disables reporting. The original
fallback and direct-relation fixture failures keep zero credit; the earlier
bound-Closure native witness remains a weaker separate observation. Independent
review accepts these private cuts and the actual359 join over `f5c4eed1f`,
which passes strict compilation at `e77c3eff0` (4.567s) while preserving current
state-aware207 guards,270 renderer-source classification and30 Generator fields.
[Ledger](coverage/semantics/undefined-property-review.json).
The pinned8.5 reference-call increment keeps the genuine returned HCELL and
borrows its captured target before PROPERTY_PREP erases the wrapper. Literal
named noarg nonbuiltin calls without fallback now preserve fixed null after
target retirement, release wrapper-only replacements at FETCH cleanup and chain
throwing cleanup B with previous H. Ten exact originals and replacement237 pass
at `cba3ab695`; pending207/stdClass225 pass at `d615fdf4d` after a fixture-only
WeakReference timing correction. Strict359 passes at the original changed cut;
native7/native2/native1 and the failed pending gate retain separate zero-model
or zero-state credit. Accepted99/79 remain unchanged. [Reference-receiver ledger](coverage/semantics/reference-property-receiver-review.json).
The independently reviewed actual361 join over `7c18fccada` passes strict
compilation at `0b6054930` (4.817s), preserving current return-replay vocabulary,
CALLS pack/NaN schemas and exception interfaces. It renews no source/state cut.
One ordinary positional CV argument now shares377's authenticated cell reception
through the existing361 source-image certificate. Native6 retains `2a9aaece4`;
strict361/source6 pass at `44597addc`, and five reached groups pass760 premises
at `50fb5bed6`, including parameter retirement before lookup, shared/scalar and
separate argument cells, saved carriers and pending H/B cleanup. The first
constructed dynamic-image fixture failure remains zero; only its callable-line
certificate changed. Earlier source10/state669 and all prior failures are unrenewed.
The actual361 composition over `43a3fed4f` passes strict at `827c12ebf`
(4.946s), preserving current compiler insertion and class-promotion interfaces.
One named ordinary CV now uses the same cell reception and authenticates deferred
SEND23 while preserving documentary INPUT24; known sends retain CV26/property27.
Native6 retains `ada28d77a`. The original source6 campaign at `3321d2547` failed
with zero whole-gate credit; its five completed per-case agreements remain valid
under the explicit source-line bridge. Changed strict361 and the affected
deferred comparison pass at `85424f5f4`. Five reached groups pass 1008
setup-inclusive premises at `5ed9fbe45`, covering named slot2/defaults, current/saved
carriers, fixed null, parameter retirement and protected H/B cleanup.
Fixture parser, binder and fallback-conversion failures remain zero; earlier
source6/state760 and source10/state669 are unrenewed.
The actual361 join over `b82bd2425` passes strict at `432084968` (4.923s),
preserving current call roots, return replay and class Override interfaces.
It renews no source/state credit.
Two positional ordinary CVs now use a local source certificate in377;
shared361 ECHO admission and99/79/cell ownership are unchanged. Deferred SEND2
reports emitted23 while preserving documentary INPUT24 and captured prefix7
despite caller mutation to99/19. Native6 retains `0be182e03`; distinct core-only
companion2 observations retain `4e9366787`. Strict361 passes at `f16303c4e`;
source6 and six reached groups pass 1207 setup-inclusive premises at `64fdea48c`,
covering first-null/later-live sends, shared formals, both parameter callbacks
before PREP, current/saved malformed carriers and H/B cleanup. The original
`is_null` source campaign retains zero credit; the second original remains
model-unrun. Earlier noarg/one-CV/named cuts and failures are unrenewed.
The actual361 join over `430face8d` passes strict at `4b39fa53c` (5.028s),
preserving current CALLS/class compiler, return replay and fatal-cleanup interfaces.
It adds no source/state credit.
Two distinct named ordinary CVs now preserve source SEND order and formal-slot
binding through377's local certificate;99/79/CELL/270 and shared361 are unchanged.
Native6 retains `4c64cd257`; the late first-SEND companion retains `b5e60e7b1`.
Changed strict361 and affected pending/late-first source2 pass at `7c2c5e8ef`;
five earlier per-case agreements retain `1378c1d0d` under the named-extraction
bridge. Five whole state gates pass 1245 setup-inclusive premises across separate
366/316/186/77/300 cuts, authenticating both emitted SEND lines, captured null,
shared cells, formal/default leave order and frame/operation pending cleanup.
The original whole-source7 and fixture failures remain zero; previous cuts are
unrenewed.
The actual364 join over `e26e3fb2d` passes strict at `2383140e3` (5.104s)
and one affected pending300 gate. Local byte observations accommodate current
Throwable string carriers; GEN363 and RETURNS378 seams remain disjoint. Earlier
source/private state cuts retain their own identities and credit.
Mixed positional-then-named ordinary CVs now use377's local source certificate;
only the deferred second named SEND needs an emitted-line override. First n0
uses the authentic NAMED_SEND carrier with generic equal-line capture. Native6
retains `f41c88dfe`; strict364/source6 and five whole reached gates pass 1235
setup-inclusive premises at `b766af8a1`, covering slot0/slot2 around default3,
shared HCELL3/payload1, parameter/default leave order, current/saved malformed
carriers and frame/operation pending cleanup. Shared105/213/99/79/CELL/270 and
all earlier accepted cuts/failures are unchanged.
The actual367 join over `4d7ef44ee` passes strict at `87aca689f` (5.179s).
Genuine variable returns keep Notice markers absent; introduced GEN request,
compound-string and static FROMCALLABLE paths are inactive. Source/state credit
remains at the separate private cuts.
The first implicit getter family now supports literal ordinary CV-base reads
through public nonstatic `__get` with one untyped required parameter and no
declared return type. Missing/public UNSET invokes it; accessible typed INITIAL
raises Error without a getter. Module380 holds the receiver once while the
getter context borrows it, verifies exact property types before receiver release,
then copies the current reference payload. Value returns stay fixed, discarded
reads retain their real RV, and H/B/C cleanup exceptions preserve previous links.
Native7 and discarded-native1 retain separate cuts; source8 passes at `7971e6693`
under the validator-only bridge to changed strict368 at `9b46165fc`.
Eight whole state groups pass 1293 setup-inclusive premises across `233992212`,
`176e6efa7` and `d3ee92ffd`. Original native/state failures and diagnostic credit remain zero; earlier
property milestones retain their separate cuts.
[Getter ledger](coverage/semantics/magic-property-get-review.json).
The reviewed actual369 join over `b9f0b1ae9` passes strict at `bae438b0f`
(5.181s, state credit0). Current class/Generator targets, return cursors and
callable factory fields are preserved; these untyped nongenerator getters leave
those paths inactive. Private source8/state1293 retain their separate cuts.
Denied private/protected literal-CV reads and ancestor-private fallback now
invoke the same public getter without hidden property type verification.
Allowed lexical VALUE uses its physical key; INITIAL raises Error without a
getter. Source-certified caller scope survives privileged getter/destructor
contexts without repeating CV/absence lookup. Native6 and source6/strict370
retain separate cuts; five groups pass 880 premises at `19cce2600`, and the
affected214 at `b5be8ecec` brings the total to 1094. The original Unsupported
baseline, preparation failure and failed cleanup-source assertion retain zero credit.
[Denied-getter ledger](coverage/semantics/magic-property-denied-review.json).
The actual370 join over `e2ef06143` passes strict at `2fc127185` (5.422s,
state credit0). Current factory/constructor callable, Generator/collector and
assertion additions preserve the ordinary getter interfaces and are inactive
in these originals. Private source6/state1094 and all failures keep their cuts.
Coercions, constrained returned cells, wider signatures, quiet/write/recursive
getters, lexically accessible nonpublic UNSET, changed Closure scopes for nonpublic access, computed
names, hooks, consumed storage and wider reference-call receivers remain required;
held278/279 add no dependency or credit.
Released-CV mutation, raw retired-container
reads, wider wrapper-pointer consumers, internal Generator/Fiber descendants,
binding-time exit, nonordinary replacement objects
and expired notice buckets remain Unsupported. The preserved `is_array` original
now stops at builtin dispatch and retains zero agreement credit. Bounded
source/current-address admission is not a
historical reachability proof. The concise
[review](coverage/semantics/duplicate-property-reference-review.json) preserves
original mismatches and the uncredited strlen observer; no earlier318 campaign
is renewed.

The actual290 composition preserves ordinary borrowed eager-cleanup certificates
and authenticates live clone windows in the existing saved Fiber-close VM without
adding heap roots. Two new exact originals cover a retired private clone maker
closing a Generator inside its Fiber and a live clone window surviving Fiber
close before a second-window write. One strict-SL reached group passes79 premises
for the sole saved carrier, heap-identical source-line forgeries, zero/one-step
resumption and terminal window retirement. Its maintained `closer-window` group
keeps this actual-parent cut separate from the earlier20/665 selection evidence.

Readonly clone-with updates305 now open an independent second window, preserve
the saved setter scope and ordered weak writes, and unwind alias/conversion
failures while retaining committed prefixes. Received values keep positive
physical write revisions, so a previously admitted Fiber write may later replace
a live slot. Genuine opcode/fixed clone makers cache durable source/site/scope
authority without extending heap lifetime. The earlier12 normal/468 unique
conditions remain accepted; later3 alias originals, parked-prior-write1 and two
retired/manual maker originals pass separately. New strict-SL77/151/81/50 reached
controls and production SL277/application0 pass. The
[contract](docs/semantics/READONLY-CLONE-UPDATES.md) and
[ledger](coverage/semantics/readonly-clone-updates-review.json) retain failures and
exact cuts. One directly affected private shutdown original also agrees exactly
after both clone objects retire at its separately recorded367e581df cut.
The separate dynamic/FCC follow-on above, destination-release13, Generator callbacks,
Deprecated dispatch, promotion/hooks/enums and wider lifecycle remain required.

Genuine clone lifecycle300 now checks access before allocation and runs the
selected callback with declaring/called scope. Per-object readonly allowances
survive Fiber parking, successful writes consume them, failed conversions retain
them, and return/throw/exit relock unused slots. Borrowed CV originals may retire;
temporary inputs and genuine intrinsic argument buffers retain their real owners.
On the private ordinary294 base, 20 normals, five declaration errors, one explicit
exit and 264 reached conditions pass; SL276/application0 passes. The
[ledger](coverage/semantics/readonly-clone-review.json) preserves original failures
and the corrected parser/fixture boundaries.
The later305 cut supplies the separate nonempty update window. Destination-release13, implicit
Generator clone creation, force-close/hooks and broader lifecycle behavior remain
required.

Backed readonly lifecycle294 now preserves first-initialization scope, initialized
write/type priority, unset, direct/nested updates and readonly class/trait identity.
Raw object source references detach; target reference binding fails without changing
the slot. Genuine first Stringable conversion retains its admitted destination
through inner initialization, same-site recursion and Fiber suspension. On the
private a939 base, 39 ordinary normals, 18 declaration controls, separate Fiber1 and
243 reached conditions pass; production SL275/application0 passes. The
[ledger](coverage/semantics/readonly-lifecycle-review.json) preserves original
failures and supersedes only288's raw-object target-reference expectation.
The new clone callback cut is separate from these ordinary gates. Destination
release, Deprecated dispatch, promotion/hooks and wider
conversions remain required.

Backed asymmetric instance setters288 now preserve lexical permission, called
diagnostics and direct/indirect/reference/unset ordering. Stringable compound
callbacks retain captured destinations, own consumers and the saved writer scope.
Private34 normal/8 compiler/350 reached checks keep their distinct cuts; one
actual38f1/Fiber281 source at a939 agrees after suspension and target retirement,
and production SL274 stages/init passes. The
[ledger](coverage/semantics/instance-set-access-review.json) preserves original
failures and the no-owner native Fiber frontier. Readonly follow-ons/hooks/magic,
wider static compound selectors and borrowed destination lifetime remain required.

Compound Stringable concatenation352 preserves the actual selected RHS slot:
defined CVs remain live through the left cast, initially undefined reads latch
null, and evaluated VAR/TMP operands retain their real owners until after the
store. Non-reference self CVs reuse the left string; reference self CVs reread.
Entry-time destination identity also preserves aliases created or rebound during
conversion. Eleven exact originals and private332 compiler/init pass at632c;
one separate caught left/right throw original passes at4bf8. One root/DIM/property
expression-result original and249 new reached premises pass at7c15. The
current-parent gate retains its separate cut in the
[ledger](coverage/semantics/compound-string-live-rhs-review.json). Earlier334/344
evidence is unchanged; wider borrowed destinations remain open.
Actual339 over CALLS351 `fd432561f` passes algo/struct/init at `0b0bd4336`,
with independent pointwise parent review and no13/249 source/state renewal.

Named static-property Stringable compounds356 retain the initial plain-slot versus
reference-cell destination and conversion branch through callbacks. Typed stores
return their verified value; initial-string reference writes and late plain-slot
alias detachment preserve Zend's unchecked backing and retained type-source history
with nonowning entry/write/retirement evidence. Eleven exact originals and private340
compiler/init pass atc4ed; a separate typed-reference conversion/rejection original
passes at163e. New368 reached premises pass ate148, including future-entry,
foreign-cell and repeated-site history rejection. Actual344 over COMP `e1c3d4d618` passes algo/struct/init at `f0e03c885`,
with pointwise353/354/355/357 and owner-factor review in the
[ledger](coverage/semantics/static-compound-string-review.json).
Ordinary-method `self`, `parent` and `static` selectors now capture the actual
lexical/called scope before callbacks; nonowning selected ENTRY history retains
the destination through nested calls, private shadows and reference rebinding.
Six exact originals and private344 compiler/init pass at `45f32a157`;323 new
reached premises retain separate144 at `b228479d6` and179 at `714465927` cuts.
The unchanged earlier keyword Unsupported record retains zero agreement.
Actual347 over `66160341f` passes algo/struct/init at `c2b0f283b`, with
exact257/296/301/360 parent review and no6/323 source/state renewal.
Dynamic class selectors now preserve the class resolved before RHS evaluation,
including once-only helper/object selection and selector mutation during RHS or
conversion. Captured references retain the original cell and typed result; scalar
concatenation restores the ordinary base without a selected-entry event. Five
exact originals and private344 compiler/init pass at `09034d789`;241 reached
premises pass at `fc7727974`. The unchanged earlier dynamic Unsupported record
retains zero agreement. Actual349 over COMP `ea58ac361` passes algo/struct/init
at `bba0c15be`, with pointwise361/362 and same-state graph-factor review and
no5/241 source/state renewal.
Computed static-property compounds366 delay name CV reads until after RHS work,
retain evaluated name/RHS operands through real class preparation, then transfer
the selected property to the existing static conversion/store. Buffered fetch
lines remain distinct from initializer error lines. Six exact originals pass at
separate `a0b4f81c9`/`82ea0e591`/`03bf61f0a` cuts; first-cut compiler/init passes.
New295 reached premises pass at `1abff50f4`, including real cold-preparation
owners, compiled-name/marker forgeries and retained REF selection. Actual-parent
compiler/init passes at `ed57a7c5c` over CALLS367 `9aec542e2` (353 modules),
with pointwise SOURCE365/367 owner/line review and no6/295 source/state renewal.
Keyword scopes entered through Closure/fromCallable or
other callable wrappers, wider borrowed lifetime and registered-handler
missing-RHS continuations remain separate; paused return producers are unchanged.

Stringable computed static-property names371 freeze the selected class and
converted bytes, check the property address, then retire the receiver before
capturing the live row, reference cell and RHS. Pending scalar writes retain
PHP's conversion/operator priority.
Failed NAME conversion and throwing final cleanup now keep the authenticated
empty-name FETCH and queued tail, with Error.previous=drop.previous=cast.
The descriptor walker restores only its saved inert base and original queued tail.
Eight of nine exact originals pass at distinct private cuts. The original
pending-masks source remains required/open: the changed public run retains its
60-second CLI timeout and zero whole agreement. Prior123 receiver/cold-owner
premises and new238 late-address/pending/projection premises have separate inputs;
changed algo/struct/init and the238 fixture pass. The preserved73.924s diagnostic
records the repaired double-throw mismatch. Current360 algorithmic compilation
passes ataa44149a overb894 with pointwise99/156 review and no accepted source/state
renewal. The unchanged original7 current run repeats CLI60 timeout in65.143s, with
exact native bytes and zero whole agreement. Standalone init/state at that
401 baseline are UNRUN.
A narrow module 46 constant-insertion factor at 30a7223 evaluates the existing lookup
once, preserving exact values/table IDs, list order and conflicting-value refusal.
Changed compilation and strict current 238 plus 23 focused premises pass, including
the nested-NAN export pipeline and ten empty/present/order/identity controls.
Original 7 still returns CLI 60 timeout in 65.092 s with exact native bytes and zero
whole agreement. Matched prefixes of 400 steps return the same BUDGET state tuple:
lookup calls fall from 689,580 to 229,972; exclusive instrumented time falls from 8.4063 s to 2.9977 s.
These wall-time profiles locate work; they do not establish a CLI 60 completion.
The initial fixture syntax failure remains preserved with zero credit.
Standalone initialization is not renewed; prior 123/private 238 keep their cuts.
Actual-parent compilation passes at 64854b87 over 8f9dda67 with 361 modules;
promotion, HCELL and replay hooks are preserved, with no source/state renewal.
A module 39 specialization at 646e075b4 over 43a3fed4 with 361 modules returns
the existing empty roots for STMT before the owning-task fallback. Compilation
and 14 focused controls pass, retaining nested scopes, ordered duplicate roots
and task-owned allocations. Same-parent prefixes of 400 steps return identical
116,334-byte BUDGET tuples. The 254,563 task_nodes calls remain unchanged;
exclusive instrumented time falls from 3.0177 s to 0.8355 s, and total instrumented
time from 23.3692 s to 20.8877 s. These measured wall times are not CLI estimates.
Required original 7 still returns only timeout after 65.157 s under the unchanged
CLI 60/outer 90/100000-step caps, with exact native bytes and zero agreement.
Prior eight sources and 123/238 plus 23 premise cuts are not renewed.
Actual-parent compilation passes at 78a713178 over 78a7c210 with 361 modules,
preserving the one-CV property seam; this checks compiler compatibility only.
A verbatim module 46 access-lookup clause reorder at 566aac7e over cf9411d67
passes compilation and 11 path/mode/first-match controls with 361 modules.
Same-parent prefixes of 400 steps preserve the complete 116,334-byte BUDGET tuple.
The 1,746,870 ppaccess_at calls remain unchanged; exclusive instrumented time
falls from 3.1486 s to 2.8034 s, and total time from 20.8399 s to 20.5914 s.
This modest matched observation is not a CLI estimate. Required original 7 keeps
its prior timeout and zero agreement; no source or accepted state cut is renewed.
Actual-parent compilation passes at 640a59899 over 7c3299fd with 361 modules,
preserving scalar replay hooks; this checks compiler compatibility only.
A new cold double-throw source at b82bd2425 with 361 modules passes native/model
agreement and 155 genuine state premises without a production change. Empty-name
lookup leaves the static default deferred, preserves Error.previous=drop.previous=cast,
and retires the owned RHS without calling its __toString. Actual operation/FETCH,
descriptor, history and heap guards pass. The preparation stop and incorrect
receiver-field fixture failure remain preserved with zero credit. Prior source/state
cuts are unchanged; required original 7 remains open at its CLI 60 timeout.
Current publication over ee06368a4 with 363 modules passes compilation and 156
carrier-aware cold fixture premises at 2009abf79; source agreement stays at b82.
ARG329 EPS/mixed-Notice and held return-verifier work remain excluded.
Live compound string gates now accept authenticated carrier bytes and preserve
the concat helper's STRINGDATA state; empty branches keep legacy unknown identity.
Ordinary inherited-static by-ref NAME/RHS agrees at 09cd/363 with 213 premises
(149 reached, 64 constructed). At 5e77/363, static Closure::fromCallable computed
keyword selection retains genuine CLOSURE_SCOPE through the RHS callback/write
and actual request retirement. The wrapper matches native bytes; 359 premises
(239 reached, 120 constructed) authenticate the entry and reject narrow forgeries.
All prior stops remain zero credit. EPS saved selection keeps ordinary compatibility;
other Closure families, INI identity, ARG329 and required original 7 remain open.
Actual-parent compilation passes at a67b4e4a over 633ecec1e with 367 modules;
pointwise Notice/ownership review adds no source or state renewal.
Inherited nonstatic `Closure::fromCallable` now admits the exact saved receiver
through existing source/body/history evidence. Ordinary-instance agreement stays
at 4d7/367; repaired wrapper agreement passes at ff368a41/367. Its 430 premises
(282 reached, 148 constructed) authenticate receiver ownership through the distinct
RHS callback/write, explicit Closure and receiver retirement, and saved descriptor
validity afterward. Missing or substituted current/saved receivers are rejected;
selection metadata adds no owner. The earlier wrapper Unsupported remains zero
credit, and required original 7 retains its separate CLI 60 timeout.
Actual-parent compilation passes at 943e2c3c over 94f4b007 with 367 modules;
pointwise promotion/property replay review adds no source or state renewal.
First-class `Closure::fromCallable(...)` now has a source-stamped factory carrier
and its own owning CONFIG kind. The returned method capture retains a nonowning
factory certificate after retirement. The direct control agrees at 6e709da7/367;
captured inherited by-ref NAME/live Stringable RHS and six new permission,
named/unpacked argument, identity and argument-retirement originals agree at
8cc7ed12/367. Its 526 state premises pass (467 genuine/derived, 59 constructed),
including factory creation, CONFIG owner count 2, distinct returned receiver
ownership, factory retirement, callback/write and explicit receiver retirement.
Invocation USER scope controls callback access; creation scope grants no later access.
The initializer Unsupported and pre-child clean-status stop remain zero credit.
The maintained renderer is byte-identical to the accepted fixture; relocation
adds no runtime renewal. Invoke aliases, nullsafe/computed method entry,
computed/keyword creation and captured-factory Fiber/wider getter callbacks stay open,
as does required original 7's CLI 60 timeout.
Current-parent compilation passes at def000e9 over ac4a95b5 with 368 modules;
pointwise storage/intrinsic/getter review adds no source or state renewal.
The [factory ledger](coverage/semantics/from-callable-review.json) keeps the
distinct native/source/state cuts and boundaries.
Literal captured-factory `->__invoke(callback: ...)` now authenticates method
entry and preserves METHOD_RESULT plus the caller tail. CONFIG owns the selected
factory while an argument clears its caller cell; the returned Closure owns its
receiver independently after factory retirement. Invocation USER permission and
API→Closure invoke error frames match native PHP. The variable control agrees at
b9f0b1ae/368; four explicit sources and 552 state premises (512 genuine/derived,
40 constructed) pass at c1cdc2b5/368. The wrong-representation state failure and
original interpreter failure remain zero credit. Maintained source/fixture bytes
are unchanged; relocation adds no runtime renewal. Original 7 stays OPEN timeout0.
Actual-parent algorithmic compilation passes at b6022a52 over 7cb33cde with
370 modules; pointwise constructor/COMP/property review renews no source/state cuts.
Literal first-class factory `->__invoke(...)` now forwards to existing identity
capture without allocating an alias object or changing the factory creation site.
The real Closure identity/by-reference control agrees at e2ef/370; the factory
witness agrees at 3cb295d1d/370 after original and alias caller-cell retirement.
Its 610 premises (550 genuine/derived, 60 constructed) preserve exact task/tail,
arena identity, CONFIG owner retention, retired factory provenance and independent
receiver/RHS/write/retirement. The interpreter failure and fixture variable collision
remain zero credit. The maintained renderer is byte-identical to the accepted
fixture; wider computed/nullsafe captures and original 7's CLI60 timeout stay open.
Actual-parent compilation passes at `0b4de6cd` over `5a127787` with 371 modules;
pointwise CLASS/ownership review adds no private source, state or native renewal.
Captured factories now select finite Throwable getters through an immutable,
nonowning creation/invocation certificate. The returned getter owns only its
receiver, reads the changed message after factory retirement, and keeps that
receiver through clone/equality and final release. The direct control agrees at
557e/371; captured live-message and new clone/equality sources agree at 771e/371.
Its 191 premises (154 genuine/derived, 37 constructed) prove actual CONFIG/mint,
parked return cleanup, restored result and last receiver retirement. The prior
Unsupported and one-step fixture failure remain zero credit. The maintained
source/renderer bytes are unchanged; relocation renews no runtime evidence.
Wider getter/binding/library targets and original 7's CLI60 timeout remain open.
Actual-parent compilation passes at `71edcca7` over `8cc17e6e` with 371 modules;
pointwise EX/RETURNS review adds no private source, state or native renewal.
The [ledger](coverage/semantics/static-compound-string-review.json) retains
the source/state cuts and failures without renewing older evidence.

Array eval/include conversion287 dispatches the real warning before parser or
file-provider work and freezes `Array` after callbacks, even when they replace
the operand. Borrowed variables gain no temporary owner; captured arrays survive
provider/parsing/compiler notices and retire before nontrivial file bodies or
catch search. Four exact destructor-free sources and 207 state premises pass at
3b2c; actual33df preserves Fiber/ArrayAccess/trait-demand routes and passes SL273
at5a0e. The [ledger](coverage/semantics/source-array-review.json) retains original
fixture/compiler failures; the destructor lifetime witness agrees in the separately
reviewed270 composition. Selected undefined/Stringable ingress, helper results and
retirement traces are installed above. Wider source producers/providers remain required.

ArrayAccess284 now admits its builtin interface contract and direct R/IS,
isset/empty, Set/append and Unset calls. Effective inherited methods and tentative
return notices preserve prototype order and ReturnTypeWillChange suppression.
Receiver/key protections, entered parameter owners and borrowed result pointers
retain native callback, reentry and exception timing, including NaN truth warnings.
Author13/205 and independent20/287 share five originals: 28 unique private programs
(26 normal and two declaration errors), 492 reached assertions. One actual465d
source at6ccb preserves private Owner/Child selection, receiver retirement and
post-Set readback through the old typed CELL. The
[contract](docs/semantics/SOURCE-ARRAYACCESS.md) and
[ledger](coverage/semantics/arrayaccess-review.json) retain separate source/compiler/
state cuts and original failures. Full nested/read-write/reference and wider
memoized consumers, plus combined Iterator/ArrayAccess notice ordering, remain
required. Newly reachable unsupported consumers stop explicitly; paused return
verification stays separate.

Fiber281 now implements live user-callback construction and direct
start/suspend/resume/throw, status, current identity and stored returns. Callback
selection is cached; genuine VM stacks, live reporting masks and C argument
buffers survive suspension while globals, INI and handler registration stay
shared. Nested waiting Fibers remain running. Thirty normal originals and thirteen
source-derived states/782 conditions retain their mixed cuts. Deferred/literal
named holes, entry-error caller provenance and raw named-buffer admission are
checked through genuine pending continuations and malformed records. Actual
constant-NEW identity and a separate running Generator preserve genuine owners;
global Generator admission stays on the actual machine while parked Fiber stacks
keep their local guards. Three Unsupported controls earn zero agreement. The
allocated-Fiber argument source and null-callsite preflight state checks retain
separate cuts.
[The contract](docs/semantics/FIBERS.md) retains the exact tested cuts.

Fiber291 now force-closes ordinary suspended callbacks through an unregistered
control: catches skip it, finally blocks run, and replacement exceptions return
through the genuine operation or parent finish. Captured destructor retirement
keeps its real empty internal root and ordered ownership. Five destruction
control lists move with the VM. Actual 270/296 composition at 279 modules
passes strict-SL initialization, one exact destructor/helper source comparison
and a 58-premise default-AL state for parked lists, ownership and resumption.
Twenty-nine normal close comparisons and
fourteen reached states/1,037 conditions retain their private cuts; request-scan
and ordinary-library controls earn zero agreement.

Fiber302 stores a returned result before ordinary callback retirement and keeps
its definedness separate from a thrown body exception. Captured destructors may
suspend, resume and receive public throws; stored results survive replacement
errors even when `getReturn` rejects the failed Fiber. Fifteen targeted normal
comparisons and twelve state groups/871 conditions retain their private cuts.
Module 308 adds protected cleanup after an actual return; the body-undefined
case remains Unsupported and its engine witness is held. The required internal/reference
callbacks, API entry, unpacking, initializer switching, request/fatal cleanup and
GC remain open. Full core stays open; returns verification remains paused.

Fiber313 supports cached string `error_reporting` callbacks with weak C receives,
owned arguments and an authenticated borrowed result tail. Handler suspension and
receiver retirement retain warning producers, resumer traces and internal scope.
The latest294-parent join preserves GC, returned-child append, source emission and
Arrow rules; strict295 compilation and one new explicit-request GC/autoglobal-eval
original pass independent review. The [ledger](coverage/semantics/fiber-core-callbacks-review.json)
preserves prior source/state cuts and separates bounded public checks from the
unconfirmed rich whole-source/full63 runs. Wider internal/FCC/reference callbacks,
initialization, request/fatal/GC consumers and complete core remain required;
the final fresh offline rebuild is outstanding and returns verification stays paused.

Fiber322 adds effectful scoped/deprecated constructor method selection,
warning-before-status ordering and immutable original maker/scope authority.
Actual Fiber nominal argument admission and inherited RuntimeException construction
close gaps found by unchanged originals. The actual305-parent interaction preserves
a private static callback made by a GC destructor after its receiver retires;
one exact source and92 reached premises pass independently. Earlier thirteen
sources and815 conditions retain their original cuts in the
[constructor ledger](coverage/semantics/fiber-callable-constructors-review.json).
Final307-parent composition passes strict308 and compatibility review; broader callable/FCC,
internal/reference/lifecycle consumers and final validation remain required.

Generator280 creates object-owned suspended frames after eager ordinary receives.
Value yields, literal iterator methods, `getReturn` and value foreach retain
captured aliases, ordinary private creation scope and real resumer traces.
Generator-specific completion bypasses ordinary declared-return coercion;
return-supertype admission mirrors the pinned one-level intersection scan.
Twenty-seven normal sources and three compiler rejections agree at e235d8dd1
in separate first5 and independent25 cuts. Six lifecycle Unsupported controls
earn no agreement. Independent source-reached carrier144/Closure154 pass at2f21,
nested77 atd7ca and abrupt44 at6c221 (419 premises across four originals).
Full public admission, live/suspended cursor owners, captured references and
natural try/finally cleanup pass; failed checks remain retained. Delegation/reference
yields, further call forms,
changed caller scopes, force-close finalizers and destruction/GC remain required.
Three introduced parent sources agree at9abff: constructor-created constant
identity, deferred REAL Closure autoload and parse-folded versus live precision.
The new constant95 state phase retains the same completed receipt through
receive/yield/return and retirement; its noncached instance owners pass full
public/heap admission. Original interpreter/fixture failures retain zero credit.
[Scope and maintained tests](docs/semantics/GENERATORS.md).

Literal Generator `send`/`throw` capture one argument before initialization,
deliver used yield results or an ordinary Throwable search, and retain actual
API arguments and live resumer traces. Twenty-three new normal sources agree
at26328 in separate author5/independent18 cuts. Fresh initialization failure keeps
the supplied exception primary and links the initialization exception as previous.
Independent array146/finally124/initialization101 pass at fixture887f51d29,
semantic26328 (371 conditions across three originals): actual input owners,
exception identity, full public admission and malformed resume rejection.
One actualc729 source at63b45/semanticca7da combines default NEW autoload,
live/default versus parser-folded precision and fresh sent-object identity.
The original SL structuring failure retains zero credit. Full Generator
follow-ons remain open.

Parameter-default NEW autoload285 resumes authentic deferred initializers after
lookup, preserving declaration strictness and formal lines. Loaded constructors
are selected afresh; allocation and all nested AST arguments precede constructor
access, while loader throw/miss suppresses arguments. Nine private sources agree
at07a78; lookup94/recursive37/retirement43 pass at ebb346, including retained
receiving owners and heap-valid pending/history tag, line and caller forgeries.
One actuald57/GEN280 source agrees at24f376: lookup/arguments/construction remain
eager before generator suspension. Original public/fixture failures and the
parameter-Closure initializer Unsupported retain zero credit; its WeakReference
lifetime oracle is native-only. The [ledger](coverage/semantics/default-new-autoload-review.json)
keeps these cuts distinct. Global-constant NEW autoload, parameter callable
initializer producers and wider lookup/link consumers remain required.

Autoload277 now implements the four required SPL control APIs with real callable
caches, owner roots and live queue cursor/capacity behavior. Ordinary named/dynamic
NEW and class-parent lookup suspend before arguments; lookup inherits source
strictness/site while explicit dispatch is weak/internal. Selected names retain
exactly one raw slash normalization. Indexed declaration certificates preserve
loader authority after unregistering and receiver/scope retirement. Thirty-four
sources pass at b967 and two at b440; guard cuts stay separate in the
[ledger](coverage/semantics/autoload-review.json). Its 263 original finite premises
pass with seven typing bindings and eight repeated setup premises. One actual
b025/global-constant REAL loader source passes at a37. Original failures and AL
timeouts remain retained; SL uses the existing exact runner at the same120s cap.
Parameter-default AST NEW is covered by285 above. Global-constant AST NEW and
wider lookup/link consumers remain required; default filesystem search is
excluded and returns stay paused.

Scalar-container continuations282 now stage missing-base, key-CV and offset
warnings through ordinary and quiet reads. Missing-base warnings resume with
independent null; defined scalar pointers can change the later message type
without creating a late array lookup. Genuine nested row/key operands retain
real owners, and terminal isset/empty string predicates remain distinct from
coalesce. Throws suppress later callbacks and writes. Author8/212 and independent13/272
share one original (20 unique private programs/484 assertions). One actualb025
source at5eefe retains private Owner/Child selection, key-temporary ownership and
live caller/static17. The [contract](docs/semantics/SOURCE-CONTAINER-READS.md) and
[ledger](coverage/semantics/container-read-review.json) retain separate source cuts
and the original formatter failure. A separate stdClass transition agrees;
the historical ArrayAccess control retains its earlier interface-contract
Unsupported and earns no guard-execution credit. Direct ArrayAccess is covered
by284 above; string/ordinary-object, wider base and GLOBALS/memoized producers
remain required.

Container continuations276 now initialize undefined/null/false CV-rooted W/RW
storage before key demand and preserve final array-reference source cells. False
callbacks retain genuine protection and distinct FETCH/ASSIGN/DIM_OP selection;
throwing paths keep native initialization/write/error priority. Source-backed raw
typed DIM_OP array backing survives COW and clears on whole-cell writes without
changing ordinary type conversion. Author12/242 and independent21/275 share three
originals (30 unique private programs/517 assertions). One actualae0 source at851
preserves private Owner/Child selection, captured source lifetime and live
caller/static17. The [contract](docs/semantics/SOURCE-CONTAINER-WRITES.md) and
[ledger](coverage/semantics/container-warning-review.json) retain the original
loader/fixture failures and separate cuts. Wider read/quiet/memoized/unset/GLOBALS
containers, string/object producers and complete core remain required.

Live precision272 now preserves registered/raw get/set/Restore through option
callbacks, runtime string types/conversions, nonnumeric comparisons and late trace
formatting. Each main/eval/file unit retains creation precision for parser-folded
literals; compiled operands retain their conversion-point precision, while genuine
constant/default/property AST operands instead use live precision after callbacks.
Sixteen exact source/profile comparisons across eleven main programs retain
d028/e594/73011 cuts. At73011,
state54/39/27/74 (194 supplied checks plus12 program bindings) and transport12 pass;
SL261 and the changed adapter jobs1 build retain their separate cuts. The actual
ae0 parent is preserved in264 modules through focused source review, with no
renewed execution. [Ledger](coverage/semantics/precision-review.json) retains the
include-history and deferred-concat mismatches plus fixture failures. Array
include/eval warning ingress, `serialize_precision` and wider raw-float Throwable
formatters remain required.

Suspended eval compilation now records genuine precision resume epochs, retaining
parser creation separately from later concat/name/fold conversion points. Image
refresh preserves escaped earlier arrays, callback allocations and enriched bound
class data; pending throw/exit still permit later compilation and publication.
Nine exact source comparisons retain c9a/f03 cuts. The325 supplied state controls
plus16 program bindings retain f03/193/da3 cuts; named compiler-handler
class causes require the real pending notice and exact eval entry. Actual266 key
scratch now seeds source creation precision separately from live AST evaluation;
one new exact source and28 supplied checks plus1 binding pass at75173 in strict
SL. Both AL timeouts and the stale-wrapper rejection remain zero-credit. The
actual318/GEN parent retains269 modules and passes SL at66453, without renewing
source/state cuts. Original compiler/fixture failures and the former Unsupported
frontier remain in the
[precision ledger](coverage/semantics/precision-review.json). Wider callback cause
selection, formatter/provider interactions and complete core remain required.

Global constant callables271 now evaluate static/no-use Closures and function or
static-method FCCs before registration. REAL lexical/called scope comes from the
immutable source entry, including inherited include/eval scope; NAMED functions
remain unscoped. Exact full declaration/value flow authenticates installed values,
while USERCONSTANTS own them. Duplicate-warning continuations retain candidates
and their pre-callback lookup prefix, preserving the original binding on return
or throw. Raw-trait METHOD notices precede allocation and resume the captured
target. Nine exact source agreements retain414/5d0/92ff cuts; seven source-derived
AL programs/341 premises pass at21b5, checking scopes, transfer forgeries, retry,
reentry and genuine collection. Original compile/interpreter failures remain
zero-credit in the [ledger](coverage/semantics/deferred-static-defaults-review.json).
Per-child alias proofs now retain the exact donor and table prefix for each
completed read, so first registration can preserve an earlier fallback without
freezing later operands. Installed rows and duplicate continuations retain only
nonowning lookup facts. Three fresh source agreements pass at9619d2f57; mixed90
and retry94 AL premises pass at4262f787e, checking distinct selections, failed-unit
transplants, candidate retirement and genuine constant roots. Their compile and
fixture stops remain zero-credit.

Global constant NEW283 now preserves raw user-instance identity through prepared
argument and constructor phases. Every argument is evaluated, including ignored
no-constructor arguments, before constructor access; immutable file/eval entry
scope governs self/parent and private access. Nonowning receipts distinguish
incomplete escaped allocations from successfully ended construction, while
USERCONSTANTS and real GLOBALS/CV owners retain values. Three exact source tuples
pass at17c12b379; argument103/inherited84/retry87 AL premises retain041ce1/00578e/
bc44da cuts (274 total). The optional-tuple and restored-MAIN fixture failures
remain zero-credit. Frozen duplicate/argument-abort destructor originals await
genuine eager release. Cold no-constructor table work adds source1 atd2fb and80 AL
premises ata1e14a2b4: the instance-template warning precedes ignored arguments,
with no allocation until table completion and no premature COMPLETE. A further
source1/81 AL premises at97dab9f8b check failed table work before allocation and
fresh declaration/NEW identities on same-text eval retry. The earlier cold fixture's three
elaboration stops and one slice-length execution failure retain zero credit.
Internal/Throwable/autoload and wider object/constant producers remain
required; full core stays open and return verification stays paused.

Deferred runtime class-link failures275 now replay the held notice prefix and
primary compiler fatal, retaining the genuine inner eval/include trace row.
Source history rederives the failed binding and exact rollback; the immediate
report requires its authentic failure/caller record. Seven exact source agreements
pass at4293f196: runtime eval, constant and include counterparts plus the four
remaining258 eval originals. Independent source-derived eval81/constant83/include84
checks pass in strict SL at the same semantic cut, proving public/history/owner
admission and retirement while rejecting forged failure rows. Earlier236 cuts
retain their identities; full traversal and core remain open.

Temporary fake/METHOD `Closure::call`268 now checks the actual selected scope,
executes user bodies and finite getters, preserves source statics and creates
durable children with only the genuine new receiver owner. Binding warnings
precede inner-name errors; reference warnings precede fresh-cell allocation and
retain frozen values through callback writes, allocations and throws. Private18
normal source agreements retain e2ce; totalized task guards at9342 pass AL252 and
five owner/frame/throw fixtures317 runner conditions (302 supplied checks and
15 reached setup; author106/independent211). The exact original factory/default
source1 and AL258 pass the actual0ef union at975fac. The final8350 parent keeps
its separate GLOBALS and cached constant-NEW routes through focused source review.
The [ledger](coverage/semantics/temporary-fake-call-review.json) preserves mixed
cuts and the original fa90 setup Unsupported with zero agreement. Unpacking,
further internal consumers and REAL temporary-current lifetime remain required;
return verification stays paused.

Global W/RW warning continuations269 now preserve caller-CV name rereads and
captured Array names through updates, compound assignment and nested array ingress.
Returning missing fetches detach callback-created constrained/reentry aliases into
a fresh null binding; throws preserve callback writes and skip later RHS demand.
Compound walks follow eager RHS computation while simple RHS CVs stay delayed.
Author9/224 and independent12/273 share four originals, giving17 unique private
programs/497 assertions ated6/baba/6e8. One actualc906 source at604958 retains private
Owner/Child selection, fresh-global detachment and live caller/static17. The
[contract](docs/semantics/SOURCE-GLOBAL-WRITES.md) and
[ledger](coverage/semantics/globals-write-review.json) preserve the original
multiline Unsupported and corrected native predictions. Container276 above adds
initial W/RW storage; wider GLOBALS/memoized consumers remain required.

Early-eval declaration diagnostics236 now suspend authentic compilation at each
publication, including generic warnings before class publication. Handler throws
and exit retain later publications while skipping the unit body; user fatals stop
compilation and retire its owners before shutdown. Pending-exception formatting
preserves the primary compiler fatal through source writes, conditional class
publication, throws, exit and nested hard eval/include compilation. Diagnostic
arguments retain physical source provenance and callbacks retain actual caller
scope/trace. Compact source plans, chronological prefixes and one real task owner
authenticate the continuation; hidden wrapper/branch claims are rejected.
Twenty-one distinct source agreements keep their separate966 through9b2 cuts;
the affected nested/file source2 also passes at3bd68993a. Authored USERfatal48
and independent pending65/handler36/Iterator28/nested42/Throwable30/formatter45
pass at ea077. The corrected nested-fatal57 passes at3bd68993a. File-public43
and history-retirement49 pass in strict production SL mode on semantic c9e6
(private43b); their union retains all59 original file predicates.
Equivalent call-admission deduplication at c9e6 retains the mandatory source
history/function-table proof; a new coherent descriptor-forgery24 check passes.
The maintained runner's optional `--sl` flag selects that mode only for the two
file phases. Actual23c composition source2 at5cf39c0dd confirms live dollar-curly
warning effects and later class publication before request destructors after exit.
The final1d4f union preserves261 object-cast frame cleanup,265 callable receipts
and267 keyword NEW source guards; these source2 results retain their5cf cutoff.
One actual261 source at0ef99 confirms a fatal formatter's NaN object cast keeps
its value while the recorded conversion warning stays suppressed.
Original failures, AL timeouts and fixture corrections remain
outside Git with no failed-run credit.
[Contract and maintained tests](docs/semantics/ITERATORS.md).

Accepted230 retains runtime/file prototype order, source erasure, direct
restoration, duplicate notices and ReturnTypeWillChange. Runtime classes publish
before callbacks; early file units publish fully before ordered delivery. Its
source19/independent11/affected trace3 and four state phases53/35/25/23 retain
their recorded cutoffs. Actual3b622 composition source3 at e1a654 retains physical
trait diagnostics, live argument/display state and effectful internal defaults.
The former four early-eval Unsupported controls had zero agreement credit.

Ordinary named keyword NEW267 now resolves self/parent/static in the actual
caller before class work and arguments. Inherited constructor entry uses its
immediate owning caller; service-unit main code follows persistent scope entry
bindings. Known function scope errors compile; main, eval, trait and Closure
errors remain deferred. Source18 normal/4 compiler and reached cold57/recursive44
plus corrected eval53 pass at91dc. Actual23c/264/257 composition at9b8 passes
private self/static and current identity after null-binding resets called scope.
Original preparation/eval-fixture failures remain in the [ledger](coverage/semantics/named-keyword-new-review.json).
Cached constant METHODs now admit compiled/named keyword NEW through exact265
receipt authority. One new source and38 reached premises pass at0da3, including
unrelated lexical/called scope and history after plain-clone retirement.
Wider autoload consumers and complete core remain open; returns stay paused.

Trait-constant callables265 retain the first shared AST method/function target,
while named/method captures record each current publication prefix and METHOD
captures select fresh called classes. REAL Closures use their own declaring scope.
Exact receipts authenticate
cached private targets after a real partial initializer failure; wrapped/plain
makers can create children with lexical/called scope and private defaults after
maker retirement. Successful constant caches own their values; history owns none.
Three source agreements and58+54 AL premises pass at4e2d; the unchanged122-premise
constructor guard passes SL at733 in27s under the same120s cap. AL timeouts remain
zero-credit in the [default ledger](coverage/semantics/deferred-static-defaults-review.json).
Compiled/named keyword NEW uses that exact cached METHOD authority through267
above; wider callable/default behavior and complete core stay open.

Non-object casts261 now populate stdClass scalars/arrays, share all-string tables
through genuine COW and fast clone, and preserve numeric round trips, alias type
owners and active foreach cursor history. NaN warnings retain the allocated object
and original operand location; NUL-key notices retain a nonowning TABLE/SERIAL
marker through callbacks and delayed reference promotion. Raw undefined buckets
keep distinct read/isset/copy/comparison behavior. Twelve full source comparisons
retain 3a/82c/b0 cuts; one actual 8ada/a4fc composition gives the first agreement for
the former251 native-only multiline cast holder. Four source-derived groups pass
208 premises at b0, with original fixture stops preserved. The
[cast ledger](coverage/semantics/object-casts-review.json) separates these cuts,
two retired-pointer originals and a longer companion timeout (zero agreement).
Actual257 destruction/frame/pruning hooks are preserved separately. Wider
raw-undefined consumers, lifecycle/GC and callback contexts remain required.

Request-stage destructors257 now repeat reverse direct globals and then scan
reusable live store handles. Once marks, bailout/failed-constructor suppression,
private visibility, nested USER calls and ordered outgoing slots retain exact
owners. Caller restoration precedes compiled CV cleanup; extras precede receiver
release. Pending throws replace and chain through remaining slots. Ignored
by-value ordinary and automatic-constructor returns release in the live callee before
locals; C destructor helper returns remain retained. Eval/include continuations
keep source history. Explicit request facts preserve startup argc order; absent
facts keep the original environment Unsupported, and dead CVs remain admissible.
Author78 source agreements and seven/303 reached assertions retain distinct
cuts; independent64 agreements, two Unsupported controls and12/548 assertions
retain theirs. Actual253/259/260 routes and final SL/AL253 pass on the preserved
a4fc parent;264/262/266 preservation is source-reviewed without old-cut renewal.
[Contract](docs/semantics/SOURCE-DESTRUCTORS.md),
[author record](coverage/semantics/destructors-review.json),
[independent ledger](coverage/semantics/destructor-review.json).
The earlier eager/prequeue Unsupported controls retain their original257 cut;
270 now supplies those releases. GC, output buffering,
queue freeing and final cleanup remain required; complete core stays open.

REAL binding264 now resolves scope before ordered static, `$this`-unbind and
internal-scope warnings. Genuine handler continuations retain selected reasons
through callback mutation and throws. The function's own compiled entries supply
`USES_THIS`, including dead eager literal-name uses and excluding nested bodies
and runtime-name folding. Valid null bindings copy REAL statics, retain reference
captures and reset called scope; explicit null scope removes class permission.
Twenty normal source agreements retain separate2312606/ed1d5 cuts. Five genuine
owner/frame cases pass289 conditions (author113, independent176).
Actual601312 composition at2cb72 passes AL251 and one cached trait-property
METHOD child source: null bind/clone retains private default permission and exact
current identity after makers retire, with called scope reset to lexical Owner.
Original classifier nondeterminism, the combined45-second timeout and fixture
elaboration stop remain separate in the
[binding ledger](coverage/semantics/real-closure-binding-review.json).
Temporary-current and internal API consumers remain required; returns stay paused.

Ordinary dynamic NEW260 evaluates string/object selectors once and captures the
class before arguments, class-table updates and constructor dispatch. Parser
literals, later compiled keywords and runtime names keep distinct scope/error
behavior; fetch/access lines stay separate from constructor call lines. Immediate
caller records authenticate recursive constructors; completed cold-table history
retains nonowning scope after a rebound Closure retires. Source26/compile3 and
retired83/recursive46 pass at0091; affected source3 at a65 and new2 plus
contexts51/rebound45 at3f817 retain separate cuts. Actual6af8/252/263 composition
at26fba passes cached trait METHOD/clone source1 and34 scope premises with lexical
HostA and unrelated called HostB. The [ledger](coverage/semantics/dynamic-new-review.json)
preserves original failures and preparation-only checks. Ordinary named keywords are covered by267; autoload and complete core stay open.

Cached property method callables (module263) now create source Closure children
with authentic lexical scope and a separate, potentially unrelated called class.
Copied full method/receipt authority survives wrapped or plain-clone maker
retirement without owning those makers. Static and receiver-free nonstatic
children, child clones and private `new self` defaults preserve these scopes.
Two normal source agreements pass at aa899; static105 premises pass at9ae61 and
default65 atb8d10. Original fixture parse/elaboration stops remain zero-credit in
the [default ledger](coverage/semantics/deferred-static-defaults-review.json).
Wider transformed callable creation contexts remain required; complete core and
paused return verification remain open.

Current Closure/binding253 returns the exact immediate ordinary Closure and
preserves existing-object `__invoke` capture identity. Transformed fake bindings
keep frozen permission and source statics while owning only their new receiver;
internal REAL copies and returned children retain genuine scope after makers
retire. Static API receivers add no argument-evaluation owner. Selected warnings
preserve scope/error order and unwind callback writes. Source24 normal at distinct
cuts, nine owner/frame fixtures444 conditions (author214/independent230), affected
older identity3/37 and private AL237 pass. Actualc139 preserves246 modules and
passes AL247 plus one inherited property-default source: REAL current/`__invoke`
identity and private fake binding/clone permission, called scope and shared statics.
Original compiler, source and fixture failures,
the global-constant Unsupported control and native-only controls remain separate
in the [ledger](coverage/semantics/closure-current-binding-review.json).
The [contract](docs/semantics/CLOSURE-CURRENT-BINDING.md) keeps temporary-current
escape and further API/keyword consumers required. REAL warning/unbinding is
covered separately by264 above. Return verification stays paused and complete
core remains open.

Object defaults (module252) now create static/no-use source Closures and
function/method callables in genuine declaring scope. Requested-class templates
share their object values with instances and preserve exact successful bindings
across late inheritance, retry and reentry; arrays copy containers and share
embedded objects. Nonowning receipts/copy certificates reject foreign transfers
and survive source retirement, including plain clones. Nine normal source
agreements retain 0d0d (first2)/0e472 (other7); six programs/335 premises retain
0e472/72d5.
One actual238 trait-import source and98 premises pass at a502: cached private
method/function targets keep their first authentic lookup, while each property
uses its own publication prefix and fresh called class. All original compiler,
permission and fixture-seek failures remain separate in the
[default ledger](coverage/semantics/deferred-static-defaults-review.json).
Other object/default producers and consumers remain required; complete core and
paused return verification remain open.

Nested coalesce-assignment262 now owns quiet row values on defined CV-rooted
array chains while the memoized write walks current storage. Computed keys run
once; variable keys stay live. Prefix copy-abort creates a genuine temporary,
while final-key abort skips a delayed RHS CV. Late keyed RHS warnings follow
entry acquisition, write captured null through handler throw and recheck a live
typed cell at the restored emitter. Author9/233 and independent11/277 share two
originals, giving18 unique private programs/510 assertions atf9/2b65/cf7. The
independent tail check found and verified the late-dispatch double-pop fix; only
five affected sources and84/76/76 states were renewed. One actual6013 source
at9ac retains private Owner/Child selection, quiet row17 versus new parent13 and
live caller/static17. Original fixture/loader failures and native prediction
corrections remain in the
[nested coalesce ledger](coverage/semantics/nested-coalesce-review.json).
Wider memoized containers, wider GLOBALS consumers and earlier
container/string/object producers remain required; complete core and paused
returns remain open.

Nested unset and append255 now suspend defined CV-rooted array walks after key
and computed RHS evaluation. Intermediate unset separates before conversion,
latches missing keys as null and skips the next deprecation if the table dies;
ordered float notices share one protection. Final unset keeps its distinct rules.
Append copy-abort retains a genuine null temporary and the computed RHS. A late
missing RHS captures null, checks the old table's liveness, and can insert into a
rebound real child even before propagating its handler's exception. Key-handler
throws still stop the append and preserve typed destinations. Author6/247 and
independent18/356 share the retained expiry original, giving23 unique private
agreements at7ee/d281/643/75c8. One actual0b private-FCC/called-class source passes
at223 with abort/TEMP and live typed caller/RHS cells. Original overlap and
corrected native/source predictions remain in the
[tail ledger](coverage/semantics/dimension-tail-review.json).
Wider memoized containers, wider GLOBALS consumers and earlier
container/string/object producers remain required; complete core remains open.

Legacy dollar-curly compiler notices258 retain the direct/computed grammar flag
through checked fresh printing and emit before child compilation with its real
path and the preceding compiler line. Main/include delivery reuses230 whole-unit
publication, genuine private emitter scope, live mask/display fallback and throw
cleanup. Five exact source/profile comparisons, SL242, 24 syntax/encoding profiles
with320 checks and37 compiler/certificate premises pass atfa084. Actual256 parent
preservation keeps243 modules without renewing those cuts. Original compiler and
fixture parse stops stay zero-credit in the
[ledger](coverage/semantics/dollar-curly-review.json). The early-eval effects pin
passes with236 at5cf39c0dd; the other four originals first pass with275 at4293f196. Wider
interpolation and file-observer gaps remain open;261 separately closes the old
non-object-cast holder pin at its recorded cutoff.

Dynamic object `::class`256 evaluates one child and returns its real class name
without a string cast. Eager parser concat keeps literal/keyword behavior; later
compiled constant operands reject. Embedded undefined-CV callbacks keep captured
null, including a throwing handler retained as the new TypeError previous chain;
dimension throws keep ordinary abort behavior. Source20 and seven full compiler
rejections pass at026ba, with165 reached premises in43+70+52 groups covering actual
lines, task/source admission, temporary retirement and read/exception ownership.
Unused preparation has zero execution. Original native prediction failures and
historical245 Unsupported stay preserved in the
[class-name ledger](coverage/semantics/object-class-name-review.json). One actual251
interpolation source atf626 on4208 retains callback receivers through global-slot
replacement and sees the later mutated operand. Actual247/251 routes are preserved;
complete core remains open.

Ordinary string interpolation251 now follows effective CAST/FAST_CONCAT/ROPE
order. Two-part fetched temporaries survive left callbacks; later variable
conversion reads live borrowed slots. Undefined direct CVs keep singleton null
but reread modes2+ without a second notice; callback-created arrays retain no
invented owner. Real Stringable/array callbacks, throwing cleanup and compiled
multiline lines preserve exact source/consumer/finish markers. Nine exact source
agreements and SL237 pass at88f; affected AFTER guards and111 distinct premises
pass ata7 in six unchanged groups with25 repeated setup premises. Original
fixture stops, full/fast timeouts and native-only non-object-cast line probe keep
zero credit. Actualcde/247 preservation retains240 parent modules plus251 without
renewing those gates. [Contract](docs/semantics/SOURCE-INTERPOLATION.md) and
[ledger](coverage/semantics/interpolation-review.json) retain these cuts. Wider
interpolation producers/source contexts, early eval compiler notices and affected
original dynamic-file observers remain required; complete core and paused return
verification remain open.

Ordinary Throwable reception250 now suspends weak-null/lossy warnings and
Stringable parsing for NEW and explicit inherited/scoped constructor calls.
Ordinary named-send priority stays intact; strict null/objects reject without
conversion. Successful string casts rewrite sent slots and retire old temporary
objects; integer trace arguments stay raw and fields commit only after all
formals pass. Private handlers, method retirement and recursive same-site calls
retain their own owners and traces. Source17 passes as2 at5e828 plus14+1 atb6cac;
141 ownership premises pass in71+70 partitions, and recursive29 passes at e6f71.
Thirteen repeated dependency bindings add no behaviors. Original overlap,
consumer-forgery and fixture failures plus the whole141 timeout stay preserved in
the [reception ledger](coverage/semantics/ordinary-throwable-reception-review.json).
Actual246 template/generic-EMIT composition1 at98c passes on ab5d; latest238/249
are preserved on e2e6 separately without renewing private gates. Complete core
remains open.

Callable default/variadic reception248 now suspends keyword/compound lookup in
actual receiving frames. Deferred class-constant defaults, named-hole preparation
and supplied/variadic operands keep their distinct order and ownership. Referenced
methods/current operands remain live, including borrowed retired arrays. Failed
lookup checks constrained sources before slow scalar fallback; lossy warnings
freeze their result and dual-role objects still invoke Stringable. Source23 normal
and one literal compiler rejection retain758/018/060 cuts; two affected221 sources
stay separate. Author116, independent180 and affected old hole35 conditions pass
on018. Actual99a composition keeps created-child default scope after a foreign
capture retires and passes AL236. Original compiler/fixture failures stay preserved;
RuntimeException Unsupported controls have zero agreement. The
[contract](docs/semantics/CALLABLE-RECEIVES.md) and
[ledger](coverage/semantics/callable-receives-review.json) retain these cutoffs.
Other internal and user-return consumers remain required; return verification
stays paused and complete core remains open.

Stringable include/require operands now convert before resolution and once
checks, retaining the receiver through rebinding and nested eval. Callback writes
determine subsequent CWD/path lookup; throw completes without file facts or a
provider nonce. Failed-open handlers resume ordered warning phases, sampling the
second message after callback1 and preserving saved owners and zero-argument
file traces. Exit, fatal and compiler-stop drops retire only their actual warning
owner; frozen output precedes shutdown callbacks. Fifteen exact source agreements
retain dcb/49/b371/dc9/4639 cuts; 81 conversion, 148 grouped warning and 45 shutdown
premises pass at their recorded revisions. SL229/231/233 stages/init also pass.
Actual f410/245 preservation retains 234 modules without renewing those gates.
[The file operand ledger](coverage/semantics/file-operand-review.json) keeps
original observer, fixture, model and timeout failures. Wider interpolation,
providers/source contexts and request lifecycle remain required.

Anonymous Closure/arrow default NEW245 resolves self/parent using the genuine
receiving lexical scope, independently of called class and receiver. Rebinding,
temporary Closure::call, imported trait makers and missing-scope errors preserve
argument order and private constructor access. Source11 passes as3+6+2 at89fe;
owner172/recursive97 pass at2d7fd, including callback retirement, same-template
saved scopes and public task/source rejection. The original object `::class`
observer remains Unsupported with zero agreement; reduced instanceof observers
retain the default behavior. Original descriptor and fixture failures stay in
the [scope ledger](coverage/semantics/anonymous-default-new-review.json).
Actual239 child composition1 at1b593 passes after temporary maker/receiver
variables retire; the child retains its receiver. Latest231/234/230/242 routes
are preserved without renewed private gates. Ordinary Throwable effects are
covered by250 above; object `::class` is covered by256 at its separate cutoff.

Writable dimension keys242 stage defined mutable CV-array W/RW fetches through
undefined/null/float/NaN callbacks, nested acquisition, updates and direct
assignment/compound consumers. Separation precedes conversion; callback-created
copies abort acquisition while real cell aliases and moved sole keepers preserve
it. Borrowed inner rows retire with their parent; aborted intermediate fetches
retain one genuine unnamed null cell. Delayed RHS CV demand follows successful
conversion. Direct GLOBALS W and named reference sends preserve selected names,
fetch/mapping priority and callable/earlier-argument owners. Throws retain the
old typed destination and previous chain. Author11 source agreements/340 reached
assertions include two independent originals; independent15 fresh agreements/266
assertions retain those two separately, giving26 unique private agreements. One
actual3b622 composition source at6ae passes private-handler/called-class and typed
caller alias/introspection behavior. Accepted231/234 routes are preserved. The
[contract](docs/semantics/SOURCE-DIMENSION-WRITES.md) and
[ledger](coverage/semantics/dimension-write-continuations-review.json) retain
original failures, revisions and the current adapter reuse. Bounded GLOBALS RW
is covered by269 above; earlier container/string/object producers remain required.

Coalesce-assignment and final unset keys249 now stage defined direct CV-array
consumers. Quiet reads retain captured values and genuine memo operands; live CV
and computed keys keep distinct later demand. Actual read/write lines, copy-induced
write abort, delayed RHS suppression and retired-storage reinitialization are
preserved. Unset keeps ordered float protection and deletes callback-shared tables
by liveness while real cells survive. Author6/255 and independent10/216 share one
multiline original, giving15 unique private agreements at cfb/ab7. Two reduced
actualab5 trait-handler sources pass at f5/ea: private selection, Child called
class, read11/write8, copied-table abort/deletion and shared typed caller cells.
Combined and first reduced coalesce CLI60 timeouts retain zero agreement. The
[contract](docs/semantics/SOURCE-DIMENSION-EDITS.md) and
[ledger](coverage/semantics/dimension-edit-review.json) keep original cuts and
native prediction corrections. Nested unset and append are covered by255 above;
wider memoized containers and other producers remain required.

Shutdown registration231 caches callable selection, private/rebound permission
and copied arguments after all argument effects. Ordered callbacks run after
normal, exit and fatal/uncaught paths, including serviced compiler failures.
Append, handled throw, exit override, weak/default/variadic reception and internal
send-warning continuations preserve selected targets and native owners. Frozen
fatal diagnostics precede the queue; effectful default message warnings finish
the builtin cache before pending exception dispatch. Exact registered and
converted argument views remain separate. Existing176 user formatters retain their
C return-warning continuation after handled throws; actual237 freezes the live
display destination after formatting. Imported trait makers preserve using scope
and physical provenance after retirement. Fatal snapshots retain runtime/compile
severity before callback mask writes; actual240 default reception retains its
warning and Stringable owners. Author checks cover 29 source tuples and 149 state
assertions; independent checks cover 77 tuples and 559 assertions. Each keeps its
recorded revision, and production stages pass on the accepted fe51 parent.
[Contract](docs/semantics/SOURCE-SHUTDOWN.md),
[author/composition record](coverage/semantics/shutdown-functions-review.json),
[independent ledger](coverage/semantics/shutdown-function-review.json).
Keyword/compound ingress now uses the staged247 consumers below. Request-stage
destructors and ordinary eager releases are covered separately above; GC, output
buffers and queue release remain required.

Internal default reception240 now suspends weak-null and lossy integer warnings
through real error dispatch and invokes genuine Stringable callbacks in formal
order. Raw integer slots and rewritten string slots preserve internal constructor
traces, with the nearest saved owner through reentrant handlers. Exact source14
atd9 and builtin/fallback2 at7c pass; all185 reached premises at7c pass in unchanged
133+24+28 source groups under120-second caps. The original full185 timeout and
first-source interpreter overlap remain preserved. One composition source at
e7ec retains imported trait Stringable ownership and handler-mutated display
fallback after the filename global retires.
[The reception ledger](coverage/semantics/internal-default-reception-review.json)
records these cuts.
Ordinary constructor effects are covered by250; anonymous keyword defaults
are covered by245 above.

Trait method composition228 supports source use, nesting, precedence, aliases,
visibility/final and abstract requirements in Zend's publication order. Imported
class/alias identities retain physical body provenance, using/called scope,
defaults, static cells, captures, Closures, goto/eval and finalizer ownership.
Failed declarations restore unpublished tables; compile warnings and direct
trait-call deprecations retain their phases and callback ownership. The
[trait ledger](coverage/semantics/trait-methods-review.json) keeps the63 source
union, separate controls and252 conditions at their actual revisions, including
original failures. Actual227/232/239 composition adds nine source comparisons and
127 state premises at separate cutoffs: saved default constructors, cold selected
references, physical interface diagnostic files and imported-maker Closure scope.
Accepted233/237 routes remain preserved; the method checkpoint remains partial.
Ordinary class-owned abstract scoped calls now reject before argument evaluation,
with access errors preceding abstract rejection and concrete/trait-warning dispatch
unchanged. At `a962cef07`/354 over `aa8ebb4d1`, strict algo/struct pass3.719/4.673s,
one normal source and24 supplied clauses plus6 setup pass (5.220s). Nineteen
clauses check the genuine rejection and all four validators; five helper-only
clauses check access/nonstatic priority and concrete dispatch. Raw evidence
under current19 `.tools/` is `method-runtime-ciqhcicl`,
`closure-call-protocol-98d5klby`, `trait266-object-algo-u5b6vb34` and
`trait266-object-struct-e68x39kk`; baseline interpreter failure `4rvh0zjs`
retains zero agreement. Source-profile recording now preserves legacy argv/text
metadata and merges dictionary profiles; five representation checks pass without
semantic reruns. Wider method/core obligations remain open.
The reviewed355 projection `da11ceff4` over `035bbe2de` passes strict
algo/struct at3.719/4.823s, preserving current storage and bound-constructor targets.
Source1/24 bridge unchanged; raw compiler evidence is
`.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-vgui9wdk`
and `trait266-object-struct-p9t_dgxh` in the same directory.
Concrete nonstatic scoped calls now check access before a missing-receiver Error;
literal constructor calls bypass ordinary method access/abstract lookup, preserving
the constructor opcode arm. At `0c48e90f3`/356 over `4563a5bf9`, strict algo/struct
pass3.770/4.770s. Two new normal originals and34/20 supplied clauses plus6 setup
per case pass (5.269/5.319s):40 genuine clauses cover actual rejection/no argument
or allocation effects and all four global validators;14 clauses are helper-only
flag/source probes. The protected-call baseline mismatch `7bc1r1bg` remains zero
agreement. Raw current19 `.tools/` evidence is `method-runtime-y4klgpdm`,
`method-runtime-cn0j7jql`, `closure-call-protocol-pxes1q9x`,
`closure-call-protocol-5t_9yrp5`, `trait266-object-algo-4_69i9m4` and
`trait266-object-struct-z558o98n`. Prior abstract/failed-owner sources and states
are unchanged and not renewed; wider method/core obligations remain open.
Final356 projection `e65e35e2a` over `43890afab` passes strict algo/struct at
3.869/4.871s, preserving current assertion/Generator fields and dispatch.
Source2/34+20 bridge unchanged; raw publish19 compiler evidence is
`.tools/trait266-object-algo-l1ao1xno` and `trait266-object-struct-qztdz26_`.
Literal private constructor denial now precedes receiver compatibility even for
an unrelated active object. At `f515fd26b`/356 over `976a55232`, strict algo/struct
pass3.769/4.770s; one new normal original and24 genuine clauses plus6 setup pass
(5.773s), including the live receiver, exact rejection/no argument effects and
all four global validators. Current19 raw evidence is `method-runtime-seg05ujm`,
`closure-call-protocol-2hk6y4ou`, `trait266-object-algo-c7g31qwq` and
`trait266-object-struct-g7x1yycz`; original normal mismatch `2oh2ovm1` retains
zero agreement. Prior constructor/protected/retained-FCC cuts are unchanged.
Final356 projection `4366f4cae` over `02bff2460` passes strict algo/struct at
3.769/4.823s, preserving current storage-release guards. Source1/24 bridge
unchanged; publish19 raw compiler evidence is `trait266-object-algo-n0wtdaju`
and `trait266-object-struct-prg8u30p` under its `.tools/` directory.
Inherited private constructor errors now name the requested class while retaining
the declaring-owner access proof. At `4c3ece53d`/357 over actual `cbdb9d10a`,
strict algo/struct pass3.772/4.821s; one new normal original and28 supplied clauses
plus6 setup pass (6.123s):26 genuine clauses cover inherited selection/rejection
and all four globals, while2 helper-only clauses check the other Error consumer.
Current19 raw evidence is `method-runtime-svn8anig`, `closure-call-protocol-66s2dn57`,
`trait266-object-algo-zgrybsbw` and `trait266-object-struct-n2_844cu`;
original normal mismatch `s0r3su65` retains zero agreement. Prior constructor
cuts are not renewed; current375 collector/task fields remain preserved.

Ordinary scoped calls without an effective constructor now preserve Zend's
constructor arm: literal and folded names raise `Cannot call constructor`,
while computed names retain the undefined-method Error before arguments.
Two safe originals and distinct17+17 genuine SL premises pass at `fbab085b0` and
`87618a93e`/358, with no argument/allocation effects and all four validators.
Strict compilation passes; the original baseline mismatch and unreached computed
fixture remain zero credit. The corrected fixture uses the authentic live CV.
[The focused ledger](coverage/semantics/missing-constructor-review.json) retains
the separate cuts. Actual `d47aee7c3` composition at `6e462b5e`/359 passes strict
SL in 4.801s with zero runtime/source credit, preserving ASSERT/INI and GC/PROP
interfaces. Private sources/states are not renewed; wider method/core stays open.

Deferred trait parameter constructors now preserve their selected scope across
class-table initialization, including actual arguments, constructor choice and
source line. Independent actual1fa6af571 compiler gates, one fresh ordinary source
and38 supplied reached checks (6 setup) pass on the accepted40e3 foundation without
307. Genuine constructor allocation, capture retirement, durable table history and
post-retirement property iteration are covered. Earlier unpublished-FCC/count
originals keep their separate Unsupported/private results and zero transferred
agreement; no whole trait-family or paused return closure is claimed.

Trait data238 composes constants and properties before parent inheritance, with
scoped invariant types, evaluated pure compatibility, source keyword diagnostics
and full using-class member identities. Inherited statics share cells; explicit
child reuse resets the original default. Owning instance templates246 preserve
importing scope independently of the live caller and retain array copy-on-write.
The [data ledger](coverage/semantics/trait-data-review.json) records72 source tuples
and265 genuine state assertions at preserved cuts; four historical dependency
controls retain92 assertions and zero old-cut agreement. Runtime link fatals keep
native severity, reporting masks and declaration phase. Further effectful collision
evaluation, readonly storage and enums remain
required; this checkpoint does not close the trait family.

Raw trait static-property warnings254 follow lookup, access, table fill and typed
read priority. Retained source/root/member/mode resumes the live cell through
handler rebinding. Computed RHS values keep one store owner; compiled literals
also retain their pool owner. Late CV values remain delayed. Handler throws still finish
the actual write/update/reference opcode, while fetch-only reference promotion
aborts later assignment or call. Typed/Stringable conversion preserves pending
exceptions. Independent source33 (author6 subset) and six reached state groups286
pass at unchanged15155; preparation and incorrect owner assertions are retained
without extra credit in the [access ledger](coverage/semantics/trait-property-access-review.json).
Actual accepted core routes, including258, are preserved in244 modules without
renewing those cuts. Wider effectful collisions, readonly storage and enum
semantics remain required; the trait family stays open.

Trait collision recording259 compares deferred operands before typed table
conversion and records direct `E_STRICT` diagnostics during the source-owned
linking fold. Constants demand incoming then existing values; properties reverse
that order. Successful publication precedes live handler delivery; a handler throw
keeps the composed class. Later link fatals flush recorded diagnostics without
calling user handlers. The [collision ledger](coverage/semantics/trait-collisions-review.json)
retains14 source tuples (11 normal/3 PHP errors) and97 reached queue/callback
guards at their original cuts. Generic arithmetic/key recording now isolates
scratch handler/display settings and follows runtime key→value→insertion order
with checked AST lines. Five affected source comparisons (four new plus one
existing array neighbor),47 additional queue/array-owner guards and bounded
AL/structure checks pass. Private-final compile warnings now join the recorded
batch at concrete/abstract binding phases and remain handler-ineligible128. Four
affected source comparisons (two new and two128 mask neighbors) and43 genuine
alias/queue guards pass at their separate cuts. Module266 binds referenced
deferred constants in their real declaring scopes before strict comparison,
retaining typed caches between operands and distinct full import identities.
Ten normal source comparisons and201 unique cache/owner/lookup-chain guards pass;20 repeated setup checks add no coverage.
Module274 stops copied expressions at their first Error, default-flushes prior
diagnostics and renders the pending exception before a no-trace composition fatal.
Ten PHP-error sources and156 reached failure/cleanup checks pass, with ten separate
formatter checks. Held-primary reporting uses the genuine failed-class route275;
one actual source and112 reached replay checks pass at separate cuts. Direct and
two-hop cyclic lookup errors now use full imported identities; two PHP-error
sources and87 reached chain/cleanup checks pass at their separate cuts. Hard failed
links now retain dependency caches owned by already published classes and retire
unpublished import caches with their array owners. Three PHP-error sources and194
supplied reached restoration/history/ownership conditions pass; six generated setup
checks are separate. A source-rederived failure marker authenticates retention
without publishing the failed class. The same disposition after a reported
initializer Error adds three PHP-error comparisons and188 supplied reached
cache-cause/cleanup checks, with six generated setup checks separate. Failed raw
trait composition adds three PHP-error comparisons and68 supplied source-kind,
cache-owner and rollback conditions; three generated setup checks are separate.
Direct trait-constant denial precedes dependency evaluation. Held/open compilation
and wider object-bearing dependencies remain required. Published Closure/FCC
dependencies now use real initializer/binder contexts, source/receipt value flow
and captured-prefix array/DIM proofs. Seven source comparisons agree (five normal,
two PHP errors); five genuine reached source/flow/ownership groups pass409 supplied
conditions, with15 generated setup checks separate. Exact cuts and the retained
DIM-dispatch failures are in the collision ledger.
Real callable-initializer expression Errors, typed rejection and array-key TypeError
now use actual Throwable fields and demand traces, keeping completed nested caches
while retiring failed owners. Four PHP-error comparisons pass atf780; four reached
groups pass678 supplied source/context/registry/cleanup conditions atba2/d33, with12
generated setup checks separate. The retained handler graph survives scratch cleanup.
Cross-file constant collision typed demand now preserves the executing class file,
physical fetch line and genuine constant-expression frame. Two PHP-error comparisons
and one reached group/139 supplied conditions pass, with five service/setup checks
separate. Wider initializer contexts and unpublished-owner FCC births remain required.
Traits stay partial.

Modules290/297/299 preserve source/collision/prefix authority for unpublished REAL
Closure births, retire failed import owners while retaining only dead receipts,
and reserve the earliest fatal trait class name before later binding or autoload.
Returning link Errors permit retry. Original author/reviewer cuts and failures stay
separate in the collision ledger. Actual313 at `cc9411c1e` over310/`064d382d` passes
strict algo/struct and one new pinned REAL/default-constructor original, with exact
`H;CALL;CTOR:7;C:C:C;AFTER;C:C;` at unchanged45/55 limits. One genuine strict-SL group
passes46 supplied conditions plus6 terminal-aware setup clauses: actual REAL
birth/cache/receipt, selected constructor7 allocation and capture retirement with
the REAL authority still live. The current constructor/default/Generator/Fiber/source
fields are retained. Module307 now reconstructs exact source method copies at the
first target's declaration prefix to validate failed FCC births after rollback.
Dead receipts and pure history replay preserve the first target without publishing
its owner or admitting a live callable. Focused source2 retain exact output/error
bytes and exits; strict-SL failed-import53 and equal-scope34 supplied conditions pass,
with12 setup clauses separate. Raw evidence is under the private
`.tools/trait-selected-constructor-current/.tools/`: `closure-call-protocol-y5x1pwdf`,
`closure-call-protocol-v81oh3gj`, `method-runtime-87l_y5f5` and `method-runtime-a2gromik`.
The first failed source's recorder label is corrected from static rejection to
runtime PHP error; its already completed duplicate adds no coverage. These focused
cuts bridge to the reviewed current composition without renewal. The322 cut at
`4c03c177d` over `f89fbee74` passes strict algo/struct at3.369/4.270s and a genuine
active DEFAULTRECEIVE/TYPE checkpoint with26 supplied conditions plus6 setup clauses
at36.874s. It preserves canonical code/default/return/static identity and rejects a
forged receive owner before the actual old-U constructor Error; no whole-source or
unwind coverage is claimed. Current raw evidence is under
`.tools/trait-fcc-parameters-composed-19/.tools/`: `trait266-object-algo-2riubhjo`,
`trait266-object-struct-k27i1h7p` and `closure-call-protocol-yveph8_d`.
The323 composition over EX338 tightens receipt access to the unfixed exporting
trait's scope. At `77d34fc10`, strict algo/struct pass3.419/4.370s and private/protected
forbidden-receipt checks pass68 supplied conditions plus12 setup clauses. Their native
originals confirm access Errors before the property fatal; they add no source-agreement
credit. The affected public failed-birth53 conditions plus6 setup clauses pass11.734s.
Raw artifacts are `trait266-object-algo-s6o6pssf`,
`trait266-object-struct-n4p5pbmw`, `closure-call-protocol-10bjo22b`,
`closure-call-protocol-08sz3xg1`, `closure-call-protocol-q5w3a8qt` and
`fcc-access-review19/native-*` under the same current
worktree's `.tools/`.
Live concrete alias/visibility lookup now uses the exact source copy plan only
when ordinary import lookup misses. At `6470366fa`, strict algo/struct pass3.469/4.322s;
three normal source tuples and one genuine birth/default/static checkpoint with44
supplied conditions plus6 setup clauses pass (18.696s). Cloned aliases share their
canonical static cells while own methods and excluded originals keep distinct targets.
Raw evidence is `.tools/trait-fcc-adaptations-current19/.tools/`:
`method-runtime-rbmzbjug`, `closure-call-protocol-tb4117ep`,
`trait266-object-algo-wqm4aoeh` and `trait266-object-struct-2n7pfvr6`.
The reviewed327 composition at `1f6313f7e` over `e044ff7cb` passes strict
algo/struct at3.369/4.220s without renewing those source/state cuts. Its raw
compiler results are `trait266-object-algo-gtfakyej` and
`trait266-object-struct-d2ofi_zz` in the same evidence directory.
Later failed FCC imports retain the exact cached target of an already published
first owner, with their own called class and source/collision prefix. At
`494f6b34f`, strict algo/struct pass3.369/4.220s; one PHP-error source comparison
and68 supplied conditions plus6 setup clauses pass (17.433s). The genuine C-to-E
failure preserves C's live cache, retires E's owner and rejects a fresh E method,
forged call scope/prefix/history and live resurrection. Raw evidence is under
`.tools/trait-fcc-later-birth-current19/.tools/`: `method-runtime-ekmhst3r`,
`closure-call-protocol-7846p_2q`, `trait266-object-algo-reoln7u9` and
`trait266-object-struct-s86zgxqr`. A missing watched runner symlink stopped the
first state invocation before numeric execution; that infrastructure failure is
retained without semantic credit.
These unchanged cuts bridge to the reviewed328 composition, preserving bound
callback RAW/INPUT, caller ownership and source fields.
Module347 retains exact first-failure method metadata for later genuine FCCs,
without restoring the failed class's imports, publication or retired live value.
Three shutdown originals cover an imported target, an own/private target and an
alias absent from the later published class, preserving literal defaults and
clone-shared static cells. The imported tuple passes at `6985967dc`; the own tuple
and69 supplied conditions plus6 setup clauses pass at `297715fb6` (29.446s), after
prefix-aware cache dispatch and the shared `039abc623` handler-context fallback.
Raw evidence is under `.tools/trait-fcc-failed-target-current19/.tools/`:
`method-runtime-w4gfa3m7`, `method-runtime-j2l114gl` and
`closure-call-protocol-v8z8eaza`. The original own/state failures
(`method-runtime-w4gfa3m7`, `closure-call-protocol-x00j9n0z`) and alias failure
`method-runtime-q6upsv1_` remain preserved without passing credit.
At the reviewed332 composition `f19c12d66` over `9d1956cd5`, strict algo/struct
pass3.419/4.370s; the alias tuple and46 supplied ordinary-receipt/scope conditions
plus6 setup clauses pass (23.352s), including declaration, call and heap validators.
Raw evidence is `.tools/trait-fcc-failed-target-publish19/.tools/`:
`method-runtime-yzmgrx7y`, `closure-call-protocol-9bii28x9`,
`trait266-object-algo-txlrnwr9` and `trait266-object-struct-zc6hpeu2`.
The earlier source2/69 cuts bridge unchanged; current source, Generator,
ArrayAccess-certificate and pruning-graph fields are preserved.
The final334 composition `5ebf803b2` over `86e7f6ccb` passes strict algo/struct
at3.519/4.370s (`trait266-object-algo-l0tbn4ov`,
`trait266-object-struct-npafxy47` in the same publish evidence directory).
Typed-property retirement and bound Fiber-start ownership remain unchanged;
the source/state cuts bridge without renewal.
Later failed imports also authenticate the first target after its owner failed,
at the later birth prefix while retaining the published-owner path. Both
Closure records stay dead and neither failed class is published. At `070170525`,
strict algo/struct pass3.519/4.371s; one shutdown PHP-error tuple and59 supplied
rollback conditions plus6 setup clauses pass (29.959s), including declaration,
call and heap validation and source/prefix/called/resurrection inverses.
Raw evidence is `.tools/trait-fcc-failed-target-current19/.tools/`:
`method-runtime-49mdsmg6`, `closure-call-protocol-a6halclw`,
`trait266-object-algo-eolich9z` and `trait266-object-struct-je7sw7n_`.
The reviewed EX/SOURCE336 composition `8b47bee97` over `b4f1e6175` passes strict
algo/struct at3.469/4.420s (`trait266-object-algo-pemw9ni4`,
`trait266-object-struct-bjiml5w8` under the publish evidence directory). Its
GC.SCAN schema and caller/source fields are preserved; source1/59 bridge unchanged.
Failed imported first targets distinguish successful data binding followed by abstract
verification failure from a failure before method-scope fixup. Exact historical
data replay selects the fixed C scope or the known unfixed trait scope; an unknown
phase denies cached selection without substituting the later class's method.
Only scratch replay reuses the authenticated direct FCC value. A live retained
FCC can evaluate `self::class` for its failed lexical owner without publishing it.
At `6f76ae9fd`/339, strict algo/struct pass3.719/4.570s, one shutdown PHP-error tuple
and59 supplied conditions plus6 setup clauses pass (49.848s), including genuine
static installation and all declaration/call/heap validators. Raw evidence under
`.tools/trait-fcc-failed-target-current19/.tools/` is `method-runtime-fag72wcy`,
`closure-call-protocol-2k36nias`, `trait266-object-algo-b1gh0tol` and
`trait266-object-struct-izuh_dgb`. Earlier Unsupported/timeout/interpreter failures
(`uh6igkol`, `xf7jjsk7`, `ppfvuqw4`) and the rejected synthetic own-root fixture
`1f6_ozo9` retain zero agreement. The native-warning catalogue transcription was
corrected from preserved raw stderr without repeating PHP. Callbacks after fixup
but before the failure marker remain open.
The reviewed344 composition `0db3c85b5` over `c527549353` passes strict algo/struct
at3.619/4.420s; these source1/59 cuts bridge unchanged. Current GC/Fiber/source
fields and static-compound selectors are preserved. Raw compiler evidence is
`.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-nke5f48d`
and `trait266-object-struct-elvmk9fw` in the same directory.
Retained `new self` now rejects an unresolved implicit abstract trait requirement
before arguments or instance allocation, using the exact copied requirements and live FCC
scope; unknown proof stays Unsupported. At `a18e91e3e`/345 over `4cd2eab3a`, strict
algo/struct pass3.569/4.469s, one shutdown PHP-error tuple and39 supplied NEW
conditions plus6 setup clauses pass (44.118s), including all four global validators.
Raw evidence under `.tools/trait-fcc-failed-target-current19/.tools/` is
`method-runtime-3w3ufl_3`, `closure-call-protocol-gbmre4ve`,
`trait266-object-algo-umrooye4` and `trait266-object-struct-o_3sgnyc`.
The reviewed347 composition `7bfa05c07` over `0ac26ef29` passes strict algo/struct
at3.569/4.522s; the unchanged source1/39 cuts bridge with current INSTANCE storage,
scoped-static selection and Generator fields preserved. Raw compiler evidence is
`.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-1knav8u7`
and `trait266-object-struct-xxwdsrqv` in the same directory.
Retained `new static` now authenticates its saved caller/source scope and constructs
the published called class. Deferred static fills keep the selected NEW certificate
instead of resolving the keyword by spelling; corresponding typed-retirement checks
are statically reviewed.
At `ba08d2141`/347 over `b03c0d918`, strict algo/struct pass3.571/4.520s,
one shutdown PHP-error tuple and40 supplied conditions plus6 setup clauses
pass (59.412s). The genuine argument-entry checkpoint checks allocation order,
completed table history, all four global validators and a forged fill certificate.
Raw evidence under `.tools/trait-fcc-failed-target-current19/.tools/` is
`method-runtime-qw3d9lht`, `closure-call-protocol-iw_iw2zf`,
`trait266-object-algo-hv4l35mf` and `trait266-object-struct-ucfu1_fr`.
The earlier genuine history failure `lqhiz3_8`, diagnostic `s0n7wcj2` and
rejected fixture inputs retain zero agreement; no assertion was weakened.
The reviewed349 composition `620c2dc38` over `07940bc4a` passes strict
algo/struct at3.669/4.520s, preserving current SCAN, source, compound-static
and Fiber fields. The unchanged source1/40 cuts bridge; raw compiler evidence
is `.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-hw829us3`
and `trait266-object-struct-h1twh_vj` in the same directory.
Own/private retained SELF now uses the same explicit data-completion proof;
equal method descriptors cannot substitute for successful data binding. At
`45f4d56df`/349 over `cea25ed85`, strict algo/struct pass3.621/4.570s,
one shutdown PHP-error tuple and44 supplied NEW/phase conditions plus6 setup
clauses pass (28.059s), including fatal/unknown denials and all four validators.
Raw evidence under the current19 `.tools/` directory is `method-runtime-wl909uqp`,
`closure-call-protocol-4ip6lkrl`, `trait266-object-algo-neuz73kp` and
`trait266-object-struct-mi7_5yec`. The imported fixup guard is equivalent;
earlier source/state cuts keep their identities.
The reviewed350 composition `55db5a21f` over `813af1719` passes strict
algo/struct at3.719/4.621s; source1/44 bridge with current callback witnesses
and stdClass storage preserved. Raw compiler evidence is
`.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-jen_5u_i`
and `trait266-object-struct-iqurkbph` in the same directory.
Explicit abstract retained SELF now authenticates the original class flags and
rejects construction even when data binding failed earlier; the implicit proof
still requires NORMAL. At `00d1acb37`/350 over `7c4a13bc1`, strict algo/struct
pass3.719/4.670s, one shutdown PHP-error tuple and39 supplied NEW/source-flag
conditions plus6 setup clauses pass (27.209s), including all four validators.
Raw evidence under current19 `.tools/` is `method-runtime-vcokv2pq`,
`closure-call-protocol-7qumzqku`, `trait266-object-algo-9ms95gjp` and
`trait266-object-struct-es2vzasj`. Earlier cuts remain unchanged.
Old trait-scoped SELF now authenticates the canonical class copy against its
published lexical trait and rejects construction with the pending NEW
certificate intact. At `0d9bde4c6`/350 over `7c4a13bc1`, strict algo/struct
pass3.669/4.670s, one shutdown PHP-error tuple and37 supplied source/scope/NEW
conditions plus6 setup clauses pass (41.881s), including all four validators.
Raw evidence under current19 `.tools/` is `method-runtime-eh0c0688`,
`closure-call-protocol-fu2_4hpy`, `trait266-object-algo-4otuss2g` and
`trait266-object-struct-qd7qmnag`. Earlier cuts remain unchanged.
The reviewed351 union `02f053676` over `4f156a297` passes strict algo/struct
at3.669/4.573s, preserving GEN request-fatal tasks and EX residual-GC fields.
Private source1/39 and source1/37 cuts bridge unchanged. Raw compiler evidence
is `.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-ucz93eec`
and `trait266-object-struct-1edjhak2` in the same directory.
Old trait-scoped STATIC now preserves the selected called class despite raw
trait-method/canonical-copy origin differences. At `2cc1fbb87`/351 over
`9782fbb4e`, strict algo/struct pass3.671/4.570s, one shutdown PHP-error tuple
and40 supplied NEW/allocation/history conditions plus6 setup clauses pass
(59.013s), including all four validators and malformed-certificate rejection.
Raw evidence under current19 `.tools/` is `method-runtime-o8ztu9z_`,
`closure-call-protocol-3yzz1hul`, `trait266-object-algo-mkqwx_04` and
`trait266-object-struct-wdvmpr1n`; previous SELF/STATIC cuts are unchanged.
The reviewed353 projection `ea6b5b5c2` over `54589b343` passes strict
algo/struct at3.719/4.721s, preserving computed-static, Generator and source
consumers; the private source1/40 cut bridges unchanged. Raw compiler evidence
is `.tools/trait-fcc-failed-target-publish19/.tools/trait266-object-algo-5o1ambud`
and `trait266-object-struct-ifvl6gz9` in the same directory.
Retained failed-class `self::n(argument())` now selects an authenticated copied abstract
method and rejects it before argument evaluation. The shared required-class proof
keeps the existing implicit SELF construction behavior; unknown phases stay
Unsupported rather than becoming a fresh named lookup. At `b40dc5c2d`/354 over
`2257ebf82`, strict algo/struct pass3.719/4.723s, one shutdown PHP-error source
and41 supplied pre-send/source/phase conditions plus6 setup clauses pass (28.598s),
including unchanged allocations/events, the exact remaining TODO and all four
validators. Raw evidence under current19 `.tools/` is `method-runtime-cl8ncs4a`,
`closure-call-protocol-rms153ed`, `trait266-object-algo-tx_skl4w` and
`trait266-object-struct-sa28i5sp`. The accepted-baseline mismatch `pynrj2xf`
retains zero agreement; previous SELF/STATIC cuts are unchanged. Parent assertion,
source, storage and collector fields remain intact. Wider failed-owner members
and broader mixed parameter-view contexts remain open.
The failed class remains unpublished; parent/interface construction contracts,
including implicit Stringable, remain required.
Three previously open full parameter-view originals now agree with PHP at
`d75312e09`/358 over `6ed4873bd`, with unchanged100000-step/45/55 limits and
preserved native tuples: constructor/default rejection, error-handler reception
and positional/named variadic Stringable conversion retain old/later/cloned scopes.
Strict algo/struct pass3.869/4.971s. The coherent change combines the shared ARG
ASCII lookup (`e9c62f818`), noncontextual/contextual property-comparison split and
existing failed-header guard order. These preserve exact bytes, bool results and
receipt authority. Unchanged97 ASCII equalities, contextual CASE28+6 and live/failed
header24+12 controls bridge; they are not rerun or new coverage. Raw successful
source results under current19 `.tools/` are `method-runtime-40mogpx6`,
`method-runtime-e03mf3zz` and `method-runtime-xp95r2ob`; compiler results are
`trait266-object-algo-mrwoqqar` and `trait266-object-struct-b53pcjvb`. The bounded
causal trace `fcc-type-trace-wh6972lv` is diagnostic-only. Separate earlier costs
(`juu9_a0t`, `26nefyt9`, `m2nj5bv3`, `zk_o28v9`) retain zero full agreement; no
single-factor speedup is inferred across cuts. Final358 projection `a68e2939b` over
`5fdc40d04` passes strict algo/struct3.869/4.820s, preserving current collector
plan/cursor fields and the unchanged source3/control cuts. Raw compiler results
under publish19 `.tools/` are `trait266-object-algo-8va4fp0i` and
`trait266-object-struct-m308jcyl`. Broader mixed parameter-view contexts, differing-owner
later births and wider failed-owner member/construction behavior remain open.
Paused return work is excluded.

Dynamic read-key continuations233 preserve selected bases/keys through missing-CV,
null/float and global-array-name callbacks. GLOBALS rereads undefined keys in the
caller environment; ordinary arrays retain their fixed converted key. Real
temporary owners and conversion protection distinguish COW, live references and
sole-table retirement; NaN keeps protection across both ordered notices. Quiet
isset/coalesce and nested temporaries keep their distinct demand/ownership paths.
Author9/246 includes the two independent NaN originals; independent14/235 passes
at its separate cut. One
actual71da constructor in a parameter default passes with private captured
handler selection, called class and authentic key line/name through root mutation.
[Contract](docs/semantics/SOURCE-DIMENSION-KEYS.md),
[ledger](coverage/semantics/dimension-key-review.json). Writable242 covers the
bounded CV-array consumers above;249 adds direct coalesce-assignment/final unset.
Nested unset, wider memoized containers, append and wider object/key/container
producers remain core work.

Prepared internal Throwable default constructors235 map completed227 values
before names, arity and sequential reception. Default declaration strictness,
finite holes and nested previous owners retain exact trace argc and ErrorException
fields. Earlier8+7/reached67 at9fa and string-slot trace2 at7fb keep their own cuts
in the [scalar ledger](coverage/semantics/internal-default-constructors-review.json);
the original count observer remains Unsupported with zero agreement.

Live `display_errors`237 retains nullable original/live INI entries and raw
get/set/Restore. Ordinary text diagnostics capture stdout/stderr/off after handler
effects, keeping their position among source output across later writes and
include retirement. Current terminal errors preserve status255 when display is
off. Ten author and one independent exact comparisons, 76 source-derived state
premises and 17 entry/transport controls pass at b8e8, alongside223-module SL
stages/init and the changed adapter build. Actualddb6/233 preservation retains
225 modules with the reviewed display and dimension-warning routes, without renewed execution.
The [display ledger](coverage/semantics/display-errors-review.json) separates
source-defined nullable controls from native profiles. The held shutdown/fatal
source matches its independent original at actual231/237 cutccd900: rendering
selects the fatal destination before queue OFF/Restore writes. This composition
has its own record; wider display, parser/profiles and request phases remain open.

Registered startup inputs225 provide original `error_reporting` and
`include_path` bytes before compilation, independently of file/CWD facts.
Getters and Restore preserve null/empty reporting, signed32 masks and raw bytes
through setters, `@` and callbacks. Restore of an unmodified reporting entry
remains a no-op even when silence leaves its live mask different from startup.
Author7 and independent2 exact profile comparisons, 99 source-derived state
premises and 15 transport controls pass at36810; that cut also passes216-module
SL stages/init and the changed adapter build. The source-equivalent actual0592
composition retains all220 parent modules plus225, with no renewed execution
credit. [Startup ledger](coverage/semantics/startup-ini-review.json).
Wider directives, startup parsing/profiles and lifecycle remain required.

Source-owned parameter default constructors227 complete lazy class tables before
allocation and evaluate every AST argument before constructor access/name mapping.
Direct/inherited dispatch preserves declaring permission, called class, default
declaration strictness and the compiled receive line. Required-reference API
warnings precede temporary wrapping; completed values and nested Stringable
receives retain genuine object/cell/frame owners. Source2/independent16 at a223,
affected cold5 at954 and reached183/affected fact2 atd441 retain separate cuts.
Actual219/222/229 composition2 at2b153 passes normal and terminal-handler paths.
Actual221 callable source1/owner39 at2a380 authenticates the suspended constructor
through deprecation callbacks and rejects a removed retained owner.
The [constructor ledger](coverage/semantics/default-constructors-review.json)
keeps original failures, the fixture line correction and fresh uncached NEW facts
precise. Anonymous keyword defaults are covered by245 and ordinary internal
constructor effects by250; complete core remains open.

Deprecated callable keyword/compound admission221 now stages supplied fixed
parameters, error registration and delayed dispatch. Warnings hold class choice
and string boundaries while rereading referenced methods; whole byref formal
replacement preserves its live value. Genuine receiving/emitting frames and a
narrow API carrier admit compound foreign-`$this` selection and declared receiver
fallback without relaxing ordinary scoped eligibility. Supplied guards exclude
authentic named default holes. Exact union branches bypass warnings; direct/FCC
raw keyword/compound calls preserve ordinary PHP lookup errors. The
[221 ledger](coverage/semantics/keyword-compound-callables-current-review.json)
records independent pins, affected checks and preserved failures. Actual include,
cold-static and GLOBALS interactions preserve real USER permission, constrained
references and captured null; initializer locations retain their declaration owner.
Default/variadic reception is covered by248 above; other internal and user-return
warning consumers remain required. Unstaged special conversion stays Unsupported.

`Closure::fromCallable`234 selects and creates durable captures over existing core
callable forms. Existing Closure inputs preserve identity; method captures freeze
live method bytes and selecting permission before raw values/makers retire.
USER admission and internal Closure getter scope remain distinct, including
foreign receiver/called-class cases. Invocation/clone retain real defaults,
source method statics and receiver ownership. Created source Closures retain
authenticated method/import scope after the parent capture retires; static
children add no receiver owner, while nonstatic children retain their bound
receiver. Imported private cold references and per-host source statics are covered.
Factory lookup-warning throws wrap only after handler/finally unwinding; argument-read throws before entry remain
unwrapped. [Contract](docs/semantics/FROM-CALLABLE.md),
[review ledger](coverage/semantics/from-callable-review.json).

Iterator224 adds compatible explicit declarations and inherited internal
obligations for source by-value foreach; callbacks use
effective runtime methods and retain the iterator/current result through key and
body. Independent source26 confirms callback order, reference results, ownership,
lexical/called scope, inherited signatures and source-interface priority at its
two recorded cutoffs. Author source5 and owner125 retain their original results.
Cursor checks enforce unique live continuation and metadata IDs below `NEXTITER`;
cursor49 and claim85 pass separately. Independent source1/reference63 and affected
fatal teardown38 pass with unchanged87d semantics; the latter corrects only a
fixture line binding. On accepted2e8, source12 passes control cleanup, arbitrary
keys, assignment priority, covariance and the remaining throwing callback stages
at284803284. Independent source1/protocol16 at the same cutoff confirms zero-argument
Stringable default reception. Earlier results and original failures remain preserved.
IteratorAggregate, ArrayAccess and remaining reference/ordinary object traversal
remain required after the early-eval diagnostic work. [Scope and boundaries](docs/semantics/ITERATORS.md).

Direct missing `$GLOBALS[key]` R-fetches226 dispatch before their consumers and
retain the original null through key/global mutation. Handler throws skip later
ASSIGN/SEND, preserving typed destinations and the original exception chain.
Quiet/reference acquisitions keep their existing real cells. Genuine76 whole-table
snapshots under explicit request facts preserve numeric keys, singleton unwrap,
shared reference owners and COW after global retirement. Author8/207 and
independent8/221 pass at distinct private cutoffs. Two current derived sources
on accepted ed6 pass at bb90, retaining private first-class handlers, called class,
eager identity reads and a cold typed static alias. The combined observer retains
its inconclusive CLI60 timeout. [Contract](docs/semantics/SOURCE-GLOBAL-WARNINGS.md),
[ledger](coverage/semantics/global-warning-reads-review.json).

Exception handlers222 retain nullable raw stacks and dispatch an uncaught
Throwable after `finally` through the ordinary weak call receiver. Genuine null
caller and saved-frame certificates preserve one argument, selected targets and
owners through restoration, replacement, nested warning handling, throws and exit.
Author29/216 and independent33/331 retain their distinct source cutoffs; two
explicit Unsupported controls add no agreement at their original cut. Actual219
composition preserves
cross-file diagnostic origins during static defaults, and production algorithm
and structure checks pass. [Contract](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md),
[author/composition record](coverage/semantics/exception-handlers-review.json),
[independent review](coverage/semantics/exception-handler-review.json).
Module247 supplies the effectful keyword/compound registration and terminal
selector through shared221 stages. Exception stacks retain raw values; shutdown
entries freeze the selected target after referenced-method warning effects.
Borrowed producer target/callsite/scope certificates preserve genuine ordinary,
C-handler, Stringable and Closure maker permissions after retirement.
[Author/composition checks](coverage/semantics/callback-api-consumers-review.json)
cover40 source tuples and140 reached assertions; the
[independent review](coverage/semantics/callback-api-consumer-review.json)
covers34 tuples and474 assertions at its own cut. Actual-parent getter Error,
trait/default and retired capture interactions pass; production algorithm and
structure checks retain the237-module cut. Accepted238/249/250 source preservation
adds no execution credit. Destructor/GC/output/free request phases stay open.

Called-class introspection223 implements `get_called_class()` using the active
authenticated called class. Plain functions and global Closures stop lookup;
captured/rebound source Closures retain their own class, while explicit builtin
Closure wrappers return `Closure`. Argument/count priority, optimized/generic
trace paths and real handler/emitter restoration are checked separately in the
[called-class ledger](coverage/semantics/called-class-review.json).

Deferred scalar/array static defaults219 retain the declaring scope, strict
property types, parent/constants/default order and first successful fills across
later failure/retry. Existing static rows own live values, arrays and typed aliases;
history stores no duplicate value. Eleven native/model agreements (seven normal,
four PHP errors) retain their original source cutoff. Five source-derived programs
accept 149 logical guards expressed as 152 sequential premises after narrow fixture
binding repairs. The [deferred-default ledger](coverage/semantics/deferred-static-defaults-review.json)
keeps original failures and unrun broader work visible. Two actual213/215
interactions at 8da51d193 retain inherited defaults through captured/private raw
handlers, captured-null cast/throwing assignment and a 214/216 Stringable receive.
Actual217 composition adds four normal agreements at 5c0887541, including saved
initializer contexts and compound callback traces, plus one cross-file fast-path
diagnostic agreement at 663811e8c. The unchanged owner41 guard passes. Module229
now supports same-default callback reentry: successful outer binding replaces
the live row, while escaped typed aliases retain ordered nonowning constraints.
Throw/type failure preserves the reentrant row; first-fill and table completion
remain once-only. Thirteen exact normal native/model comparisons and an inherited
67-premise ownership/history fixture pass at bf0954840. The earlier Unsupported
controls and declaration-order failure remain historical evidence; prior18/149
checks were not renewed. Cold static-reference continuations232 now keep the
captured RHS cell rooted through class-table initialization and reselect the live
target afterward. Immutable dynamic/ordinary method self/parent/static snapshots
survive callbacks and selected first-fill/retirement/table history. Seven exact
normal source agreements pass at69cc4546c;84 ownership/history premises pass at
0288de513 after narrow fixture syntax and selected work-block validator repairs.
Original failures remain separate; prior31/149/67 checks were not renewed.
Captured/rebound Closure keyword references239 now retain authentic nonowning
scope/binding evidence after pruning. Nested creation copies its immediate
creator's body, scope, receiver and nullable callsite, including error and
terminal callbacks; ordinary method ancestry stays exact. Nine new source
agreements and bound69 premises pass atd6bc09789; handler58/terminal35 pass at
860a8a19a after one fixture ordinal-binding repair. Temporary Closure::call child
creation now retains authentic source/receiver scope after maker collection;
nonstatic children keep the receiver and static children keep only nonowning
evidence. Five source agreements/global77 pass at e32dcc64a, affected callback81
at49d0b9579 after making ordinary/copied scope rules disjoint, and a fresh
same-class source/35 atadbfde09e: six sources/193 premises total. The original
validator failure is retained. Module246 now owns deferred scalar/array instance
templates by requested class and declaration, copies actual parent state at link
time, and fills constants, private-shadow instance layouts and statics before
allocation. Strict failure/retry and reentry retain once-only fill history;
objects copy template values and arrays remain owned after object collection.
Eight exact source agreements pass at80900fa4b; three programs/172 phase, copy
and ownership premises pass at449b45763 after a fixture source-origin binding
repair. Original compilation failures remain separate. Module252 extends these
templates to certified Closure/FCC values; other object/default producers and
wider consumers remain required.


Private and protected method arrays and class-method strings support callable
admission, selection, capture/clone and delayed error-handler dispatch. Object
selectors can redirect to the selecting parent's private method; concrete class
selectors use the requested class table. Protected access follows the root
prototype. Captures retain genuine selecting permission after makers retire,
while direct calls and API callbacks authenticate the real saved caller/emitter.
The current missing-CV assignment writes captured null through the referenced
caller argument after its private handler throws. Source1/94 stays separate from
the original author19/261 and independent16/345 checks.
The [scoped-callable ledger](coverage/semantics/scoped-callables-current-review.json)
keeps original failures and the three ordinary named-receive exclusions distinct.

Missing-CV reference sends retain the existing86/105 behavior: genuine null
cells, no warning and named-slot priority. Module220 rejects captured-null
ASSIGN through live typed aliases, retaining their value and replacing a handler
throw with a caller TypeError whose previous chain owns the original error.
At484d, author9/211 and independent5/249 pass; the latter corrects two fixture
phase assumptions without replaying passing models. The actual3919 composition
accepts one reduced scoped-handler source at5bce: TypeError context, typed caller
alias and the handler chain survive private selection and retired global owners.
The original observer-heavy source retains its inconclusive CLI60 timeout. The
[consumer ledger](coverage/semantics/warning-consumers-review.json) preserves
original failures and distinct revisions.

Warning-read consumers213 retain original null for six casts, selected copies and
ordinary by-value sends across handler mutation. Selected callees and prior arrays
keep their real owners; named-slot errors precede warnings. Direct ASSIGN writes
null even after a handler throws, before the same exception continues. Its
original rejected constrained-write control is addressed by private220 above.
Mixed author21 normal tuples/control0 and
58/60/65/53=236, plus independent10/197, retain their actual revisions and original
failures. Fresh actual6395 composition at181f separately accepts source1/94 and
independent cached-callee source1/96, covering static-reference sends, the real
outer-array prepass redirect and cached target/handler retention. Source-equivalent
publication preserves subsequent reporting, parameter backing and named-class
changes. [Consumer ledger](coverage/semantics/warning-consumers-review.json).

Fixed and variadic Stringable receives preserve receive order, captured cells,
caller strictness and backing authority; constructor-free defaults retain declaring
scope and fresh objects. Named constexpr `::class` retains source spelling and
authentic deferred/rebound lexical scope. Counts and original failures remain in
[parameter](coverage/semantics/weak-string-parameters-review.json),
[variadic/default](coverage/semantics/variadic-default-string-review.json) and
[constant](coverage/semantics/class-constants-current-review.json) ledgers and the
family table below. Internal and anonymous keyword constructor defaults retain
their235/240/245 cuts; broader attribute/modifier and callable initializer consumers
remain required.

Nonstatic private/protected `__invoke` supports bare calls, callable admission,
object capture/clone and bare-object error handlers through the effective runtime
method table. Explicit method calls keep lexical visibility. Compilation checks
parameters/body before the static fatal or nonpublic warning; inheritance access
errors retain preceding warnings. The [publication ledger](coverage/semantics/invoke-publication-current-review.json)
separates the original source/compiler/runtime checks from the current strict USER
truth-warning interaction, failures and unchanged return-classification boundary.

Method-array and class-method-string error handlers register raw values and
select afresh at dispatch. Entered targets retain genuine emitter scope, arguments
and owners through member mutation, nested replacement, throw and false fallback.
The [method-handler ledger](coverage/semantics/handler-callables-current-review.json)
keeps mixed author/independent checks, current CONFIG PIPE and original failures
at their actual revisions.

Diagnostic ingress217 dispatches runtime `E_STRICT` and lossy reporting
conversions through authentic handler continuations. Selected values survive
callback declarations; integer conversion precedes dispatch and the setter reads
the old mask afterward. Saved initializer facts and busy class scopes retain
normal/throw cleanup and expression/fetch exception locations. Fourteen author
and four independent sources plus 211 conditions keep their actual revisions.
Current 210 compilation and one scoped private-handler/Stringable-backing/lexical
class-name source comparison establish added composition separately. The
[diagnostic ledger](coverage/semantics/reporting-diagnostics-review.json) retains
original failures and cutoffs. The separate
[eval-location increment](coverage/semantics/compound-eval-location-review.json)
retains genuine filename owner/root/child through compound class, method/Closure
and static-property callbacks, with real eval call sites and lexical scopes.
Compiler exceptions use their failed unit; ordinary runtime exceptions keep the
execution override. Five original agreements/81 controls retain their distinct
cuts. One current inherited static-default/private-handler source plus214 compiler
stages at2c0c validate that composition and the static-fill compiler-prefix bridge.

The installed families compose as follows; each ledger records its scope and limits.

| Family | Current behavior and evidence |
| --- | --- |
| Class constants183/184/212 | Lazy scalar/array and selected Closure/FCC caches preserve strict types, inheritance priority and compile-entry availability. Named constexpr `::class` and rebound lexical defaults preserve source spelling/scope. Catalogue of 93 and 159 + 44 + 63 callable/class-name guards retain separate cutoffs; broader consumers remain open. [Constants ledger](coverage/semantics/class-constants-current-review.json). |
| Warning-truth decisions209 | Branch/loop/short-circuit/NOT/ternary-condition choices consume the captured null even after handlers define the CV. Saved consumers and thrown-handler cleanup retain authenticated source/line. Later cast/copy/SEND checks are recorded separately below. [Truth ledger](coverage/semantics/warning-truth-review.json). |
| Warning-read consumers213 | Six casts, selected ternary/coalesce copies and ordinary by-value sends preserve captured null, aliases and selected targets through callbacks. Direct ASSIGN retains its null write through throw. Mixed21/control0+236 and independent10/197 remain separate from fresh static-reference/outer-array source1/94 and cached-callee source1/96 at181f. [Consumer ledger](coverage/semantics/warning-consumers-review.json). |
| Borrowed warning reads208 | Strict identity retains the old reference cell across callbacks without adding an owner; saved callers and throw cleanup preserve it. Defined ordinary `$GLOBALS[key]` uses the real table. Getter/setter and method-string interactions keep separate revisions. [Warning-read ledger](coverage/semantics/warning-reads-review.json). |
| Error handlers/reporting206/207/211 | Raw registrations and selected targets retain four arguments and genuine emitting frames through mutation, replacement, nested reentry, throw and false fallback. Reporting get/set/Restore separates full raw bytes, signed32 masks and modified-entry state across suppression and handler writes; twelve normal sources across two revisions and 74 conditions are accepted. Fifteen nondeprecated error constants resolve exactly. Diagnostic ingress217 adds runtime `E_STRICT` and handled lossy reporting conversions with distinct 14+4/211 evidence and current source1. Broader handler forms and producer coverage remain open. [Diagnostics](coverage/semantics/reporting-diagnostics-review.json). [Reporting](coverage/semantics/reporting-ini-review.json), [method handlers](coverage/semantics/handler-callables-current-review.json), [earlier handlers](coverage/semantics/error-handlers-review.json). |
| Exception handlers222 | Raw nullable set/get/restore stacks and null-caller uncaught dispatch reuse ordinary calls with one authentic Throwable. Selected snapshots survive registry removal; weak receive, by-reference warning resume, nested restoration/replacement, throws, exit and fatal masks preserve ownership and termination. Author29/216 and independent33/331 pass at recorded cutoffs; actual219 source1 and production algorithm/structure gates pass. [Exception contract](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md). |
| Class-method strings210 and FCC119 | Full-byte lookup separates frame-based callable admission, computed static dispatch and fixed compatible-this selection. Captures/clone retain immutable source certificates and defaults/static cells. A named throwing handler preserves the selected static caller and arguments. [String ledger](coverage/semantics/class-method-strings-current-review.json). |
| Method arrays205 | Public source method arrays retain immutable selected receiver/owner/called-class certificates through dynamic calls and capture. Current two-slot INI checkpoint **f9f47f115/61370c98/1353** accepts source1/finite103; broader resolution remains open. [Array ledger](coverage/semantics/array-callables-current-review.json). |
| Include/configuration | Failed CHDIR warnings retain provider certificates and caller frames through handler CWD/raw writes, false fallback and throw. One current throwing source/136 conditions, earlier three sources and compiler25 checks keep separate revisions. Stringable CHDIR PIPE retains post-callback CWD/held operands; unary CONFIG PIPE preserves source strictness through borrowed warnings. [PIPE ledger](coverage/semantics/include-config-pipe-review.json). Raw getters, primitive/null Restore, weak-null handler continuations and two-slot INI ownership retain their separate checkpoints. [Readback](coverage/semantics/include-ini-readback-review.json), [INI](coverage/semantics/include-stringable-ini-option-review.json). |
| Stringable SET/Restore and paths | SET separates raw INI bytes from effective C-string paths. Weak Restore uses exact full-name lookup and preserves callback mutations on misses. Current ARG/Restore checks retain caller arguments and zero-argument callbacks. [Restore](coverage/semantics/include-stringable-restore-review.json), [prefix](coverage/semantics/include-ini-prefix-review.json), [SET](coverage/semantics/include-set-current-review.json). |
| Typed static properties197 | Weak simple Stringable assignment rechecks live aliases and retains paired callback owners. Current Restore/ARG/INI composition preserves full property bytes, caller arguments and normal/throw cleanup. [Property ledger](coverage/semantics/typed-static-string-assignment-review.json). |
| Weak string parameters214/216/218 | Fixed and positional/named variadic receives preserve caller strictness, nominal/callable precedence and captured cells; existing constraints reject before callbacks. Newly attached sources permit only the parameter-authorized backing value. Constructor-free defaults use genuine scratch cells, declaring method scope and fresh objects. Source6/state299/independent2 and variadic/default6+6/focused4/independent3/state336 retain separate cutoffs. [Parameter ledger](coverage/semantics/weak-string-parameters-review.json), [variadic/default ledger](coverage/semantics/variadic-default-string-review.json). |
| Static setters200/201 | Backed final/asymmetric declarations normalize equivalent setters and preserve inheritance/error priority; direct and indirect consumers retain lexical access, live raw-slot checks and typed aliases. [Setter ledger](coverage/semantics/static-setter-access-review.json). |
| Instance setters288 | Backed typed setters preserve lexical/prototype permission, called diagnostics, reference/indirect/unset priority and raw-object exceptions. Staged Stringable compound callbacks retain exact destination/consumer and saved writer scope. Private34 normal/8 compiler/350 reached premises retain distinct cuts; actual Fiber source1 and SL274 pass at a939. Wider static selectors, writable append receivers and sole borrowed destination retirement remain open. [Instance ledger](coverage/semantics/instance-set-access-review.json). |
| StaticCall reference acquisition141/142 | Getters with untyped return signatures retain scoped selection, typed and legal untyped static aliases and returned-cell cleanup. Typed REF flags preserve initialization/error priority even when discarded. Direct reference sends retain the real cell; ignored untyped getters leave raw values unchanged. Ownership/type-source and getter/borrowed-read checks keep their distinct revisions. [Reference ledger](coverage/semantics/static-method-reference-review.json). |
| Argument introspection198/199 | Ordinary current and saved frames retain genuine named/unpacked argument views through invocation and callbacks. [Argument ledger](coverage/semantics/argument-introspection-calls-current-review.json). |
| Object invocation and callable typing | Effective nonstatic `__invoke` lookup includes private/protected methods, retaining declaring owner, called class and receiver across argument effects and clone. Explicit access remains lexical. Callable-before-string parameters preserve dual-role objects; shared ordinary by-value return classification adds no fresh return agreement. [Publication](coverage/semantics/invoke-publication-current-review.json), [earlier invocation](coverage/semantics/source-invoke-current-review.json), [parameter reception](coverage/semantics/callable-string-current-review.json). |
| Selection and capture | Source method selection preserves owner/called class; capture/clone retains selected targets and scoped defaults/static cells without retaining retired origin-only creators. [Capture](coverage/semantics/method-capture-current-review.json), [default caches](coverage/semantics/closure-default-cache-review.json). |
| Compiler publication190–196 | Ordered class/function availability, early diagnostics and authenticated declaration history compose with calls and callbacks. Compile-stop freezes saved callers and retires active file replies; it does not perform ordinary unwind. [Publication ledger](coverage/semantics/compiler-publication-review.json). |

Executables and compiler inputs are reused; source-equivalent publication adds
no rebuild or fresh execution credit. Earlier selector, capture, invocation and
baseline milestones remain in [MILESTONE-HISTORY.md](MILESTONE-HISTORY.md) and the
linked ledgers. [Cleanup](coverage/semantics/error-origin-author.json) and
[migration](coverage/semantics/throwable-migration-review.json) retain deferred
failures and interrupted evidence.

## Remaining core work

- Calls: other internal and user-return
  keyword/compound warning consumers,
  magic/autoload/internal consumers, dynamic compile-warning handler delivery,
  transformed wrappers and broader CONFIG PIPE consumers. Only the selected captured-static
  array and string Closure PIPE routes are covered. Direct defined/missing
  `$GLOBALS[key]` reads and explicit-request full-table snapshots are admitted;
  233 additionally stages earlier missing key-CV and null/float/global-array-name
  conversions through nested/quiet reads. Writable242 adds bounded CV-array W/RW
  and direct GLOBALS reference fetches;249 adds direct CV-array coalesce-assignment
  and final unset;255 adds nested unset and append, and262 adds nested coalesce
  assignment on defined CV-rooted arrays;269 adds GLOBALS W/RW name/missing-entry
  continuations with direct updates/compounds and nested array ingress.
  Container276 adds undefined/null/false W/RW initialization and final array-reference
  ingress;282 stages missing/scalar R and quiet-container warnings with genuine
  row/key owners. ArrayAccess284 adds the builtin contract and direct R/IS,
  isset/empty, Set/append and Unset calls. Writable292 adds direct compound and
  ordinary nested W/RW/Unset Get; append304 adds intermediate and compound append,
  and309 adds final simple append to returned children. Module319 adds untyped/mixed
  reference Get;326 adds named sends and nested captured-row updates, and329
  adds VALUE-return Notice callbacks;334 adds real Stringable DIM_OP conversions
  and callback-unset key receives. Finally-sensitive Notice ingress, bare/fall-through
  NULL, handler exit, wider memoized consumers and combined Iterator/ArrayAccess notice ordering,
  initial string/ordinary-object reads, wider variable/property bases and writable
  memoized/unset/append containers stay open.
  Wider memoized and GLOBALS quiet/unset consumers, wider key/object/container
  producers and ordinary snapshots without request facts remain open.
- Include/configuration: wider initializer/callback/compile-warning consumers,
  wider startup directives/parsing/profiles,
  other warning producers, OS services and lifecycle. The
  [include contract](docs/semantics/INCLUDE-SOURCES.md) separates these consumers.
- Values, references and coercion: dynamic object `::class`, dynamic hole provenance and broader weak
  parameter/property conversion, constrained-reference object conversion, wider nonstatic delayed receivers and
  broader reference-result consumers. Other object-bearing default producers and
  wider Closure creation contexts remain Unsupported.
  Uncertified object transfers, unretained update selectors, builtin FCC targets and
  wider callable initializers remain Unsupported; modifiers/attributes stay open.
  Wider deprecated constant consumers remain open. Generic, scalar-loop, CV/compiled-CONST
  and bounded physical-array return replay are integrated, as is deferred reference-return
  Notice dispatch. Bounded single-active-finalizer CV replay and aliased-CV Stringable
  reference conversion 186 and bounded sole-local-CV lifetime 381 are integrated.
  Immutable string-literal consumed continuation is also integrated. Effectful VALUE,
  other CONST/NULL and multiple-active histories, genuinely released
  CV targets, destructor throw/reentry, real suspension and wider typed consumers
  remain open. [String contract](docs/semantics/USER-STRING.md),
  [finally contract](docs/semantics/SOURCE-FINALLY.md).
- Objects and lifetime: remaining static members, effectful trait data composition,
  enums, hooks, readonly and wider instance setter consumers,
  traversal, output handlers and lifecycle callbacks. Static cells remain
  partial across wider producers, bind/clone, include/eval reactivation
  and GC. [Method](docs/semantics/SOURCE-METHODS.md),
  [static-property](docs/semantics/SOURCE-CLASS-STATICS.md) contracts.
- Control and diagnostics: Generator/Fiber, remaining warning/read producers,
  broader API/callable argument consumers and remaining request phases.
  Broader constant consumers and compiler reporting interactions remain open.
  Called-class introspection223 leaves builtin Closure rebinding, builtin API
  callback targets, suspension and wider reference-result consumers open.

`returns_verify` has resumed with the authorized temporary verifier. Preserve
held branches and evidence, and do not retry the rejected engine experiment.
Generic, scalar-loop and CV/compiled-CONST delayed replay are integrated, as is
bounded physical-array owner recovery. Bounded single-active-finalizer CV replay and deferred VALUE/NULL Notice dispatch are
integrated, as are bounded aliased-CV Stringable reference conversion 186 and sole-local-CV
lifetime 381 and immutable string-literal consumed continuation. Wider owner domains,
effectful VALUE, other CONST/NULL or multiple-active histories,
genuinely released CV targets, destructor throw/reentry, real suspension and wider typed
consumers remain required.

Rocq interaction-tree semantics and BOLA proofs follow completed PHP core.

## Validated baseline

The post-arrow checkpoint is **1026/0ec57507**, with arrow capture and returns
117/118 at **87cdc532f**. Its [review](coverage/semantics/post-arrow-integration-review.json)
binds these distinct profiles and independent audits:

| Gate | Accepted observations |
| --- | --- |
| Compiler | 5,751 source lints, 8 access sources, 15 line observations; existing binary reused |
| Explicit request | 263 source profiles, 526 responses with exact request/environment facts |
| Callable | 946 maintained rows in 18 suites plus one regression; 1,894 responses |
| Ordinary | 5,706 source comparisons (4,060 normal, 1,006 PHP errors, 640 static rejections), 21 separate controls; 11,435 process records |

These are observations, not unique PHP programs or current full-core coverage.
Ordinary, request and callable profiles have different environment contracts;
their counts are not interchangeable.

## Validation and integration limits

Configuration permits eight pairs/16 agents; the numerical/model concurrency
cap remains five until explicit resource coordination, with coordinated slot
handoffs. Record the tested revision, compiler/runtime identity, relevant inputs,
environment, exact commands/exits and raw originals. Independent review focuses
on semantic counterexamples and reliable completion; investigate failures
narrowly and repeat only affected checks. Metadata adds no execution credit.

Interrupted runs, timeouts, Unsupported and budget controls are never native
agreements. Paused-state fixtures complement original-source comparisons; passing
subsets do not establish equivalence or full core. Final combined current-source
gates and a fresh copied-path, network-isolated offline rebuild remain required.
