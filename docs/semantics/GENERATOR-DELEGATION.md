# Generator delegation

Module 289 executes language `yield from` over arrays, source `Iterator` objects
and Generator graphs. Arrays retain their own cursor and embedded references.
Iterator callbacks run as ordinary calls in `rewind`, `valid`, `current`, `key`,
then `next` order. The yield-from expression over arrays or Iterators returns null.
Generator delegation forwards `send` and
`throw` to the active leaf and supplies its natural return to the waiting parent.
Waiting siblings observe shared progress without gaining an extra method trace.

Module380 acquires nested `IteratorAggregate` results through borrowed
`getIterator()` calls. Every returned Aggregate occurrence owns its raw result;
layers retire inside-out, then the original operand retires before rewind.
Persistent CVs remain borrowed, including unchanged global reference cells;
reference-valued original operands own their raw cell until retirement.
Raw reference getter returns and already-closed Generator results raise their
native Exceptions.

A returned Generator is consumed through its iterator hooks. The outer cache
copies raw values and reference cells, the expression returns null, send values
are ignored by the inner iterator, and injected exceptions stay in the outer
Generator. Acquisition receipts separate this route from shared child graphs.
Internal rewind/next operations borrow data already owned by the outer iterator.
A Generator getter's stored frame owns its receiver once; genuine parked getters
retain their parent resumer and source authority in the Fiber VM.

When layer or original-operand cleanup throws after constructing the iterator,
the pinned early exception branch retains its data until request cleanup.
The model keeps that single data owner in a source-authenticated request record.
A later real rewind exception instead releases data before catch.
Seventeen unchanged native-grounded originals agree at separate private cuts.
Twenty-five genuine-source groups/720 ownership and counterexample premises pass;
original failures retain zero credit in the
[Aggregate ledger](../../coverage/semantics/yield-from-aggregate-review.json).
At that acquisition cut, Iterator NaN warning continuations remained required.
At that cut, changed original operands and wider operand modes remained required.

Acquired Iterator `valid()` NaN warnings retain the raw returned operand and the
actual acquisition receipt through ordinary handler invoke, result and cleanup.
The final decision rereads a live numeric reference once; a copied NaN stays true.
The original Aggregate operand has already retired. False results and thrown
handlers release the raw retval before iterator data immediately, without adding
a request-retention record. Default warnings use the ordinary dispatcher.
Genuine parked handlers preserve the parent resumer and one delegation claim in
their Fiber VM; shifted receipts, old direct markers and duplicate saved claims
are rejected. Nine exact originals agree at `c52ae1d16`; twenty genuine-source
groups/637 physical ownership and authority premises pass at `d825e3fc0`. The
[warning ledger](../../coverage/semantics/yield-from-valid-nan-review.json) tracks
their separate state checks. Other post-handler raw payload tags remain an explicit
Unsupported dependency. Earlier direct-delegation evidence is unchanged.

A getter may rebind the original borrowed CV or owning reference operand before
returning terminal Iterator/Generator data or a rejected non-Aggregate raw value.
The engine rereads the original operand only for an Aggregate self comparison;
other rejections use the original class name. Independent keepers protect all
six validated callback receivers, and existing raw-cell/data ownership is
unchanged. Changed operands returning another Aggregate remain explicit
Unsupported/zero agreement. Nine genuine-source groups/376 physical owner and
source-authority premises pass; both original fixture failures retain zero credit.
[Rebound review](../../coverage/semantics/yield-from-rebound-operand-review.json)
records these originals and their source-reached owner checks.

Getters can detach an independently completed child without resuming the parent.
The copied current remains available until advancement, while the key becomes
null. A detached COMPLETE continuation owns its copied return value and adds no
child root. Its child index checks a closed tombstone with a matching return;
it does not certify unique historical child identity. Natural cleanup retires
the input, cache and return owners through their actual source continuations.

Callback admission binds the actual owner, source unit/path, stage, target, line
and saved lexical/called scopes. Only the immediate authenticated implicit call
overrides reference-result demand: `valid`, `current` and `key` consume a result;
`rewind` and `next` discard one. Nested ordinary calls keep their source demand.
This extends accepted99 caller plumbing without using paused return work.

An Iterator `valid()` NaN warning retains the raw returned operand through its
handler. The pinned Zend source selects the double branch, warns, then rereads
the payload (`vendor/php-src/Zend/zend_interfaces.c:129` and
`vendor/php-src/Zend/zend_operators.h:423`). A handler's float rewrite or integer
union bits can therefore change validity. The raw operand keeps its reference
cell through handler rebinding/unset. Its held retval owner releases before
`current`; the witness's otherwise unowned old cell then retires. Throwing
handlers discard the input.
Other final value tags stop at an explicit raw-payload-history dependency.

Aborted shared children restore the waiting parent with NORMAL completion, then
its genuine FROM_NEXT step starts a new ClosedGeneratorException search. The
existing Throwable transition audit remains unchanged. Admission rejects cycles,
duplicate or moved claims, inconsistent source/stage metadata, invalid cursors,
and wrapped or stranded internal tasks.

Private source review at the earlier direct-delegation cuts records 52 normal agreements and four compiler
rejections in separate cuts. Three exact Unsupported controls earn no agreement:
IteratorAggregate stops at its earlier interface declaration contract, started
force-close stops in this tested cut, and NaN handler changes to other raw
value tags need payload history. The Aggregate control provides no acquisition
guard execution evidence. [Reference yields328](GENERATOR-REFERENCE-YIELDS.md)
add live child caches and warning reinjection. Broader reference producers, complete destruction/GC and wider
Generator call forms remain required; this milestone does not close core PHP.
Ordinary last-owner forced close is covered by [Module303](GENERATOR-FORCE-CLOSE.md).
Module 360 adds normal request close with actual input detachment before finally,
independent CV owners, shared Generator store order and physical delegated cache
release. A consumed CURRENT reference borrows only its own authenticated storage
stage; copying that payload to a real unstaged Generator is rejected. Nested normal
exception handlers preserve both close claims and inner cache lifetime.
[The new ledger](../../coverage/semantics/generator-request-delegation-review.json)
records eight originals and 553 reached premises separately from earlier cuts.
Abrupt terminal cleanup, parked/escaped storage and wider GC remain required.

The source cuts are `generator-delegation-review-l1z91u_r` (5), `lxz1qh12` (19),
`xv0889dc` (10), `ikge9tqx` (8), `ger2ks_r` (4 compiler), `otx8ejdq` (7), and
`dx4si3ra` (3 new state-source tuples).
Original transition, null-cache and expectation failures remain in those records.
Ten source-derived protocol programs pass in twelve finite groups: 284 reached
conditions in `generator-delegation-protocol-uv41eu46`, 94 in `llcocuxj`, and 240
in `d_f3xfvg`. These 618 premises include setup and source/phase bindings; they
are not distinct semantic tests. Current/key/cache groups retain demand, trace,
cache, ownership, full public admission and continuation obligations. Public
admission includes the task/frame/current/Generator predicates formerly repeated
as helper checks. Original AL timeouts, rule-overlap and mistaken fixture
expectations retain zero credit. Phase30 reachability in `bv4l6a19` supplies no
full admission credit. Actual-parent compilation and the introduced source pass. Two new property
ingress/owner groups pass in `generator-delegation-protocol-qxalr9p6`: 33 plus
54 reached premises (87, including setup). They prove the genuine physical
property fetch, receiver-to-result owner transfer, nested callback demand,
full public/heap admission and malformed carrier/key rejection, then exact
zero-budget/direct-resume normal completion. The earlier SL fixture elaboration
failure in `fcvtc_mc` retains zero credit.

The actual `38f1dfaa045f` parent (273 modules) plus this reviewed milestone
compiles all 274 modules in `generator-delegation-ingress-compile-v7v7b987`.
One new normal tuple agrees in `generator-delegation-review-w4pqipa9`: a Fiber
creates a dormant private-scope Generator, then external resumption consumes an
ordinary byvalue ArrayAccess getter inside Iterator `current()`, which returns a
property reference. The live current, key/return aliases and lexical/called scopes
survive their genuine owner transitions. A concrete property-base ingress uses
the existing visibility-aware quiet physical-slot probe, then the real source
fetch; it adds no user call or diagnostic during classification. This exercises
Modules 281, 284 and 289 plus existing embedded-reference aliases. Module 287's
eval/include array-warning continuation is not exercised by this source.

The original reference-dimension source reaches explicit Unsupported in
`generator-delegation-review-dmm3pad0`; the attempted ordinary read of a byref
getter instead produced the genuine PHP-error mismatch in `de4jsilh`. Both keep
zero agreement. After the ingress fix, unchanged byref-read bytes reach the
existing `ArrayAccess by-reference result protocol` boundary in `w4pqipa9`,
also with zero agreement. Read/write/reference dimensions and byref getter
results remain required; the successful new source has its own distinct ID.

Records span `.tools/traversal-generator-delegation-14/.tools` and
`.tools/traversal-generator-delegation-actual-7m32k0at/.tools` in the main
workspace. Reports retain source bytes, runtime/tool identity, profile,
environment, commands and exits. Private evidence binds HEAD `93b45b79e` plus
the demand/NaN/search-guard diff. Actual evidence binds `38f1dfaa045f`/273 plus
reviewed Module 289 and the one-clause Module 284 ingress through its retained
`composition.json` and `union.diff`; the enclosing Git HEAD alone cannot
identify that 274-module copy. PHP is pinned
to 8.5.10 CLI NTS 64-bit, `LC_ALL=C`, `TZ=UTC`; source caps are 60/90 seconds and numeric
checks use 300 seconds with one serial actor.

The actual282 merge preserves the newer call, destruction and Fiber fields.
[Introduced composition checks](GENERATOR-FIBER-CLOSE.md) cover delegation close
through a warning handler and replacement previous chain; private cuts stay separate.

`python3 tests/semantics/generator_delegation_review.py --select iterator-valid-nan-reference-zero`
compares the complete native/model tuple.
`python3 tests/semantics/generator_delegation_protocol.py --mode check --sl --select iterator-rebind-cache`
executes source-reached ownership, admission and continuation conditions.
Strict SL uses the existing runner with caching disabled and deterministic
checking enabled, at the same 300-second cap as AL.
`--mode prepare` compiles fixtures without execution and earns zero state credit.
