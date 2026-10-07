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

## Required follow-ons

Five destruction control lists move with each VM stack: calls, releases, frames,
operations and cleanups. Object-store handles, request-pass state, abandoned
cleanup and property caches stay shared. Request scans, fatal cleanup, GC and
suppressed `exit` in a destroyed Fiber remain required consumers.

`getReturn` after graceful close without an actual return, request/fatal cleanup,
deprecated constructor callable stages,
wider core internal callback bodies, reference forwarding, API callable/FCC entry,
`start` unpacking and switching during initialization/source loading remain
required. The first transfer domain rejects active or saved constant/default and
autoload initialization, and active Generator execution, including switches in
their helper calls. Their shared pending flags and parked ownership remain
required consumers. Actual late Fiber-shutdown/frameless switching restrictions need
their own stages; ordinary registered shutdown callbacks and destructors are not
blanket blocked at this pin. Property and broader object consumers remain tracked
separately. Full core and paused return verification are not closed by this cut.
