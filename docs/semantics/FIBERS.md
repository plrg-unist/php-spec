# Fibers

Module 281 models live PHP 8.5.10 Fibers: constructor selection, direct
`start`, `suspend`, `resume`, `throw`, status, `getCurrent` and `getReturn`.
The first milestone covers existing declared nongenerator user callbacks with
by-value parameters. Selection is cached when the constructor receives its callback;
later changes to a referenced method name do not select another function.
Callable validation precedes the repeated-constructor status error. Callback
receive is weak because the Fiber enters through an internal call.

The model moves each VM continuation, local symbol table, frames, scratch owners
and live reporting mask. Heap storage, references, globals, handler registries,
INI and allocation counters remain shared. A saved main continuation does not
copy the shared global symbol table. Fresh callbacks take their reporting mask
from current INI; resumed callbacks restore their saved live mask. Nested waiting
Fibers remain running and cannot be resumed as suspended Fibers.

The raw constructor callback has its genuine function-name owner. Cached target,
permission and dynamic-construction certificates own nothing. Suspended tasks,
locals and saved frames retain their actual values. Waiting C API frames retain
their receiver and original `start`/`resume`/`throw` arguments. A parked static
`suspend` continuation retains its original argument without a Fiber self-owner.
The stored return value remains owned by the terminated Fiber; later array writes
from `getReturn` use ordinary copy-on-write and reference rules.

Each activation by `start`, `resume` or `throw` consumes a fresh global stamp;
`suspend` and terminal transfers back to the caller retain that activation stamp.
Admission checks the active caller chain, each saved stack and exact
source/task/function/line/argument metadata. Mapped `start` slots authenticate C
callback named preflight with a null callsite. Dynamic `new $class` retains only
its authenticated nonowning birth certificate after its temporary construction
marker retires. Termination clears callback/cache/continuation data. Caught
injection keeps the exact Throwable; uncaught callback exceptions cross the Fiber
root once. Traces include waiting Fiber API frames and their original buffers.
Callback name errors arise before a callback frame exists; their file and line
come from the waiting `Fiber::start` caller, and the failed Fiber terminates.
Global Generator ownership is checked on the actual machine. Parked Fiber views
retain their own task/frame checks and exclude active Generator resume markers;
an unrelated Generator can run while a Fiber remains suspended.

Private scoped descriptor validation checks shared live eval/class/directory
contexts on the active VM. Its parked validation view clears loader contexts
and separately rejects direct, wrapped and saved-frame markers; VM restoration
itself is unchanged. On the actual296 composition, a real Stringable chdir
inside a running Fiber agrees with native PHP. The maintained
`fiber_chdir_scope_protocol.py` has73 reached owner/log/marker/retirement predicates:
all pass on the corrected fixture, while the original72 elaboration failure
keeps zero runtime credit. This lane has SOURCEPENDING empty; broader source
helper and transfer domains remain required.

The primary engine routes are `Zend/zend_fibers.c`: VM capture/restore 123–155,
fresh entry 567–636, transfer 639–711, constructor 872–893, APIs 895–1098 and
object destruction 769–816.

## Validation

`tests/semantics/fiber_review.py` preserves original bytes, native/profile
identity and exact native/model streams. `fiber_state_review.py` seeks real
source states in production SL mode and checks continuation ownership, malformed
records, budget resumption and completion. Raw reports stay in ignored `.tools`.
No engine divergence or portability claim is made by these focused results.
Thirty normal originals, three zero-agreement Unsupported controls and thirteen
source-derived states/782 conditions retain the mixed cuts below.

| Checks | Accepted cut and raw report |
| --- | --- |
| First two original sources | `466ba2ba6` with recorded working-tree corrections, `fiber-review-9m0ul0ob` |
| Remaining sources: 23 normal agreements | `6fbdfdc25`, `fiber-review-xfvffr3u` |
| Affected nested source: allocated Fiber argument | `f6c30c7f6`, `fiber-review-caky5lmf` |
| Deferred/literal named holes and entry-error provenance: two normal originals | `29f6ba481`, `fiber-review-c9g38gpt` |
| Four independent states, 166 conditions | `d515fd003`, `fiber-state-review-m4i2tuy4` passing rows only |
| Three corrected independent states, 149 conditions | `d515fd003` with fixture corrections published in `c18091bdd`; `fiber-state-review-ssrq4m18` dynamic row and `fiber-state-review-znwx84k9` |
| Affected nested preflight state, 56 conditions | `6e053c12c`, `fiber-state-review-i4_ozv12` |
| Reporting/INI and parked-handler states, 137 conditions | `949d94782`, `fiber-state-review-_egc0_sx` |
| Named-default and entry-error states, 172 conditions | `6dc7900c4`, `fiber-state-review-8tppvo5a` |
| Actual constant-NEW identity transfer and separate running Generator: two normal originals | `5b720fd10`, `fiber-review-yxlc_qs5` |
| Autoload and active-Generator helper transfer controls: no agreement | `5b720fd10`, `fiber-review-yxlc_qs5` |
| Separate running Generator with parked Fiber, 102 conditions | `5e81060c6`, `fiber-state-review-1pzg3rap` |
| Module AL checks | `ae3c73e1d`, `fiber-al-hmn8wukf`, 264 modules; entry-error cut `29f6ba481`, `fiber-al-n_s2keum`; prior preflight cut `6e053c12c`, `fiber-al-csrau3ee` |
| Actual-parent AL checks, 271 modules | `07c427f3e`, `fiber-al-wvfym0ir`, preserving accepted `0e1252529`; prior interaction cut `5b720fd10`, `fiber-al-nu57_5eg` |

Sources use 100000 steps, 60 seconds per model and a 75-second process cap;
state checks use 4000-step seek/resume budgets and 120 seconds per case. Runs are
serial. The profile uses PHP 8.5.10 CLI NTS 64-bit with `LC_ALL=C`, `TZ=UTC`;
commands, exits, exact working-tree inputs and executed binary hashes are in each
report. Native preparation uses a 75-second subprocess cap. Reproduce selected
cases with repeated `--case`
arguments; `--native-report` reuses exact matching native originals.
Default maintained source runs exclude the four retained `count()` originals
and the held undefined-result engine witness. The latter accepts only its
preserved native report; no fresh engine observation is made.

Original compiler failures, the source dispatch failures in
`fiber-review-mslnabzj`, `fiber-review-fhy6k1o_`, `fiber-review-u0pcirvf` and
`fiber-review-hkzhd_y9`, and unsuccessful state rows retain zero credit. The
initial nested source/state failures remain in `fiber-review-xfvffr3u` and
`fiber-state-review-m4i2tuy4`; their affected successful checks above replace only
those rows. The two named continuation checks first rejected full admission in
`fiber-state-review-zfq15mg_`: their saved `start` buffer guard lost the optional
argument-name type. The affected checks above validate the corrected correlation,
including changed or missing raw names. That failure and the fixture parse failure
in `fiber-state-review-07w9vwmt` retain zero credit and their original raw inputs.
The named-default original using ordinary `define()` remains an explicit builtin
body boundary in `fiber-review-igz0sgwl`, with no Fiber events or agreement.
The const-initialized original's first failure in `fiber-review-62uis9p4`
preserves its successful default prefix and the missing-line error-path stop.
The affected successful original above keeps that earlier failure at zero credit.

## Ordinary force-close

Module 291 implements bounded ordinary force-close on the accepted eager-release source.
`zend_fiber_object_destroy` marks a suspended Fiber destroyed and resumes its
stack with an unregistered graceful control. User Throwable catches skip that
control; finally blocks may return a real value or replace it with an ordinary
exception. The original pending release owns the Fiber while the close frame
owns its graceful zval. Close traces stop at the callback boundary without an
invented public API or destructor-caller row.

Callback retirement transfers the raw callback to ordered release while the
Fiber remains running and destroyed. The pending finish task owns its exception;
the matching Fiber certificate owns nothing. Cleanup starts after the callback's
lexical frame retires. Its stored return value survives a captured-object
replacement exception, although `getReturn` then rejects the failed Fiber.
A private captured destructor instead raises a source-less Error from global
scope: `[no active file]`, line0 and an empty trace. Capture-time resurrection
retains the terminated Fiber and its actual returned value. Replacement errors
hand back to genuine operation, frame or parent-finish pending slots without
discarding remaining release jobs.

Captured destructor frames authenticate the empty internal root through their
genuine result producer and terminal finish; they acquire no callback lexical
scope. After the Fiber terminates, its private control remains valid storage only
while the matching ordered release owns every reference. It cannot regain catch
or pending-exception authority. Genuine two-owner cleanup retires one reference
before freeing the control.

The private combined source has 29 normal close comparisons: 25 originals and
four supported `foreach` trace observers, across `fiber-review-m6ssczam`,
`fiber-review-xkfv6zlp`, `fiber-review-n37exgls`, `fiber-review-3mgw86q7` and
`fiber-review-umrupbw6`. Four original `count()` observers stop at the library
body and earn zero agreement. The 33 native close originals include four
request-scan witnesses with zero agreement: three reach the suspended-stack
prune boundary, and the object-store witness now stops at its authenticated
internal handle (`fiber-review-5hcar_aq`). Its earlier silent normal result in
`fiber-review-n37exgls` remains a failure.

The reviewed 291 cut's 275-module AL checks pass in `fiber-al-dhcopa60`. Three authored
source-reached states/215 conditions pass in `fiber-state-review-6zo1dfo6`
(two rows) and `fiber-state-review-5u7eeare`; the first fixture syntax failure
remains zero credit. Eleven independent states/822 conditions pass across
`fiber-state-review-vg04eps9` (six rows), `fiber-state-review-9zgmnvth` (three rows)
and `fiber-state-review-bvygo02o` (two rows). The original internal-root admission
and one-step fixture failures, the retiring-control failure in
`fiber-state-review-wmjf7goa`, and pure diagnostic queries retain zero credit.
`fiber_retirement_review.py` maintains these independent states. Semantic review
accepts this cut; its source is integrated without renewing the earlier evidence.

## Ordinary callback retirement

Module 302 retires the raw callback on the running Fiber
after the callback frame returns or throws. The actual result is stored before
ordered release; a separate definedness flag distinguishes a returned null from
a callback that threw. One terminal task owns the pending exception, while its
matching Fiber certificate borrows it. Admission counts return, throw and
force-close terminal kinds together and rejects duplicate or changed kinds.

Captured destructors can suspend, resume or receive a public `throw`; their
continuations, result and pending exception remain owned by the Fiber. Resume
renews the finish certificate and saved task stamps. A replacement exception
preserves the old real exception and the stored result, even when `getReturn`
rejects the failed Fiber. Shared raw callbacks and returned captures keep their
genuine owners. Ordinary private-destructor errors use the current public
`Fiber::start`, `resume` or `throw` scope and provenance; force-close retains its
separate source-less global root.

Entered destructor frames match their genuine result producer's target,
receiver, callsite, normalized line and saved caller scope. Their C callsite can
differ from the saved caller origin; ordinary frame-site fallback grants no
authority to a malformed destructor pair.

Force-close of suspended cleanup preserves a result already returned by the
body. The accepted302 cut stopped before private-control injection when cleanup
protected a real exception. Module 308 extends the returned-result branch below.
The body-throw witness remains an exact Unsupported boundary: the body never
returned, and its undefined-result protocol remains required. Its native witness
is held and its preserved comparison earns zero agreement.

AL checks pass for 276 modules in `fiber-ordinary-al-kjr9z54c`. Fifteen targeted
normal comparisons pass: eight new originals, four affected ordinary controls
and three force-close result/scope controls. The protected-real witnesses stop
with exact output/event prefixes in `fiber-review-sz0q5k0z` and
`fiber-review-nywumd4m`. Three authored source states/227 conditions pass in
`fiber-state-review-__28gz97` (two rows) and `fiber-state-review-3zph8o_0`.
The original middle timeout retains zero credit; its affected fixture checks
whole-state zero-budget preservation and one actual completion from that paused
state. Nine independent groups/644 conditions pass across
`fiber-state-review-joqr1vup` (three unchanged groups) and
`fiber-state-review-9k7ok2d8` (six affected groups). The original heavy body
group retains every predicate across separate ownership/budget and actual
completion phases from the same source-reached state. The earlier compiler
syntax failure, protected-close boundary mismatch, independent combined timeout,
frame-admission failure, fixture field-order error and pure diagnostic queries
retain zero credit. `fiber_ordinary_state.py` and `fiber_ordinary_review.py`
maintain the authored and independent groups. Semantic review accepts this cut;
its source is integrated without renewing the earlier evidence.

Actual 270/296 composition at 279 modules passes strict-SL initialization, one exact
destructor/helper source comparison and a 58-premise default-AL state. The state
moves all five destructor lists, preserves the real owners and rejects a missing
parked producer before bounded resumption. Reports `fiber-accepted-composed-sl-unyelm2e`,
`shutdown-review-yddaops0` and `shutdown-state-review-galnzk9s` are under
`.tools/calls-fiber-integrate-17/.tools`. The initial missing runtime-link stop
and stale-helper elaboration failure remain zero credit; only that fixture
observation changed to the original explicit five-list predicate.

## Protected returned results

Module 308 preserves an earlier real exception when force-close interrupts a
captured destructor after the callback returned, including a defined null. The
private control's dynamic `previous` slot owns that real child. A nonowning pair
records the genuine write and matches the active finish certificate or its
authentic retiring operation. With the captured producer payload unchanged,
replacing the property child with another older live Throwable is rejected;
changing only the receipt cannot authenticate the unchanged property. The receipt adds no owner and can remain after the
control and child retire.

The source-less deprecation uses the restored Fiber reporting mask and line 0.
An eligible shared handler remains unentered while private control is pending;
its registration survives. A finally replacement filters private control and
links the old real exception directly. A later captured destructor can replace
pending control after the previous write. In these witnesses, the original
control and child release on the restored caller before the caller reads the
stored result; a child destructor can itself observe that terminated Fiber.

Source 63766192, patch e67cb587 over the accepted302 base, passes AL for 277 modules
in `fiber-protected-al-fjcnvo8u` and fourteen distinct normal comparisons.
The source reports are indexed outside Git in
`.tools/calls-fiber-current-14/.tools/fiber-protected-308-prep-16/source-results.json`.
The earlier body-throw control and the ordinary post-close dynamic-property
warning have exact Unsupported comparisons in `fiber-review-u2nd8y53` and
`fiber-review-___3cc1r`, with zero agreement. The original verbose finally source
timed out at the existing 60 second cap in `fiber-review-dms99xrd`; the distinct focused
source passes in `fiber-review-fi2ylmf3`. The original dynamic-property warning
failure remains `fiber-review-8bkqxy08`; its distinct array-key warning companion
passes in `fiber-review-abok_36q`. Both gaps remain required follow-ons.
Three authored source groups/227 conditions and eleven independent groups/860
conditions pass. Their exact reports are indexed beside the source results in
`state-results.json`; `fiber_protected_state.py` and `fiber_protected_review.py`
maintain identical source/check data. The two schema-affected existing groups
pass separately in `fiber-state-review-gsjgh1fs` and `fiber-state-review-h8npgal7`
(54 and 61 conditions). The malformed previous-child failure
`fiber-state-review-y4jx1snr`, local/global fixture failures and missing-catalogue
harness stop retain zero credit. Semantic review accepts this bounded 277 module cut.
The 280-module composition over integrated 291/302 parent `9dd9ca8b3` passes
strict-SL initialization, the exact defined-result original and two reached
strict-SL groups/113 premises: previous-child/receipt rejection 36 and ordered
control/child retirement 77. Reports `fiber-protected-composed-sl-8lnv1fpq`,
`fiber-review-2d4l4tb7`, `fiber-state-review-1lf_0ogs` and
`fiber-state-review-9zmisdrn` are under `.tools/calls-fiber-protected-16/.tools`.
This separate cut does not renew or add distinct originals to the 277 counts.
The final GEN/include parent `ed7f23c67` composition, tested at `68b9ec4c4`,
passes strict-SL 285 initialization, the same exact defined-result comparison
and the two strict-SL groups/113 premises. Its reports
`fiber-protected-composed-sl-c5kbvkbr`, `fiber-review-zw0a2mof`,
`fiber-state-review-4db8u833` and `fiber-state-review-h0hyhipg` are under
`.tools/calls-fiber-protected-composed-16/.tools`. The unchanged source and
reviewed hooks are now integrated; neither composition adds distinct originals
to the 277 counts. Recover the reached gates with `fiber_protected_review.py`
selecting `private-previous-cannot-transplant-another-live-real-throwable` and
`retiring-private-control-keeps-previous-child-and-genuine-release-count`.

Admission checks producer and heap consistency, not reachability from the entire
prior execution. The 32-condition diagnostic `fiber-state-review-50bdeosz` changes
the authoritative captured-old payload and its property projection together,
retaining the control identity, closer and terminal role. That alternative state
is structurally admitted; the diagnostic earns zero acceptance credit.

## Internal reporting callbacks

Module 313 supports string `error_reporting` callbacks, including case and
leading-backslash lookup, with an immutable concrete cached target. The internal
root receives weakly even from strict source. Named arguments map before entering
the C handler, so unknown/duplicate-name failures have only the public Fiber API
frame; entered arity/type failures also retain the real reporting frame.

CONFIG owns its copied C buffer. The unique core-result tail borrows those
arguments and authenticates the original start site, mapped ENTRY, constructor
cache and running/suspended Fiber. Handler suspension retains the C producer in
the saved frame after the original public start buffer returns. The warning keeps
the start location while resumed traces use the actual resumer. Ordinary strict
handler source calls retain their own strict receive behavior.

Handler receiver retirement retains the real C reporting frame, original argument
and public API suffix. Private destructor errors stop at that internal root and
report Fiber scope. Handler/destructor mask writes precede the old-mask sample;
the successful setter updates shared INI while returning to the caller restores
its saved live mask. The defined C result precedes the Fiber result store.

The [review ledger](../../coverage/semantics/fiber-core-callbacks-review.json)
retains 19 distinct normal originals at their original cuts and the separate
strict-SL compiler/state evidence. The rich public-destructor original still
times out as a whole-source run. Six bounded reached cuts execute its original
clauses 0..54; two additional components check scope-code admission and the actual
zero-step state. Clauses 55..57 involving literal `drive(S, 0)` are derived from
those checks and the checked driver composition, not credited as an exact run.
The original 63-premise fixture remains an explicit selection in
`fiber_core_review.py`; its default selects the five other independent groups.
`fiber_core_state.py` maintains the two author groups. Fixture relocation adds no
execution credit. Wider internal callback bodies and Fiber callable/FCC entry
remain required.

The separate tested 291-module parent composes the newer protected cleanup and clone
birth rules with 313. Active eval/include admission uses the live source state;
parked Fiber tasks and frames are checked with empty loader contexts. The exact
Stringable-eval/reporting, clone-born cache and finite-file originals agree with
PHP. Genuine eval response/owner and borrowed C-result checks pass with97 recorded
premises. The independent running-file47 rejects parked direct/frame markers
without changing the heap; its direct control keeps the authentic Fiber-wait head.
Its eval-only counterfactual is a VM predicate, not an older full-chain run. The
earlier46 retains its narrower head-rewrite scope. These cuts add no runtime
credit to older campaigns or nonempty fast/helper pending-exception state.

The latest 295-module join over integrated parent `892d8b187` preserves canonical
GC301, returned-child append309, source emission316 and Arrow311 rules, including
the shared scoped source/Fiber validator. Strict compilation and one fresh source
pass: the reporting handler collects an ordinary array cycle, then a Stringable
eval child reads literal `$_GET` after cast retirement. Native and model use the
same explicit primitive CLI request facts and produce `1|S|D|E|19:30719:2`.
The generic invocation's missing-request Unsupported retains zero agreement.
These new gates do not renew older source/state cuts or confirm full63/rich execution.

## Scoped constructor callables

Module322 routes deprecated `self`, `parent`, `static` and compound array method
selectors through the existing effectful callable stages. Class selection precedes
its warning; an aliased method is read afterward. Warning handlers may mutate,
throw or suspend, and callable validation still precedes the repeated-constructor
error. The cached target keeps its original lexical/called/receiver scope after
aliases change and makers retire, including a maker entered through another Fiber.
The immutable receipt adds no heap owner; actual raw callbacks and live receiver
entries retain their ordinary owners.

Admission binds direct raw members, actual maker `this`, producer/capture history
and constructor source. Pending new-expression result markers pair with their
authenticated live constructor owner; completed markers bind the selected cache
to that new source. Actual Fiber values gain nominal typed argument admission.
The unchanged throwing-handler original also required the finite inherited
RuntimeException kind/parent/base/constructor mappings.

The [constructor ledger](../../coverage/semantics/fiber-callable-constructors-review.json)
records thirteen normal originals at separate source cuts and strict296/three
author/seven independent groups at the corrected descriptor cut. A separate
305-parent composition passes strict306, one exact collector-destructor source
and92 independent reached premises. The receiver has retired before the child
starts; its arena identity authenticates the private static callback through pure
maker history, with no receiver owner added. GC runs in main and creates no
collector worker. Heap-identical producer/source substitutions are rejected;
zero/one-step entry and defined18 completion preserve the actual C buffer.
The final307-parent join preserves ArrayAccess326 and computed-name327 guards
and passes strict308 compilation. Earlier runtime cuts retain their revisions.
Maintained source/state scripts preserve checked original fixtures and stop at
the first failure;
relocation adds no execution credit. The earlier rich whole-source and full63
literal runs remain unconfirmed zero credit.

## Static API first-class callables

Module331 models first-class `Fiber::getCurrent` and `Fiber::suspend` captures.
The Closure keeps its exact capture source and selected method-name snapshot;
class aliases, dynamic names, object-style input, clone and `__invoke` aliases
preserve that selection. Static object-style input is nonowning and may retire.

Direct calls own one temporary Closure and their genuine C argument buffer.
Explicit `__invoke` calls retain the wrapper Closure and copied outer buffer as
well as the inner call owner. Normal resume and injected throw release those owners
in engine order, so an argument destructor can still observe the Closure.
Direct Closure callbacks use a distinct C-root owner alongside the Fiber's raw
callback; their immutable target pointer adds no owner. Admission authenticates
source, selected kind, exact buffer/tail pairing and flat active/saved task trees,
rejecting heap-identical substitutions and hidden runtime-owner markers.

The [static-callable ledger](../../coverage/semantics/fiber-static-api-callables-review.json)
keeps the ten normal originals at their separate private cuts, strict309 and
source-reached author/independent checks. Maintained scripts create checked
original fixtures and stop at the first failure. Wider API captures, binding and
lifecycle consumers remain required; this cut does not close the rich whole-source,
full63 or final offline validation gates.

The actual317 composition over `e91fc6d6` passes strict compilation and
initialization while preserving newer collector/source/GC guards. Earlier source
and state cuts keep their original revisions and gain no renewed runtime credit.

Engine routes are `zend_create_fake_closure`, `zend_closure_get_closure` and
`zend_closure_internal_handler` in `Zend/zend_closures.c`,
`zend_call_function`/`zend_call_known_fcc` in `Zend/zend_execute_API.c`, the
ordinary dynamic/method call handlers in `Zend/zend_vm_def.h`, and the static API
handlers and C callback entry in `Zend/zend_fibers.c`.

## Bound API first-class callables

Module337 supports first-class `resume`, `throw`, `getReturn`, `isStarted`,
`isSuspended`, `isRunning` and `isTerminated` captures. Dynamic method names,
clone and `__invoke` aliases preserve the selected method and receiver. Loose
Closure equality includes receiver identity. The fake Closure owns that Fiber;
the CONFIG and waiting API frames borrow the receiver and own only their actual
argument buffers. Explicit `__invoke` retains its separate outer Closure owner
and copied buffer.

Waiting resume/throw operations authenticate the selected Closure, receiver,
kind, source, line and exact sent buffer against their genuine result tail.
Nested saved callers retain that protocol. Direct and explicit invocation keep
their distinct API/Closure trace frames, and last-capture retirement can close a
suspended receiver. Public calls to the exposed idle collector authenticate their
capture through the saved caller while the collector executes its C loop.
The [bound-callable ledger](../../coverage/semantics/fiber-bound-api-callables-review.json)
records strict318 initialization, nine new normal originals, explicit Unsupported
controls and source-reached ownership/admission checks at their private cuts,
separately from the actual322 compiler and collector interaction checks.
Earlier331 evidence retains its original inputs.

Module341 admits these fixed captures as Fiber C-root callbacks. Their immutable
RAW Closure determines CONFIG's receiver and selected Closure; the C result tail
owns the call reference while waiting APIs borrow the receiver. Nested transfers
and public idle collector calls authenticate the actual runner and outer caller
chain. Callback retirement can force-close its last captured receiver before the
original `start` argument destructor. C-root API trace frames have no file or line site;
unknown named arguments fail at public `start` before handler entry.
The [C-root ledger](../../coverage/semantics/fiber-bound-core-callables-review.json)
retains its separate source/state cuts and the affected337 former Unsupported
original. Earlier331/337 cuts are not renewed.

Module348 adds bound `start` captures for direct and explicit `__invoke` calls.
Their selected receiver survives argument-side reassignment; the original
positional/named buffer reaches the target unchanged. The Closure owns the
receiver, while pending SEND and waiting API frames own only their buffers.
Explicit invocation retains its additional Closure owner and copied buffer.
Nested same-capture argument calls distinguish their source sites. Status errors
follow argument evaluation, and `start` trace frames retain the real callsite,
including explicit invocation. Pre-entry argument throws release the call's
Closure owner.
The [start-capture ledger](../../coverage/semantics/fiber-start-callables-review.json)
keeps the accepted cuts and original failures separate.

Module351 executes captured `start` as a Fiber C-root callback. Immutable RAW
selection retains the receiver; RAW and the result tail own separate Closure
references. The original outer `start` buffer and the C handler's copied buffer
have separate owners, while the waiting inner API borrows its receiver. Genuine
saved caller chains authenticate nested captures and reject missing result tails.
Inner `start` trace frames have no file or line site; the outer frame retains its
real callsite. Last RAW retirement can release both capture and receiver before
the original argument destructor. The
[start C-root ledger](../../coverage/semantics/fiber-start-core-callables-review.json)
keeps the new cuts and the earlier348 Unsupported observation distinct.

Module354 adds bound `__construct` captures through direct, explicit `__invoke`
and C-root entry. Immutable receiver selection, clone/equality and the original
callback survive rejected reinitialization. Callable parsing precedes the READY
status error, including deprecated selectors whose handlers throw or suspend.
Its query and warning continuations retain the exact adjacent capture owner;
C-root calls retain their genuine RAW/result owners and copied argument buffer.
Known valid registered callbacks can reach repeated-constructor rejection without
executing or caching an unsupported library body. Explicit entered constructor
and `__invoke` trace frames retain the real site and indexed arguments; pre-entry
unknown names have neither frame. Static constructor capture raises the native
nonstatic-method error. The
[constructor-capture ledger](../../coverage/semantics/fiber-constructor-callables-review.json)
keeps the original builtin failure and distinct accepted cuts.

Module358 selects Fiber APIs through `Closure::fromCallable` with simple method
arrays or static class-method strings. Dereferenced callback members freeze the
selected receiver and method; the completed factory call authenticates source,
line, arity and unpack history without rereading retired arrays. Historical
factory owners add no roots. Bound captures own their receiver once, while
static object-style selectors remain valid after that object retires. Clone,
equality and direct, explicit `__invoke` or C-root calls reuse their existing
API protocols. Successful waiting resume/throw frames retain the real callsite,
independently from handler-entry error formatting.
The [factory ledger](../../coverage/semantics/fiber-from-callable-review.json)
keeps the new checks and original trace failure at their distinct cuts.

Module362 selects fixed bound and static APIs through ordinary callable-array
invocation with simple method names. Dynamic INIT freezes dereferenced receiver
and method members before arguments. Nonowning receipts authenticate genuine CONFIG, saved WAIT and static
CONTINUE tails after selector arrays or member references change. The ordinary
call owns one bound receiver and transfers that owner to its waiting API;
static object selectors own none and suspend names the actual running Fiber.
Recursive argument frames keep independent receipts at the same source site.
Constructor parsing preserves its exact callable-query and warning continuation.

Module 367 executes ordinary array-selected `start` with its frozen receiver and
original positional or named buffer. The pending call owns both once, and its
waiting API takes those owners. Nonowning receipts authenticate the actual source
and saved caller after selector retirement; completed selection stays valid after
receiver retirement. Recursive argument frames keep separate receipts. Abrupt cleanup transfers owners
to the existing release queue in positional-values, receiver, extra-named-values
order. Body and entry errors retain the real `start` callsite.
The [array-start ledger](../../coverage/semantics/fiber-array-start-review.json)
records six exact originals and 267 independent plus 160 author premises.

Module 364 converts simple Fiber API arrays to first-class Closures, including
start and constructor methods. Its ARRAY witness authenticates the actual dynamic
FCC source, INIT/conversion lines and dereferenced member snapshot; factory and
method-capture witnesses remain separate. The conversion task's bound receiver
owner moves into the Closure, and static object inputs stay nonowning after
retirement. Existing clone/equality, direct, explicit invoke and C-root protocols
preserve their buffers, traces and callback cleanup. Live-static and bound receiver
checks are disjoint; duplicate conversion tasks fail local admission.

Module 370 executes simple raw Fiber API arrays as C-root callbacks, including
start and constructor methods. RAW retains its actual array members; frozen
cache receivers and result markers are borrowed. CONFIG and START invocation
own copied arguments, while outer start buffers keep their separate owners.
Saved Fiber states and actual callers authenticate fixed transfers and parked
static continuations
entered through dynamic start and public idle collector calls. Constructor
warnings preserve the original start site across a later resume. Inner API
trace frames have no file or line site, and last RAW retirement can force-close
its target before original argument destruction. The
[raw-array ledger](../../coverage/semantics/fiber-array-core-callbacks-review.json)
keeps the new source/state cuts and earlier Unsupported baseline separate.

Module 374 unpacks arrays into the original START buffer for ordinary methods,
ordinary callable arrays and captured calls. A live cursor owns the current pack;
frozen dereferenced entries and completed pack history own nothing. Each pack
resets positional-after-named detection, while duplicate names span the buffer.
Saved APIs authenticate historical packs after their arrays retire. Copied
C-root START buffers retain no pack witness; the genuine outer API retains it.
Abrupt cleanup retires the active pack first, then positional values, EX(This),
and named values from the unfinished call. Direct
Closure calls release their Closure after named values; explicit `__invoke`
releases it as EX(This). Pack errors retain their actual pre-entry trace.
The [start-unpack ledger](../../coverage/semantics/fiber-start-unpack-review.json)
keeps these new checks separate from earlier captures and callback consumers.
Module 376 unpacks Generators through native resume operations and Iterators
through their real callbacks. A source CV is borrowed; temporary operands and
iterator data retain separate owners. Iterator `current()` references survive
`key()` and are dereferenced before `next()`. Saved callbacks authenticate their
source and unpack instruction line; completed history remains valid after the
iterator retires. Callback errors retire iterator data and temporary operands
before the unfinished call buffer. Without an effectful cleanup domain, ordinary
pruning consumes those owners without creating an inactive release task.
The [Traversable ledger](../../coverage/semantics/fiber-start-traversable-review.json)
records the source and reached-state checks. NaN `valid()` warns at the actual
unpack line while retaining its original raw return. A handler may mutate or park
that reference; the C truth test rereads its live payload after handler cleanup,
while a copied NaN stays true. The INVOKE/RESULT/CLEAN wrappers preserve exactly
one pending START, including its data owner after the source CV changes. Throwing
handlers retire raw retval, iterator data and temporary operand before the call
buffer. The [NaN ledger](../../coverage/semantics/fiber-start-nan-review.json)
records these separate cuts. IteratorAggregate START packs now acquire a distinct
Iterator or Generator through the real public, nonstatic `getIterator()` contract.
The original input remains borrowed or owning as before; the aggregate identity
adds no iterator-data root. Its `getIterator()` receiver is borrowed, including parked
frames. Generator creation gives the copied frame one receiver owner and retains
the exact unpack argument/index/line authority. Raw reference, scalar and self
returns raise the native Exception and survive until authenticated unwind.
Successful cleanup retires returned iterator
data before a temporary aggregate operand; callback errors preserve the same order
before the unfinished buffer. The [Aggregate ledger](../../coverage/semantics/fiber-start-aggregate-review.json)
tracks the contract, source and reached-state cuts. Nested Aggregate acquisition,
foreach/yield-from/ordinary-call unpack consumers, wider raw payload changes and
compound array or factory selectors remain required.
Undefined-result `getReturn` and paused return verification are not extended.
Relevant engine routes also include `zend_create_closure_ex` and
`zend_closure_compare` in `Zend/zend_closures.c`, and
`zend_init_dynamic_call_object` in `Zend/zend_execute.c`.

## Required follow-ons

Five destruction control lists move with each VM stack: calls, releases, frames,
operations and cleanups. Object-store handles, request-pass state, abandoned
cleanup and property caches stay shared. Request scans, fatal cleanup, GC and
suppressed `exit` in a destroyed Fiber remain required consumers.

`getReturn` after graceful close without an actual return, request/fatal cleanup,
wider core internal callback bodies, reference forwarding, wider API callable/FCC entry,
nested IteratorAggregate acquisition, wider raw payload changes and switching during
initialization/source loading remain required. The first transfer domain rejects active or saved constant/default and
autoload initialization, and active Generator execution, including switches in
their helper calls. Their shared pending flags and parked ownership remain
required consumers. Actual late Fiber-shutdown/frameless switching restrictions need
their own stages; ordinary registered shutdown callbacks and destructors are not
blanket blocked at this pin. Property and broader object consumers remain tracked
separately. Full core and paused return verification are not closed by this cut.
