# Call argument unpacking

The paired107/108 slice expands arrays into direct user-function calls. Integer
keys send positional arguments in insertion order; their numeric values do not
select parameter positions. String keys bind fixed parameters or ordered named
variadic entries through the existing named binder. The string-key phase belongs
to each unpacked container: an integer following a string in that container
errors, while a later unpack container begins its own phase. Explicit positional
arguments after unpack remain a static error. Later explicit named arguments
retain their original source index while using accumulated destination slots.

Each UNPACK_NEXT task owns its operand independently of the arguments already
sent. It stores the current entry cursor and container string-key phase, without
a historical starting argument count or prior operand snapshots. Source argument
index, effective positional extent, fixed holes, and ordered extra names remain
separate. HOLE has no operand and differs from PHP NULL, even when a diagnostic
renders a missing trace slot as NULL.

The emitted operand class determines whether reference sends may update entries
of the unpacked array. Ordinary literal and folded variable names are CVs, excluding auto-globals and
whole GLOBALS; user-call and
reference-assignment results are VARs. Ordinary assignments, conditional and
coalesce results, computed variable reads, and dimension reads have value
semantics for this operation. List assignment and suppression follow their
source-derived emitted result class. Return-reference designation alone does not
determine the class. Existing source constant, redirect and name descriptors
supply compiler facts; dependent builtin result lowering remains explicit.

Eligible CV/VAR arrays undergo the source-pinned reference-demand prescan and
copy-on-write separation before entry errors. Entries are promoted and bound as
the loop reaches them. A captured reference operand preserves its cell identity;
borrowed reads do not add an owner that spuriously forces another separation.
Temporary value arrays give new references to non-reference entries while
preserving existing reference cells. Earlier sent arguments remain rooted if a
later entry errors, another argument calls a function, or the source variable is
unset. Normal and abrupt cleanup release the container and sent owners through
the ordinary heap and call machinery.

Expanded fixed holes use named default preflight before ordinary typed receive.
Successful deferred scalar defaults are cached before receive coercion; omitted
reference parameters receive independent cells. Preflight and binding inspect
live formal definedness and the effective positional extent. Trailing formals
remain absent until ordinary receive. Typed named tails retain the diagnostic
index max(fixed parameter count, effective positional ARGC)+1; extra named reference
SEND errors use fixed parameter count+1, while explicit fixed named destinations
use their mapped fixed index+1. Suppression and saved caller ownership
follow the accepted101 protocol.

SEND_UNPACK uses the final operand emission line. An original NArg-root CODEEXPR
marker records that line separately from the child call's own emitted line and
the outer call line. The marker has a false constant flag and adds no operand
mode descriptor. Validation projects only actual unpack marker and classifier
consumers from checked source, with literal/folded CV names source-bound at the
active PREP stage. Pending stages bind source lane, callee, source index,
remaining arguments and mode-valid owners. Entry stages check cursor range,
key phase and collected destination presence. At entry zero before any earlier
unpack, the explicit source prefix determines the initial slot shape; later
containers keep their accumulated dynamic slots. Prior values are not replayed.
Arbitrary consistent sent values, container entries and reference-cell values
remain legitimate paused states.

At the array checkpoint, Traversable expansion required object semantics. The
direct Iterator extension below adds that consumer. Builtin bodies, builtin
default receives and wider callbacks remain required integration work; their
source name/mode catalogue does not constitute body execution. Reporting
configuration, other callables, static locals, closures, objects, exceptions,
dynamic source, lifetime and the final complete-core gates remain pending. This
checkpoint closes no entire semantic family.

Validation covers55 exact source outcomes (31 normal,18 PHP errors,6 static
rejections),29 compiler phase comparisons and56 source projections,34 public
state controls with824 assertions,12 adjacent runtime profiles, and two author
ownership cases with435 assertions. Three builtin result contexts remain
explicit dependencies. Independent review adds seven source profiles, four
state cases with1063 assertions, and14 exact compatibility cuts against the
accepted972 baseline. These sets overlap. The cursor guard repair retains the
earlier gate identities; the final two-line unused-helper removal has an exact
zero-reference and byte/mode bridge.

The [runtime record](../../coverage/semantics/call-unpack-runtime.json),
[compiler record](../../coverage/semantics/call-unpack-compiler-pairing.json), and
[independent review](../../coverage/semantics/call-unpack-review.json) bind the
source profiles, failed originals, immutable inputs, and raw process closures.

## Direct user Iterators

Module385 admits direct user Iterators in ordinary source-function call unpack.
The unpack marker owns selected Iterator DATA independently of raw
temporary/reference INPUT; its cursor tracks traversal. A source CV stays borrowed.
The actual argument origin, emitted line, callee, source remainder and destination
modes authenticate pending and saved callbacks. Callback receivers are borrowed;
same-source reentry uses distinct frame-local cursors rather than a global
source-site singleton.

The current cache remains raw through key(). The user Iterator wrapper unwraps
reference-valued keys, normalizes numeric strings, and rejects non-int/string
keys. Values are dereferenced after key effects. Sent arguments own their copies;
next() retires the cached current value first. On error, key, unsent cache, DATA
and raw INPUT retire before pending arguments. Thus an invalid object key dies
before an unsent current object, while a sent object survives DATA cleanup.
An abort operation owns the pending exception while the remaining jobs finish,
including when a destructor replaces the exception. Its source receipt adds no
owners and remains valid after DATA retirement.
Raw valid() results retire before current() or empty completion. Temporary DATA
and INPUT retire before target entry, including empty traversal and defaults.

A by-reference target emits the native argument-number/function/line Warning.
For null/bool/int/float payloads, handlers may mutate a live reference, park or
throw. Resume reads the raw payload once and creates a fresh callee reference
cell; a copied current value is unaffected by handler writes to its source.
Warnings retain actual cursor/cache ownership through invoke/result/cleanup and
saved Fiber views. Copied KNOWN strings also keep their bytes and authenticated
carrier through key/handler writes, named variadic binding and Fiber park/throw.
Zend SEND_UNPACK dereferences and adds a payload reference before the warning,
then wraps the value in a fresh callee cell. Copied strings remain stable across
the callback; immutable string metadata has no modeled heap owners. A live
REFERENCE payload may change during the handler. Authenticated INTERNED_STRING
references now reread that live payload into the fresh callee cell, including
scalar-to-interned handler changes and named variadic or parked Fiber sends.
Zend's interned string flag makes Z_TRY_ADDREF_P inert; no detached payload owner
is needed. The raw source cell retires before next(), independently of the new
callee cell. Handler throw retires raw cell, DATA and temporary INPUT in order.
REQUEST_STRING and plain reference strings, including handler replacements,
remain Unsupported pending their separate pre-warning payload-hold contract.
At that cut direct Generator/Aggregate unpack, other call targets and Generator
callbacks remained explicit follow-ons. The
[string review](../../coverage/semantics/iterator-call-unpack-string-review.json)
records the bounded source and independent state cuts.
The [interned reference review](../../coverage/semantics/iterator-call-unpack-interned-reference-review.json)
retains the two affected originals' earlier native bytes without replaying the
four copied-string agreements or six unaffected state groups.

The first copied KNOWN object slice acquires an explicit HOLD before the warning
when SENT is empty. This matches SEND_UNPACK's Z_TRY_ADDREF_P before zend_error,
followed by ZVAL_NEW_REF even when the handler throws. Normal resume transfers HOLD
to the fresh private reference cell and retires the raw current cache before next().
Throw retires cache, DATA and raw INPUT before the failed argument's hold, so
the retained originals destroy the distinct Iterator before the payload after a
handler drops the last independent source owner. Actual Fiber park/resume and
injected throw keep that payload separate from a rewritten global source. HOLD
matches the exact copied object only at byref; earlier, NaN and completed stages
require no hold.
The abort SOURCE receipt validates this shape after payload retirement without
adding an owner. The
[object hold review](../../coverage/semantics/iterator-call-unpack-object-review.json)
records the native-first slice separately from earlier evidence.

Later copied-object warnings now admit a vacant fixed parameter slot when the
earlier sent buffer contains only fixed slots. The parked task retains HOLD
separately; abort inserts that owner at the selected slot before enumerating
argument cleanup. Native positional sends destroy the earlier payload first;
reversed named keys destroy the failed first-parameter payload first. Both follow
cache, DATA and raw INPUT retirement. Active and retired SOURCE admission check
the real by-reference target, slot vacancy and positional/named phase without
requiring retired payloads to remain live. Extra-named/variadic object warnings
remained Unsupported at that cut. The
[fixed-slot review](../../coverage/semantics/iterator-call-unpack-object-sent-review.json)
keeps the five new originals and their reached checks separate from prior cuts.

One direct construction of a statically named Iterator implementation now admits
fixed-to-extra object warnings with an untyped variadic and no positional extras, and
extra-to-fixed warnings with a by-value variadic tail. Failed arguments map through
the real named buffer: fixed slots retire before extra named entries, after raw
cache, DATA and INPUT. Parked HOLD remains separate. An authenticated singleton
private object cell received by an untyped by-reference variadic is collected as
a DIRECT item in a separated logical rest array. Its original named-send cell
still retains the payload until call teardown, so clearing the rest item does not
destroy it early. This abstracts Zend's shared-table/COW route; the model does not
claim its pre-write array identity or owner counts. Shared references use the old
alias path. Extra-to-extra and later positional variadic objects remained open
at that cut. General shared-buffer release before COW, arrays and REFERENCE
object payloads remain open.
The [extra-named review](../../coverage/semantics/iterator-call-unpack-object-extra-named-review.json)
records the new source cuts and the original failed native expectation.

Copied-object warnings after earlier extra names retain the earlier private
cells and append the failed payload in insertion order. Both extra names use the
same variadic parameter number. Normal rest writes preserve the original cells;
a thrown second warning retires cache/DATA/INPUT before earlier and failed payloads,
including real parked injection. The
[extra-to-extra review](../../coverage/semantics/iterator-call-unpack-object-extra-extra-review.json)
keeps these originals separate from the prior cuts.

Later positional copied objects now enter an untyped by-reference variadic at
the same authenticated direct Iterator construction, with no earlier named
extras. `RECV_VARIADIC` adds a reference owner for each packed rest item; the
existing ALIAS representation shares the original private argument cell with
the frame's EXTRA buffer. A rest-item write changes that cell and retires the
current payload before F, while the earlier payload survives until frame cleanup.
Warning throw still retires raw cache/DATA/INPUT before earlier and failed
arguments in positional order, including real parked injection. Typed tails and
wider call sites remained open at that cut. The
[positional variadic review](../../coverage/semantics/iterator-call-unpack-object-positional-variadic-review.json)
records this slice separately from the named DIRECT rest abstraction and prior cuts.

Nullable single-class positional tails now use that same ALIAS receive route.
Unpack warnings and fresh private-cell sends precede `RECV_VARIADIC` type
verification, so a rejected later class still has a sent cell while only the
earlier item has entered rest. A generated TypeError captures dereferenced
argument values in its owning trace; the caught error retains both payloads
after the private cells and partial rest retire, through the final output.
Warning-handler and parked injected exceptions keep the earlier Iterator-then-
payload cleanup order. Typed named buffers remained open at that cut; other type
shapes and wider sites stay open. The [typed positional review](../../coverage/semantics/iterator-call-unpack-object-typed-positional-variadic-review.json)
preserves the corrected native expectation and the separate validation cuts.

The same nullable single-class signature now permits named copied-object warnings
at the authenticated direct Iterator construction, with no positional extras.
Typed `RECV_VARIADIC` separates rest, verifies each item and retains its reference.
The existing ALIAS fallback shares each private cell with the named-send owner;
a current-item write destroys its payload before F. A later rejected class leaves
only the earlier rest item, then the TypeError trace owns both dereferenced values
under their original keys and insertion order. Handler and parked injection retain
raw/DATA/INPUT retirement before named payloads. Other type shapes, wider sites and
general shared-buffer alias/COW interactions remain open. The
[typed named review](../../coverage/semantics/iterator-call-unpack-object-typed-named-variadic-review.json)
keeps these originals and reached checks separate from prior cuts.

Copied KNOWN arrays now use the existing HOLD and container graph for a first
positional send into an untyped fixed by-reference parameter at one direct
statically named Iterator construction. SEND_UNPACK adds the array owner before
the warning, then transfers it into the fresh private cell. The container's
child edges are counted once even with multiple container owners. Thrown warnings
retire raw cache, DATA and INPUT before the last array owner expands child cleanup;
the acyclic one-child originals destroy the Iterator before the child. Normal
element writes destroy the child before F. Parked handlers retain the same array
through main-source replacement. Documentary SOURCE admission checks only shape,
site, target and key phase after container retirement. At that first-send cut,
later/named/typed array warnings, broader array/COW interactions and raw REFERENCE
arrays remained open.
The [array review](../../coverage/semantics/iterator-call-unpack-array-review.json)
records these originals separately from previous object and typed-tail cuts.

Copied arrays also admit earlier fixed-slot sends and named keys at the same
direct construction. The selected parameter must be fixed, untyped and by
reference, its slot vacant, and the sent buffer must contain only fixed slots.
The existing hold maps into that slot on warning throw: positional sends release
earlier then current containers, while reversed named slots release current then
earlier. Each container expands its child edge once. Normal fresh-cell element
writes destroy the current child before F, while the earlier child survives to
frame cleanup. Real parked injection retains both containers and scalar main
rewrites. Documentary SOURCE uses only call/key/slot metadata after array and
child retirement. At that fixed-slot cut, extra-named, variadic and typed arrays remained
unsupported; broader COW and live-reference interactions remain open. The
[array fixed-slot review](../../coverage/semantics/iterator-call-unpack-array-sent-review.json)
keeps these originals and source frontiers separate from the first-send cut.

Untyped positional by-reference variadic array sends use the same container hold
at the direct construction site, with no named extras. Receive increments each
incoming reference before packed insertion, so rest items alias the original
private cells. Nested current-item writes release that child before F; the
earlier child remains until frame cleanup. Second-warning throws and real parked
injection retain Iterator-before-earlier-before-current cleanup. The fixed-slot
arm remains unchanged, while the variadic arm requires integer keys and TYPEeps;
no receive, schema or documentary contents check changes. At that cut extra-named/
typed arrays remained open; broader COW/live-reference interactions remain open. The
[positional variadic review](../../coverage/semantics/iterator-call-unpack-array-positional-variadic-review.json)
records the three new originals separately from earlier cuts.

Nullable-array positional by-reference tails retain the same warning hold and
packed ALIAS receive at the direct construction site, with no named extras.
Only the array-plus-null type shape is added to variadic warning admission;
fixed parameters still require no type. RECV_VARIADIC verifies each item before
incrementing its reference and collecting it. A later scalar rejection leaves
only the earlier rest alias; the generated TypeError trace owns a DIRECT earlier
array snapshot after private cells retire, retaining its child through E. Normal
nested writes destroy the current child before F, while warning and parked throws
retire Iterator before earlier and current children. No receive, trace, schema or
documentary contents rules change. Extra-named/other typed arrays, broader COW and
live-reference payloads remained open at that cut. The
[typed positional array review](../../coverage/semantics/iterator-call-unpack-array-typed-positional-variadic-review.json)
keeps the four originals and their source frontiers separate from prior cuts.

Nullable-array named by-reference tails admit copied containers at the same
direct construction, with no positional extras. The disjoint NAMED_EXTRA arm
requires a real array-plus-null variadic reference parameter and a vacant key.
Typed RECV_VARIADIC verifies before adding each reference to its separate keyed
rest array; the existing ALIAS fallback remains unchanged. A nested alpha-child
write releases B before F while zeta retains A until frame cleanup. A later
scalar17 rejection leaves only zeta collected; its TypeError trace owns DIRECT
keyed snapshots and retains the earlier container/child after call cells retire
through E. Warning and parked throws retire Iterator then zeta and alpha in
insertion order. Documentary SOURCE checks no retired contents. Untyped named
arrays, other type shapes, broader COW and live references remained open at that
cut. The
[typed named array review](../../coverage/semantics/iterator-call-unpack-array-typed-named-variadic-review.json)
records four new originals separately from the positional cut.

Untyped named tails now admit copied arrays under the same direct-site,
no-positional-extra guards. The private receive predicate requires an actual
untyped by-reference variadic, the original named-send cell and exactly one cell
owner. Its collected rest item is DIRECT to the payload array while the original
send cell retains that array. This separated logical rest abstracts Zend's shared
extra-named table before COW; it does not assert native table identity or owner
counts. A nested alpha write copies its container, leaving the original child B
alive through F; frame cleanup then releases zeta's A before alpha's B. Shared
cells retain the existing ALIAS fallback, as do foreign sites and positional
extras. Warning and parked throws preserve Iterator-before-container/child
retirement in named insertion order, and documentary SOURCE reads no retired
contents. General shared buffers, other types, wider sites, embedded references,
cycles and broader COW/live-reference interactions remain required. The
[untyped named array review](../../coverage/semantics/iterator-call-unpack-array-named-variadic-review.json)
records three new originals separately from the typed cut.

Initial reference-object payloads are now admitted when CURRENT is the ALIAS cell
of an Iterator-owned declared untyped nonstatic property. This bounded route uses
the first positional send, empty sent buffer, direct statically named Iterator
construction and untyped fixed by-reference target. SEND_UNPACK dereferences and
adds a payload owner before warning dispatch; HOLD owns that object independently
of the raw HCELL. SNAPSHOT records its identity without adding an owner. Live
callback admission checks property/source-cell identity and rejects missing,
foreign or changed captures. Documentary SOURCE checks only frozen structural
authority after retirement, without reading dead STORE/property contents.
Normal send transfers HOLD into a fresh private callee cell; a key-created global
alias remains an object after that cell is cleared. Abort releases raw HCELL,
DATA/INPUT and then detached object, preserving Iterator-before-payload output.
Other reference sources, live payload replacement, reference arrays and broader
send/target shapes remained required at that object cut. The
[property reference review](../../coverage/semantics/iterator-call-unpack-reference-object-review.json)
preserves the corrected alias source and original failed probe separately.

The same stable property-reference capture now accepts array containers with one
acyclic destructible child, without embedded references. HOLD owns the container;
SNAPSHOT adds no owner, and the raw HCELL remains independent. The fresh callee
cell shares that container until a nested write separates it when the source
global alias survives Iterator retirement. Its original child then stays alive
through F until alias unset; without that alias, the child's destructor precedes
F. Abort consumes raw HCELL, DATA/INPUT, held container and then its child. Active
capture checks remain exact, while documentary SOURCE reads no retired STORE,
property or array contents. Object-only query compatibility is retained.
Other reference sources, live replacements, later/named/typed sends, wider sites
and broader array/COW interactions remained required at that array cut. The
[reference array review](../../coverage/semantics/iterator-call-unpack-reference-array-review.json)
records this slice separately from the object cut.

The first key may now name the first fixed untyped by-reference parameter in the
same direct Iterator construction with an empty sent buffer. Both stable object
and bounded array property references use the existing detached payload hold,
nonowning snapshot and fresh private callee cell. A source alias remains separate;
array writes retain their ordinary copy-on-write behavior. The completed send
records named-argument history, so a later positional key raises Error before
another warning or target entry. This follows `SEND_UNPACK` and
`zend_handle_named_arg`, then `ZVAL_DEREF`, `Z_TRY_ADDREF` and `ZVAL_NEW_REF` in
the pinned engine. Later fixed destinations, typed/variadic reference sends,
other sources and live payload replacement remained required at that cut. The
[named reference review](../../coverage/semantics/iterator-call-unpack-named-reference-review.json)
keeps this extension separate from the earlier positional cuts.

An initial named reference send may now select any fixed untyped by-reference
parameter at the same direct site, with no previous sent arguments or named phase.
The selected slot creates genuine earlier argument holes; its warning number and
argument count use the selected position. The captured key stays fixed when a
handler changes a returned key reference. Defaults fill the holes before the
body while the distinct private payload cell stays owned. A missing required
earlier parameter raises `ArgumentCountError`; its real trace retains the supplied
payload through caught-exception release. Object aliases, array COW and warning
cleanup retain their existing rules. Actual later sends, typed/variadic targets,
other sources and live payload replacement remained required at that cut. The
[reference-hole review](../../coverage/semantics/iterator-call-unpack-reference-holes-review.json)
preserves previous evidence and the affected earlier helper checks separately.

Initial stable property-reference sends also admit the exact normalized
`[class, null]` and `[array, null]` shapes at fixed by-reference parameters.
The empty sent buffer, direct construction, untyped source property and stable
capture bounds remain. Positional slot0 reaches its type receive without holes;
named later slots fill earlier defaults first. Receive checks the dereferenced
private cell after Iterator retirement. It adds no persistent parameter constraint,
so a subsequent integer write succeeds while source aliases keep the original
payload; nested array writes still use COW. A mismatch creates the real TypeError
with owning DIRECT trace arguments, retaining the payload after callee retirement
until caught-exception release. A warning-handler throw precedes this receive.
This follows `SEND_UNPACK`, `ZVAL_NEW_REF`, `RECV`/`RECV_INIT` and
`zend_verify_recv_arg_type`. Reversed union order, nonnullable/other type shapes,
variadic targets, actual later sends and wider source/live replacement behavior
remained required at that cut. The
[typed reference review](../../coverage/semantics/iterator-call-unpack-typed-reference-review.json)
keeps the new source/state cuts separate from prior evidence.

Noninitial stable object property-reference sends now accept a free fixed untyped
by-reference slot after at least one earlier fixed slot is filled, with no named
extras or positional extras. The same direct construction and stable untyped
source-property bounds remain. Earlier sends may own either a copied object or a
private cell; the current raw HCELL and detached HOLD stay separate. Returning one
raw property twice still produces two distinct private cells. Named selection can
fill earlier holes; positional keys still require no previous named phase.
`SEND_UNPACK` and `zend_handle_named_arg` check invalid or occupied keys before
capture and warning. Aborts retire Iterator data before failed arguments in fixed
parameter order, including reversed named sends. Retired SOURCE authentication
uses the frozen object shape without reading dead source storage. The filled-slot
bound does not assert replay of prior value history. Later arrays, typed targets,
variadic reference sends and wider sources/live replacements remained required at
that cut.
The [noninitial reference review](../../coverage/semantics/iterator-call-unpack-noninitial-reference-review.json)
records this extension separately from initial-send evidence.

Noninitial stable array property references now use that same fixed untyped
target admission. `SEND_UNPACK` dereferences and adds an array owner before the
warning, then `ZVAL_NEW_REF` gives each send a distinct private cell. Earlier
fixed arguments can hold a copied array or a private reference. Multiple array
owners do not duplicate the container's child edges. Returning the same raw array
twice still permits a nested first-parameter write to copy its container while
the second retains its child; a separate source alias likewise survives private
nested writes. Aborts retire Iterator data before arguments in fixed parameter
order, including reversed names and a second warning suspended in a Fiber.
Retired SOURCE checks keep frozen array shape after raw cell and container
retirement without reading dead storage. One-child arrays without embedded
references provide the new differential/state evidence; admission uses the
existing array graph rather than a new child-shape restriction. Later typed or
variadic reference targets, wider sources, live replacements and broader
array/reference/COW interactions remained required at that cut. The
[noninitial array reference review](../../coverage/semantics/iterator-call-unpack-noninitial-array-reference-review.json)
keeps these originals and the sole affected prior documentary check separate.

Noninitial stable property-reference sends now admit the same exact normalized
nullable single-class and nullable-array shapes at fixed BYREF targets. Existing
filled-slot, vacancy, named-history, source-property and direct-site bounds stay
in force. `SEND_UNPACK` warns and creates each source-free private cell before
`RECV`/`RECV_INIT` and `zend_verify_recv_arg_type` check types in parameter order.
Those checks add no persistent parameter type source: incompatible body writes
still succeed, while repeated raw arrays and source aliases retain ordinary COW.
A rejected later receive materializes owning DIRECT trace arguments for earlier
and current payloads; private argument retirement does not destroy trace-owned
objects or array children. Reversed named failures retain parameter order in the
trace, including an earlier by-value array. Warning-handler throws and real Fiber
injection precede receive rejection. Reversed union order, nonnullable/other type
shapes, variadic targets, wider sources/sites, live replacements and broader array/
reference interactions remained required at that cut. The
[noninitial typed reference review](../../coverage/semantics/iterator-call-unpack-noninitial-typed-reference-review.json)
keeps these new cuts and the affected prior type-admission check separate.

Stable property-reference object/array payloads now also enter untyped positional
BYREF variadic tails, before or after earlier fixed/rest sends at the same direct
site. Numeric keys require no prior named phase or extra-named buffer. Existing
capture, HOLD and SNAPSHOT checks stay in force; `SEND_UNPACK` gives each item a
fresh private cell before `RECV_VARIADIC` collects packed ALIAS entries. Repeated
raw properties still produce distinct cells, and nested array writes preserve
other entries/source aliases through COW. Original EXTRA owners survive removal
of the local rest array until frame cleanup. Second-warning throws and Fiber
injection retire Iterator data before the earlier/current payloads; documentary
SOURCE checks read no retired cells or array tables. Typed or named variadic
reference sends, wider sources/sites, live replacements and broader array/reference
interactions remained required at that cut. The
[positional variadic reference review](../../coverage/semantics/iterator-call-unpack-reference-positional-variadic-review.json)
keeps these new cuts and the affected prior admission check separate.

Positional property-reference variadic sends also admit the existing exact
normalized `[class, null]` and `[array, null]` shapes. Numeric-key, no-named-phase,
stable untyped source-property and direct-site bounds remain unchanged. Each
`SEND_UNPACK` warning precedes its fresh private cell; `RECV_VARIADIC` checks
types while collecting packed ALIAS entries, with original EXTRA owners retained.
A later mismatch leaves earlier accepted entries intact and creates a TypeError
whose DIRECT trace owns every supplied argument, including by-value prefixes
and rejected arrays. The trace outlives callee retirement; source aliases keep
their separate roots after caught-error release. Successful receive adds no
persistent parameter type source, so later integer writes succeed and nested
array writes retain ordinary COW. A second warning throw or real parked Fiber
injection precedes even an earlier argument's first receive rejection. This
follows `SEND_UNPACK`, `ZVAL_NEW_REF`, `RECV_VARIADIC` and
`zend_verify_variadic_arg_type`. Reversed union order, nonnullable/other type
shapes, named reference tails, wider sources/sites and live replacement remain
required. One-child acyclic arrays establish the new evidence domain without
adding a child-shape admission restriction. The
[typed variadic reference review](../../coverage/semantics/iterator-call-unpack-reference-typed-positional-variadic-review.json)
keeps these cuts and two affected prior guard checks separate.

Iterator valid NaN warnings keep the raw retval in CURRENT through handler invoke,
result, cleanup and saved Fiber frames. The native `zend_user_it_valid` wrapper
calls `i_zend_is_true`, retires that retval, then permits SEND_UNPACK to check the
exception or fetch current. Its DOUBLE arm rereads the payload after the warning
without redispatching its tag. Numeric references therefore use their live double
bits; an integer minimum reads signed-zero bits and is false. Copied NaN stays true.
The pure existing numeric decision helper performs one reread without another
warning, and raw retval cleanup precedes current or DATA/INPUT teardown. Later
warnings keep earlier sent owners and named phase; handler throw preserves ordered
abort cleanup. Nonnumeric raw-tag changes stay explicit Unsupported.
The [NaN review](../../coverage/semantics/iterator-call-unpack-nan-review.json)
keeps this increment separate from the original unpack source/state cuts.


## Direct Generator operands

Module405 expands Generator operands into plain source-function calls using the
native iterator protocol. Acquisition checks CLOSED before adding a DATA owner.
The unpack marker owns the original operand, acquired DATA and sent arguments;
resume borrows DATA through an authenticated source-argument site and real saved
resumer. Cached values are dereferenced and copied into by-value slots before
next resume, including reference-yielding producers. No extra CURRENT owner or
synthetic `Generator::rewind`/`next` trace frame is introduced. Integer/string key
checks and named-slot errors precede the remaining by-reference-target refusal.

Normal completion and finally precede target defaults and typed receive. A body
throw retains its actual Generator function trace. Abort cleanup releases DATA,
INPUT and sent arguments in order: a temporary Generator closes/frees its cache,
while an independent CV delays that close until unset. Receive TypeError traces
own their copied arguments after the Generator retires. Abort source receipts
check syntax and input mode without rereading retired payload storage. This follows
`SEND_UNPACK`, `zend_generator_get_iterator`, its iterator callbacks, and
`zend_generator_close`. Last-owner storage keeps the existing quiet release
carrier when ordinary destructor execution is inactive, following
`zend_generator_free_storage` and `zend_objects_store_del`.
At that cut active yield-from producers stopped at the authenticated `Unsupported` boundary.
By-reference targets, wider call targets and broader
Generator/delegation/Fiber lifecycle interactions remain required. The
[Generator unpack review](../../coverage/semantics/generator-call-unpack-review.json)
keeps the new source/state evidence separate from prior Iterator campaigns.


## Delegated array producers

Ordinary Generator call unpack also admits active array delegation with an
existing source-authenticated record, positive position and present current
cache. The delegated table and CURRENT operand keep their real owners; SEND
copies/dereferences the cached value into a by-value slot before the next resume.
This preserves reference-cell snapshots and COW between repeated nested rows.
Existing named/default/receive checks and ordered abort release apply unchanged.
A retained CV keeps the delegated table after a key error; last-owner unset
releases that table before forced finally, then the independent current cache.
A temporary closes before its sent arguments retire. The queued close preserves
the real caller release receipt and any child-destructor exception through finally
and cache cleanup. This follows
`zend_generator_get_next_delegated_value`, `zend_generator_dtor_storage` and the
native Generator iterator callbacks used by `SEND_UNPACK`.
Non-array delegates and by-reference targets remain explicitly `Unsupported`.
The [delegated-array review](../../coverage/semantics/generator-call-unpack-array-delegation-review.json)
keeps new evidence and the promoted prior control separate from the direct-yield cut.
