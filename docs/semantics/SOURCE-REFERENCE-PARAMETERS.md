# Positional reference parameters

This increment extends source named calls with untyped positional reference
parameters and value returns. It remains part of the complete-core plan.
Defaults, parameter/return types, reference returns, variadics, named/unpacked
arguments, closures and other callable protocols remain separate work.

The later [named-send continuation](SOURCE-NAMED-ARGUMENTS.md) also preserves
private call-result references through an error-handler Notice, including
source-CV rebinding, named variadics, reference returns and cancellation.

## Send and bind

Selected error handlers now receive the `Only variables should be passed by
reference` Notice from bounded positional user calls as well. Both the selected
function and the direct by-value producer are ordinary,
attribute-free nongenerators. Fixed producer names retain the existing
no-fallback route. Pending
values and untyped reference payloads admit null/bool/int/float, non-NUL
interned strings, authenticated REQUEST strings at roots and scalar array leaves,
the live array graphs and quiet root `stdClass` payloads
described below. String and array
reference cells have no parameter-backing metadata. The actual next
`CALL_ARGS` vector owns the new private cell before dispatch, preserving prior
sent cells through source-CV rebinding. Normal/false handling continues later
arguments once; a supplied throw cancels call entry and caller assignment, then
retires the private cell before catch. Reference returns retain their real cells.
The certificate binds the emitting origin, exact positional prefix/vector modes,
fixed or variadic destination and emitted Notice line. Actual reference producers
remain quiet, while TMP values still raise their argument Error before the
handler. Wider producers, property sources beneath object fields, raw/NUL strings, wider owning values, typed root sources,
unpack and callback lifetimes remain partial. See the
[positional Notice review](../../coverage/semantics/positional-reference-send-notice-review.json).

The named and positional Notice receipts also admit non-NUL interned string
values and untyped string reference cells without parameter-backing metadata.
A producer's by-value string stays frozen while the handler changes its global;
earlier sent reference cells follow real writes and retain identity through
rebinding/unset. The carrier adds no heap owner; the actual sent cell owns the
payload. After reception, ordinary concat may produce a request string and a
reference return carries the updated cell into the caller. Request strings outside
the root/array-leaf/quiet-object-field admission below, raw/NUL strings, typed/property/coercion sources and broader lifetimes remain
partial. See the
[interned-string review](../../coverage/semantics/interned-reference-notice-review.json).

A producer may also take one positional argument written as a literal ordinary
CV. This route requires one fixed required untyped formal, passed by value or
reference, with no parameter attributes, and an untyped producer return. The
producer finishes before the outer Notice and releases its formal owner. An
unescaped by-value formal cell retires; escaped aliases retain their real owners.
The copied result and earlier outer sent cells then survive handler writes,
rebinding or unset of that argument
CV. Validation checks its original syntax without looking up the current CV or
adding an owner of its former cell. The Notice uses the inner CV's compiled line,
separately from the producer call instruction's line. Named/unpacked/computed
producer actuals, special CVs (`this`, auto-globals and `http_response_header`),
and optional/variadic/typed/attributed producer signatures remain outside this
new route; the old no-argument domain is unchanged. See the
[completed-producer review](../../coverage/semantics/producer-cv-reference-notice-review.json).

The one-CV route also admits one required `array` formal passed by value, with
its raw identifier and exact normalized type authenticated. The producer returns
by value without a return declaration. Its frame and formal retire before the
outer Notice; the saved array remains valid when a handler replaces the caller's
original CV with an integer. An incompatible argument raises TypeError before
the producer body and outer Notice. Array formals passed by reference and typed
producer returns remain outside this addition. See the
[array-BYVAL review](../../coverage/semantics/array-producer-cv-reference-notice-review.json).

Named and positional Notices also admit an unqualified namespaced producer
whose current primary function has the call's source unit and genuine early
`PPFUNCTION` publication. Primary-only lookup and authentic declaration history
establish that this target was present before the producer ran. Current lookup
or the descriptor's `EARLY` flag alone is insufficient. Existing source,
signature, argument, payload and ownership bounds remain; private-cell allocation
and callback resumption stay unchanged. A global fallback that installs a local
primary during its body remains Unsupported, as do wider late/dynamic contexts.
See the [early-primary review](../../coverage/semantics/namespaced-primary-producer-reference-notice-review.json).

Completed producers also admit finite vectors of multiple literal ordinary CVs
with exactly matching required fixed untyped formals and an untyped return.
Duplicate actual CVs are valid; raw and normalized reference modes must match.
The last inner CV's compiled line supplies the Notice line, accounting for both
finalized and deferred/forward call compilation. Qualification uses original
source syntax after actual names or formal cells have disappeared. Captured
values, live prior references, table COW, true caller unset and cancellation keep
their separate owners. The [multiple-CV review](../../coverage/semantics/multi-cv-producer-reference-notice-review.json)
records seven new Notice agreements and a separate quiet control using eight
native originals once, with independent 316/402 fixture cuts. Wider multi headers
and actual forms remain partial; old zero/one and typed-singleton routes are unchanged.

Named and positional Notice operands also admit finite acyclic array graphs
through DIRECT children and ordinary ALIAS cells with scalar/interned, array
or quiet stdClass payloads. The ancestor path crosses both edge kinds, allowing
sibling sharing while rejecting cycles. Each table owns its physical entries once; an
array-valued cell owns one current table edge, independently of incoming owner
multiplicity.
The returned root owner moves into the real private cell before dispatch.

COW unwraps a singleton reference into a copied DIRECT value. Shared and repeated
entries retain the same cell, so handler writes and array-payload retargeting
remain visible through them. Nested array COW separates selected descendants
while preserving outside copies. A supplied throw releases the private cell and
retires cells and tables only when their last real owner leaves.

Embedded cells must be live, marked and defined. Except for the bounded property
source below, property sources remain excluded. Coercion sources,
parameter backing, container initialization, retained/debt and foreach-release
histories, and native count units remain excluded. An array-valued cell must
expose exactly its current child edge; released payload histories cannot supply
that edge. Newly admitted child headers exclude literal retained/debt records,
native count units, immutable tables and every table reachable from a
compiled-pool root. Existing root-array admission is unchanged.

USER object payloads, INDIRECT/uninitialized entries,
property sources beneath object fields, raw/NUL strings and wider producer/callback lifetimes remain partial.
The [array-cell review](../../coverage/semantics/alias-child-reference-notice-review.json)
records source, physical-owner, COW, cleanup and budget cuts separately. Earlier
[DIRECT-graph](../../coverage/semantics/direct-child-reference-notice-review.json),
[flat-array](../../coverage/semantics/array-reference-notice-review.json) and
[scalar-reference](../../coverage/semantics/alias-array-reference-notice-review.json)
evidence keeps its own scope. Generic ownership and GC header/callback receipts
are unchanged.

Quiet root `stdClass` values and ordinary object reference cells also cross the
Notice. The actual sent/private cell owns one object edge; incoming aliases of
another cell do not multiply that cell's payload edge. Handler property writes
preserve identity after source unset or replacement. A reference return retains
the private cell, while later scalar rebinding leaves outside object aliases
intact. Supplied throw cancellation retires the last-owned object and notifies
WeakReference before catch, preserving the saved Throwable and old assignment
target while skipping later sends and body entry.

The target must be an allocated stdClass with a complete canonical local record
of DIRECT null/bool/int/float or authenticated non-NUL string fields, with
non-NUL startup names.
Normal dynamic MATERIALIZED records are allowed without OBJECTTABLES. Cached
tables, owning/reference fields, freeing/called targets, native object units and
WeakMap key registrations are excluded; GC ACTIVE/PLAN/WORKER must be empty,
without requiring an empty ordinary root buffer. An object REFERENCE also needs
its actual CELL-to-object edge and the ordinary no property/coercion/backing,
container, debt/retained/release or native-cell-unit fences. USER instances
and wider lifetimes remain partial. The
[stdClass review](../../coverage/semantics/stdclass-reference-notice-review.json)
records three source agreements and separate named, throw and refusal state cuts.

Finite Notice array graphs also admit DIRECT quiet stdClass leaves. An array
copy adds one object edge for each copied object entry, independently of the
number of incoming owners of either table. It preserves object identity and
shared scalar property writes. Source replacement does not redirect the pending
old array; the returned reference keeps the genuine private cell. A supplied
throw drops the private cell, table and sole object before catch, notifying
WeakReference without user destruction or collection.

Every array ancestor of an object leaf, including the root, must be allocated,
mutable and outside compiled-pool reach, with no literal retained/debt record or
native count unit. The path crosses DIRECT and ALIAS-array edges; existing cell
fences and path-local cycle rejection remain. Repeated object IDs are leaf
sharing, and multiple incoming table owners do not multiply its object edges.
The root-stdClass object helper remains literal, including scalar-only fields,
inactive collector and no WeakMap key registration. Old scalar/array routes keep
their earlier root admission. Owning fields, USER instances and broader
lifetimes remain partial. The
[DIRECT-leaf review](../../coverage/semantics/direct-object-leaf-reference-notice-review.json)
records separate source, actual COW, throw, ancestry and budget cuts.

Ordinary ALIAS object leaves use those same quiet-target and whole-ancestor
bounds, plus the embedded cell fences above and an exact current CELL-to-object
edge. A shared cell owns its current object once, independently of incoming
table or CV owners. Handler assignment through that cell retargets every ALIAS
view. Root COW retains a shared cell and adds an entry owner, without adding
another object payload edge. A singleton reference instead unwraps to a DIRECT
object entry: the copied entry adds an object edge, and replacing it leaves the
old table's cell unchanged. Ordinary object-CV property writes preserve shared
identity in both cases. A supplied handler throw retains the real pending
private-cell/array graph until cleanup; the completed graph retires last-owned
cells, tables and objects, with WeakReference NULL observed in catch. The
[ALIAS-leaf review](../../coverage/semantics/alias-object-leaf-reference-notice-review.json)
records four originals and separate physical-edge, continuation and refusal cuts.

An ALIAS object leaf may carry finite genuine sources from rooted ordinary
objects' plain public `stdClass` properties. Distinct owners may share a
declaration; owner/key/declaration tuples remain unique. Each class is parentless
and has no methods or interfaces; constants use the bound below. Each nonstatic,
nonreadonly, nonfinal property has no default, hook or set restriction.
Canonical unmaterialized slots may alias that selected cell with their own
reciprocal source and CELL edge, hold
a quiet DIRECT `stdClass` with its real object edge, or be fresh `PROP_INITIAL` /
explicitly unset `PROP_UNSET`. Repeated object identities retain each physical
edge; descriptor and physical-slot lists must match completely. Every source object
must survive logical heap pruning,
without a cached table, native unit, WeakMap key registration or pending destruction.
Positive cell ownership cannot replace that per-owner lifetime check.
Type-source metadata adds no owner. Shared COW retains remaining constraints,
including after the ordinary leaf CV disappears. A rejected scalar write leaves
the object intact. Explicit property unset or transfer removes one source while
the source object stays rooted; only the final source removal untypes the old
cell. Explicit CV and old-table removal can then permit singleton DIRECT copying.
Quiet-target, whole-ancestor and other cell fences remain unchanged.
Source-object retirement and wider lifetimes remain partial. Two source
agreements and separate owner/COW/refusal cuts are in the
[finite typed-leaf review](../../coverage/semantics/multi-property-alias-stdclass-reference-notice-review.json).
The [same-owner extension](../../coverage/semantics/same-owner-property-alias-stdclass-reference-notice-review.json)
adds three/four-slot source observations, including INITIAL plus actual UNSET
reentry, and keeps final-only transfer between cells on one owner. The
[direct sibling extension](../../coverage/semantics/direct-sibling-property-alias-stdclass-reference-notice-review.json)
adds two source agreements for distinct/repeated quiet children and staged weak
release, plus 149 unique conditions for admission, retarget, COW and refusals.
Different-cell aliases, nonquiet DIRECT children and wider source-owner lifetimes
remain partial. Quiet static DIRECT siblings and same-class instance complements
of static sources use the separate proofs described below.

Finite plain public static `stdClass` declarations in one ordinary class may
also constrain that leaf. An actual row may alias the selected cell with its
reciprocal source or hold a quiet DIRECT `stdClass`; a fresh INITIAL row adds no
root. Different-cell and UNSET rows remain excluded. A partial transfer
can finish through the ordinary writers after the Notice, while a new Notice
during the split stays Unsupported. The
[same-class static review](../../coverage/semantics/same-class-static-alias-stdclass-reference-notice-review.json)
keeps the positional/named source and reached/derived state cuts separate.
The [DIRECT static sibling extension](../../coverage/semantics/static-direct-sibling-alias-stdclass-reference-notice-review.json)
preserves each actual static root, including duplicate quiet objects, through
retarget, failed binding, COW, final transfer and staged value replacement. DIRECT
rows add no type source; stale selected CLASS sources remain refused. Raw source,
active descriptor, class/arena, quiet-object and history fences remain unchanged.
Grouped items authenticate their exact source index and absent default within
the actual plain property group without hooks, using compiler-produced occurrence
tables. Existing owner and writer protocols remain unchanged; see the
[grouped-static review](../../coverage/semantics/grouped-static-alias-stdclass-reference-notice-review.json).

Named global source classes may have finite own public untyped nonfinal constants
whose raw initializers are `NScalarInt`. The complete raw class/group/item walk
authenticates names, owners, indexed occurrences, initializer children and exact
folded `PINT`/`PVSCALAR` pools. No constant or scalar pool adds an owner. Both
instance and static source guards use this proof, retaining the old constant-free
route and all property/source/quiet/owner bounds. Wider constants remain partial;
see the
[integer-constant review](../../coverage/semantics/class-int-constant-alias-stdclass-reference-notice-review.json).

One raw `NExprUnaryMinus(NScalarInt z)` is also admitted. Its exact parent and
`PCFIELD 0` child occurrences must agree, both `z` and `0-z` must fit a signed
long, and the parent pool must contain folded `PINT(0-z)` / `PVSCALAR`. The
direct-literal arm is unchanged. Two original source agreements and 319 unique
state conditions retain separate private cuts in the
[unary-minus review](../../coverage/semantics/class-negative-int-constant-alias-stdclass-reference-notice-review.json).

Namespaced companions also authenticate a valid short raw class name through the
owner's canonical unit/path/file/positive-line context and exact namespace join.
Global equality, the empty-constant path and existing integer/minus, source and
ownership proofs remain unchanged. The
[namespace review](../../coverage/semantics/namespaced-class-int-constant-alias-stdclass-reference-notice-review.json)
retains two author507/peer505 source agreements, 262 unique state conditions and
the separate joined508/source0 load. Earlier unqualified producer failures remain
source0; only the accepted witnesses' inner calls were qualified.

Same-class instance/static declarations compose their proofs against actual
state. Static members consume no object slot or edge; ALIAS instance complements
need a genuine selected-cell source for the exact declaration/key and class.
Fresh INITIAL, actual UNSET and quiet DIRECT complements may instead use another
genuine source on the same instance, authenticating the queried descriptor's exact
class membership and physical declaration/key/state. The full owner/slot/pruning
proof retains every real child edge, including duplicate identities. Static
INITIAL under an OBJECT-only source adds no root.
When an exact-class INSTANCE arena record exists, static-only mixed membership
without a genuine selected instance source remains partial; pure-instance hole
laws are unchanged. Both split-cell orientations
remain outside Notice admission. The
[same-class mixed review](../../coverage/semantics/same-class-mixed-property-alias-stdclass-reference-notice-review.json)
and [hole extension](../../coverage/semantics/same-class-mixed-hole-alias-stdclass-reference-notice-review.json)
retain their separate original-source and state cuts.
The [DIRECT-complement extension](../../coverage/semantics/same-class-mixed-direct-alias-stdclass-reference-notice-review.json)
adds two exact source agreements and 211 unique conditions for genuine mixed
membership, retarget, failed binding, shared COW and partial/final source transfer.
Its new proof promotes two current valid mixed-source predicates; the REF22
DIRECT refusal remains historical. CLASS-only membership with an exact-class
INSTANCE record and different-cell aliases remain refused. Quiet static DIRECT
rows follow their separate root proof above.

If the stable arena contains no INSTANCE record for the exact declaring class,
the class walk can validate unused plain instance declarations without an instance
witness. Every raw grouped item must have its exact indexed origin in the actual
class members and equal its indexed occurrence. The selected index must be in
range and identify that same raw item; absent defaults, no hooks, public `stdClass`
and setter bounds remain required. These declarations add no slot, source, edge
or root. Past/non-rooted exact-class records also block this route; other origins
do not establish PHP ancestry facts. The
[singleton review](../../coverage/semantics/static-only-mixed-alias-stdclass-reference-notice-review.json)
retains its cuts. The
[grouped extension](../../coverage/semantics/grouped-unused-mixed-alias-stdclass-reference-notice-review.json)
adds two source agreements and 129 unique state conditions, including extra raw
items without descriptors. Wider static-only contexts remain partial.

Required canonical `array` producer formals also accept by-reference reception
from the existing one-CV argument. The raw and normalized BYREF flags must match;
the by-value arm remains unchanged. Entry checking adds no persistent parameter
type constraint: the producer may save the array, replace its shared caller cell
with an integer and return the saved array before Notice. Handler writes to that
caller cell remain separate from the saved array and fresh private argument cell.
Three original comparisons reuse native observations once. Author AL108 and peer
AL129 retain separate source/state cuts; prior REF32 evidence remains historical.
Wider headers/lifetimes stay partial. See the
[array-BYREF review](../../coverage/semantics/array-byref-producer-cv-reference-notice-review.json).

Those required `array` formals also admit canonical `array` return declarations.
The raw return and normalized type must agree before the old argument proof is
reused; the actual descriptor retains its return type and ordinary return
verification runs before Notice. The returned array survives formal/frame
retirement, while the separate private argument cell can later hold an integer.
Three originals agree with native observations run once: two Notice cases and
one caught return-TypeError control. Author AL149 and peer fixture-SL174 retain
separate cuts; the unchanged peer AL174 timeout is inconclusive. Actual source
composition and joined loading are separate/source0. Other return types and
wider headers/lifetimes remain partial. See the
[array-return review](../../coverage/semantics/array-return-producer-cv-reference-notice-review.json).

Required untyped one-CV formals now admit those same canonical `array` returns.
A scalar argument can produce a fresh array: BYREF reception preserves the caller
cell, while BYVAL reception preserves the captured scalar after caller mutation.
Ordinary return verification precedes private-cell creation and Notice dispatch.
Three originals agree using native observations once. Author fixture-SL177 and
peer fixture-SL192 retain separate cuts; the actual return/header front and the
affected prior header-only check have zero source credit. One wrong-table fixture
premise and both Unsupported baselines retain zero credit. Other return types
and wider headers/lifetimes remain partial. Actual joined SL508 at `484d489ce`
passes separately with zero source credit. See the
[untyped array-return review](../../coverage/semantics/untyped-array-return-producer-cv-reference-notice-review.json).

The same canonical `array` return is admitted for multiple literal CV actuals
with matching required fixed untyped formals. Return verification preserves the
input tables and source constraints; frame retirement precedes private-cell
creation. Current prior references follow handler writes, while returned-array
COW preserves outside snapshots. The private cell may later hold an integer.
A sole private table retires on handler cancellation; a caught return TypeError
keeps its saved argument array alive through the exception trace. The
[multiple-CV array-return review](../../coverage/semantics/multi-cv-array-return-producer-reference-notice-review.json)
records three Notice agreements and a separate prelaw return-priority control
using four native originals once, with independent 397/149 fixture cuts. Other
declared multi returns and typed multi formals remain partial.

The same required untyped/`array` one-CV producers also admit raw `?array`
returns with the exact normalized `[array, null]` type. The ordinary descriptor
and return verifier retain that type. An array return owns its fresh table;
a null return has no heap child and lets an unescaped formal array retire before
Notice. The separate private reference remains untyped after handler reentry.
Three new originals agree using native observations once. Author fixture-SL182
and peer fixture-SL172 retain separate cuts; the two actual old-fence fronts and
the old null-source Unsupported control have zero source credit. That cut does
not cover explicit union syntax or wider headers/lifetimes. See the
[nullable array-return review](../../coverage/semantics/nullable-array-return-producer-cv-reference-notice-review.json).

Explicit `array|null` and `null|array` return headers now admit those same
one-CV producers. Each raw member must match its normalized builtin in source
order; ordinary return verification still precedes Notice. Array ownership,
null-result formal retirement and the fresh untyped private cell retain their
separate behavior. Three originals agree using native observations once.
Author fixture-SL187 and peer fixture-SL181 execute 368 conditions: 302 reached
and 66 derived, with their 507/505-module cuts kept separate. Old-fence fronts
105/110 and the affected header control31 have zero source credit. Actual joined
SL508 passes separately at `ab60fab36` with zero source credit. Other returns and
wider headers/lifetimes remain partial. See the
[ordered union return review](../../coverage/semantics/union-array-return-producer-cv-reference-notice-review.json).

Canonical `int` returns also admit those existing one-CV producers. The raw
identifier must match the exact normalized singleton type. Weak return coercion
copies a numeric string without writing back through its source alias; strict
return failure precedes the outer Notice. An integer read from an aliased array
element survives retirement of its by-value formal and old table. The fresh
Notice cell remains untyped and can later hold a string or array independently
of the caller and former array element. Three originals agree using native
observations once. Author fixture-SL155 and peer fixture-SL191 execute 346
conditions (292 reached, 54 derived), retaining separate 507/505-module cuts.
Old fronts91/103, Unsupported baselines and preserved fixture failures have zero
source credit. Actual joined SL508 passes separately at `b1e8a2876` with zero
source credit. Other returns and wider headers/lifetimes remain partial. See the
[integer return review](../../coverage/semantics/int-return-producer-cv-reference-notice-review.json).

Canonical `float`, `bool` and `string` returns share that singleton-header
authentication. At the REF39 cut, strings had to be non-NUL and
interned. Strict integer-to-float return conversion, weak `'0'` to false and weak
`5` to interned `'5'` preserve the caller's stored value. Strict string-return
failure precedes Notice. Actual array-formal retirement and later untyped private
string/array writes retain their separate owners. Four originals agree with
native PHP; a fifth asserted that cut's `Unsupported` boundary for the valid
request string produced from `17`. All five native originals run once.
Fixture-SL246/196 execute 442 conditions (383 reached, 59 derived) at separate
507/505-module cuts; old fronts91/103 and Unsupported controls have zero source
credit. Actual joined SL508 passes separately at `13e4bb86d` with zero source
credit. Its request-string boundary is extended below; the historical evidence
keeps its original identity. See the
[scalar return review](../../coverage/semantics/scalar-return-producer-cv-reference-notice-review.json).

Canonical `int`/`float`/`bool`/`string` returns also admit multiple literal CVs
with the same matching required fixed untyped formals. Weak return conversion
preserves captured input stores and tables, and string returns retain existing
non-NUL carrier authentication. The last compiled CV supplies the Notice line
after the producer frame retires, even if a caller name has been removed. Private cells accept
later array/scalar replacement and string COW without inheriting a return
constraint; prior sent references retain current handler writes. A caught failed
owning return retains its argument through the TypeError trace until exception
unset, when WeakReference observes release. The
[multiple-CV scalar-return review](../../coverage/semantics/multi-cv-scalar-return-producer-reference-notice-review.json)
records four Notice agreements and a separate prelaw error-priority control from
five native originals once, with independent 470/287 fixture cuts. Nullable/union
multi returns and typed multi formals remain partial.

Multiple-CV producers also admit raw `?array` returns with exact normalized
`[array, null]`, retaining the required fixed untyped formal vector. Actual
verification preserves returned snapshots before frame retirement and private
Notice-cell creation. ARRAY COW keeps an outside REQUEST-string snapshot; NULL
has no heap child and can later become a string or integer in the untyped private
cell. Prior references retain current handler writes. Three Notice originals and
a separate corrected prelaw invalid-return priority control agree using four
current natives once. One superseded library-call preparation remains at zero
credit, giving five physical native observations. Separate fixture-SL356/240 cuts
and two surgical current50 header flips are recorded in the
[multiple-CV nullable-array review](../../coverage/semantics/multi-cv-nullable-array-return-producer-reference-notice-review.json).
At the REF52 cut, ordered-union multi returns and typed multi formals remained partial.

Multiple-CV producers also admit explicit `array|null` and `null|array` return
headers. The two distinct raw members must match their normalized builtin types
in source order; the required fixed untyped vector and ordinary verifier are
unchanged. ARRAY/null snapshots retain their separate lifetimes after frame
retirement and caller-name removal. Named prior references remain current, and
private cells permit later byte COW and integer replacement. Three Notice
originals and one separate prelaw invalid-return priority control agree using
four native originals once. The [multiple-CV ordered-union review](../../coverage/semantics/multi-cv-union-array-return-producer-reference-notice-review.json)
records independent 362/241 fixture cuts, one current REF52 header-only expectation
flip and the separate combined joined load. At the REF53 cut, nullable scalar and wider unions, typed multi formals and
wider lifetime contexts remained partial.

The same multiple-CV vector now admits canonical `?int`, `?float`, `?bool` and
`?string` returns with exact normalized `[scalar, null]`. Return verification
uses callee strictness: integer to FLOAT promotion, weak INT/BOOL conversion,
authenticated REQUEST-string preservation and childless NULL retain their
captured snapshots. Private cells may later hold arrays, other scalars or byte
COW results without inheriting return constraints. A strict INT return resolves
its real deferred CV before TypeError, preceding Notice, consumer entry and
assignment. Five Notice originals and a separate prelaw strict-priority control
agree using six native originals once. The [multiple-CV nullable-scalar review](../../coverage/semantics/multi-cv-nullable-scalar-return-producer-reference-notice-review.json)
records separate 551/389 fixture cuts, the preserved fixture-only operand failure
and four current header-expectation flips without old campaign replay. At the REF54 cut, explicit ordered scalar/null and wider unions, typed multi
formals and wider contexts remained partial.

Explicit `scalar|null` and `null|scalar` returns now admit the same multiple-CV
producers, with `scalar` one of canonical `int`, `float`, `bool` or `string`.
Exactly two distinct raw members match the normalized types in source order;
one is NULL. Existing callee-strict verification, frame retirement, snapshot
identity and private-cell COW/replacement retain their separate behavior. Five
Notice originals and one prelaw strict INT-priority control agree using six
native originals once. The [multiple-CV scalar/null-union review](../../coverage/semantics/multi-cv-union-scalar-return-producer-reference-notice-review.json)
records separate 557/399 fixture cuts and one current54 header-only predicate
flip, without old campaign replay. At the REF55 cut, wider unions, typed multi
formals and wider contexts remained partial.


Completed producers with multiple literal ordinary CV actuals also admit matching
fixed required canonical `array` formals, mixed with untyped formals or all ARRAY.
Raw identifiers, normalized singleton ARRAY types and BYREF match pointwise; the
existing receive verifies values before the producer body. Parameter types add
no persistent cell constraint: an ordinary reference formal may later hold INT23.
Captured snapshots, frame retirement, the last compiled CV line and existing
return/payload/source/backing/ownership/GC guards remain. Three Notice originals
and one separate prelaw second-argument TypeError control agree with four native
originals once. Separate 384/249 fixture cuts also distinguish a dynamic table's
last-owner retirement from a literal table's surviving POOLS owner. The
[multiple-CV ARRAY-formal review](../../coverage/semantics/multi-cv-array-formal-producer-reference-notice-review.json)
retains the recorder/fixture failures and diagnostics at source0. At the REF56 cut,
wider formal types/defaults/variadics/attributes and lifetimes remained partial;
Owned-NUL remains held.


The same finite ordinary-CV vector now admits matching required fixed canonical
`int`, `float`, `bool` and `string` formals alongside ARRAY/untyped formals.
Standalone normalized singleton types match raw identifiers pointwise. Existing
reception uses caller strictness: BYVAL coercion preserves the caller value,
while ordinary BYREF coercion changes the shared cell without a persistent
parameter constraint. Three Notice originals and one separate prelaw strict
second-argument TypeError control agree with four native originals once. Frame
retirement, snapshots, current prior references, private arrays/raw byte COW and
cleanup retain existing return/payload/source/backing/ownership/GC guards. The
[multiple-CV scalar-formal review](../../coverage/semantics/multi-cv-scalar-formal-producer-reference-notice-review.json)
records separate 420/233 fixture cuts, a matching old header-only predicate change
and preserved fixture failures/diagnostics at source0. At the REF57 cut,
nullable/union and wider formals/defaults/variadics/attributes and lifetimes
remained partial; Owned-NUL remains held.

The multiple-CV vector also admits canonical `?array`, `?int`, `?float`, `?bool`
and `?string` formals with exact normalized `[kind, null]` and pointwise raw
nullable/BYREF authority. Caller-strict reception accepts NULL unchanged; weak
BYVAL conversion preserves caller snapshots, while ordinary BYREF cells may
change type again in the producer body. Existing return verification,
frame-retirement, last compiled-CV line and ownership guards remain. Three
postlaw Notice originals and one separate prelaw strict parameter-priority
control agree with four native originals once. The
[multiple-CV nullable-formal review](../../coverage/semantics/multi-cv-nullable-formal-producer-reference-notice-review.json)
keeps author454 and independent236 fixture checks at their separate507-module
cuts, preserves the original fixture failures at source0, and records the sole
actual508-module joined load. Singleton scalar/nullable formals, wider unions,
defaults/variadics/attributes and lifetimes remain partial at this cut;
Owned-NUL remains held.

The same finite formal proof also admits a singleton literal ordinary CV with
canonical int/float/bool/string or nullable ARRAY/int/float/bool/string type.
The new arm excludes untyped and singleton ARRAY types, preserving those old
alternatives. BYVAL coercion keeps the caller snapshot; ordinary BYREF aliases
can change type in the body and survive caller-name removal. Existing return
headers, caller-strict reception, frame retirement and private-cell ownership
remain. Three postlaw Notice originals and one separate prelaw strict INT
parameter-priority control agree with four native originals once. The
[singleton formal review](../../coverage/semantics/singleton-cv-typed-formal-producer-reference-notice-review.json)
keeps author318/independent207 fixture checks at separate507-module cuts and the
actual508-module joined load separate. Singleton nullable scalar/ordered scalar-null
returns, formal unions/defaults/variadics/attributes and wider lifetimes remain
partial at this cut; Owned-NUL remains held.

Singleton completed producers also admit canonical nullable int/float/bool/string
and exactly ordered scalar|null/null|scalar return headers. Raw identifiers and
normalized branches match pointwise; callee-strict verification and producer-frame
retirement precede private Notice-cell creation. Three postlaw Notice originals
and a separate prelaw strict bool|null return-priority original reuse four native
observations once. The [nullable-return review](../../coverage/semantics/singleton-cv-nullable-scalar-return-producer-reference-notice-review.json)
keeps author287/peer184 private507 fixtures and the sole actual508 load separate.
Formal unions, broader headers and lifetimes remain partial; Owned-NUL stays held.

Root Notice operands now also admit non-NUL REQUEST strings whose identity and
bytes match current `STRINGDATA`. At the REF40 cut only KNOWN operands and the existing
unconstrained scalar REFERENCE arm used this state-aware check; nested array/object
payloads and source/coercion/backing guards retained their earlier bounds. Returned
snapshots stay independent of caller aliases through handler and private-cell
byte writes. An earlier named REQUEST argument also stays frozen after its source
changes and the producer's by-value array formal/table retires. A throwing handler
retires the private cell before catch. Existing string-offset writes produce
byte-only values with unknown identity; preserved snapshots retain their authentic
carrier, and carrier metadata adds no heap edge. Three new originals agree, with
one nested-array Unsupported control and four native executions once. Separate
fixture-SL213/226 cuts retain 507/505 modules. The affected older weak `17` return
has one new agreement and fixture-SL57 using its saved native observation; REF39
is not renewed. Its array-leaf and DIRECT-object-field boundaries are extended below;
raw/NUL strings and wider headers/lifetimes remain partial. See the
[request-string return review](../../coverage/semantics/request-string-return-producer-cv-reference-notice-review.json).

Existing finite array graphs also admit authenticated non-NUL REQUEST strings
in DIRECT entries and ordinary unconstrained ALIAS leaves. The same scalar check
now serves those two entry arms; all cell, header, ancestor, source and backing
guards stay in place. Handler retargeting preserves the current shared leaf while
copied strings and COW children remain independent. Repeated DIRECT edges count
separately, while one physical child table owns its ALIAS edge once. Deletion,
private overwrite and supplied throw retire only last owners. Byte writes retain
unknown identity; separate ordinary integer output can append string metadata.
Three newly admitted Notice originals agree using five fresh native observations
once across those originals, a separate pre-admission quiet-COW control and an
object-field Unsupported control. Fixture-SL255/229 retain separate 507/505-module
cuts. The prior REF40 nested control has one affected source agreement and
fixture-SL30 using its saved native observation; three affected peer predicates
execute positively in fresh REF41 checks. Historical REF40 is not renewed.
Its then-Unsupported REQUEST object-field case is extended below. Raw/NUL strings
and wider headers/lifetimes remain partial; the Owned-NUL hold is unchanged. See the
[array-leaf review](../../coverage/semantics/request-string-array-leaf-reference-notice-review.json).

Existing quiet `stdClass` Notice targets also admit authenticated non-NUL REQUEST
strings in ordinary DIRECT fields, at roots and existing array object leaves.
The slot fold now receives state for carrier authentication; field declaration/name,
complete-record, childless-object, liveness, table, GC, WeakMap and native-count
bounds stay in place. Handler field writes remain visible through shared object
identity while copied string snapshots stay unchanged. Object and field-cell
aliasing remain distinct: retargeting an ordinary array ALIAS cell changes one
object payload edge, independently of its incoming names. Private overwrite,
array-entry deletion and final-owner release retain the observed WeakReference
notifications; supplied throw also retires a sole private object before catch.
At REF42, three new originals agreed and a genuine ALIAS-valued object field stayed
Unsupported, using four fresh native observations once. Fixture-SL242/261 retain
separate 507/505-module cuts. The former REF41 object-field control has one
affected agreement and fixture-SL32 using its saved native observation; prior
slot-helper controls are checked by matching fresh predicates. Historical REF41
is not renewed. Its ALIAS-field control is extended below; owning fields, raw/NUL
strings and wider contexts remain partial. The Owned-NUL hold is unchanged. See the
[object-field review](../../coverage/semantics/request-string-object-field-reference-notice-review.json).

Ordinary quiet `stdClass` ALIAS fields now admit live, marked, defined and
childless cells with primitive or authenticated non-NUL string payloads. The
slot fold preserves all declaration/name, source, backing, coercion, container,
history and native-count fences. Object children must equal the existing
physical property-release vector: repeated fields own separate cell edges,
independently of incoming object handles. Handler property rebinding moves one
edge; field deletion, last-object release and outside-alias cleanup retire only
their real owners. A supplied throw retires a sole field cell and object before
catch, including its WeakReference notification. Three new originals agree;
an owning-array ALIAS-field original remains Unsupported, using four fresh
native observations once. Separate fixture-SL300/282 cuts check repeated-edge
counts, independent scalar snapshots, raw byte writes and staged retirement.
The former REF42 scalar-ALIAS control has one affected agreement and fixture-SL36
using its saved native observation; historical REF42 is not renewed. Other owning or
cyclic field payloads, raw/NUL strings and wider contexts remain partial; all
outer object/GC/WeakMap/table/ancestor bounds and the Owned-NUL hold stay in place.
See the [scalar ALIAS-field review](../../coverage/semantics/stdclass-alias-scalar-field-reference-notice-review.json).

Ordinary ALIAS fields also admit existing finite object-free array graphs with
live mutable roots outside compiled-pool reach. A physical reach check rejects
object descendants before recursive array admission. Each cell owns one current
table edge, independently of incoming field/CV names. Retargeting, nested COW and
shared scalar aliases preserve outside copies and their real owners; deletion,
last-object release and throw cancellation retire only exhausted cells/tables.
Three new Notice sources agree; a separate quiet COW control agrees and a genuine
object/array cycle stays Unsupported. Five current originals run natively once;
one superseded preparation remains separate. Fixture-SL361/312 retain distinct
507-module cuts. The old REF43 pooled-array control stays Unsupported in a
focused23 check using its saved native observation; historical REF43 is not
renewed. Pool/immutable field roots, owning object fields, raw/NUL ingress
and wider source/backing/lifetime contexts remain partial; the Owned-NUL hold
is unchanged. See the
[ALIAS-array-field review](../../coverage/semantics/stdclass-alias-array-field-reference-notice-review.json).

Ordinary DIRECT array fields use the same finite object-free graph and mutable
nonpool-root bounds. Each physical field owns its array edge: two fields sharing
one table contribute two owners, independently of incoming object handles.
Field-specific nested COW separates both fields from an outside copy while
embedded scalar aliases stay shared. Deletion and last-object release retire
the actual tables; a promoted/exported field cell can keep its array alive after
the object's WeakReference notification. Throw cancellation also releases repeated
array edges before catch. Three new Notice sources and a separate quiet control
agree; a genuine DIRECT object/array cycle stays Unsupported, using five native
originals once. Separate fixture-SL352/329 retain 507-module cuts; historical
REF44 is not renewed. That cut left owning object fields partial; pool/immutable
roots, raw/NUL ingress and wider source/backing/lifetime contexts retain their bounds.
See the [DIRECT-array-field review](../../coverage/semantics/stdclass-direct-array-field-reference-notice-review.json).

DIRECT quiet `stdClass` fields now form finite acyclic object paths. A path-local
object ancestor list permits shared siblings and repeated physical fields while
rejecting self and ancestor cycles; array fields remain object-free. Handler
retargeting and shared-object writes preserve actual identities, and repeated
child edges retire only when their last owners leave. Reference exports can keep
a child alive after its parent dies. Supplied throw cancellation releases the
private root and repeated descendants before catch. Three new Notice sources and
a separate quiet control agree; two real object cycles stay Unsupported, using
six native originals once. Separate fixture-SL383/361 retain 507-module cuts;
historical REF45 is not renewed. Public helper interfaces, all existing object,
cell, source, header and GC guards, and Owned-NUL are unchanged. That cut left
owning ALIAS object fields partial. See the
[DIRECT-object-field review](../../coverage/semantics/stdclass-direct-object-field-reference-notice-review.json).

Ordinary ALIAS object fields now retain one current object edge per live marked
cell. Multiple property/CV aliases add cell owners, while property rebinding moves
one physical field edge. Handler retargets and exports preserve the current child;
overwriting its payload can notify WeakReference while scalar aliases of the cell
remain alive. Repeated-cell throw cleanup releases the entire last-owned object
chain before catch. The same path-local ancestors reject self and ancestor cycles;
array fields stay object-free. Three new Notice sources and one separate quiet
control agree, with two Unsupported cycle controls and six native originals once.
Separate fixture-SL399/350 retain 507-module cuts. One quiet expected-output
correction reused unchanged source/native facts; its original failed expectation
keeps zero credit. Existing source/backing/history/GC guards and Owned-NUL remain.
At that cut, mixed object/array fields stayed partial. See the
[ALIAS-object-field review](../../coverage/semantics/stdclass-alias-object-field-reference-notice-review.json).

Finite mixed array/object paths now cross DIRECT and ordinary ALIAS fields.
Separate array and object ancestor lists travel across both edge kinds, allowing
shared siblings and equal numeric IDs while rejecting alternating cycles.
Table COW adds physical entry edges; it preserves shared object identity and
one current payload edge per cell. Exported aliases can outlive parent objects,
and payload replacement can retire a table or object before its cell aliases.
Repeated mixed-graph throw cleanup retires the last-owned cluster before catch.
Three new Notice sources and a separate quiet control agree, using seven native
originals once; two alternating cycles and a finite typed-source graph remain
Unsupported. Separate fixture-SL462/434 retain 507-module cuts and the original
fixture failures keep zero credit. Object fields still require ordinary cells:
property-source validation below an object ancestor stays excluded, preserving
the earlier root-array source route. Mutable nonpool field headers, existing
cell/source/backing/history/GC bounds and Owned-NUL are unchanged. See the
[mixed-field review](../../coverage/semantics/mixed-object-array-field-reference-notice-review.json).

Default Notices without a selected handler use that same inner CV line on the
bounded completed-producer route. Matching SEND tasks, current quiet payloads
and the existing source qualifier select this correction; other contexts retain
their earlier line calculation. One SEND still stores the genuine private cell
in the actual argument continuation, with the outer callsite unchanged. The
named counterpart also reports duplicate Errors at the SEND line before any
Notice or new reference. See the
[default-line review](../../coverage/semantics/default-reference-line-review.json).

The selected function origin remains fixed before argument effects. Each send
consults its normalized `psparam.BYREF`; surplus arguments remain by value.
Writable variable arguments prepare their original name/dimension expression,
acquire its location, initialize missing slots to null, and promote the final
cell. The resulting `REFERENCE` operand owns that cell immediately. Subsequent
argument effects may unset or rebind the original variable without changing the
sent cell. Frame entry binds the parameter name to the cell, while by-value
parameters and surplus arguments retain copied values.

Source expression result kind is separate from runtime reference identity.
`$ppsend_var` models the relevant compiled result distinction: calls and reference
assignments produce VAR operands; destructuring preserves its RHS result and
reference patterns request MAKE_REF. Ordinary assignments, updates, conditionals
and coalescing produce TMP operands. TMP sends to required-reference parameters
throw the exact argument error. A VAR holding an actual reference passes that
reference; a VAR holding a value emits `Only variables should be passed by
reference`, allocates a temporary reference and enters the body. Diagnostic lines
come from the original argument occurrence, separately from the outer call line.

## Shared dimensions and destructuring

The compiler's call-result dimension admission also reaches ordinary writes,
reference acquisition, destructuring and foreach targets. Writable temporary
containers use unnamed slots; acquisition transfers the held value owner to the
slot before array-copy ownership checks. A captured reference outlives its
otherwise dead temporary container. Literal-array dimensions remain statically
invalid for known writable fetches; deferred reference fetches fail at runtime
after the measured key effects. Deferred VAR expression bases can remain usable.

A reference-binding target in a temporary dimension raises the pinned engine's
`Cannot assign by reference to an array dimension of an object` error, despite
its wording also applying to returned arrays. A reference-list RHS preserves
actual references, but a value-returning call or extracted temporary value stays
a value. Each reference fetch from that value emits `Attempting to set reference
to non referenceable value`. Nested list values remain values; final reference
leaves receive detached cells. Passing the resulting value to a reference
parameter emits the separate send notice. Ordinary list results preserve actual
VAR references rather than unconditionally dereferencing the RHS.

## Ownership and public resumption

Existing operand-root traversal owns pending references in CALL_ARGS/CALL_SEND,
current/saved locals, held temporaries, and saved continuations. Return/error
unwinding uses the established frame and iterator cleanup. Temporary reference
acquisition retains a result owner until the next consumer moves it; array
literal insertion avoids counting that same owner twice.

Public entry validates source-derived reference-task origin/index/target and
pending operand modes. A sent reference must designate an allocated, marked,
defined cell. By-value sends and surplus values have KNOWN operands. These are
finite representation checks: arbitrary legitimate values, aliases, mutations,
unsets and rebindings are not reconstructed from source history.

## Engine provenance and validation boundary

The sole oracle remains vendored PHP8.5.10 CLI NTS64. Relevant authored symbols:
`zend_compile_args`, `zend_compile_list_assign`, `zend_compile_assign`,
`zend_delayed_compile_dim`, `zend_separate_if_call_and_write`,
SEND_VAL_EX/SEND_VAR_NO_REF(_EX)/SEND_REF, FETCH_DIM_W/FETCH_LIST_W, MAKE_REF,
ASSIGN_REF, and `zend_fetch_dimension_address_read` in the pinned Zend compiler,
VM definitions and executor. Ordinary-library execution is not delegated to PHP;
compiler builtin result-kind facts do not implement library bodies.

Author and independent reports bind the exact source bytes, native/provider
profiles, stdout/stderr/status, actual tools and loaded modules. Original
Unsupported states, temporary-dimension mismatches, fixture syntax/elaboration
errors, the list-target rule overlap and the interrupted exploratory state run
remain distinct from final agreement. No full-callable or full-core closure is
claimed by this increment.

Current [independent acceptance](../../coverage/semantics/reference-parameter-review.json)
binds tested882 to canonical884 through the explicit unchanged two-file bridge.
[Author history](../../coverage/semantics/reference-runtime-originals.json) and
[publication/CLI evidence](../../coverage/semantics/reference-runtime-publication-originals.json)
retain their separate scopes and original failures.
