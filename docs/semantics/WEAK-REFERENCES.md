# WeakReference and WeakMap protocols

Module 296 implements the pinned PHP 8.5.10 `WeakReference::create` and `get`
protocol on the reviewed eager-destruction 270 source. Twenty-one exact original
sources agree; nine reached cuts pass 344 physical premises. Five Unsupported
controls earn zero agreement. The [ledger](../../coverage/semantics/weak-reference-review.json)
keeps their separate tested snapshots. Canonical292/304/270 composition separately
passes strict277 initialization and one exact returned-object weak lifetime source;
bounded ordinary cyclic collection is covered separately by
[module301](CYCLE-COLLECTION.md). Wider collection and WeakMap protocols remain required.

A successful wrapper records an immutable semantic object ID. The target adds
no ownership edge. `create` returns the same allocated wrapper for a target,
or allocates a fresh wrapper after its predecessor retires. `get` copies a live
target into the ordinary result owner. Discarding or saving that result uses the
existing ordered release machinery.

Wrappers satisfy nominal `WeakReference` argument and property types independently
of referent lifetime; rejected receives name the actual internal class.
The [raw Fiber-array review](../../coverage/semantics/fiber-array-core-callbacks-review.json)
records the separate nominal-type source and reached checks.

Object IDs never reuse. `get` checks target allocation and the actual ordinary
INSTANCE/stdClass storage359 stage, without a second registry or a store-handle identity.
Ordinary `__destruct` and resurrection keep the target live. For the reviewed ordinary
INSTANCE/stdClass property-child free_obj path, Weak notification precedes child
release while one physical parent pin remains allocated, so `get` already returns
null. WeakMap value callbacks have a separate notification-order boundary below.
Native notification clears its raw pointer; the model retains the nonowning semantic ID as borrowed history.
Closed Generator storage355 instead retains its weak target through Closure/cache
release and notifies on final retirement. The ordinary pin, saved Fiber and
Generator RETURN-child checks are recorded in the
[property lifetime review](../../coverage/semantics/duplicate-property-reference-review.json).

Direct NEW allocates a null-born candidate before evaluating arguments. Its
internal constructor always throws; unknown named arguments fail before the
body. This transient record requires a genuine pending constructor or failed-release
continuation. The actual pending-throw operation and source scope authenticate
failed release; validated allocated Fiber/Generator carriers retain saved scopes.
NEW's result continuation must name the selected candidate. Deferred constant-AST
WeakReference construction stops explicitly before allocation; wider initializer
support remains required.

Abandoning a carrier with a pending null-born candidate stops before actual free,
preserving its authentic release owner and saved stack. Genuine forced-stack
unwind remains required. The entry reason is `abandoning WeakReference constructor
argument stack`; final Fiber cleanup reports the existing `force-closing a
suspended Fiber` boundary, while Generator cleanup retains the entry reason.

Selection covers direct static calls and instance/nullsafe calls, including
computed API names admitted by the existing method-selection path. Instance
syntax for static `create` retains borrowed selector history without a receiver
owner. `get` and explicit `__construct` retain their real receiver. Arguments,
API errors and traces use the existing internal-call protocol. Clone throws its
native Error; first-class API captures stop explicitly. Property protocols,
wider callable consumers and collection APIs are not implemented by this module.

The pinned contracts are `Zend/zend_weakrefs.c` (`zend_weakref_find`,
`zend_weakref_create`, `zend_weakref_get` and the three API bodies),
`zend_objects_store_del` in `Zend/zend_objects_API.c`, and
`zend_object_std_dtor` in `Zend/zend_objects.c`. Notification precedes outgoing
property release and follows the destructor/resurrection decision.

Maintained checks: `weak_reference_sources.py`, `weak_reference_state.py`,
`weak_reference_review.py`, and `weak_reference_state_review.py`. Original
compiler, source and reached-state failures remain in ignored `.tools` with
zero credit. The final combined offline rebuild remains required; paused return
verification is unchanged.

## Wrapper creation during live map teardown

Modules359/386 admit `WeakReference::create` for a unique allocated empty-map
storage pin with pending NOTIFY in the current tasks or saved frames. The
existing wrapper must be the actual allocated find result and match NOTIFY.
After that wrapper's ordinary retirement, creation appends a fresh wrapper
and changes only the pin's borrowed notification identity. Neither the wrapper
nor NOTIFY owns the map; the existing physical pin and callback-local copy do.
The callback releases that copy before returning.

The reuse/recreation originals (88/123 bytes) agree at `ac980b0`.
Three reached groups pass 123/133/77 checks, totaling 333. The first two bind
actual CONFIG_INVOKE/source/frame authority and argument-owner removal
(three to two map owners), with stale notice, handle, duplicate-pin and
competing-find controls. The last reaches notification after callback cleanup: clearing
only NOTIFY makes the new wrapper null while the map stays physically pinned,
then physical retirement schedules a valid HANDLE release. It stops before
consuming that job; originals supply complete endings. The original
`freeing instance new weak reference` refusal remains zero agreement.

The engine basis is `zend_weakref_find`, `zend_weakref_create`,
`zend_weakref_register` and `zend_weakmap_free_obj` in `Zend/zend_weakrefs.c`.
Map value cleanup precedes its std_dtor notification, allowing wrapper
reuse or fresh registration while the callback-local target remains live.
Nonmap/freeing-key creation, notified pins, inactive or fatal carriers,
throwing callbacks after creation, additional strong targets retained beyond
cleanup and wider map/ephemeron protocols remain required. Earlier cuts and
failures retain their separate evidence in the
[ledger](../../coverage/semantics/weak-map-review.json).

## Multiple entries and selective Key retirement

M141 adds an ordered `WEAKMAPENTRIES` storage alternative for at least two
records, preserving all old empty/singleton values. Actual source/RHS/selected
operands authenticate appends of unique empty-property `stdClass` Keys and direct
parentless methodless leaf Values. Read, quiet read and presence select the actual
entry. Recursive helpers handle finite lists; the two PHP witnesses have two
entries with separate Values or one shared Value. Every slot contributes its own
physical owner edge, while Keys remain weak.

New-table presence activates existing eager cleanup. A genuine freeing-Key pin
allows only that dying Key in table validation; siblings retain normal guards.
Notification transfers only the removed slot into one Value job and preserves
the remaining record, including BEFORE, when normalizing to singleton storage.
Existing pending-release closure keeps cleanup active after normalization.

Source2 and author158/3 plus peer128/2 pass 286 Boolean/five raw transitions at
`8f71bbef1`/412. Separate X retires while Y survives. Shared Value has owner2 before
notification and across one-edge-to-job transfer, then owner1 after that job ends;
last-Key singleton cleanup retires it. The borrowed Key wrapper remains visible
while X's own freeing pin hides its weak get before physical disposal. Exact
append/notification/pin budgets and full native endings pass.

A valid-heap old NULL payload refuses conversion through the public driver.
Duplicate-Key metadata preserves the shared heap and fails uniqueness; tail
removal preserves the prefix record. These and excluded-consumer queries are
constructed/helper controls with no extra PHP credit. Native/genuine refusals
retain `c5ccf2792`/411. Original app0 iteration-name and author record-list syntax
failures remain zero; only corrected preflight/author repeat, without source or
native replay. At that cut, CONFIG/GC/foreach/teardown and old392/402/408
new-kind fallbacks stay explicit exclusions. Wider payload/property/class/callback forms,
wider replacement/unset and cross-map/reentry/Fiber histories remain partial.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Last-owner multiple-entry Map teardown

M142 authenticates the actual popped Map release/owner0, canonical leaf-value
table, independently owned live Keys and every pending slot job. Before any
Value decrement, all Key registrations are removed into old empty-Map storage.
The existing pin retains Map allocation and pending weak notification while
`entries_nodes`/`destruction_values` transfers each slot without deduplication.
Existing pending-release closure keeps cleanup active after normalization.
Only twenty lines in422 change;257/39/386/30 and the ordered manifest stay exact.

Two originals and author144/3 plus peer156/3 pass 300 Boolean/six raw transitions
at `61a02e28e`/412. Separate X retires before Y starts its freeing pin. Shared
Value has two pending job owners, then one after the retained first decrement,
then an own freeing pin before physical disposal. Map allocation and both Keys
survive these Value jobs; final Map/Value weak-null and independent Key retirement
match the complete native endings. The fixtures record pending Map notification
without assuming a mid-pin weak-Map get result.

An added external Map-root counterstate changes ROOTS/owners while preserving
allocated nodes/edges; the generic retained-release branch keeps the table and
Values. It adds no PHP source credit. Native/genuine teardown refusals retain
`70b7d5a0c`/412. All repaired/focused checks pass first execution, with no replay,
cap increase or separate preflight. Wider Key properties/classes, non-leaf,
reference/array/callback Values, wider multiple-entry replacement/unset,
iteration/CONFIG/GC and cross-map/freeing/reentry/Fiber combinations remain partial.
Keys outside the authenticated retained-live shape still refuse.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Multiple-entry by-value foreach

M143 adds a finite weak-Key snapshot cursor without rooting its historical IDs.
The saved `FOREACH_NEXT` owns Map DATA once. Cursor identity, range, uniqueness
and current-entry subsequence checks survive consumed Key death and storage
normalization; fetch separately validates quiescent leaf storage and reuses the
existing Value-then-Key target stores. Actual implicit Key notification retains
its authenticated freeing-pin authority. Explicit mutators and active many-entry
reads keep their earlier fences.

Two originals and author139/4 plus peer171/3 pass 310 Boolean/seven raw transitions
at `43c9ebe17`/412. Exhaustion overwrites the first targets, retires that Key/Value,
and continues with the same nonowning snapshot over singleton storage. Natural
exit retires Map while the last copied targets survive. First-body break drops
DATA and uses bulk teardown; its fetched Value survives while the sibling retires.
Both endings then release the copied targets. Stale singleton history after
quiet pruning is distinguished from physical Map allocation.

Heap-identical range/duplicate snapshot forgeries refuse publicly. A constructed
registry-only query has no Map owner without its saved task. These controls add
no PHP credit. Native/genuine refusal2 retain `f220222919`/412; strict app0 is
separate. All repaired/focused checks pass first execution, with no replay or cap
increase. Multiple-entry byref/wider payloads, explicit mutations, active read/API,
CONFIG/GC and wider Key/property/callback/context histories remain partial.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Multiple-entry reference sharing

M144 adds a distinct reference cursor and validated marked entry cells containing
methodless leaf objects. Fresh fetch transfers Map-to-Value into
Map-to-HCELL-to-Value; the reference body adds a CV cell owner. A later fetch
rebinds only that CV, preserving an escaped first-cell alias. Internal slot updates
keep Key/BEFORE/order. Post-loop reads dereference the authoritative cells and
bulk teardown transfers cell nodes alongside direct values. Earlier by-value and
append paths retain explicit direct-kind guards.

Two originals and author149/3 plus peer177/3 pass 326 Boolean/six raw transitions
at `cf9ccf997`/412. First-cell owners go3-to2 on loop rebinding while each Value
keeps one cell edge. Independent writes change the intended Map slots. After
Map removal, each alias cell remains owner1 and retires separately; stale
STORE/REFCELLS IDs own nothing. Break transfers mixed cell/direct jobs, preserving
the fetched cell2-to1 before detached rebinding and final disposal.

Constructed NULL payload keeps valid cursor/descriptor authority but reaches an
explicit storage refusal; a heap-identical mode/direct-kind forgery refuses
publicly. Existing-cell reuse is helper-only. These add no PHP credit. Native and
genuine refusals retain `ccbc21cb62`/412; strict app0 is separate and all affected
checks pass first execution without replay or cap increase. Multiple-entry NULL,
wider payloads, explicit mutation, by-value ALIAS traversal, active read/API,
CONFIG/GC and wider Key-notification/callback/context histories remain partial.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Selective multiple-entry ephemeron collection

M145 admits one global Map with finite independent DIRECT Value-to-own-Key
backedges. Keys have empty properties; Values are parentless/methodless with one
public untyped direct Key property. Both insertions precede backedge writes.
All conditional Map edges are stripped for one real-root classification.
Protected Keys restore Map-to-Value; white Keys reveal virtual Key-to-Value edges.
Absent-Map helper roots strip without discovery. Physical owners stay unchanged.

Canonical GC_FREE authority removes only complete unreachable pairs and packs
surviving records unchanged, including BEFORE. Generic301 planning, counting and
physical disposal stay exact. Two sources and author 146/1 plus peer 176/2 pass 322
Boolean/three raw transitions at `296aa24f5`/412: unheld collection returns 4 then 0.
Holding the first Key collects the tail pair (2), preserving entry presence and
normalization, then collects the released survivor (2) with a final 0.
No protected Value get precedes release. The second trace actually buffers A
without X, so virtual discovery is tested rather than inferred from counters.

Added-root stale-plan and incomplete-pair refusals, active-cursor and nil-Map-root
queries are constructed/helper controls with no PHP credit. Stale OBJECTS IDs
remain nonowning after physical retirement. Native/genuine refusals retain
`2ccf7e19a`/412; app0 is separate, and all affected checks pass first execution
without replay or cap increase. Wider maps/backedges, ALIAS/array payloads,
callbacks, active iterators/frames/Fibers/workers and mixed graphs remain partial.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Cross-entry ephemeron dependencies

M147 extends the GC-only direct-property authority to actual member-Key targets.
Unique targets form finite Key permutations, including the old self-pairs.
Existing conditional edges and reach closure propagate protection across entries;
projection, complete-pair preparation, counting and collector code stay unchanged.
Ordinary non-leaf table consumers remain outside this slice.

Two crossed-entry sources and author150/1 plus peer173/2 pass 323 Boolean/three raw
transitions at `744bb372b`/412. Unheld collection returns 4 then 0. Holding only A
protects A-to-X-to-B-to-Y (0); after release, A is eligible while B/X/Y are absent from the eligible buffer,
yet all four are discovered and collected (4), with a final 0. No protected Value,
KeyB or Map weak get precedes release. The Map remains independently rooted.

Added-root/incomplete-plan public refusals, active-cursor and many-to-one target
queries are constructed/helper controls with zero PHP credit. Native and genuine
baseline retain `2f5088dd4`/412; baseline refusals remain zero. All affected
checks pass first execution.
The two PHP witnesses use a two-entry swap; non-permutation targets, wider
properties/payloads, callbacks, maps and active contexts remain partial.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Collection of an unheld Map cycle

M146 admits one global singleton Map whose direct methodless Value owns that
Map through one public untyped property. Its empty-property stdClass Key stays
independently live. The ordinary-node hook admits only this validated Map shape.
White-Map tracing retains entry discovery even when Value is not buffered;
protected and older Key-backedge projections keep their existing behavior.
Canonical FREE authority requires both Map and Value and a retained Key, then
unregisters the entry before unchanged301 atomic disposal and counting.

Two sources and author126/2 plus peer161/2 pass 287 Boolean/four raw transitions
at `93dfab694`/412: unheld collection returns 2 then 0; quiet Map protection returns 0,
then 2 after release and 0 again. Key identity survives both objects and retires
only after its explicit unset. The separate admission-only61/1 diagnosis at
`bda0d3cfc` reaches Map-buffered/Value-absent with the old count1 plan; it adds no
source agreement. Native/genuine refusals retain `cf2f4a700`/412.

Added-root/incomplete-plan refusals and cursor/empty-hook/supplied-root/stripped
queries are constructed or helper controls with zero PHP credit. Stale OBJECTS
IDs remain nonowning after physical retirement. Wider maps/entries, Key/Value
properties, aliases/arrays, callbacks and active iterator/frame/Fiber/worker
contexts remain partial. [Review and recovery](../../coverage/semantics/weak-map-review.json).

## Destructor-free singleton ephemeron collection

Modules301/386 admit explicit collection for one live map, a `stdClass` leaf key
and a parentless value with no declared methods and one public untyped key
property. Insertion occurs while that property is null; the ordinary property
write then supplies the backedge. The initial cut limited other allocated
objects to weak wrappers.

The physical graph contains Map→Value→Key, optionally through a reference cell
or the admitted property array, for eager ownership. GC restores Map→Value when
map and key are reachable. With a live map and white key, a virtual Key→Value
edge instead discovers the unheld
component; this adds no physical owner. A held key protects the value, and a held
value reaches its key.
Shared entries instead retain Map→HCELL→Value→Key until collection.
An authentic destructor-free GC_FREE plan clears that entry before the unchanged
strong resurrection guard and existing count, buffer, store and handle disposal.

The unheld and held originals (63/114 bytes) agree at `0167ec6c`; the held source
observes key-only and value-only protection before releasing both. Three reached
cuts pass 169/135/135 checks, totaling 439 with three setup assertions per case.
They authenticate source/current call and property authority, logical versus
physical reachability, count two or zero, dead-entry cleanup and live-map
preservation. Empty-map identity, coherent nonbackedge refusal, malformed call
line, stale held-white-root and zero/one-budget controls pass. Checks stop at the
collection return; originals supply complete endings. The original accepted
source's `WeakMap ephemeron collection` refusal remains zero agreement.

The basis is `zend_weakmap_get_gc`, key-entry helpers and `gc_scan_black` in
`Zend/zend_weakrefs.c` / `Zend/zend_gc.c`: an entry is retained when both map and
key are live. Wider maps/destructor callbacks, typed properties, wider reference
or value shapes, inactive contexts, unheld-map and general ephemeron graphs remain
required. Countable remains nominal-only and count library execution is excluded
by CORE. Earlier cuts retain their evidence in the
[ledger](../../coverage/semantics/weak-map-review.json).

## Reference-cell backedges and Key-only discovery

M134 admits the canonical ALIAS of a live marked HCELL holding Key in the same
public untyped property, limited to methodless Value. The old DIRECT admission
keeps its two original checks. Actual ownership remains Map→Value→HCELL→Key;
In the ALIAS case, Key stays a physical leaf with one object owner. The cell has
one property owner, or a second external alias owner while held.

The quiet held source reaches its next collection with only Key buffered.
The old tracing graph missed Value and reached the existing
strong resurrection refusal. The virtual white-Key edge now discovers Value and
its cell without changing the eager graph, roots, disposal or that guard.
Protected live-Key and no-live-map branches stay exact. DIRECT walks already
reaching Value loop back to a visited node, preserving count and free order.

Four originals and 282/4 focused checks pass at9e37/409. Unheld collection returns2
then0; held collection returns0 before the alias drops, then2. Quiet ALIAS and
DIRECT controls omit pre-release gets, so observation cannot seed Value's buffer
slot. The author134/2 follows real CONFIG/TRACE/FREE, count2 excluding the cell,
exact budgets and a valid-heap external-root stale-plan refusal. Peer148/2 follows
actual protected ownership, Key-only discovery and both GC_FREE steps. Allocation
of Key/Value/HCELL ends and weak gets return NULL, while stale STORE/REFCELLS
history remains recorded without a live node, edge or owner. Protected/no-map
root-list controls are helper-only, without a PHP reachability claim.

Native4/baseline4/diagnosis166/1 retain323b/409. The three ALIAS refusals and DIRECT
non-destructor-resurrection refusal stay zero credit; no fixture/recorder failure, retry, cap change
or accepted historical replay occurred. All actors are reaped/CPU5 released.
Typed or wider reference-property forms, ALIAS-Value destructor callbacks,
array values/properties, wider graphs/maps,
unheld-map and inactive contexts remain partial; count-library bodies stay excluded.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Shared entry-cell collection

M140 admits explicit collection through the actual shared entry cell. A
by-reference foreach acquires that cell while Value's public untyped property
is NULL, then breaks. Source writes the direct Value→Key backedge and removes
the ordinary Value/original Key/copied Key CVs before GC. The unheld source also
drops its loop alias; the held source keeps it through the first collection,
then drops it without an intervening Key/Value read.

Physical ownership is Map→HCELL→Value→Key. The new disjoint ALIAS-entry lane
validates the marked/allocated/defined cell and methodless Value; conditional
tracing strips only Map→HCELL and lets white Key discover HCELL. Protected Key
keeps the physical graph. Prepare requires cell, Key and Value in the canonical
unreachable free set. Existing DIRECT/ARRAY lanes and generic301/39 stay exact.

Two originals and author139/2 plus peer159/2 pass 298 Boolean/four raw transitions
at `28d3b2974`/411. Unheld GC returns2 then0; an external entry alias protects with0,
then collection returns2 then0. COUNTED contains only the two objects while
FREESET also contains HCELL. All three allocations end, Map survives and target
WeakReferences become NULL; old STORE/REFCELLS rows remain nonowning. The reached
post-alias cell is discovered despite not being buffered; no Key-only buffer
claim is made. Exact raw/public begin/free budgets pass.

Constructed missing-marker helper, added-cell-root stale-plan and coherent
uncounted-cell omission controls refuse without extra PHP source credit. Both
genuine baseline refusals retain `58b7dc8c62`/411; all repaired/focused checks pass
first execution without replay, cap increase or separate preflight. NULL/scalar/
array reference entries, reference/array property backedges in this lane, wider
typed properties, Value callbacks, unheld/multiple Maps and active/Fiber/reentry
GC remain partial. Acquisition/read/release APIs keep their existing bounds.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Array-property backedges and COW

M139 admits a mutable nonproxy array `[0 => $key]` in the methodless Value's
single public untyped property, assigned after insertion while that property
was NULL. The new admission arm authenticates the actual Key and physical
Value→Array→Key edges. Existing conditional Key→Value discovery and generic301
tracing, count and disposal remain unchanged; no virtual edge owns storage.

Two originals and author137/2 plus peer165/2 pass 302 Boolean/four raw transitions
at `d55d0e471`/411. Unheld GC returns3 then0. An external copy of the property
array protects the component with0; setting only its element to NULL performs
COW, leaving the original property array intact. The next GC returns3 then0,
retiring Key, Value and the original array while the fresh NULL copy and Map
survive. There is no intermediate Value weak get to seed its buffer entry.

The reached proofs bind actual array owners before and after COW, conditional
discovery, exact counted/free sets and resumption budgets. Old ARRAYS.ITEMS rows
remain nonowning after allocation ends. Constructed external-root and coherently
incomplete-free-plan counterstates refuse through the public driver; a valid-heap
wrong-object singleton is a helper-only refusal. None adds PHP source credit.

Native2/genuine Unsupported2 retain `d953f6e786`/411. The original author134/2
record-syntax stop remains zero; splitting the same four fields passes137/2
without runtime/source changes or replay. Wider array layouts, property aliases,
proxies/immutable arrays, typed/wider properties, Value callbacks, reference
entries, unheld/multiple Maps and general GC/Fiber/reentry remain partial.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Array-valued entries

M135 admits first insertion of one ordinary mutable nonproxy array
`[0 => &$key]`, binding its live marked reference cell to the actual leaf Key.
Physical ownership is Map→Array→HCELL→Key. Conditional tracing strips Map→Array
and lets a white Key discover Array; it adds no physical owner. The existing
object-valued helpers and collector/disposal rules stay unchanged.

Two originals and 306 Boolean/four raw checks pass at9bf6/409. Unheld collection
returns2 then0; a quiet external alias protects the entry with0 before release,
then collection returns2 and the weak key becomes NULL. Array and Key are counted;
the cell is also physically disposed. Old ARRAYS/STORE/REFCELLS rows retain no
live edge or owner. Actual pending insertion, both held passes and exact resumption
budgets are checked independently. Constructed DIRECT-array, stale-root and
incomplete-free-plan controls refuse without extra PHP source credit.

Native/baseline retain d8e/409; the original SL binding failure at363ce retains
zero. Surrounding ordinary arrays/cells use existing generic collection, with no
additional source witnesses here. Other array layouts, replacement/callbacks,
wider maps, unheld-map and inactive/Fiber contexts remain partial.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Ordinary foreach DATA and copied CVs

M136 adds by-value traversal of a singleton Map with a leaf `stdClass` Key and
parentless methodless leaf INSTANCE Value. Key and Value targets are distinct
ordinary unbound/undefined/NULL CVs. The saved `FOREACH_NEXT` task owns iterator
DATA once; its `OBJECTITER` row is nonowning metadata. The object Key is copied
directly through `LIST_STORE`, without array-key coercion. Existing loop cleanup
handles exhaustion and `break`, with a bounded saved-owner hook in129.

Two originals and 287 Boolean/five raw checks pass atb7af/410. After the body
unsets original Map/Key CVs, DATA retains Map and copied Key/Value identities.
Loop cleanup retires Map while those two CV copies survive; each later unset
retires its own object. Constructed registry-only and same-heap cursor2 controls
distinguish metadata from ownership and reject invalid cursor progress.

First/second insertion, replacement and explicit entry removal refuse active
cursors; implicit Key-death notification is unchanged. The separate native
delete/reinsert control emits `B;E;`; its reached offsetUnset refusal retains
zero agreement. The original normal-but-skipped baselines and two compiler stops
also stay zero. A strict application0 preflight and corrected affected source2
keep their separate records. Reference traversal, scalar/array or wider values,
other/overwritten targets, wider getIterator histories, mutation and wider map/callback/
Fiber histories remain partial. Empty storage shares finish without an extra
PHP witness. [Review and recovery](../../coverage/semantics/weak-map-review.json).

Module 424 also admits the actual zero-argument `WeakMap::getIterator()` factory
for an ordinary Map CV in this methodless singleton lane. Its returned
`InternalIterator` owns Map once; the factory cursor row is nonowning and fences
explicit entry mutation from creation. Foreach owns the wrapper as DATA and
retains a separate current-value cache through the body. The cache adds one
Value owner; next or atomic methodless break removes it. An external Iterator
can retain Map after break; otherwise exhaustion retires both while copied
Key/Value CVs survive until their later unset. Stale object/store rows add no owner.

Two originals and 133/2 author plus 132/2 peer checks pass 265/4 at `95d732f3b`/413.
Same-heap missing/retargeted cursor controls and a missing-cache-root control
refuse through public descriptor validation with zero PHP credit. Native and
genuine baseline retain `77988f229`/412; baseline refusals remain 0, with no failed
repaired/fixture run or replay. Strict application0 is separate. Manual methods,
by-reference/nested or wider traversal, current-entry death, callbacks, hidden
native allocation-handle histories and GC/CONFIG remain partial. There is no
intermediate cache-before-DATA release-order claim for the atomic leaf drop.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## By-reference entry cells and Key retirement

M137 adds singleton by-reference `foreach` with distinct ordinary fresh/NULL CV
targets, a leaf `stdClass` Key and NULL or a parentless methodless leaf INSTANCE
Value. Fetch promotes the entry to one authoritative ALIAS cell and binds the
loop CV to it. Physical ownership becomes Map→HCELL→Value; hidden DATA still
owns Map once. Rebinding releases the old Value, and an escaped loop alias can
retain the cell after DATA and Map retire.

A direct NULL entry has false `isset`. After reference acquisition, raw
`isset` becomes true while ordinary read remains NULL, coalesce takes its
fallback, and `empty` stays true. The residual alias also writes back through
Map. When quiet RC pruning would retire Key but keep a validated REF-entry Map,
existing eager cleanup performs its notification first; active releases/operations
stay valid through cleanup. Removing the Map edge transfers its cell owner into
one real queued job. The surviving alias retains Value until its own unset.

Two sources keep separate cuts: escaped lifetime agrees at `e975008b1`; corrected
NULL sharing/notification agrees at `ae4590a36`, both with 410 modules. Author 155/3
and peer 159/2 pass 314 Boolean/five raw transitions at `ae4590a36`. Valid-heap
malformed-cell/cursor controls refuse; direct-mode/ordinary-object owner and
CONFIG queries are constructed controls. Physical cell/referent allocation ends
while stale OBJECTS/STORE/REFCELLS history stays nonowning.

The first repair's NULL mismatch and the first author finder failure retain zero;
its closed escaped agreement remains accepted. Only affected NULL/author checks
repeat, at unchanged caps; two application0 preflights add no source credit.
General quiet direct-entry Key notification, other reference/value/target forms,
reference-entry ephemeron GC, explicit iterator/reference APIs, active entry
mutation and wider Map/callback/Fiber histories remain partial.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Quiet direct-entry Key notification

M138 extends the retiring-Key activation to direct NULL/methodless-leaf slots.
It removes only the ALIAS-only premise, preserving existing storage authority,
RC pruning and cleanup continuation. Validated PHP witnesses use an
empty-property `stdClass` Key and a parentless methodless empty-property Value.
The held source binds an external reference only after insertion, so Map VALUE
stays direct. Key retirement removes the entry and transfers its one direct Value
owner to a real job; unheld Value retires, while the held Value survives until the
external alias drops. Both sources then execute empty by-value traversal with
unchanged NULL targets.

Source2 and author131/3 plus peer145/2 pass 276 Boolean/five raw transitions at
`c5e5661cd`/410. Entry registration precedes the Key weak wrapper, whose borrowed
notification stays visible while the Value job runs. Value's own freeing storage
pin hides its weak get before physical disposal; final probes see both targets
as NULL. A restored actual Key binding and direct NULL/empty-job shapes are
constructed controls with no extra PHP credit.

Native2 and genuine stale-entry Unsupported2 retain `52af2e140`/410; unheld also
exposes a retained-Value mismatch before refusal. All repaired/focused checks
pass first execution without native/baseline replay, cap increase or a separate
preflight. Wider Std Key properties/storage, other scalar/array payloads in quiet
notification, broader method/class/callback/Fiber combinations, wider maps/graphs
and reference/CONFIG/ephemeron-GC extensions remain partial. Existing destructor
routes retain their earlier evidence.
[Review and recovery](../../coverage/semantics/weak-map-review.json).

## Ordinary Std graphs beside a methodless ephemeron

At `fa2e00c6`, module386 admitted allocated, nonfreeing outside `stdClass` graphs when the
conditional Value has no methods or destructor. The earlier independently
rooted leaf arm is unchanged; its new complement admits nonleaf or unrooted Std
objects only in that methodless lane. Existing full property/heap authority and
the live singleton map/key/value shape still apply. Physical edges, conditional
tracing, GC plans and disposal in301 are unchanged.

Two originals (93/103 bytes) agree at `fa2e00c6`. An independent `Other.self=Other`
cycle collects with the unheld pair (count 3), while a held Key protects the pair
and lets only Other collect (1); later Key release permits pair collection (2).
The unheld (150) and corrected held (207) checks bind real CONFIG/TRACE/plan/FREE
states, exact disposal and weak outcomes, stale-owner rejection and budget
replay. At the held stage, coherently rerooting its actual Key CV to Other
protects only Other (fresh plan 2); redirecting its materialized self property
to Key protects the pair too (fresh plan 0).

A separate 48-check source-reached post-destructor control preserved the then-active
destructor/nonleaf refusal using a valid Other→Key graph. Total 405 checks end at
GC return, fresh plan or completion-only refusal; originals supply endings.
The original ephemeron Unsupported and failed 207-check fixture that reused
physical edges from before the CV reroot remain zero credit. Wider Value classes,
destructor-created graphs, map shapes and inactive contexts remain required.
The basis remains `gc_scan_black` and `zend_gc_collect_cycles` in
`Zend/zend_gc.c`, including its `get_gc == zend_weakmap_get_gc` branch, and
`zend_weakmap_get_key_entry_gc` in `Zend/zend_weakrefs.c`.
[Ledger](../../coverage/semantics/weak-map-review.json).

## Destructor callbacks and ephemeron retracing

The singleton cut also admits a sole local public ordinary `__destruct` on the
parentless Value, with no parameters or return type, alongside its one public
untyped key property. The live map and leaf `stdClass` key bounds remain.
Existing module301 protects the destructor-reachable Value/Key pair in the
first pass, invokes the real callback once, then retraces current roots.
Callback weak and entry reads see the pair alive. Saving Key protects Value
through the conditional map edge; dropping that root permits collection without
calling the destructor again. Physical ownership and destructor-free entry
preparation remain unchanged.

The earlier cut admitted an additional allocated, nonfreeing `stdClass` leaf
only when independently reachable without Map→Value. Its source-valid later
GC_TRACE refused wider changed shapes; the already-called extension below
supersedes that negative for ordinary Std graphs.
Three originals (150/158/169 bytes) agree at `18a03e08`; 128/136/165/154 reached
checks total 583. They authenticate first-pass protection and destructor entry,
post-callback disposal, saved-Key retention and the rooted outside leaf, with
malformed method/source, stale-owner and then-active nonleaf refusal controls.
The saved-Key stage is genuine; dropping its root in the same stage is a
coherent counterfactual, with the original supplying the later source execution.
Checks stop at destructor entry or collection return. Original Unsupported,
initial-state arity and ordered-reach fixture failures retain zero credit.

The basis is `gc_call_destructors` and `zend_gc_collect_cycles` in
`Zend/zend_gc.c`: destructor marking and nested-component protection precede
callbacks, then tracing runs again. Wider methods, properties, outside graphs,
unheld/multiple maps, inactive contexts and throwing callbacks remain required.
Countable stays nominal-only; count execution is excluded by CORE. Earlier cuts
retain their evidence in the
[ledger](../../coverage/semantics/weak-map-review.json).

## Std graphs after the value destructor

The graph admission arm also accepts the actual Value in DESTRUCTION.CALLED.
The enclosing singleton/main-thread shape still authenticates its sole public
source-backed destructor, live map/leaf Key and public key backedge. The old
rooted-leaf arm and its graph complement remain disjoint; no roots, tracing,
plans or disposal in301 change. An uncalled destructor still denies the
nonleaf/unrooted outside graph.

Both originals (180 bytes each) agree at `c3e844a5`: independent callback-created
Other.self lets Key/Value collect (2) while Other survives, then Other collects
after its global root drops (1). Other→Key instead retains the pair (0), then
all three collect after Other drops (3), with one destructor invocation.
The 149/182 source-reached checks total 331. They authenticate post-D PASS1,
physical versus conditional edges and real plans/free; a coherent existing-CV
root drop proves count 3 without changing CALLED. Stale held-owner plans reject.
Clearing borrowed CALLED history tests helper/shape denial only; it does not
claim the old collector continuation remains valid. Checks stop at GC return,
with originals supplying full endings.

Active tests replace the obsolete EX66 post-D 48-check negative and trim only the 11
now-false EX63 negative clauses, retaining its exact 143-check positive prefix. Earlier
154/48 results remain historical at their original cuts. The accepted source
rows retain timeout 120 and the 182-check state retains timeout 160; original Unsupported,
CLI60 and numeric120 timeout records stay zero. Wider Value methods/classes,
map shapes and inactive contexts remain required.
[Ledger](../../coverage/semantics/weak-map-review.json).

## WeakMap comparison

Distinct live nonfreeing maps compare with order zero through Zend's standard
zero-default-property shortcut. The comparator does not inspect entries or call
private values, and creates no entry/key/value owners. Array and declared-property
comparisons then continue to later leaves. Three exact sources and 246 Boolean
premises/9 raw steps cover opaque entries, later casters, COW and throw cleanup.
The existing empty/single-entry producer and lifetime bounds remain; mixed-object,
numeric, iteration and wider map protocols are separate.
[Comparison ledger](../../coverage/semantics/weakmap-comparison-review.json).

## WeakMap array casts

Module386 casts a live allocated nonfreeing map to a fresh mutable empty array,
including populated maps. Zend returns no property view for ARRAY_CAST, so neither
keys nor private values enter the result or gain owners. Ordinary cast resolution,
source returns and temporary cleanup remain in force. Two exact originals and 177
Boolean premises/6 actual casts cover empty/temporary/populated fronts, owner1,
real COW/reference history, key/value retirement and budget resume. Pure pin and
bounds controls establish helper refusals only; freeing casts and wider map
producers/lifetimes retain their existing limits.
[Array-cast ledger](../../coverage/semantics/weakmap-array-cast-review.json).

## WeakMap first entry and key retirement

Module386 admits zero-argument `new WeakMap()` and one first insertion with a
live `stdClass` leaf key and ordinary INSTANCE leaf value. Declared WeakMap,
ArrayAccess, Countable, IteratorAggregate and Traversable identities are preserved.
Countable is nominal-only here; count library execution is excluded by
[CORE](CORE.md) and stays Unsupported. Other map methods and wider iteration remain
required. The entry owns its value and keeps only a nonowning key ID. Source, current BASE/key/RHS operands and the
assignment result remain authenticated. This first-entry lane stops on occupied
entries, wider shapes and an existing entry for the key in another map; bounded
extensions are described below.

Ordinary key free creates the real stdClass storage359 pin before detaching the
entry. Its value edge becomes an authentic DESTRUCTION_VALUE job, so shared
owners survive and the last owner selects the value destructor once. The initial
callback/storage cut keeps both key and value allocated under physical pins
while their weak lookups are null; the original supplies eventual physical retirement.
Wider nonempty-map free and wider collection with a live nonempty map remain
Unsupported. The initial cut claims no ephemeron tracing or cycle/count closure.

Zend notification payloads preserve registration order. When a key wrapper is
created after insertion, native PHP returns that key during the value callback;
an earlier wrapper is already null. Entry BEFORE records the actual wrapper
identity at insertion; borrowed pin NOTIFY preserves a later wrapper through the
value callback and cleanup. GET authenticates an allocated wrapper and the unique
basic leaf-key pin, then creates ordinary temporary ownership. Notification clears
only NOTIFY before unchanged physical key retirement. The pending Exception stays
owned through both transitions when the callback throws. Retired wrapper metadata
adds no root; coherent replacement-identity controls distinguish a new wrapper from
the insertion snapshot without claiming creation during freeing is implemented.

The initial original matches all 45 native output bytes at `0fc26e6`; 375 lifetime
checks pass at `58b8873`, 49 GC refusal checks at `58b8873` and 116 notification
refusal/control checks at `8df2808` remain historical. EX56 replaces only the active
116-check refusal with the tested 106-check late GET record. Three early/late/throw
originals agree at `c1cf6c7`; four source-reached groups pass 73/106/119/95 checks,
totaling 393 with three setup assertions per case. Pin cuts stop at a scheduled valid HANDLE
release; the originals supply complete endings. The first normal fixture's
elaboration failure retains zero credit, separately from its corrected pass.
General multi-map order, wider wrapper creation during freeing, retained strong keys,
wider map protocols, wider nonempty-map free and ephemeron collection remain
required. No collection/count closure is claimed. Maintained checks reuse cycle_collection_cases.json and
cycle_collection_state_review.py; the
[WeakMap ledger](../../coverage/semantics/weak-map-review.json) preserves all
separate cuts, failures and raw recovery paths. The engine basis is
`Zend/zend_weakrefs.c` (entry addref, zend_weakref_register/unref and
zend_weakmap_free_obj), plus `Zend/zend_objects.c` and
`Zend/zend_objects_API.c` for ordinary storage notification and destructor order.

## Interleaved notifications across two maps

A separate module386 second-write lane admits two singleton maps sharing a leaf
`stdClass` Key and ordinary leaf INSTANCE values, with the actual Key wrapper
registered between the entries. Current task, RHS, selected value and quiet
operands authenticate the new insertion. BEFORE snapshots select the earlier
entry in either map allocation order; equal snapshots remain outside this scope.

Key retirement detaches only that earlier value edge into a real VALUE release.
The later entry and its value owner stay intact through the first callback. One
physical Key pin borrows NOTIFY: the first callback sees Key live, then notice
clearing makes GET null before the later VALUE release is scheduled. Continuation
requires the remaining historical wrapper identity and current find result, so a
coherent empty BEFORE cannot reopen notification. Shared value ownership and the
same pending Exception survive the existing release paths.

The normal 93-byte original agrees at `e5b19d0`; the throwing 100-byte original and
106 insertion, 99 first-transfer, 103 notification-head and 97 pending-head checks
pass at `b12f93a`, totaling 405. The continuation premises are true for the earlier
normal cut, which retains its evidence. Shared-Value redirection with unused Second
in HELD is a coherent counterfactual; the other boundaries are source-reached.
Checks stop at insertion or scheduled VALUE releases, with originals supplying
complete endings. Original Unsupported and duplicate-schema compiler-wrapper
failures retain zero credit.

The engine basis is payload insertion order in `zend_weakref_register` and
sequential `zend_weakref_unref`/`zend_weakref_unref_single` in `Zend/zend_weakrefs.c`.
More maps/entries, equal-BEFORE or general registration order, wider mutation/read
while Key is freeing, wider graphs and escaped callback owners remain required. No
GC, reference, presence, method or iteration widening is claimed. Countable stays
nominal-only. [Ledger](../../coverage/semantics/weak-map-review.json).

## WeakMap own teardown

A genuine last-owner VALUE release can retire one nonempty map whose stdClass leaf
key remains strongly held and whose ordinary INSTANCE leaf value has no children.
The entry detaches into an authentic value release before its destructor, while
an empty WEAKMAP storage pin owns the map. Borrowed NOTIFY postpones notification
of its existing wrapper through callback cleanup; it adds no owner.
GET creates ordinary temporary ownership;
notification clears before physical map retirement. Throwing value cleanup retains
its pending Exception through both transitions, and the key CV stays independent.

The normal 81-byte and throwing 88-byte originals agree at `0c9b358`.
Retention (161 checks) passes there; callback GET (97 checks), normal pin (105)
and throwing pin (104) pass at `061e372`, totaling 467 lifetime checks. A separate 86-check genuine write refusal keeps a freeing map pin empty;
its coherent no-pin control uses the same authenticated assignment operands.
The original 82-check control's missing retired-slot cleanup retains zero credit.
Both pin cuts stop at a scheduled valid HANDLE release without consuming it;
the originals supply complete endings. The final compiler and strict init pass at
`061e372`; the earlier struct-header recorder failure and its revalidated actual
artifacts remain separately recorded in the ledger.

The engine basis is `zend_weakrefs_hash_clean_ex` and `zend_weakmap_free_obj` in
`Zend/zend_weakrefs.c`: key registrations detach and stored values destruct before
the map's own std_dtor notification. `zend_objects_store_del` gives free_obj its
physical pin; `zend_weakref_get` adds the callback's real temporary owner. Wider
map teardown, mutation or wider wrapper creation during freeing, additional strong
key/map owners retained beyond callback cleanup, wider entry/key/value protocols
and ephemeron collection remain required. Countable
is nominal-only; count execution remains excluded/Unsupported per CORE.

## Scalar own teardown during eager cleanup

A last-owner singleton Map with a supported null/bool/int/string value can now
use the same physical teardown while its live stdClass leaf Key remains held.
The object-value predicate is moved unchanged into a disjoint helper arm; current
consumed-release, zero Map owners, BEFORE and held-Key authority remain required.
Scalar `value_nodes` and Value jobs are empty. A real empty RELEASE task precedes
the existing empty-map pin; notification, physical retirement and store-handle
release use the unchanged protocol. Key and held Sentinel each retain one owner.

The plain 40-byte original already agrees at `b88b45fc`: without destructor classes,
Fiber or generator work, ordinary leaf pruning retires the Map. A separate held
`ReleaseSentinel::__destruct` activates eager processing and exposes the genuine
nonempty storage refusal. The active 42-byte original agrees at `f68c6f09`; its Sentinel
runs only after Map/Key probes. The plain positive cut is retained without replay,
and the key-first native 40-byte observation has zero model credit.

Two genuine active-source cuts (160/100, total 260) pass for the consumed release,
empty release/pin transfer and notice/physical retirement/actual handle release.
Coherent supported scalar and request-string substitutions keep the same physical
edges and release authority; malformed string, extra Map owner, stale release,
wrong BEFORE and unheld Key controls refuse. Normalized replay binds the raw
steps. Full originals supply later Key/Sentinel retirement and endings. The
original active Unsupported remains zero; no prior active record is superseded.

The engine basis remains `zend_weakmap_free_obj`, `zend_weakrefs_hash_clean_ex`
and scalar zval cleanup before own std_dtor notification. No collector, root,
producer, receiver or notification-body change is made. Wider maps/keys/values,
wider scalar replacement, freeing mutation, escaped owners, callback/throw contexts
and wider GC remain required. [Ledger](../../coverage/semantics/weak-map-review.json).

## Ordinary dimension reads

Module386 admits authenticated object-key `KEY_R` reads from a live map. The
source access certificate must match the current task, BASE/result and key input.
A matching entry returns through `key_read_done`, creating a genuine strong value
result. Key notification then removes only the map owner: a held CV keeps the
value live and uncalled until its own release.

A missing object key throws Error using its class name and actual destruction
store handle, preserving the existing entry and value ownership. The 56-byte
held-copy and 88-byte missing-key originals agree at `c4c097e`. Checks for the
value copy (110), key release with a held value (74) and missing-key Error (113)
total 297, including three setup assertions per case. The missing cut follows real
Error materialization before catch; originals supply complete endings. The original 73-check control
miscounted the two `DESTRUCTOR_ENTER` roots and retains zero credit. Earlier cuts
stay at their tested revisions.

The engine basis is `zend_weakmap_read_dimension` in `Zend/zend_weakrefs.c`: an
ordinary `BP_VAR_R` read returns the stored zval; a missing object key reports the
class and object-store handle. Wider presence, reference/compound reads, other key
types, methods/iteration, wider entry shapes, mutation during freeing and ephemeron collection remain required. Countable stays nominal-only; count execution remains
excluded/Unsupported per CORE.

## Presence and scalar first entries

Module386 admits terminal `isset` and `empty` with a live map and nonfreeing
`stdClass` leaf key. For `isset`, a matching null value and a missing key both
return false; false, zero and empty strings return true. `empty` returns the
negation of stored truth. The existing
`KEY_TEST` carrier supplies the final boolean without calling `offsetGet` or
creating a Value owner.

Empty singleton storage also accepts null, bool, int and valid string first
values. The original object-value predicate remains disjoint and unchanged.
Current task/RHS/selected operands authenticate the new scalar lane. Module242
recognizes an interned literal RHS only through its actual child, raw compiled
string and source/precision-authenticated `compiled_string_value` producer;
same-byte request carriers cannot impersonate it. Stored carriers are preserved.

The object original (87 bytes) agrees at `144597d2`; its VARIABLE RHS excludes the
later string-source arm. The scalar original (180 bytes) and four reached cuts
(104/140/61/72, total 377) pass at `b7c1624a`. Object probes retain two Value
owners; coherent null/truth substitutions retain the original CV owner. Current
source/capture and wrong-carrier controls refuse. Cuts end at raw test results or
insertion; originals supply explicit scalar unset, Value release and full endings.
The unchanged Unsupported, original binding diagnostic and first scalar refusal
retain zero credit. No prior active record is superseded.

The engine basis is `zend_weakmap_has_dimension`, `zend_weakmap_write_dimension`
and `zend_weakmap_unset_dimension` in `Zend/zend_weakrefs.c`, plus
`ZEND_ISSET_ISEMPTY_DIM_OBJ`. Explicit methods, wider quiet/reference reads,
nonobject/freeing keys, float/array/reference values, wider scalar replacement/teardown and
wider map/GC protocols remain required.
[Ledger](../../coverage/semantics/weak-map-review.json).

## Quiet reads and coalesce

With a live singleton WeakMap and nonfreeing `stdClass` leaf key, `KEY_IS` returns
an ordinary copy of the stored pvalue. Missing keys return null without Error.
Only null selects the `??` RHS; false, zero, `''` and `'0'` remain exact results.
The internal selector returns directly through `key_read_done`, using the actual
current task/base/selected/key and retained source consumer. It does not use the
generic boolean presence then Get sequence. Ordinary read and terminal test
rules remain unchanged.

Two originals (61/166 bytes) agree at `df2997be`: present values skip a scalar
fallback assignment, missing/null reads take it, and a saved object copy survives
entry removal until that copy is dropped. Three reached cuts (135/76/68, total 279)
pass. The raw object read changes Value owners from two (CV and Map) to three
(result, CV and Map);
the genuine missing-key read leaves the original entry and its owners intact.
Coherent table substitutions retain the original Value CV. The actual null
coalesce-finish step schedules the RHS before changing the sentinel; coherent
non-null falsy finish controls skip it. Current-source/capture forgeries refuse,
and zero/one budget replay preserves the same states. Checks stop at raw reads
or RHS scheduling; originals supply complete endings. The original Unsupported
remains zero, and no active old record is superseded.

The engine basis is `zend_weakmap_read_dimension` (`BP_VAR_IS`), the object branch
of `zend_fetch_dimension_address_read` and its `ZVAL_COPY_DEREF` result, and
`ZEND_FETCH_DIM_IS`. This raw result owns the Value before the later coalesce
consumer assigns a CV. Explicit methods, `??=`, reference/compound results,
nonobject/freeing keys, reentrant or wider nested quiet reads, wider scalar replacement
and wider scalar teardown, iteration/general map order and wider GC remain
required. [Ledger](../../coverage/semantics/weak-map-review.json).

## Reads during postponed Key notification

An ordinary `KEY_R` read can use a physically pinned leaf stdClass Key while its
unique active TODO/saved-frame pin has pending NOTIFY. The allocated wrapper must
be the actual find result and match NOTIFY. The existing current task, base, input
and source certificate still authenticate the read, and the map must be live.
The pin supplies the actual object-store handle; shutdown handle iteration keeps
its existing exclusion of freeing instances.

A matching read creates an ordinary strong Value result and releases its temporary
Key owner through the shared release path. A missing entry materializes Error with
the actual handle, then retains that Error through temporary-Key cleanup until
THROW_SEARCH. The later map edge and Value owner stay intact. Once NOTIFY clears,
neither an extra strong Key owner nor inactive, duplicate or competing notice
metadata authorizes another read.

Two originals (111/162 bytes) agree at `2565d378`; copy (146), cleanup (65) and
missing Error (98) checks total 309. Reached cuts stop at shared release, scheduled
later VALUE or THROW_SEARCH, with originals supplying complete endings. Coherent
cleared-notice/extra-owner controls are distinct from malformed or inactive-only
carrier controls. Earlier Unsupported attempts, the operand diagnostic and both
receiver-fixture forecasts retain zero credit; the final fixture authenticates the
real destructor METHOD_TARGET.

The engine basis is `zend_weakmap_read_dimension`, `zend_weakref_get` and sequential
`zend_weakref_unref_single` in `Zend/zend_weakrefs.c`, with the physical free_obj pin
in `zend_objects_store_del`. Wider freeing keys/maps, escaped targets, inactive
carriers, mutations, presence/reference/method/iteration and general registration
or ephemeron protocols remain required. Existing get and cleanup rules are unchanged.
[Ledger](../../coverage/semantics/weak-map-review.json).

## Explicit entry unset

The singleton module386 authenticates the actual `UNSET_ARRAY` task, source access certificate
and current map/key operands. A matching entry clears before value release; the
existing eager edge comparison transfers its owner into a real VALUE job and
UNSET operation. Missing live object keys leave the entry unchanged. A separate
value CV survives matching removal and delays the destructor.

The normal 62-byte, throwing 69-byte and held/missing 87-byte originals agree at
`0c01e5f`. Four reached groups pass 136/100/94/88 checks, totaling 418. The pending
throw cut follows actual Value cleanup and transfers the same Exception owner
from operation exit to THROW_SEARCH; originals supply the complete endings.
The original message assertion expected a plain string and remains zero; the
corrected case checks bytes while preserving string-carrier identity.

Module422 also admits explicit dimension unset for inactive finite leaf-object
or validated entry-HCELL tables. Missing object Keys are no-ops; deletion packs
the exact retained records/BEFORE into singleton storage. Two sources and
139/2 author plus165/2 peer checks pass 304 Boolean/four raw transitions at
`5a7beee8a`/412. Raw direct X has owner0 but is still allocated; in these methodless
Many-to-singleton witnesses, public quiet pruning retires it without release jobs.
An escaped cell keeps owner1 and its Value. Rewriting it leaves A absent and B
unchanged; Map/Y retire before the final slot/cell/Z release. Keys remain live
until their explicit unset. Stale STORE/REFCELLS/OBJECTS history adds no owner.

Constructed NULL-table, captured-OFFSET and ghost-cursor helper refusals add no
PHP credit. Native and genuine baseline retain `9b3f9adf3`/412; baseline refusals
remain zero, and all affected checks pass first execution without activation lift.
Public method dispatch, wider payload/callback/freeing/active-context and
wider replacement/CONFIG/GC consumers remain partial.

The engine basis is `zend_weakmap_unset_dimension` and `zend_weakref_unregister`
in `Zend/zend_weakrefs.c`: absent object keys are no-ops; matching removal releases
the stored value while the key remains independent. Nonobject keys, wider unset
contexts/reference payloads, public methods, active-iteration mutation and
ephemeron protocols remain required;
mutation during freeing stays Unsupported. Earlier evidence retains its cuts.

## Occupied entry replacement

The singleton module386 admits same-key replacement with a leaf `stdClass` key and
ordinary leaf old/new INSTANCE values. Only VALUE changes: KEY and BEFORE preserve
the original registration, and the old callback observes the new entry.
Existing eager release handles shared and same-value owners. ACCESS_RESUME
retains the receiver through old cleanup without copying
the new value or key; original owned operands keep their ordinary roots. Unused
results finish with NULL, while used results copy the selected RHS value after
cleanup.
The carrier releases OP_DATA, the receiver, OP2 key and OP1 base in engine order.

Five normal/throwing/held/reentrant/result originals agree and 548 reached checks
pass at `70bf0c4`. The owned-key original and 94 checks pass at `302b5c9`, totaling
642. The later ordering change leaves prior variable-key roots literally [Map].
Reached cuts authenticate real VALUE jobs, shared release, a copied live object,
pending Exception transfer and map storage pin creation; originals supply endings.
The original budget-resume fixture failure and key-order mismatch retain zero
credit; the old 74-check preparation was never run.

Module422 also admits occupied finite-table replacement with direct or validated
leaf-object entry cells. Shared source authority keeps fresh-key DIRECT insertion
separate from an actual Many member; VALUE-only update preserves KEY/BEFORE/order.
The mature receiver continuation defers used-result copying until cleanup ends.
Two sources and author128/3 plus peer169/3 pass 297 Boolean/six raw transitions at
`4035dd2cf`/412: direct X retires; an old entry HCELL detaches and retains X while
Map receives direct Z. A separate old-cell rewrite leaves Map/sibling unchanged;
Map/Z/Y retire before the escaped cell/S and final Keys.

Receiver/new-Value deltas, real VALUE/HCELL jobs and used/z/Map owner3 sharing are
reached checks. Singleton-domain/tail-update and OFFSET/marker queries are
helper-only, with zero PHP credit. Native and genuine baseline retain `8b86fb948`;
baseline refusals and both original127/3 finder failures remain zero. The exact
fixture cause was BUDGET input to a NORMAL-only capture; only affected author
checks repeated after normalization and a paused-stage control. The earlier
stage2 scheduling forecast was wrong. Source/runtime evidence was not renewed.

The engine basis is `zend_weakmap_write_dimension` in `Zend/zend_weakrefs.c` and
`zend_assign_to_object_dim`/`ZEND_ASSIGN_DIM` in `Zend/zend_execute.c` and
`Zend/zend_vm_def.h`. Replacement publishes before old destruction without key
re-registration; assignment result copying follows the handler. Other key/value
shapes, wider entry graphs/reference payloads, mutation during freeing, public
methods, active iteration and ephemeron protocols remain required. Countable stays nominal-only, with count
execution excluded/Unsupported per CORE.

## Scalar occupied entry replacement

The same-key lane also accepts the existing bounded null/bool/int/string family
on either side of replacement. Old ordinary leaf object premises remain exact;
scalar writes keep current RHS/selected/source and carrier authority. KEY/BEFORE,
receiver roots, publication, release and result bodies are unchanged.

Two originals agree at `5dd834c5`/391. An old destructor observes the captured new
scalar entry and the unassigned result sentinel, then changes the actual RHS CV.
After cleanup, the used result reads that changed CV while the map keeps its
captured value. The companion replaces a scalar with false, then with an object;
the result alone keeps that object alive after entry/CV removal.

The 76/71 reached checks (147) bind real assignment publication, the sole old VALUE
job, post-destructor readback, no scalar release job and new object owners 1→2→3.
Current task/result/source and invalid value/carrier controls refuse. Normalized
checkpoint views preserve the original failed seek as zero credit. Checks stop at
readback, with originals supplying complete endings. The dedicated
`weak_map_scalar_replacement_state.py` retains the tested helper predicates.
Wider key/value shapes, mutation while freeing, references, methods, iteration
and broader GC remain required. [Ledger](../../coverage/semantics/weak-map-review.json).
