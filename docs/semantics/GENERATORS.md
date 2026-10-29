# Generators

Module280 creates Generator objects after ordinary argument, type and default
receives. The function body and Closure lexical loads remain deferred until
initialization. Named functions, ordinary Closures and ordinary object method
calls use the accepted call machinery; no unaccepted return implementation is
required.

[Same-class comparison](../../coverage/semantics/generator-fiber-comparison-review.json)
now returns order zero for distinct Generators, including fresh, paused and closed
values. It preserves the deferred frame, captures and cached results.

The Generator owns its suspended function frame. Resuming moves that frame into
the machine and saves the actual resumer. Yielding moves it back into the object.
The frame, received arguments, receiver and Closure captures are outgoing heap
edges of the Generator, not permanent roots. Natural completion releases the
execution frame but retains the last yield cache, return value and Closure owner.

By-value yields retain raw keys, copied array containers and embedded reference
cells. Key expressions precede value expressions; a simple key CV is fetched
after value effects. Implicit integer keys wrap at the pinned signed64 boundary.
The old yield cache is released before fetching the next CV operands. Ordinary
eager destructors remain an explicit dependency boundary.

Literal `current`, `key`, `valid`, `rewind`, `next` and `getReturn` calls initialize
a fresh Generator as required. Rewind follows the actual root's first-yield
history; synthetic shared-child resumes preserve that history. Fresh `next`
initializes and advances, while empty initialization
preserves the first-yield flag. `getReturn` starts an uninitialized Generator,
then returns its by-value completion or throws without advancing a suspended
yield. Positional excess arguments run before the argument-count error and appear
in its trace.

A named Generator entered by direct zero-argument CURRENT or NEXT can suspend
inside an already running Fiber. Its actual resume operation and parameter cells
move with that VM; the running Generator owns no duplicate frame. Resume restores
the same body and supplied-Throwable injection follows its real catch/finally.
An outside NEXT before the first yield fails both native initialization and resume,
chaining two Errors; with an existing cache only resume fails. The
[transfer review](../../coverage/semantics/generator-fiber-transfer-review.json)
keeps the original pre-target observer refusal separate from the reached transfer
fence. Method/Closure helpers, wider delegation, reference caches and wider
close/collection histories remain unvalidated.

Ordinary named helpers above that body also survive Fiber transfer. Each genuine
caller frame is projected only for local validation; the real VM keeps all helper
locals, parameters and continuations. Full-prefix flatness and one resumer prevent
a duplicate or nested marker from disappearing during the query. One/two helper
frames retain two/three independent parameter cells for the same object; normal
returns or supplied-Throwable unwinding retire them in actual order. The
[helper review](../../coverage/semantics/generator-fiber-helper-transfer-review.json)
keeps native discovery, the genuine refusal and source/state cuts separate.
Method/Closure helpers, by-reference returns, wider delegation/cache/other-API histories,
CONFIG consumers and wider close/collection remain unvalidated.

Named native `yield from` chains also retain every real resumer and source claim
when the active leaf suspends in a Fiber. A local proof follows authenticated
`FROM_RESULT` pairs to the direct CURRENT/NEXT root; full-prefix checks prevent
hidden or duplicate carriers. Stored VM scans preserve occurrences without
deduplicating them, and the actual machine and pending-initialization bits stay
unchanged. Fresh one-link normal return and supplied-Throwable abort have source
agreement. Cached NEXT retirement and the two-link caught-Throwable whole source
also agree under a fixed, separately recorded 180-second model limit. Their
earlier 100-second timeouts retain zero credit; sources and operational rules
are unchanged. [Review and reproductions](../../coverage/semantics/generator-fiber-delegation-transfer-review.json).

A primed named Generator entered by one-value `send` also retains its authentic
resumer across Fiber suspension. The native argument buffer owns its value
separately from the delivered CV, survives that CV's unset and retires before
the caller continues, including supplied-Throwable unwinding. An object yield
can additionally belong to the Generator cache, stored Fiber return and caller
copy. This extends admission without adding roots or changing operations.
[SEND review](../../coverage/semantics/generator-fiber-send-transfer-review.json).

Plain unbound Closure-created Generators can also suspend their direct CURRENT
body inside a Fiber. The source-authenticated raw callee moves with the real VM;
copied captures own values separately, while reference captures share their cell
with the outer variable. Natural completion or supplied-Throwable unwinding keeps
the closed Generator's callee and captures until actual Generator destruction.
Fresh outside NEXT chains initialization and resume Errors for this callee form
as well. Existing capture and frame roots are unchanged. Method/bound wrappers,
Closure helper/delegation combinations and wider collection remain partial.
[Closure transfer review](../../coverage/semantics/generator-fiber-closure-transfer-review.json).

Ordinary public instance-method Generator bodies also move their real
`METHOD_TARGET` callee with the VM. The receiver remains one physical callee
owner while parked; admission validates its live receiver and original class,
source and call context. No roots or transfer operations change. A scalar-yield
body releases its receiver at completion, while a closed self-yield cache keeps
one owner until Generator destruction. Supplied Throwables preserve identity
through caught or unhandled retirement and the caller's finally.

Four native originals and four source comparisons pass. The genuine baseline
selects only the fresh CURRENT original and explicitly refuses Fiber transfer,
with zero agreement. Strict/source results retain `3eedf46ed`; 335 focused
premises retain `0c0079651`, and only the corrected 89 retain `aa0534778`.
The original fixture incorrectly required an empty WeakReference row after
retirement. Its diagnostic confirms nonowning target history with public NULL,
physical receiver absence and owner zero; that failure and diagnostic remain
zero credit. Scoped/static/bound/accessor wrappers, wider helper/delegation,
reference and collection combinations remain partial.
[Method receiver evidence and recovery](../../coverage/semantics/generator-fiber-transfer-review.json).

Direct named by-reference Generators can also park during NEXT with a cached
reference cell from an earlier yield. The Generator keeps the original cell
while the Fiber VM owns the running frame; rebinding its source variable name
does not retarget the cache. `current()` reads the live cell while the Fiber is
parked, and the next yield retires the old cache before caller continuation.
An outside NEXT sees one running-Generator Error when this cache is defined;
the fresh, uncached path retains its two-Error chain. Supplied Throwable
unwinding and a closed cache keep their existing cell ownership. Admission
requires a named by-reference producer and live cell; method/Closure cached
reference forms and wider helper/delegation combinations remain partial.
[Reference transfer review](../../coverage/semantics/generator-fiber-reference-transfer-review.json).

A primed direct named Generator can also suspend inside a local `catch` or
pending `finally` while handling `Generator::throw($given)`. Its old by-value
yield cache stays on the Generator, and the saved resumer carries the same
Throwable through the Fiber VM. Resuming the Fiber can yield a new value,
propagate the original Throwable, or replace it with a supplied Fiber throw;
three primed THROW sources distinguish identity, `Previous`, reentry Error and
cache release; a fresh CURRENT source preserves the earlier path. Admission
requires one valid Throwable, a defined by-value cache and a direct named
callee. At that cut, by-reference, method, Closure and delegated THROW
transfers remained partial.
[THROW transfer review](../../coverage/semantics/generator-fiber-throw-transfer-review.json).

A fresh direct named `Generator::throw` can park before its first yield. Its
saved advancing resumer owns a temporary Throwable made for the call while the
Fiber holds the running body. On normal resume the first yield is followed by
injection: the exception can escape or be caught and followed by a recovery
yield. If `Fiber::throw` aborts the pre-yield pause, the original API Throwable
escapes with the Fiber Throwable as `Previous`. Three exact pre-yield sources
and one 86-premise reached state cover the uncached owner and resumer; two
post-yield fresh sources and a primed source are unchanged controls. Other
fresh call shapes and wider producer/delegation/lifecycle combinations remain
partial. [Fresh THROW transfer review](../../coverage/semantics/generator-fiber-fresh-throw-transfer-review.json).

A primed direct named by-reference Generator can also enter `throw` with a
cached reference cell. Its saved resumer owns the supplied Throwable, while the
Generator retains the original cell through a catch or pending-finally Fiber
pause. `current()` dereferences that cell without resuming; rebinding the
source name leaves the cache intact. A later yield or Generator release retires
the old cell. Normal resume preserves the original Exception, and
`Fiber::throw` makes it the replacement's `Previous`. Four original sources,
including an independent cache-only release probe, agree with PHP 8.5.10,
with 102 author source-reached state assertions and an unchanged by-value
control. Admission requires a live cell, by-reference
producer, one valid Throwable and direct named target. At that cut, other
producer, callee and delegated THROW forms remained partial.
[Reference THROW review](../../coverage/semantics/generator-fiber-reference-throw-transfer-review.json).

A primed ordinary public method Generator can now enter `throw` with a
by-value cache. The saved resumer owns the temporary Throwable and the
authenticated `METHOD_TARGET` retains the actual receiver across the Fiber
pause. A scalar-yield receiver dies at Generator completion; a self-yield
cache retains it after close until Generator release. Normal pending-finally
resume preserves the original exception, while `Fiber::throw` replaces it
with the original as `Previous`. Four exact new sources, including an
independent cache-replacement probe, and two source-reached states/157 checks
distinguish these owners; the direct named by-value source remains an
unchanged control. By-reference method, fresh method, Closure and delegated
THROW forms remained partial at that cut.
[Method THROW review](../../coverage/semantics/generator-fiber-method-throw-transfer-review.json).

A primed plain unbound Closure-created Generator can now enter by-value
`Generator::throw` while its body suspends in a Fiber. The saved resumer owns
the temporary Throwable, and the real `CLOSURE_TARGET` retains the selected
Closure and its copied or reference capture. Rebinding an external variable
name leaves the old captured cell intact; a copied capture retains its old
object while an original reference cell observes later writes. The old yield
cache remains readable while parked. A recovery yield retires that cache, and
a closed Generator retains both an object cache and its Closure capture until
release. Normal and supplied-Fiber-Throwable paths preserve the native
exception identity and `Previous` order. Five new exact sources, including
independent cache replacement, and three reached states/302 assertions cover
this bounded shape; the direct named control is unchanged. At that cut,
Closure BYREF and fresh THROW, bound Closure, method BYREF/fresh, delegated
and helper forms remained open. [Closure THROW review](../../coverage/semantics/generator-fiber-closure-throw-transfer-review.json).

A fresh plain unbound Closure-created by-value Generator can also enter
`throw` before its first yield and suspend in a Fiber. The original API
Throwable stays in the advancing saved resumer, with empty cache and reference
cell. Normal Fiber resume reaches the first yield before injecting that
Throwable; a catch may yield a recovery value, or a `finally` may let the
original escape. Copied captures retain an old object, while reference
captures read their original cell after the external name is rebound. The
closed Generator retains its Closure and object cache until its own release.
An injected `Fiber::throw` before the first yield makes the original Throwable
escape with the supplied one as `Previous`; an outside `current()` reentry
produces one Error with null `Previous`. Four exact fresh originals, including
an independent abrupt case, an unchanged primed control and 117 source-reached
strict premises support this boundary. By-reference, method, bound Closure,
delegated and wider lifecycle paths remained partial at that cut.
[Fresh Closure THROW review](../../coverage/semantics/generator-fiber-fresh-closure-throw-transfer-review.json).

A primed plain unbound Closure-created by-reference `Generator::throw` now
transfers an authenticated cached reference cell and Closure target through a
Fiber catch or pending `finally`. The Generator keeps the old cell when an
external source name is rebound; a copied Closure capture and an original
reference capture remain distinct. While parked, `current()` reads the old
cell and an outside `next()` gets one running-generator Error with null
`Previous`. The saved temporary Exception reaches the catch or survives a
normal `finally`; a supplied `Fiber::throw` replaces it with the original as
`Previous`. Weak references show the cache and Closure remain live through
close and retire when the Generator is dropped. Three authored exact sources,
one independent normal-finally source, two unchanged direct/by-value controls
and 136 custom source-reached checks
support this bounded path. The reference-capture source first timed out at
180 seconds with zero credit, then passed a selected 240-second budget. At
that cut, fresh by-reference Closure THROW, method by-reference/fresh,
bound/delegated and wider lifecycle paths remained partial.
[Closure reference THROW review](../../coverage/semantics/generator-fiber-closure-reference-throw-transfer-review.json).

Fresh unbound Closure-created by-reference Generator::throw now transfers
while its cache is empty and the saved resumer is advancing toward the first
yield. Zend initializes to that yield before injecting the original
Throwable. The yielded CV supplies a live reference cell; throw() returns
a dereferenced snapshot, so a later cell write changes current() without
changing the returned value. An external name rebind leaves the old cell
selected, and copied versus reference Closure captures keep distinct owners.
Normal catch/finally and independently frozen pre-yield Fiber::throw abort
sources agree with pinned PHP. Four new exact sources, two unchanged controls,
and 118 custom source-reached checks cover this bounded transfer. Three
authored sources were Unsupported on the unchanged parent; one first
reference-capture timeout remains zero credit. Method by-reference/fresh,
bound/delegated and wider lifecycle paths remain partial.
[Fresh Closure reference THROW review](../../coverage/semantics/generator-fiber-fresh-closure-reference-throw-transfer-review.json).

A primed ordinary public method-created by-reference Generator now admits
`throw` with an authenticated cached cell and receiver. The saved Fiber resumer
keeps the temporary Throwable, while `current()` reads the old cell after its
external source name is rebound. `throw()` returns a dereferenced snapshot;
later writes through the old cell change `current()` without changing that
snapshot. Normal and supplied `Fiber::throw` paths preserve exception identity
and `Previous` order. Separate receiver and cached-object lifetimes agree in
three authored sources and an independent cache-replacement source. Two direct
BYREF/method BYVAL controls, strict compilation and 129 source-reached checks
pass. The three authored sources were `Unsupported` before the edit. At that
cut, fresh method, bound/delegated and wider lifetime forms remained partial.
[Method reference THROW review](../../coverage/semantics/generator-fiber-method-reference-throw-transfer-review.json).

A fresh ordinary method-created by-reference `Generator::throw` now also
transfers before its first yield. Its advancing resumer keeps the original
temporary Throwable while both caches are empty; the authenticated method
context keeps the receiver. Rebinding the external parameter name leaves the
old cell selected, and the first yield creates the reference cache. The returned
value is a snapshot while later `current()` follows cell writes. Normal cleanup
separates receiver retirement from a distinct cached object; a self cache keeps
the receiver after close. Before the first yield, supplied `Fiber::throw` aborts
without a cache and the original Throwable escapes with the supplied one as
`Previous`. At that cut, fresh by-value method THROW, bound/delegated and wider
lifecycle forms remained partial.
Four new originals agree exactly with PHP; two source-reached cuts check
229 custom premises for admission, cache ownership and cleanup.
[Fresh method reference THROW review](../../coverage/semantics/generator-fiber-fresh-method-reference-throw-transfer-review.json).

Fresh ordinary public instance-method by-value `Generator::throw` now uses the
same authenticated empty-cache transfer. Inherited methods retain Parent lexical
scope, Leaf called scope and the real receiver; copied parameters remain separate
from caller writes. Resuming to a yield installs a value cache. Normal and supplied
throws preserve distinct Token versus self-cache lifetimes and the pre-yield versus
pending-finally `Previous` order. Four new originals agree exactly with PHP;
three source-reached fronts check 307 custom premises. Two I63/I61 controls retain
their parent cuts, and I69 BYREF evidence is not replayed. At that cut, fresh direct
named BYREF THROW and static/scoped/bound/delegated or wider lifecycle forms
remained partial.
[Fresh method THROW review](../../coverage/semantics/generator-fiber-fresh-method-throw-transfer-review.json).

Fresh ordinary named by-reference `Generator::throw` now transfers before its
first yield with a saved original Throwable and empty caches. Shared parameter
cells survive source-name rebinding; the API returns a snapshot while `current()`
follows cell writes. Checked dynamic selection retains the original registered
function, and a copied by-value formal becomes a reference cache only at yield.
Normal and supplied throws retain local/cache ownership and the distinct pre-yield
versus pending-finally `Previous` order. Four new originals agree exactly; three
source-reached fronts check 313 custom premises, including full-VM forged-context
rejection. I62/I61 controls retain their parent cuts without I69/I70 replay.
Static/scoped method targets, bound/delegated and wider lifecycle forms remain
partial. [Fresh reference THROW review](../../coverage/semantics/generator-fiber-fresh-reference-throw-transfer-review.json).

Shared Generator delegation records pending initialization separately from the
first-yield flag. Synthetic shared-child operations preserve this nonowning bit;
an actual API or iterator root resume clears its own bit. Cache-only getter
refreshes preserve it. An actual `next()` with pending initialization and a live
current consumes the bit without advancing, including after child detachment.
This history also determines the [forced-close exception](GENERATOR-FORCE-CLOSE.md)
for an inherited middle that owns a copied current.

A pending `send` on a source-authenticated detached root with a nonowning copied
return clears initialization and returns a dereferenced current snapshot without
advancing. `YIELD_FROM` has reset the native send target, so the argument is not
buffered. Argument cleanup precedes receiver release, keeping a sole receiver
alive while destructors run. A returned row stays separate from a reference cache
changed by that cleanup; an argument-destructor throw preserves the cleared bit.
Synthetic shared-child resumes also preserve the first-yield flag: an inherited
middle rejects rewind, while a previously initialized middle can still accept it
after shared advancement. The [pending-send review](../../coverage/semantics/generator-pending-init-send-review.json)
records both histories.

Pending `send` also admits an owning copied return at a simple-CV assigned
`yield from`, with no other owning suspended tasks or held values. It preserves
the waiting return while capturing the cache before ignored-argument cleanup.
Actual next consumes that return; close retains its count. If an argument
destructor throws, the cache snapshot survives receiver retirement and can replace
that exception before caller catch. The
[owning SEND review](../../coverage/semantics/generator-pending-owning-return-send-review.json)
records this path separately from pending `throw`.

An inherited-pending ancestor can also `send` through finite native links to
that owning simple-CV return, even when the call first detaches the completed
child. Only the selected receiver's initialization clears; the physical middle
still waits without buffering the argument. Normal argument destruction can
change a raw reference cache or remove every Generator alias while the captured
result survives. Actual outer next consumes the return; inherited-pending middle
close instead retains it and skips finally. The
[ancestor SEND review](../../coverage/semantics/generator-pending-owning-chain-send-review.json)
checks separate receiver, middle and child identities, COW and mutable return cells.

Pending `throw` on that actual detached receiver now also preserves the owning
simple-CV return. It reaches the caller without advancing, leaves getters live,
and parks the frame so close omits its finally. Close transfers the return count
to request retention before dropping frame owners; its embedded cells remain
mutable. The transient cache copy retires independently before catch and may
replace the supplied exception with Previous intact. The
[owning THROW review](../../coverage/semantics/generator-pending-owning-return-throw-review.json)
keeps the direct receiver distinct from an inherited-pending ancestor. The latter
now follows finite native links, including first child detachment inside THROW.
Only the receiver clears initialization; the physical middle retains both its
pending bit and parked source site. Its copied return survives getters and close;
the transient cache copy retires independently, including after sole-receiver
cleanup and replacement exception chaining. The
[ancestor THROW review](../../coverage/semantics/generator-pending-owning-chain-throw-review.json)
checks those identities, same-array COW and mutable returned cells.
A parked owning continuation can also take another pending THROW through a
still-pending receiver. Only that receiver bit clears; the physical source site,
frame and copied return remain unchanged. Reversing middle/ancestor calls proves
that the leaf bit does not control this early return. Distinct and same-object
exceptions and sole-middle cache replacement are checked in the
[repeated THROW review](../../coverage/semantics/generator-repeated-pending-owning-throw-review.json).
Pending SEND at that same owning continuation also returns before body entry.
It clears only the selected receiver bit and snapshots current before normal
ignored-argument cleanup. The physical frame/site and return count stay intact;
row COW and used-cache survival after Generator retirement are checked in the
[parked SEND review](../../coverage/semantics/generator-parked-pending-owning-send-review.json).
For normal unused SEND in this owning-return slice, current remains copied
through ignored-argument cleanup, then retires before the selected receiver.
Argument-driven COW therefore sees the snapshot, while its old payload can die
before ancestor finally blocks. An assigned SEND result keeps its copy through
receiver cleanup until the caller drops it. This correction requires the exact
consumed argument/receiver slots; abrupt argument callbacks remain unvalidated.
See the
[unused SEND review](../../coverage/semantics/generator-unused-pending-send-review.json).
An owning argument identical to current can also take this path when the fresh
result masks its consumed slot. The tested cases have argument, result and current
as three owners; two quiet releases leave only current before receiver cleanup.
A shared array keeps one element-edge set throughout. Assigned calls keep
the net result transfer; other masked shapes remain unvalidated. See the
[aliased SEND review](../../coverage/semantics/generator-unused-pending-send-alias-review.json).
Normal unparked pending ancestor SEND also releases an unused copy before the
receiver.
An exact refresh-produced child release stays before the argument and result;
a prior getter leaves no prefix. The tested child/copy return counts share one
array element-edge set until child storage retires. Assigned copies, argument
COW and equal-cache cleanup keep their separate lifetimes; see the
[normal SEND review](../../coverage/semantics/generator-unused-detached-send-review.json).
At the pre-refreshed direct physical receiver, normal pending SEND likewise
releases its unused copy before forced finally. A byref raw row then has no
snapshot forcing COW, so replacing its old element runs its destructor before
`J-END`. Assignment retains the extra container until the caller drops it.
Equal argument/current values still supply two real release owners; clearing an
object-valued raw cell in finally can throw before the next statement. See the
[direct SEND review](../../coverage/semantics/generator-unused-direct-detached-send-review.json).
At that cut, direct refresh prefixes remained unvalidated.
Direct pending SEND now also authenticates an allocated closed child before
refreshing its normal owning return. It releases that child before argument,
unused result and receiver cleanup. Rebinding raw current during argument
evaluation preserves the older argument; finally sees the new row or object.
Assignment keeps its independent copy. Wider refreshes, abrupt argument
callbacks, body entry and collection remain unvalidated; see the
[direct refresh review](../../coverage/semantics/generator-unused-direct-refresh-send-review.json).
A pre-refreshed direct pending SEND can likewise have a node-free copied return
and an owning current value. The current snapshot survives normal argument
mutation, then an unused copy retires before receiver finally; assignment keeps
its copy. Tests cover `return 0`, NULL and a literal string without retaining an
owning return receipt. Wider input histories, abrupt argument callbacks, body
entry and collection remain unvalidated; see the
[scalar-return SEND review](../../coverage/semantics/generator-unused-scalar-return-send-review.json).
Without a getter, direct pending SEND can refresh one allocated closed child to
that node-free COMPLETE. The child releases its cache edge before normal
argument cleanup; the unused current snapshot retires next, before receiver
finally. Assignment,
argument-time row COW and a cache RuntimeException inside finally preserve their
distinct owners without an owning return root. Ancestor/wider refreshes, abrupt
argument callbacks, body entry and collection remain unvalidated; see the
[node-free refresh review](../../coverage/semantics/generator-unused-scalar-refresh-send-review.json).
Pending ancestor SEND also handles one native link to a PAUSED bare-statement
yield, without a send target or buffered input. The selected receiver clears
its initialization bit while the child stays paused. Its current snapshot
survives normal argument cleanup; an unused copy retires before receiver
release. In the tested alias-drop histories, Child finally runs before Middle
finally. Assignment keeps the copy. Row COW and a
cache RuntimeException from Child finally distinguish these owners without a
COMPLETE or copied-return root. Wider links, abrupt argument callbacks, body
entry and collection remain unvalidated; see the
[bare-yield SEND review](../../coverage/semantics/generator-unused-bare-yield-send-review.json).
One pending native ancestor above a normal node-free COMPLETE middle also
returns current without entering either body. Child refresh contributes its
exact closed-child release; a prior getter leaves no prefix. Only selected
Upper clears its bit. In the tested alias-drop histories, still-pending Middle
skips J while Upper finally mutates the row. A first pending Middle NEXT clears
that physical bit independently: later Upper SEND can trigger Middle finally,
where slot clearing throws a cache RuntimeException before Upper finally,
with Previous NULL. Unused copies retire after normal argument cleanup;
assignment keeps its copy. Wider chains, masked or abrupt arguments, body entry
and collection remain unvalidated; see the
[node-free ancestor SEND review](../../coverage/semantics/generator-nodefree-ancestor-send-review.json).
Zero-argument CURRENT also drops an unused snapshot before releasing its
receiver. The validated producer first clears selected Upper with an
initialization-only NEXT and leaves one already-refreshed native link to a
node-free COMPLETE Middle. CURRENT preserves both initialization bits.
Assignment retains its copy through cleanup until the caller drops it. The
normal cache destructor runs before Upper finally in the tested sole-receiver
history; raw-row mutation and a cache RuntimeException inside initialized Middle
finally distinguish the missing extra owner. Wider child prefixes/endpoints
and collection remain unvalidated for this CURRENT rule. See the
[unused CURRENT review](../../coverage/semantics/generator-unused-current-review.json).
The same pre-refreshed one-ancestor endpoint now drops unused CURRENT snapshots
while selected Upper is still pending. CURRENT preserves both bits; physical
Middle can already be initialized by its own NEXT. Its row rewrite releases the
old value inside Middle finally, while assignment retains its copy through both
finally blocks until caller drop. Normal and throwing object slot clears occur
inside live Middle finally; a separately global-owned Exception is not selected
as Previous. The existing close plan runs both J and K in these originals. See the
[pending CURRENT review](../../coverage/semantics/generator-pending-unused-current-review.json).
The target CURRENT can now perform the first refresh through one allocated
CLOSED Child. The original child link, actual refresh, updated node-free Middle
and exact child-only slot loss authenticate this path. Child's complete owned
children must equal the transferred current operand, keeping its storage release
quiet. The existing child-storage prefix precedes receiver cleanup, with no unused
snapshot owner; assignment retains its ARRAY. Extra key/return/Closure owners,
masked child/current identities and wider histories remain unvalidated. See the
[first-refresh CURRENT review](../../coverage/semantics/generator-refresh-unused-current-review.json).
The pre-refreshed direct node-free pending SEND path also survives an ignored-argument
destructor throwing a supplied Exception. Its remaining snapshot and receiver
cleanup still run. Assignment context keeps the VM temporary through physical
finally, but no CV store completes after the argument throws. Argument-time
row COW separates the old snapshot from live current; a RuntimeException from
slot clearing inside Middle finally links the supplied Exception as Previous,
whose own Previous remains NULL. This validates existing rules without a
runtime change. Wider, parked and collection histories remain unvalidated; see the
[abrupt argument SEND review](../../coverage/semantics/generator-abrupt-argument-send-review.json).
The same abrupt argument cleanup is validated through one native ancestor.
Only selected Upper clears initialization; inherited-pending Middle still skips
finally, while an independent Middle NEXT permits physical finally execution.
Unused snapshot retirement, assignment's unstored temporary, argument-time COW
and a cache RuntimeException before Upper finally preserve their distinct owners
and supplied Previous identity. No runtime rule changes; wider links, owning
returns, parked/reentrant histories and collection remain unvalidated. See the
[ancestor argument-exception review](../../coverage/semantics/generator-ancestor-abrupt-argument-send-review.json).
Pending zero-argument NEXT also clears only the selected receiver bit while
preserving that parked owning frame/site and copied return. It returns NULL
without a current snapshot; a later explicit getter creates a separate copy.
Sole-receiver cache destruction can therefore precede caller delivery, without
chaining an older caught exception that is merely globally owned. See the
[parked NEXT review](../../coverage/semantics/generator-parked-pending-owning-next-review.json).
One owning buffered input at a parked simple-CV used yield also admits pending
zero-argument NEXT through native links. Only the selected receiver clears its
bit; the physical child, input and parked frame stay unchanged. NULL adds no
cache owner. Physical close orphans the input before storage releases current,
so a cache destructor can run before ancestor finally blocks and caller delivery.
See the [buffered NEXT review](../../coverage/semantics/generator-parked-pending-buffered-next-review.json).
A first pending SEND can instead replace that sole owning LIVE input with one
new owning argument. The old count becomes orphaned without decrement; the new
input becomes LIVE before the selected receiver initializes and current is copied.
The physical child/frame stay parked. A used snapshot survives Generator storage
retirement, separately from both request-late inputs. Row COW and old-input cells
versus new direct copies distinguish these owners in the
[buffered SEND review](../../coverage/semantics/generator-parked-pending-buffered-send-review.json).
With exactly one owning LIVE input record, another pending THROW preserves it
without writing it or entering the parked child. The selected receiver alone
clears initialization; distinct and reused supplied exceptions keep their
identities. An unused API return drops its transient current copy before receiver
cleanup, whereas a call in assignment context retains its temporary copy until
exceptional result cleanup. A sole-cache destructor can therefore run before or
after ancestor finally blocks, independently of the orphaned input. The
[repeated buffered THROW review](../../coverage/semantics/generator-repeated-pending-buffered-throw-review.json)
also checks raw-row COW and mutable input cells after close.
Previous orphans, multiple records, nonowning arguments, nonpending body entry and
wider loop/held continuations remain outside this admission. Explicit collection
is outside this validated slice.

A direct detached parent with an owning copied return now admits ordinary unpack
at a simple-CV assigned `yield from`. Null-key rejection leaves its COMPLETE
continuation intact. Actual next transfers the value into the parent result;
forced close instead preserves that single count before frame cleanup and finally.
The current cache retires separately and may replace the unpack Error. A returned
array retains its live embedded cells, so later writes can retire old referents.
The [owning-return review](../../coverage/semantics/generator-owning-detached-return-review.json)
keeps normal consumption, close retention and the original affected control separate.
Ordinary unpack now also follows finite native ancestor links to that owning
simple-CV continuation. Refresh can detach the child without an intervening getter;
the ancestor borrows current while the physical middle owns the single return copy.
A null key errors before sending or callee entry. Actual outer next consumes the
return normally; close retains it and respects the middle's initialization history.
The [owning-chain review](../../coverage/semantics/generator-owning-chain-unpack-review.json)
checks these paths, cache-error replacement and mutable returned cells. Wider
continuations and explicit collection while that copied result waits remain open.

Pending `send` through finite native Generator links can also fill a paused
child's used yield assigned directly to a simple CV. It clears the actual root's
initialization bit and returns a current snapshot without advancing. When a later
direct or forwarded `next` resumes the child, it transfers the single buffered
owner into that yield result. Closing before consumption or overwriting with
another `send` preserves the pinned engine's untraced reference count; its payload
destructor runs in the request object-store pass, after ordinary finally and caller output. Pure getters
preserve the buffer. The [shared-send review](../../coverage/semantics/generator-pending-shared-send-review.json)
distinguishes payload ownership from reference caches, method receivers and
Generator frames. Other used-expression shapes remain Unsupported; this slice
makes no general cyclic-collection claim.

A non-pending direct or native forwarded `throw` into that paused child releases
the buffered yield result before searching its catch handlers. The slot uses a
temporary decrement that does not register a potential GC root; outgoing child
slots keep ordinary cleanup. An aliased current remains alive until its own cache
is replaced. A payload-destructor exception replaces the injected exception while
keeping it in the previous chain. The [buffered-throw review](../../coverage/semantics/generator-buffered-throw-review.json)
checks these distinct owners and the real exception-search continuation. Pending
`throw`, acquired data and other yield-result shapes remain outside this route.

A pending `send` through native links to a bare statement yield instead ignores
the argument and adds no buffered owner. It returns a dereferenced current
snapshot without advancing. Argument destruction precedes receiver release: it
can change a live reference cache after the snapshot or throw while initialization
stays cleared. Real aliases determine later child/middle finally order. The
[unused-target review](../../coverage/semantics/generator-pending-unused-send-review.json)
checks scalar/object caches, COW snapshots and the supplied cleanup exception.
Other discarded-expression shapes remain outside this bounded admission.

Pending `throw` on a delegating actual root can reach a bare statement yield
through native links, or a detached current with a node-free copied return.
It clears initialization without entering the body and throws the supplied
Throwable to the caller. A transient dereferenced current copy survives receiver
close, then retires before caller catch; its destructor can replace the exception
and preserve the previous chain. The physical frame keeps nonowning parked-source
history, so getters preserve its cache while later real resumption stays
Unsupported. Explicit close omits that frame's finally even after initialization
was cleared. The [pending-throw review](../../coverage/semantics/generator-pending-throw-review.json)
initially bounded suspended task/held owners to empty. A simple-CV used yield can also carry
one authenticated live input: pending `throw` and getters leave that count in
place. Physical leaf close retains it until request-store destruction, including
when receiver retirement closes the child before caller catch. It does not run
the non-pending slot decrement above. Two pending
ancestors let a lower `send` fill the slot while an upper `throw` still takes
this no-advance path. The [pending-buffered review](../../coverage/semantics/generator-pending-buffered-throw-review.json)
separates input, current-copy and raw reference-cache owners. Other owning
unfinished temporaries and later exception-opline resumption remain open.

One by-value array `foreach` may also be suspended at a bare yield, without a
buffered input or other owning task/held values. Parked close retains its one
container count, removes the iterator and releases ordinary locals. COW arrays,
mutable embedded references and a nested Generator keep their distinct owners.
Explicit collection while that frame is parked is Unsupported; see the
[parked-foreach review](../../coverage/semantics/generator-pending-foreach-throw-review.json).

The [joint lifecycle review](../../coverage/semantics/generator-pending-buffered-foreach-throw-review.json)
adds one buffered simple-CV yield result inside that loop. Pending throw preserves
both counts; physical close orphans the input and retains the iteration container
separately. Even when they name the same array, its element edges occur only once.
A later shared-cell rebind drops that cell's old referent while the buffered old
object remains retained. Cache snapshots and replacement exceptions keep their
existing cleanup order. Other owning suspended values and later resume stay open.

A bare yield inside one by-reference array loop retains its acquired
reference wrapper across parked close. The item CV aliases an embedded cell and
retires separately. Replacing the wrapper's value drops its edge to the old array
while the new value stays retained; an escaped item write changes that entry. See the
[reference-foreach review](../../coverage/semantics/generator-pending-reference-foreach-throw-review.json).
The [buffered reference-foreach review](../../coverage/semantics/generator-pending-buffered-reference-foreach-throw-review.json)
adds one authenticated simple-CV used-yield input to that loop. The input value and
acquired wrapper contribute separate owners, with one set of array-entry edges.
Whole-wrapper replacement or an escaped-item write can therefore leave the old
input alive while the wrapper reaches the new value. Wider owning tails, object
loops and later parked resume remain open.

Literal `send` and `throw` validate and capture their single argument before
initialization. Fresh calls first reach the initial yield, then deliver the
value or Throwable at that suspension. `send` supplies the result of a used
yield expression; `next` supplies null when no buffered input exists. Closed
`send` returns null, while closed `throw` rethrows the same object. If fresh initialization throws, `throw` keeps
its supplied exception as primary and links the initialization exception as its
previous exception. Ordinary catch/finally execution can yield again before the
pending exception resumes.

The saved API operation owns its argument through initialization and resumption.
Arrays keep copied-container behavior and shared embedded references; objects
retain identity. API trace rows retain the actual argument and live caller.
Admission separates pending argument evaluation from completed resume arity,
type and phase. A restored exception search precedes one closed, unsuccessful
resume marker; it cannot be duplicated or moved into a saved owner frame.

Value `foreach` uses the native Generator iterator protocol without adding a
synthetic method trace row. Direct method resumption adds its actual method row.
Both retain the live resumer and eager receive arguments, including nested calls
to the same Generator function. Ordinary private-method creation keeps its
original source caller permission after that caller returns.

Generator declarations mirror Zend's one-level return-supertype scan. A pure
intersection containing `Iterator`, `Traversable` or `Generator` is accepted even
when the resulting Generator does not satisfy every intersection member. A DNF
intersection branch does not expose its inner names to that scan. Generator
completion does not perform ordinary declared-return coercion.

Admission authenticates source functions and yield unit/path pairs, suspended
frame scopes, Closure targets and one real saved resumer per running Generator.
Internal continuations cannot hide in source wrappers or branches. Public
admission and ownership checks use actual source-reached states.

[Implicit ArrayAccess Get344](SOURCE-ARRAYACCESS.md) creates mixed/untyped Get
Generators, with both declaration reference flags. The real saved frame owns the
receiver and arguments; a nonowning source certificate authenticates Get after
its caller returns. Ordinary close preserves the actual destructor continuation
and pending exception through its finished marker.

Array, source Iterator and Generator graph delegation are covered by
[Module289](GENERATOR-DELEGATION.md), including shared progress, return transfer,
live callback references and natural owner cleanup. [Reference yields328](GENERATOR-REFERENCE-YIELDS.md)
add live cells, value-API snapshots, foreach/destructuring aliases and authentic
Notice/cleanup readback. Aggregate acquisition has separate START and
[foreach scopes](ITERATORS.md); Module380 adds bounded nested Aggregate
[yield-from acquisition](GENERATOR-DELEGATION.md) with generic Generator data,
null results and phase-specific error cleanup. Aggregate ordinary-call unpack,
broader reference producers, dynamic/nullsafe API calls, named/unpacked API
arguments, scoped static and other implicit callback creation, and creation
through changed/imported caller scope remain required.
[Module303](GENERATOR-FORCE-CLOSE.md) adds ordinary last-owner forced close,
pending finally execution and ordered input/frame/cache release.
[Module310](GENERATOR-FIBER-CLOSE.md) extends ordinary paused-Generator release
to the active Fiber stack while preserving real parked caller owners. Module378
retains a foreach Generator getter's real receiver and statement/line receipt
through break-driven finally throw and Fiber suspension; saved close IDs preserve
unique running-operation ownership. Wider terminal cleanup, running-Generator
transfers, switching finalizers, general user destructors and cyclic collection
remain required; their explicit Unsupported controls earn no agreement. Natural
return/throw/finally cleanup remains distinct from forced close.

Normal request cleanup340 uses real global/store owners and borrowed zero-owner
buckets. Module349 also closes fresh store frames without running their bodies,
preserves immediate CV-handler ordering, and releases a closed Generator's Closure before its
caches. Module355 retains a physical closed-Generator storage pin through those
releases, preserving weak liveness, readable RETURN and pending child exceptions.
[Storage-pin checks](../../coverage/semantics/generator-storage-pin-review.json)
remain separate from the [fresh cuts](../../coverage/semantics/generator-fresh-store-review.json).
Module 360 extends normal request close to delegated inputs, preserving input-before-finally
order, independent CV owners, shared store order and the physical CURRENT cache slot.
Nested normal handlers keep the genuine inner/outer close claims and cache owners;
queued source views remain distinct from actual handler contexts.
[Eight originals and 553 reached premises](../../coverage/semantics/generator-request-delegation-review.json)
retain separate cuts. Composition with 346 modules over `9cacdbf51` passes strict
compilation at `4d867f6b0`; earlier source/state cuts retain their inputs.
Module 363 handles uncaught request-finally exceptions and throwing registered
handlers. Normal custom rendering retains the Generator/cache and original handler
exception, including live Weak lookup and registry changes. Reporting freezes
before the reported exception's release; bailout then preserves the real abandoned
carriers and marks later destructors called. C-root traces retain internal frames.
[Seven exact fatal originals and 493 reached premises](../../coverage/semantics/generator-request-abrupt-review.json)
retain separate cuts; the original refusals remain zero agreement. Actual 351 over
`7c4a13bc1` passes strict compilation at `ba1c17c07`; current schema, storage and
collector/source guards remain intact, without renewing earlier source/state cuts.
Normal post-report stdClass and ordinary child storage add one exact fatal original
and 161 premises at its own cut, preserving real pins and full admission through
Weak lookup and the authenticated future continuation. Composition with 353 modules
over `a210cd253` passes strict compilation at `b7b693fa3`; prior cuts remain separate.
At request C root with no current exception handler, a throwing custom renderer
reports and releases its builtin inner Throwable before bailout abandons the
original report and Generator/cache owners. Three exact fatal originals and 527
reached premises retain separate cuts, including the real receiver decrement,
handler exception retention and reporting mutation after emission. Actual 356 over
`2b98ff468` passes strict compilation at `72d5f7353`, preserving current fields;
private source/state cuts retain their own inputs. A renderer-installed handler
that returns normally releases its inner exception before restoring the registry.
The invalid-return warning runs before fatal reporting reads the live original cache;
callbacks receive Unknown/line0 and can refresh it through `parent::__toString()`.
Three fatal originals and 611 reached premises validate the real handler/destructor
pins, transient Weak owners, warning delivery, cache mutation and replay at separate cuts.
Actual 358 over `b721887ce` passes strict compilation at `00536106a`; current
source/argument/storage fields remain intact and private 3/611 retain their inputs.
A throwing renderer-installed handler rethrows at its genuine C root and receives
its own fatal report. Authentic EHR, renderer-return and outer-report carriers keep
the original exception and Generator/cache alive; its custom renderer has three
real owners from CURRENT, STRINGIFY_RESULT and REPORT. The new exception releases
after frozen emission and before bailout, including a destructor that sets reporting
to zero. Two exact fatal originals and 163/180 strict premises retain separate cuts.
Final 358 over `ea04fbbe4` passes strict compilation at `ff3d3278b`, preserving the
named-SEND warning shapes. Earlier 2aa/646 and source/state cuts retain their inputs.
A throwing renderer warning callback passes its new exception to the restored
handler at the real C root. Handler release precedes raw warning-handler restoration;
the original empty cached fatal report then releases its receiver before bailout.
The handler carrier owns the warning object independently of the consumed inner
exception; original REPORT and real Generator/cache owners survive throughout.
Exact source1 and compiler358 retain `558e53a9c`; strict220 retains `80be20cde`, with
authentic continuations, malformed producer rejection and budget replay. Original
binding stops and the incorrect fixed-argument phase remain zero. Actual361 over
`59c163ef4` passes strict compilation at `7983c825f`, preserving current ARG/CALLS
fields; private source/state cuts retain their inputs. A ROOT/nonuser ordinary
property-child destructor throwing during reported-exception release, with no live
handler, emits a second fatal before abandoning the real unfinished tail. The
Parent free_obj pin keeps Weak lookup null while two Leaf C claims and actual
Generator/cache owners survive. Unreleased fatal FRAME/FRAMES retain INSTANCE pins
and the old reported Exception's pending HANDLE/occupied GC slot. Discovery excludes
saved DESTRUCTION and SOURCE certificates. Exact source1 retains `7d3574e75`; strict549
and complete compiler361 retain `47c8c3c1c`. Prior refusals, diagnostics and failed
checks remain zero. Final361 over `e889a1592` passes strict compilation at
`77e534575`, preserving EX34's301/372 collector guards; this source has no collector
task. Private source/state cuts retain their inputs. A declared property ALIAS,
after its last local alias is unset, transfers HCELL then Leaf during release and
follows the same second-fatal path. The model never reuses reference-cell IDs;
the retired marker and STORE value provide release evidence without a cell root
or referent edge. Actual SOURCE/result claims still retain exactly two Leaf C
owners. New source1/compiler361 retain `c5b8de418`; strict677 retains `4870a1a8c`.
Original refusal, reached discriminator and bounds syntax stop remain zero;
actual363 over `d54dd9fa8` passes strict compilation and affected SL677 at
`a2847abb8`. Three shared message observations use bytes across immutable string
carriers; source/compilerc5 and private state487 retain their original cuts.
The parent renderer's byte-extraction rule and actual pin/handle owners remain
intact. A declared array child retires HARRAY before its sole owning Leaf entry
reaches the same ROOT/nonuser release tail. Its in-range retired row certifies the
child without another array pin, GC slot or heap edge; primitive siblings are
allowed, while multiple owning nodes, nested arrays and reference entries remain
outside that slice. A real external shared-array owner prevents entry release and
the second fatal. Exact source2, strict712/77 and complete compiler363 retain
`5da367130`; original refusal and reached118 diagnostic remain zero at `4c410b607`.
Actual364 over `70c5ff9fc` passes strict compilation at `3aeb34484`; the new
retired-owner carriers remain empty because neither source has switch/foreach
or reference-return replay. Parent frame/fatal-history fields are preserved;
private source2/789 retain their inputs. A sole owning reference entry additionally
retires HARRAY then HCELL before the real Leaf release. The original array row,
stable retired-cell marker and STORE value certify both consumed layers without
array/cell roots, referent edges or GC pins; primitive siblings remain allowed.
An explicit global reference keeps HCELL and its Leaf edge live after array
retirement, preventing the second fatal. Exact source2, strict816/113 and complete
compiler364 retain `9faf09e39`; the helper-load stop, failed local-CV control,
primary refusal and reached172 diagnostic retain zero credit. Actual366 over
`87752f2a0` passes strict compilation at `807fa6013` (6.471 seconds). Empty parameter
attributes/plain traces preserve existing owners; Aggregate/Fiber, quantity and
undefined-read hooks are inactive. Parent frame/fatal-history fields are preserved;
private source2/929 retain their original inputs. Multiple owning nodes and recursive
containers remain
outside this slice. Wider handlers, rendering,
child lifetimes, reacquisition, message warnings, parked or escaped storage and
generic terminal cleanup remain required.

[Arrow Generators311](ARROW-GENERATORS.md) validate the existing capture
and implicit-return routes. Eager parameters, sent results, delegation, scope and
original signatures retain separate source/state cuts. Value-warning cleanup
retains the same Throwable, cached key and closed Closure owner. A separate
frozen287 default/Fiber/eval composition passes one source and148 reached
premises. The actual292 property/collection parent separately passes the same
source and75 reached physical-HANDLE/Arrow-close premises. Final294 passes strict
compilation; earlier source/state cuts retain their own tested parents.

[YIELD key warnings321](YIELD-KEY-WARNINGS.md) cache the value before an ordinary
missing key-CV warning. Handler reference/array writes preserve the copied value;
the read freezes null without advancing the implicit index. Actual child resumer
markers distinguish delegated exception reinjection from direct API close.
Cached user-destructor release retains an authenticated operation/frame carrier
and replacement exception priority. Wider producers and lifetimes remain required.

Constructor-created global constant instances follow the existing noncache
policy for object defaults. Receives, yield caches and return values retain the
original instance identity; the completed source receipt adds no heap owner.
Ordinary deferred body NEW can run a registered autoload Closure. Generator
functions used as implicit autoload callbacks remain a required scope boundary.

Twenty-seven normal sources and three compiler rejections agree at `e235d8dd1`
in separate first5 and independent25 cuts. Four independent source-derived
phases pass: carrier144 and Closure154 at `2f21dec3e`, nested77 at `d7ca57f5c`
and abrupt44 at `6c221db16`. Their 419 premises check full public admission at
genuine stable states, moving frames, cached/reference owners, cursor uniqueness
and natural try/finally cleanup. Closure154 is the passing phase in the record
whose later nested check failed; original failures remain retained.

Three introduced parent sources agree at `9abff30b8`: global constant default
identity, deferred REAL Closure autoload and parse-folded versus live precision
after a container warning. A new 95-premise constant phase passes at the same
cut, checking full public/heap admission, unchanged nonowning receipts and the
2→3→3→1 receive/cache/return/constant owner flow. Their raw records are
`generator-independent-cigy7vgb` and `generator-review-protocol-1z9ssugw`; the
initial `generator-independent-gbe1sfu4` interpreter failure and native fixture
failures remain retained with zero credit.

Raw private records are `.tools/generator-independent-n_gi07p8` (first5),
`generator-independent-3xhzyjou` (remaining25 and six zero-credit controls),
`generator-review-protocol-j09b_g9p` (carrier), `generator-review-protocol-eos1w4wf`
(Closure), `generator-review-protocol-0zcv39l1` (nested) and
`generator-review-protocol-8m71dnav` (abrupt). These directories retain runtime,
profile, commands, exits, exact bytes and stable semantic inputs.

Twenty-three new send/throw sources agree at `26328ca39` in separate five and
eighteen source cuts: `generator-effects-review-_839imxs` and
`generator-effects-review-zjs5gu53`. They cover fresh/paused/closed inputs,
argument errors before initialization, array/reference sharing, real API trace
arguments, catch/finally suspension and reentrant calls. The original
`generator-effects-review-xsm5m8_5` structuring failure earns no agreement;
an equivalent operand-binding rewrite passes production SL preparation.
Three new source-derived phases pass at fixture `887f51d29`, semantic `26328ca39`:
array146, finally124 and initialization101 (371 conditions). Full public and
heap admission check actual input/cache/return owners, pending-finally exception
identity and previous chaining. Heap-valid count/type/phase/method/line, wrapped or
stranded resume, and doubled/misplaced search mutations reject; zero-budget
resumption matches direct execution. Their raw record is
`generator-effects-protocol-szlr6xpv`.

One introduced source agrees on actual parent `c729a1f62`, semantic union
`ca7da215e` and fixture `63b45bb26`: default NEW autoload changes live precision
before eager argument/construction, while the body retains parser-folded text;
fresh `send` retains its distinct object input and the original default return.
Raw record `generator-effects-review-w21x2zng` keeps this cut separate.
The actual union also passes production SL structuring with the complete main
and a fresh adapter build (`generator-effects-actual-sl-n4ctdfq0`).

`python3 tests/semantics/generator_review.py --select first-current-rewind`
compares ordinary PHP source with the pinned native runtime.
`python3 tests/semantics/generator_review_protocol.py --select carrier`
checks source-reached frame movement, cached owners and malformed continuations.
`python3 tests/semantics/generator_effects_review.py --select send-fresh-target`
compares input delivery and exception injection with the pinned runtime.
`python3 tests/semantics/generator_effects_review_protocol.py --select array-input`
checks actual input owners and resume admission.
Raw commands, profiles and observations stay in ignored `.tools` directories.
This slice does not establish complete Generator or complete core semantics.
