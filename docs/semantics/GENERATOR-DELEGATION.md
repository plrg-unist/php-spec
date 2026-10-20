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

Module405 also consumes these acquired Generator leaves during ordinary by-value
Generator call unpack, directly or below finite active shared links. Admission
requires allocated parent/data objects, a present copied CURRENT, position1 and
the existing source-valid acquisition receipt. Child cache, parent cache and
sent arguments retain separate owners; generic iterator completion returns null
and retires unused child returns before the parent tail. Temporary key errors
close the child before parent finally and cache/SENT release. Independent child
CVs preserve their own cached rows through real body throws and COW replacement.
The [acquired-Generator ledger](../../coverage/semantics/generator-call-unpack-acquired-generator-review.json)
records the focused source and reached-state evidence. Ordinary Aggregate call
operands and valid-key by-reference targets remain separate boundaries.

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
unchanged. At that earlier cut changed operands returning another Aggregate remained
Unsupported/zero agreement. Nine genuine-source groups/376 physical owner and
source-authority premises pass; both original fixture failures retain zero credit.
[Rebound review](../../coverage/semantics/yield-from-rebound-operand-review.json)
records these originals and their source-reached owner checks.

Known Aggregate returns now compare the first live object-valued CV/reference
payload, then each owned raw layer. An independently kept original can be the
first repeated layer even after a deeper getter rebinds the source and retires
the former payload. Self returns from immutable inputs and deeper layers retain
the fixed class rejection; no comparator/history owner is added. Returned layers
and original input still retire before rewind, with terminal data protected.
Nine selected originals agree; a first nonobject original with a known Aggregate
return stays Unsupported/zero agreement. The [source-comparison ledger](../../coverage/semantics/yield-from-source-comparison-review.json)
keeps the affected historical control separate. Sixteen genuine-source
groups/732 physical ownership and authority premises pass without state corrections.

Getters can detach an independently completed child without resuming the parent.
The copied current remains available until advancement, while the key becomes
null. A detached COMPLETE continuation owns its copied return value and adds no
child root. Its child index checks a closed tombstone with a matching return;
it does not certify unique historical child identity. Normal continuation transfers
the copied return into RESULT. For an owning value at a direct simple-CV assignment,
forced close preserves its count before dropping the saved continuation; finally
and current-cache cleanup still run normally. Its object-store destructor may run
after caller output. Retained arrays follow mutable embedded cells rather than
pinning their former referents. The
[owning-return ledger](../../coverage/semantics/generator-owning-detached-return-review.json)
also checks ordinary consumption and cache-cleanup replacement of the unpack Error.
Ordinary unpack also reaches that owning simple-CV continuation through finite
native ancestor links. The middle holds one copied return; ancestors borrow its
current. Null-key rejection precedes sends, and later outer next consumes the
return normally. Close preserves the return count; an inherited pending-init
middle skips finally, while an advanced middle keeps ordinary finally behavior.
The [owning-chain review](../../coverage/semantics/generator-owning-chain-unpack-review.json)
also covers cache destruction before outer finally and returned-cell mutation.
Wider continuation/GC paths remain open.

Module405 also admits detached leaves below finite active shared links when the
copied return owns no heap nodes. The null key raises the real unpack Error before
SEND or callee entry; a prior `current()` snapshot can already have copied a row.
Retained middles later consume the real return and continue their source tails.
Initialization history controls whether forced middle close executes finally:
shared internal resumption preserves pending initialization, while an actual
root resume clears it. A direct middle `next()` can clear it without advancing.
The [nested-detached ledger](../../coverage/semantics/generator-call-unpack-nested-detached-review.json)
records the paired retained/temporary cases and their physical cache owners.
Pending `send` on these detached roots now returns a cache snapshot without
advancing; see the [API review](../../coverage/semantics/generator-pending-init-send-review.json).
An owning simple-CV copied return can take the same pending `send` without
consumption or buffering the argument. The copied cache is captured before
argument cleanup, including reference-row COW; the return keeps its independent
owner through normal next or close and later embedded-cell writes. The
[owning SEND review](../../coverage/semantics/generator-pending-owning-return-send-review.json)
also checks a snapshot destructor after receiver retirement and its previous chain.
That owning return may also wait below a finite native ancestor receiver. Pending
`send` can refresh and detach the completed child itself, then clears only the
receiver's initialization bit. The physical middle keeps its pending bit and
owning COMPLETE. The cache is captured before argument cleanup. After COW, its
snapshot and the copied return own two old-array counts with one element-edge
set; the raw reference cache follows the new array. The
[ancestor SEND review](../../coverage/semantics/generator-pending-owning-chain-send-review.json)
also checks a used cache after all Generator aliases retire and ordinary next
consumption versus inherited-pending close.
Pending `throw` on the actual detached middle likewise leaves its owning simple-CV
return intact, but parks the frame before caller escape. Getters preserve current;
close omits that frame's finally and retains the copied return independently of
the transient cache snapshot. A return/cache array alias keeps separate container
counts with one element-edge set; later raw-cache COW and embedded-cell writes
remain live. See the [owning THROW review](../../coverage/semantics/generator-pending-owning-return-throw-review.json).
Pending THROW also follows finite native links to that owning continuation.
It may detach the completed child itself, then clears initialization only on the
selected ancestor while parking the physical middle. Its copied return and cache
snapshot retain independent counts; a real row write can COW the raw cache away
from a held snapshot and the same copied return without duplicating element
edges. The [ancestor THROW review](../../coverage/semantics/generator-pending-owning-chain-throw-review.json)
also covers sole-receiver replacement cleanup and late returned-cell writes.
A later pending THROW may target that same parked owning continuation directly
or through finite native links. The selected receiver must still be pending; the
physical middle need not be. Native HANDLE_EXCEPTION is already installed, so
this call preserves parked history and returns before body entry. Its separate
current snapshot can retire after receiver close; returned array aliases and
embedded cells keep their owners. See the
[repeated THROW review](../../coverage/semantics/generator-repeated-pending-owning-throw-review.json).
Pending SEND can take the same early return through a direct or native-linked
receiver while its owning copied return is parked. Actual receiver initialization
clears, independently of the physical middle bit; the parked frame/site stay
unchanged. SEND captures the dereferenced current before normal ignored-argument
cleanup. After row COW, the used snapshot and copied return retain two old-array
counts with one element edge, while the raw reference cache follows the new row.
Receiver retirement can leave the used cache as its sole owner. See the
[parked SEND review](../../coverage/semantics/generator-parked-pending-owning-send-review.json).
Normal unused SEND now schedules its real copied current between ignored-argument
and receiver release. Source demand and the actual discarded-result tail must
agree; the consumed argument/receiver slots must match exactly. The original
owner-order observation stays unchanged. A raw-row snapshot survives argument
COW and alias retirement until ARG-END, then its old payload retires before
ancestor finally. Assigned results keep their copy through receiver cleanup.
See the [unused SEND review](../../coverage/semantics/generator-unused-pending-send-review.json).
When argument and current are the same owning value, the fresh RESULT can match
the old argument root, leaving only the receiver in the removed-slot list. The
authenticated argument and new result still require two real release jobs before
the receiver; original owner-order observation stays unchanged. Their two quiet
drops preserve one array element-edge set. Assigned calls retain the net result
copy; see the [aliased SEND review](../../coverage/semantics/generator-unused-pending-send-alias-review.json).
For an unparked pending ancestor SEND, refresh may first detach one closed
child.
That authentic removed-edge prefix precedes argument, unused current and receiver
releases. The temporary return copy shares its array with the child; child
storage retires before argument cleanup. A prior getter needs no prefix, and
assigned calls retain their result. See the
[normal SEND review](../../coverage/semantics/generator-unused-detached-send-review.json).
The identity-refresh proof also admits the direct pending physical receiver at
that normal owning return. Argument cleanup and unused-result release precede
its finally; assigned copies retain their independent owner. Raw-row writes
therefore distinguish one container from an assigned snapshot, while shared
reference cells keep their own edges. At that cut the closed-child-prefix proof
was ancestor-only; see the
[direct SEND review](../../coverage/semantics/generator-unused-direct-detached-send-review.json).
The direct pending receiver now also admits exactly one allocated closed child
whose actual refresh produces an owning copied return. Its authenticated child
release stays first; the copied return temporarily has child and waiting-slot
owners, then survives child retirement independently of current. The raw cell
can follow an argument-time rebind while the argument retains its earlier value.
See the
[direct refresh review](../../coverage/semantics/generator-unused-direct-refresh-send-review.json).
The direct identity case also authenticates a simple-CV COMPLETE whose copied
return owns no heap node. Source/tail, empty held/task owners and inactive
collection bound the endpoint; the owning-return receipt stays separate. The
current copy still owns its array or object through normal argument cleanup.
After argument COW, the old snapshot and live raw row have distinct containers
and element edges. No child prefix or owning return is manufactured; see the
[scalar-return SEND review](../../coverage/semantics/generator-unused-scalar-return-send-review.json).
A shared pure endpoint proof now also authenticates the direct no-getter case
with one original allocated CLOSED child. Actual refresh supplies the node-free
COMPLETE, and its sole removed child edge precedes argument/result/receiver
release. The raw cell temporarily has child and middle cache owners; no copied
return owner is added. Owning receipts and finite ancestor proofs remain separate;
see the [node-free refresh review](../../coverage/semantics/generator-unused-scalar-refresh-send-review.json).
For pending SEND over one native link to a PAUSED bare-statement-yield child,
refresh is identity: there is no closed-child prefix, COMPLETE or copied-return
owner. Source demand and the real discarded tail select argument, unused
current-copy and receiver release in that order. The tested shared row cell has
three owners: global, Child REFCELL and Child frame CV; its array still has one element
edge. Empty held/task owners, an empty input registry and inactive collection
bound this arm; wider chains stay separate. See the
[bare-yield SEND review](../../coverage/semantics/generator-unused-bare-yield-send-review.json).
A separate fixed one-ancestor proof now reaches an allocated physical Middle
with a normal node-free COMPLETE. It authenticates the real link/site, empty
held/task owners and input registry, then reuses the direct endpoint proof and
inactive-collection bound. Physical Middle's initialization bit is independent
of selected Upper. Refresh contributes only its actual allocated CLOSED-child
prefix; an already-refreshed endpoint contributes none. Owning-return walkers,
source demand, result/slot ownership and the common release scheduler remain
unchanged. See the
[node-free ancestor SEND review](../../coverage/semantics/generator-nodefree-ancestor-send-review.json).
Literal pending NEXT takes the same initialization-only return through a direct
or finite native-linked receiver, preserving the actual parked source and frame.
Its NULL result owns no current snapshot. After a raw-row write performs COW,
the copied return alone keeps the old array and its single element-edge set;
the live reference cache follows the new row. Returned embedded cells stay mutable
after close. See the
[parked NEXT review](../../coverage/semantics/generator-parked-pending-owning-next-review.json).
Actual parked body entry and wider owning continuations remain open.
Pending `send` through native shared links can now buffer a paused child's yield
result when it is assigned directly to a simple CV. When a direct or forwarded
`next` resumes the child, it consumes that value without adding another owner.
Close and overwrite preserve its native request-late count independently of the
chain and raw reference cache; see the [shared-send review](../../coverage/semantics/generator-pending-shared-send-review.json).
Bare statement yields instead have no send target. Pending `send` captures the
current snapshot, then retires its ignored argument before the receiver, without
advancing or buffering it. Reference-cache writes and a supplied destructor
exception preserve that ordering through later real next or forced close; see the
[unused-target review](../../coverage/semantics/generator-pending-unused-send-review.json).
Non-pending `throw` through native links instead releases a buffered simple-CV
yield result before child catch search. Its one temporary owner stays separate
from current/reference caches and earlier orphan counts; payload cleanup can
replace the injected exception with its exact previous chain. See the
[buffered-throw review](../../coverage/semantics/generator-buffered-throw-review.json).
Aggregate/Iterator data is outside this route. Owning copied returns and other
used-yield shapes remain Unsupported.

Pending `throw` follows a separate no-advance path through native links to a bare
yield or detached current with a node-free copied return. It throws to the caller
while retaining a used copied current through receiver retirement. Only the physical leaf is parked;
getters preserve it and later real resume through any ancestor is Unsupported.
Explicit close omits the parked frame's finally, including a detached middle with
cleared initialization. Other suspended task/held owners stay outside this admission;
see the [pending-throw review](../../coverage/semantics/generator-pending-throw-review.json).
A used simple-CV yield with one authenticated buffered input also takes this
pending path. The input becomes request-late only when the physical child closes,
including during receiver retirement before catch, and remains separate from
current snapshots and reference caches. A lower pending `send` can consume its
initialization while an upper pending `throw` still returns without advancing;
see the [pending-buffered review](../../coverage/semantics/generator-pending-buffered-throw-review.json).
A still-pending ancestor can then take zero-argument NEXT without consuming or
overwriting that one owning input. It returns NULL, leaving the child parked.
After real row COW, only the input keeps the old array, with one element-edge set;
the raw reference cache follows the new row. An embedded input cell remains
mutable after close. See the
[buffered NEXT review](../../coverage/semantics/generator-parked-pending-buffered-next-review.json).
A first pending SEND can overwrite the sole owning LIVE input with a new owning
argument before the same initialization-only return. The old record becomes
orphaned without releasing its value; the new record is LIVE. Current capture
precedes argument/receiver cleanup, so row COW separates the old input and used
snapshot from the raw reference cache. With an old `[&$slot]` input and new
`[$slot]` input, post-close rebinding keeps the original object through the new
direct edge and the replacement through the old shared cell. See the
[buffered SEND review](../../coverage/semantics/generator-parked-pending-buffered-send-review.json).
A second pending THROW with exactly one owning LIVE input record leaves it
unchanged. Its actual receiver must still be pending, independently of the parked
physical child's bit. An unused result adds no surviving current owner before
receiver cleanup: input/raw-row aliases keep two array counts and one element-edge
set, then real COW leaves the old array input-only. A call in assignment context
keeps its temporary copy through receiver cleanup. The
[repeated buffered THROW review](../../coverage/semantics/generator-repeated-pending-buffered-throw-review.json)
separates these lifetimes and same-object rethrow from post-close cell rebinding.
The [parked-foreach review](../../coverage/semantics/generator-pending-foreach-throw-review.json)
adds exactly one by-value array loop at a bare yield. Physical child close retains
the iteration container, preserving shared reference cells and late
payload/Generator cleanup. The
[joint lifecycle review](../../coverage/semantics/generator-pending-buffered-foreach-throw-review.json)
adds one authenticated input at a simple-CV used yield in that loop. The input and
container remain separate owners, including across COW, shared-cell rebinding and
receiver cleanup before caller catch. At a bare yield in one by-reference array
loop, close retains the acquired wrapper itself, allowing whole-wrapper and
escaped-item writes after close; see the
[reference-foreach review](../../coverage/semantics/generator-pending-reference-foreach-throw-review.json).
The [buffered reference-foreach review](../../coverage/semantics/generator-pending-buffered-reference-foreach-throw-review.json)
adds one simple-CV input in that reference loop. Its value remains independent of
the acquired wrapper across physical close and later wrapper or entry writes.
Other input/loop shapes, object loops, nested owning loops and later parked
resumption remain open.

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
