# Generator force close

Module303 normally runs pending finally bodies when an ordinary last-owner release
closes a started Generator. Unstarted bodies remain silent. This extends the reviewed
Module289 delegation baseline without using held IteratorAggregate work or
unaccepted ordinary-return changes.

Close first releases the delegated array/Iterator input or Generator graph link,
then executes the parent's pending finally bodies. Parameters and locals still
own their values; raw current and copied key caches survive until storage release
after the finally bodies. Thus a temporary delegated child closes before its parent
(`1IOZ`), while a parameter-owned child closes afterwards (`1OIZ`). A started
child held only through an array's reference cache also closes afterwards
(`OIZ`). Separately rooted children and waiting siblings remain live.

An owning child return copied into a direct simple-CV `yield from` result has
a separate unfinished-slot count. Close moves it out of the frame without a
decrement, then follows the existing finally and cache-cleanup order. Payloads
receive their normal request-store destructor calls; arrays and embedded reference
cells remain shared and mutable. Actual next consumes the result normally.
The [owning-return review](../../coverage/semantics/generator-owning-detached-return-review.json)
checks both paths and a temporary cache destructor replacing the unpack Error.
Finite native ancestor unpack keeps the same one physical copied-return count.
Input unlink can retire the middle cache before outer finally; its destructor
may replace the key Error with Previous intact. The initialization-history rule
below also applies to that owning middle, as the
[owning-chain review](../../coverage/semantics/generator-owning-chain-unpack-review.json) checks.

The pinned engine has an initialization-history exception. A middle first entered
only through shared outer resumption can retain pending initialization. After
input unlink, its own defined current makes forced resume clear that bit and
return before finally. A detached copied CURRENT qualifies; a cache borrowed only
through a shared leaf does not. The model releases the real frame and pending
exception through the existing jobs, retaining caches until storage release.
Direct initialization clears the bit, as does a later direct `next()` that consumes
it without advancing. An admitted detached pending `send` also clears it before
argument cleanup, including cleanup that throws; those middles execute finally
on close. The
[nested-detached review](../../coverage/semantics/generator-call-unpack-nested-detached-review.json)
preserves both native close orders and the earlier omitted-finally observation.

For a bounded owning copied return, pending `send` likewise clears initialization
without consuming the result. Close retains that count before finally. If an ignored
argument's destructor throws, the returned cache snapshot survives receiver storage
retirement; its later destructor can replace the exception before catch. The
[owning SEND review](../../coverage/semantics/generator-pending-owning-return-send-review.json)
distinguishes that snapshot from the request-late return value.
With a native ancestor receiver, pending `send` clears that receiver rather than
the owning physical middle. An inherited-pending middle therefore still skips
finally on close, while the initialized outer and cleared receiver execute theirs.
Normal argument destruction can retire the chain before the used cache result
reaches the caller; that snapshot remains independent of the retained return.
Actual outer next instead consumes the return and reaches the ordinary tails.
See the [ancestor SEND review](../../coverage/semantics/generator-pending-owning-chain-send-review.json).

An unconsumed used-yield input installed by pending shared `send` has a separate
lifetime. In the pinned engine its result slot precedes the live range used by
unfinished-frame cleanup. Closing frees the frame and executes finally without
decrementing that count; overwriting the slot also retains the old count. The
model keeps only the payload owner through these steps, with immutable source
history, then runs its destructor in the normal request object-store pass. It
does not retain the child or API receiver. The [shared-send review](../../coverage/semantics/generator-pending-shared-send-review.json)
checks both close orders arising from real local aliases and a payload/cache
alias whose sole remaining owner is this count.
The first pending SEND overwrite of one parked owning input uses this same
lifecycle: the old record is orphaned before the new LIVE record is installed,
and close preserves both counts. A used current snapshot can outlive every
Generator and retire only after caller delivery. An old input cell and a new
direct object copy retain different values after rebinding, with request-store
destruction following native handle order rather than input-record order. See the
[buffered SEND review](../../coverage/semantics/generator-parked-pending-buffered-send-review.json).

Non-pending `throw` into the paused used-yield child follows exception cleanup
instead: it releases the buffered slot before catch search, without orphaning
that count. Current caches and earlier orphan counts remain separate. Payload
destructor replacement preserves the injected exception in its previous chain; see the
[buffered-throw review](../../coverage/semantics/generator-buffered-throw-review.json).

A bare statement yield has no such result slot. Its ignored pending-SEND
argument retires before the method receiver; it cannot acquire the used-slot
request-late owner above. A throwing argument destructor preserves cleared
initialization and the same Exception through real child/middle close. The saved
API current snapshot keeps its separate cache owner during this cleanup.
The [unused-target review](../../coverage/semantics/generator-pending-unused-send-review.json)
distinguishes both paths and real local-alias close order.

Pending `throw` has a separate exception-opline history. At a bare yield,
used simple-CV yield with one authenticated live input, or
detached current with a node-free copied return, pending initialization returns
before body entry but the physical frame remains parked at the native exception operation. Later
explicit close skips that frame's finally even though initialization is cleared.
Real CV/context owners still retire through the existing frame jobs; other owning
suspended task/held temporaries are excluded. A used API result's copied current
keeps a cache alive through sole receiver close, then releases before caller catch.
An unused result drops that copy before receiver cleanup.
A cache destructor can replace the injected exception with its previous chain
intact. No exception owner belongs to the parked Generator. The
[pending-throw review](../../coverage/semantics/generator-pending-throw-review.json)
checks reference-child and detached-middle histories; later body entry remains
Unsupported because the global exception-opline history is not yet modeled.
For a direct detached middle with an owning simple-CV copied return, pending
THROW also parks the frame. Close first transfers that return's count out of the
saved continuation, then skips finally and releases the remaining frame owners.
The exact source receipt remains valid during the parked CLOSING interval and
after retirement. A separate current copy can keep a cached object alive until
receiver retirement and then replace the exception before catch; returned arrays
retain mutable reference cells. See the
[owning THROW review](../../coverage/semantics/generator-pending-owning-return-throw-review.json).
With an inherited-pending ancestor receiver, THROW clears only that receiver
and parks the distinct physical middle, which still carries its pending bit.
Middle close uses the same copied-return transfer and skips finally; its source
receipt is valid while CLOSING has both pending and parked history. Cache-copy
cleanup can run after upper finally and replace the supplied exception before
catch, independently of the retained return. See the
[ancestor THROW review](../../coverage/semantics/generator-pending-owning-chain-throw-review.json).
A second pending THROW can clear the still-pending selected receiver without
executing the parked frame. The copied return and parked source site stay intact;
close keeps the same transfer and finally omission after either receiver order.
A sole-middle snapshot destructor replaces the second supplied exception after
ordinary ancestor cleanup, independently of the retained return. See the
[repeated THROW review](../../coverage/semantics/generator-repeated-pending-owning-throw-review.json).
Pending SEND likewise leaves the owning copied return and parked frame intact
while clearing only the selected receiver initialization bit. Its current copy
precedes normal ignored-argument cleanup, including alias retirement; a used cache
can outlive all Generators and retire after caller delivery. Close retains the
same copied-return count and skips the parked middle finally. Returned cells
remain mutable after close. See the
[parked SEND review](../../coverage/semantics/generator-parked-pending-owning-send-review.json).
For normal unused SEND, the captured current survives argument cleanup but drops
before receiver cleanup. Its cache destructor can therefore precede the queued
ancestor finally, while the independent copied return stays request-late. The
scalar-argument cache destructor throws a RuntimeException whose Previous stays
NULL; an older caught Exception exists only in globals. An assigned result
retains its copy through receiver retirement; see the
[unused SEND review](../../coverage/semantics/generator-unused-pending-send-review.json).
Equal argument/current values supply distinct argument and result owners for two
quiet releases. In the tested case with one receiver owner, retirement destroys
the last cache before the ancestor finally, independently of the request-late
copied return. A throwing cache still has no pending older Exception to chain;
see the
[aliased SEND review](../../coverage/semantics/generator-unused-pending-send-alias-review.json).
Normal unparked pending ancestor SEND preserves the proven optional
closed-child release before argument, unused snapshot and receiver cleanup. Its copied return stays
independent of the cache. Row COW preserves the old snapshot through ARG-END;
an equal-cache argument can produce a new RuntimeException with Previous NULL
before ancestor finally. See the
[normal SEND review](../../coverage/semantics/generator-unused-detached-send-review.json).
Pending NEXT preserves that parked return across the same close transfer but
creates no current copy. A temporary sole receiver releases its cache during
storage cleanup, before caller delivery; a throwing cache has no older caught
exception pending merely because that exception remains in globals. The real
storage pin, NULL operation value and independent retained return are checked in
the [parked NEXT review](../../coverage/semantics/generator-parked-pending-owning-next-review.json).
A live used-yield input stays in place at the pending THROW step. Physical leaf
close retains its count before retiring the parked frame; the payload runs only
in the request object-store pass. It is neither released before caller catch nor
owned by the transient current copy. Cache/input aliases and a distinct throwing
cache preserve their separate counts in the
[pending-buffered review](../../coverage/semantics/generator-pending-buffered-throw-review.json).
Pending NEXT can preserve that one owning input without a current copy. During
last-owner cleanup, the physical child's storage pin releases its cache before
the queued ancestor finally blocks. A cache throw reaches the caller without
chaining an older exception that is merely globally owned; the orphan input
remains request-late. See the
[buffered NEXT review](../../coverage/semantics/generator-parked-pending-buffered-next-review.json).
A repeated pending THROW also preserves one owning LIVE input until physical close
orphans it. For an unused API return, cache destruction runs in the child's real
storage pin before queued ancestor finally blocks; the second supplied exception
remains pending, while the earlier caught exception is only globally owned. A call
in assignment context keeps a result temporary and delays that cache destructor
until after receiver cleanup. Both keep the same input and Previous identity, as
checked by the
[repeated buffered THROW review](../../coverage/semantics/generator-repeated-pending-buffered-throw-review.json).
At a bare yield in one by-value array `foreach`, parked close instead transfers
the iteration container count into request retention before releasing CV/context
owners. It removes that iterator without decrementing the array; visited-item
CVs, locals and cached current copies still retire normally. Embedded cells keep
their live referents, and an array-owned Generator closes in the object-store
pass. See the [parked-foreach review](../../coverage/semantics/generator-pending-foreach-throw-review.json).
At a simple-CV used yield in that loop, the input is already orphaned when queued
frame close transfers the array count. Both remain owned, even if they name the
same HARRAY; its element edges are not multiplied. Local and current-copy cleanup
still proceed, including a replacement cache exception before caller catch. A
shared-cell rebind after close can therefore retain both the old input object and
the cell's new referent. See the
[joint lifecycle review](../../coverage/semantics/generator-pending-buffered-foreach-throw-review.json).

For one by-reference array loop at a bare yield, the retained count belongs to
the acquired reference wrapper. Close removes the iterator and retires the item
CV alias, leaving the wrapper and entry mutable.
Whole-wrapper replacement and escaped-item writes after close therefore have
distinct release effects. See the
[reference-foreach review](../../coverage/semantics/generator-pending-reference-foreach-throw-review.json).
With one authenticated simple-CV used-yield input, physical close first orphans
that input and then retains the acquired wrapper. A later wrapper or entry write
drops only its own edge, leaving the old input value alive. The
[buffered reference-foreach review](../../coverage/semantics/generator-pending-buffered-reference-foreach-throw-review.json)
checks these independent counts and ordinary cache-replacement cleanup.

The release walk preserves physical owner order, including compiled local-slot
order and key-before-value cleanup after a forbidden keyed yield. It can close
other started Generators through ordinary reference/array/object edges. General
user destructors remain an explicit dependency; this is not cyclic collection.

Ordinary eager slot release enters the same close walk before generic object
freeing. The actual operation or frame keeps its remaining release jobs and
pending Throwable while finally runs. Closing-Generator frame restoration takes
priority over ordinary eager CV staging; a replacement exception returns to the
outer release carrier, so later slots still release before propagation. Pending
eager releases without an operation or frame carrier remain Unsupported.

The [321 cache-release interaction](YIELD-KEY-WARNINGS.md) admits an uncalled
cached destructor through an authenticated top carrier and release-only path to
its exit. Local/caller pending exceptions merge before entry; replacements update
the same Generator release and exit. Other close stages and wider user-destructor
release remain required.

Forced entry skips the unfinished body and its catches. Already-entered finally
return/throw/break/goto outcomes release their held values in the actual caller
before proceeding outwards. Normal finally completion skips the ordinary body
suffix. New explicit return or throw uses the retained outer control tail:
a new exception may be caught inside the Generator and execute that continuation.
The caller's pending exception is restored if the new one is caught, or chained
only when a new exception actually escapes. The existing Throwable audit is
unchanged; forced entry fabricates no Throwable or return.

Finally execution retains the actual function, private lexical scope, called
class and live caller trace. A finalizer can start another Generator, whose
ordinary yield remains allowed. Only the currently closing Generator forbids
yield. Complex operand effects occur before rejection. Ordinary yield rejects
before delayed CV/key reads; yield-from reads its CV first, including its real
undefined-variable handler, then rejects before iterable classification. A
throwing handler becomes the forced Error's previous exception.

Admission checks one queued/entered close claim per Generator, genuine
zero-owner release excluding only its authenticated self pin, source suspension
identity and the complete remaining finally plan. The live forced marker is
mandatory. Captured foreach cursor owners remain visible while queued and retire
through the existing cursor cleanup. Heap-valid duplicate claims/cursors,
surviving external owners, wrong scopes/callers, erased or forged finally plans,
ordinary-marker substitution and stranded input continuations reject at
full public admission.

Module 340 continues normal source exhaustion through the real shutdown,
reverse-global and ascending object-store passes, including pure Generators.
Direct-global last-owner release follows these close rules and frees the cache.
Store close also closes externally owned suspended frames; it marks the real
handle called and transfers one native dtor pin, without replacing other owners.
An escaping exception reaches a registered normal handler after frame close
and before cache release. Uncaught exceptions and abrupt handlers remain required
Unsupported controls with zero agreement.

Store dtor returns with bare `GC_DELREF`. If frame cleanup removed the last
real owner, borrowed `(object,handle)` retirement keeps the allocated bucket and
outgoing cache graph with zero physical owners. Actual WeakReference acquisition
clears this retention, so its later ordinary last-owner release frees storage.
Admission checks the consumed handle, processed index, called mark, phase and
unique zero-owner certificate. Existing collector bare-retirement preparation
runs first; this metadata adds no heap root or collector-buffer tag.

The [request ledger](../../coverage/semantics/generator-request-finally-review.json)
records 19 distinct normal originals and 692 physical strict-SL premises across
separate cuts. 85 premises assert required abrupt controls and grant no observation
agreement. The actual330 composition over `7a0f8044f` passes strict compilation
at `1399d8a7e`; source/state cuts retain their own inputs. The original zero-owner
observer mismatch and earlier fixture/source failures remain zero.

Module 349 closes fresh frames during the real store pass without entering body
or finally. It releases bound cells and receivers in order, transfers the single
Closure owner into closed storage, and retains the actual store pin through CV
destructors. A normal exception handler runs before later CV release; admission
preserves the existing root destructor and store continuations. Ordinary closed
storage releases the Closure before value/reference, key and return caches,
without changing heap graph traversal. The [fresh and storage ledger](../../coverage/semantics/generator-fresh-store-review.json)
keeps original mismatches and separate source/state cuts.
The composition with 337 modules over `ed1c8c6a2` passes strict compilation at
`5dc524df4`. Its fresh typed-slot interaction retains the constraint through the
earlier child destructor and detaches it at the genuine slot release: one new
normal source and 79 strict premises, without renewing the private ten/584 cuts.

Module 355 retains the real free-storage pin for ordinary closed Generators.
It transfers Closure, value/reference, key and return owners one slot at a time,
keeping raw caches readable and the weak target live through child callbacks.
Only the final sole-pin release retires the allocation and then the store handle.
Pending Throwable ownership remains on the existing operation/frame; the same
continuation works after an ordinary forced close.
The [storage-pin ledger](../../coverage/semantics/generator-storage-pin-review.json)
keeps six exact normal sources and 784 new strict premises at their own cut.
Two affected maintained queues separately pass 209 premises. Actual342 over
`dc68616a3` passes strict compilation at `f78a1a06b`; earlier cuts are unchanged.

Delegating request close, abrupt terminal cleanup, parked storage work and
escaped reacquisition remain required. Nested ordinary-object storage during a
RETURN read is a separate required lifetime frontier; no full lifecycle claim.

Pinned authority is `vendor/php-src/Zend/zend_generators.c`, especially
`zend_generator_dtor_storage` and `zend_generator_free_storage`, plus authored
`ZEND_YIELD`/`ZEND_YIELD_FROM` in `Zend/zend_vm_def.h`,
`zend_execute_API.c::shutdown_destructors`, `zend_objects_API.c::zend_objects_store_call_destructors`
and `zend_exceptions.c::zend_throw_exception_internal`. The target remains PHP
8.5.10 CLI NTS 64-bit with the project profile, `LC_ALL=C`, `TZ=UTC`.

Independent source review closes 40 normal tuples and two compiler rejections
across `generator-force-close-review-rlbhdmu_` (first16), `78yejgzi`
(remaining22 plus compiler2) and `k7mcky3f` (introduced foreach2). Five exact
Unsupported controls earned no agreement at that303 cut: request-end close, a self-cache cycle,
bare finalizer exit, exit with a started local child and warning-handler exit.
Module310 separately covers ordinary paused-Generator release inside an active
Fiber. Wider request/terminal cleanup, parked running Generators, cyclic GC, user
destructors and broader Generator/reference APIs remain required.

Eight ordinary source programs pass in eleven finite state groups: 88 reached
premises in `generator-force-close-protocol-9scbub2v`, 287 in `ref9gfv7` and 194
in `vx6br71h` (569 including source/phase bindings and repeated setup). These
are setup-inclusive conditions, not distinct semantic tests. Each passing group
executes its full body, full public/heap admission, exact zero-budget state and
direct/resumed normal completion. The groups include heap-valid malformed-state
rejection. Original compiler, optional-result, malformed-DONE overlap and
scope-observer failures retain zero.

Records live in `.tools/traversal-generator-force-close-xa0fu1q3/.tools` in the
main workspace. The tested copy is actual `38f1dfaa045f`/273 plus reviewed289 and
the one-clause284 property ingress (274), then303 (275). Parent composition and
union records, per-cut candidate diffs, runtime/compiler identities, commands,
exits and exact observations identify this copy; enclosing Git HEAD alone does
not. The final compiler `generator-force-close-compile-6s5b2q2l` produces
8,662,573 bytes of complete structured output with empty stderr and exit0.
Private validation reuses the maintained binaries and grants no new offline
rebuild or final combined-core credit. Canonical integration preserves the newer
eager-destruction and Fiber clauses; the bounded actual282 composition passes the
[introduced compiler, source and state checks](GENERATOR-FIBER-CLOSE.md).
Original Unsupported observations for the two now-admitted last-owner sources
remain in their earlier cuts. 340 separately promotes the byte-identical request
and self-cache-cycle originals; their old Unsupported observations stay zero.

`python3 tests/semantics/generator_force_close_review.py --select graph-temporary-child`
compares the complete native/model tuple at source60/outer90 seconds.
`python3 tests/semantics/generator_force_close_protocol.py --mode check --sl --select graph-input`
executes source-reached state conditions through the maintained strict SL runner
at300 seconds, caching disabled and deterministic checking enabled, jobs1.
Native mode and fixture preparation earn zero model/state execution credit.
