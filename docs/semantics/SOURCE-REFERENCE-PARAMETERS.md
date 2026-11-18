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

Required producer formals also admit exactly ordered kind|null/null|kind pairs for
array/int/float/bool/string through the existing raw/normalized/BYREF fold, for
singleton and multiple literal CV actuals. Caller-strict reception preserves BYVAL
snapshots and permits ordinary BYREF entry coercion without a persistent type
constraint. The [union-null formal review](../../coverage/semantics/cv-union-null-formal-producer-reference-notice-review.json)
keeps three postlaw Notice originals, one prelaw strict parameter-priority control,
native4 once,480/216 private507 fixtures and the sole actual508 load separate.
Broader unions, defaults/variadics/attributes and lifetimes remain partial.

The same two-member proof admits distinct members of array/int/float/bool/string/null.
Raw source order still matches normalized branches pointwise. Weak int|float
reception uses numeric-string classification, while string|bool prefers STRING
over BOOL; ordinary BYREF entry conversion adds no persistent constraint. The
[distinct-union review](../../coverage/semantics/cv-distinct-builtin-union-formal-producer-reference-notice-review.json)
keeps native4 once, postlaw Notice3/prelaw priority1,560/231 private507 fixtures and
the sole actual508 load separate. Larger unions and wider contexts remain partial.

Formal unions over exactly array/int/float/bool/string/null also admit three to six
distinct members through an ordered raw/normalized fold. Seen kinds reject duplicates;
exact exhaustion rejects count/order mismatches. The old two-member arm stays literal.
The [primitive-union review](../../coverage/semantics/cv-primitive-union-formal-producer-reference-notice-review.json)
keeps native4 once, postlaw Notice3/prelaw priority1,480/242 private507 fixtures and
the sole actual508 load separate. Existing STRING membership precedes weak numeric
preference; ordinary alias entry conversion adds no persistent constraint.
Other types, signatures and wider contexts remain partial; Owned-NUL stays held.

Return headers also admit exactly two distinct NONNULL array/int/float/bool/string
members through pointwise raw/normalized proof and the unchanged argument gate.
Callee-strict verification precedes frame retirement and private Notice-cell creation;
the strict numeric-REQUEST control enters its body, then rejects at RETURN before
Notice, consumer or assignment. The [nonnull-return review](../../coverage/semantics/cv-distinct-builtin-union-return-producer-reference-notice-review.json)
keeps native4 once, Notice3/prelaw RETURN-priority1,280/261 private507 fixtures and
the sole actual508 load separate. At that cut, higher return unions and wider contexts remained partial.

Completed singleton and multi-CV producers also admit three to six distinct ordered
array/int/float/bool/string/null return members. The existing raw/normalized fold
rejects duplicate, count and order mismatches before reusing the argument proof.
Exact membership precedes weak scalar preference; callee-strict return verification
and frame retirement precede private Notice-cell creation. The
[primitive-return review](../../coverage/semantics/cv-primitive-union-return-producer-reference-notice-review.json)
keeps the native, source, state and canonical-load cuts separate. The exact raw
triple control in the current two-member test suite accepts its normalized triple;
its historical results retain their original identity. Wider types, signatures,
owners and lifetimes remain partial; Owned-NUL stays held.

Canonical standalone `null` return headers also use the completed singleton and
multi-CV producer route. Exact raw/normalized proof reuses the argument guard;
nonnull returns reject even in weak mode. Producer verification and frame
retirement precede the fresh private Notice cell, which has no persistent return
constraint and may later hold strings, arrays or integers. The
[null-return review](../../coverage/semantics/cv-null-return-producer-reference-notice-review.json)
keeps the native originals, new Notice agreements, weak RETURN-priority control,
state fixtures and canonical load separate. Wider contexts remain partial;
Owned-NUL stays held.

Canonical standalone `mixed` returns also use the completed singleton and
multi-CV producer route. Exact raw/normalized authentication reuses the existing
argument proof. Mixed preserves the admitted value without coercion; producer-frame
retirement still precedes private Notice-cell creation. The
[mixed-return review](../../coverage/semantics/cv-mixed-return-producer-reference-notice-review.json)
keeps three new Notice agreements, the separate prelaw strict RECEIVE-priority
control, four native originals run once, private state fixtures and the sole actual
canonical load distinct. Existing formal/payload/source/ownership bounds remain;
Owned-NUL stays held.

Required canonical `mixed` formals share the completed singleton and multi-CV
producer proof. Each raw identifier matches its sole normalized mixed branch and
reference mode. Mixed includes NULL and preserves admitted values under either
caller mode; BYVAL formal cells retire before private Notice-cell creation, while
ordinary BYREF formals use the real caller cell without a persistent type
constraint. The [mixed-formal review](../../coverage/semantics/cv-mixed-formal-producer-reference-notice-review.json)
keeps four fresh Notice agreements/native originals run once, separate private
state cuts and the sole actual canonical load distinct. Existing return, payload,
source and ownership bounds remain; nullable/union mixed and wider contexts remain
partial, with Owned-NUL held.

Required canonical standalone `null` formals also use the completed singleton
and multi-CV proof. The raw identifier matches its sole normalized null branch
and exact reference mode. NULL reception preserves identity in either caller
mode; other values fail reception before the producer body or Notice. Ordinary
BYREF formals add no persistent alias type constraint, so body mutation can
replace the caller cell with a quiet object. The
[null-formal review](../../coverage/semantics/cv-null-formal-producer-reference-notice-review.json)
separates three fresh Notice agreements from the weak REQUEST receive-priority
control, four native originals run once, the private fixture cuts and the sole
actual canonical load. Existing return, payload, source and ownership bounds
remain partial; all paused boundaries, including Owned-NUL, remain held.

Required canonical standalone `false` and `true` formals share that pointwise
proof. Each raw identifier matches its normalized singleton tag and reference
mode. Neither literal type coerces another value, even under weak reception.
Ordinary BYREF formals add no persistent constraint; BYVAL formal retirement
still precedes private Notice-cell creation. The
[literal-Boolean formal review](../../coverage/semantics/cv-literal-bool-formal-producer-reference-notice-review.json)
keeps three new Notice agreements, two distinct weak integer RECEIVE-priority
controls, five native originals once, separate private fixtures and the sole
actual canonical load distinct. Non-null or wider literal-Boolean union headers
and contexts remain partial; all existing holds remain.

Canonical standalone `false` and `true` returns share the completed ordinary-CV
producer proof. Exact raw identifiers match their normalized singleton tags;
neither type coerces other values under weak return checking. Actual verification
uses callee strictness and precedes frame retirement and fresh private Notice-cell
creation. The private cell remains untyped through later mutation and cleanup.
The [literal-Boolean return review](../../coverage/semantics/cv-literal-bool-return-producer-reference-notice-review.json)
keeps three new Notice agreements, two weak integer RETURN-priority controls,
five native originals once, separate private fixtures and the sole actual canonical
load distinct. Constructed int-return controls distinguish callee and caller
strictness at the actual RETURN stage with source credit zero. Non-null or wider union
literal-Boolean formals and returns, wider contexts and all held lanes remain partial.

Canonical `?false` and `?true` formals and returns also share the completed
ordinary-CV producer proof. Raw nullable identifiers match exact normalized
`[kind,null]` order. Only the exact literal tag or NULL passes, without weak
scalar coercion; required reference modes, caller-strict reception and callee-strict
return verification remain intact. Ordinary BYREF formals add no persistent
alias constraint. Frame retirement precedes the fresh untyped private Notice cell.
The [nullable literal-Boolean review](../../coverage/semantics/cv-nullable-literal-bool-producer-reference-notice-review.json)
keeps four fresh Notice agreements, one RECEIVE-priority and one RETURN-priority
control, six native originals once, separate author400/peer452 fixture-SL507 cuts
and the sole actual canonical load distinct. Exactly four matching current old
nullable predicates become positive without historical campaign renewal.
Non-null or wider literal-Boolean unions, broader contexts and all held lanes remain partial.

Explicit `false|null`, `null|false`, `true|null` and `null|true` formals and
returns also share that completed ordinary-CV proof. Raw two-member unions
match normalized members in source order. At this cut a literal member paired with null;
only its exact Boolean tag or NULL passes, without weak scalar coercion.
Caller reception, callee return verification, producer retirement and separate
alias/private-cell ownership retain their existing rules. The
[ordered literal/null review](../../coverage/semantics/cv-union-literal-bool-producer-reference-notice-review.json)
keeps four fresh Notice agreements and two distinct RECEIVE/RETURN-priority
controls, six native originals once, separate author487/peer532 fixture-SL507
cuts and the sole composed canonical load distinct. Four current helper files
contain five matching expectation corrections without historical campaign renewal.
Wider literal-Boolean unions and broader contexts remained partial at that cut;
all held lanes remain.

Two-member headers also admit one literal Boolean with array/int/float/string
in either source order. Exact raw/normalized order and distinctness remain;
any pair wholly drawn from bool/false/true is refused. The literal branch stays
exact, while weak conversion may select its admitted scalar alternative.
Caller-strict reception, callee-strict return verification and frame retirement
retain their existing rules. Ordinary BYREF entry conversion changes the real
caller cell without a persistent parameter constraint; BYVAL conversion preserves
the caller and its snapshot. The fresh untyped Notice cell remains separate.
The [nonnull literal-Boolean review](../../coverage/semantics/cv-nonnull-literal-bool-producer-reference-notice-review.json)
keeps native6 once/source6 (Notice4/RECEIVE1/RETURN1), separate author679/peer504
fixture-SL507 cuts and the sole composed production-SL508 load distinct. Five
current helper files contain six matching expectation corrections without
historical campaign renewal. The following increment extends the larger unions;
wider contexts and every exact held lane remain partial.

The existing ordered primitive fold also admits one `false` or `true` member
among three through six distinct builtin members. It rejects a second Boolean
kind (`bool`/`false`/`true`) and retains exact raw/normalized order and count.
Exact tag membership precedes weak scalar selection; numeric strings use their
numeric classification when both int and float occur. The existing actual
RECEIVE/RETURN, frame retirement, private-cell and payload/owner proofs remain.
The [primitive literal-Boolean review](../../coverage/semantics/cv-primitive-literal-bool-producer-reference-notice-review.json)
keeps native6 once/source6, author635 and independent466 fixture-SL507, separate
prelaw184/276 and actual009eabd9 production-SL508 loading distinct. Two current
helper files correct four matching larger-union expectations without historical
campaign renewal. Unsupported2 and the first failed619 fixture retain zero credit.
The next increment extends builtin object declarations; class names, wider
signatures, source/ownership and lifetimes remained partial at this cut.

Completed ordinary-CV producers also admit canonical `object`, raw `?object` and
ordered builtin unions containing object in their required formals and returns.
Exact raw/normalized type authority, source order/count and one Boolean kind remain; six
non-Boolean kinds plus one Boolean kind imply at most seven members. The existing
quiet `stdClass` payload, actual reception/return, frame retirement and private-cell
ownership proofs remain unchanged. BYREF reception permits later scalar rebinding;
returned objects retain their separate physical owners. The
[object-header review](../../coverage/semantics/cv-object-producer-reference-notice-review.json)
keeps native6 once/source6, author393/peer297 fixtures, prelaw139/152 and the sole
actual084e00dd49 production-SL508 load distinct. Two current helpers correct exact
object-triple expectations without historical renewal. Preserved fixture and
expectation failures remain zero credit. Class-name/callable/iterable types, wider
contexts and all exact held dependencies, including V110, remain partial.

Completed ordinary-CV producers also admit canonical fully qualified `\stdClass`
required formals and returns. The raw `NNameFullyQualified` bytes equal the sole
normalized class-name bytes before case-insensitive stdClass matching. Actual
reception/return verification, ordinary BYREF rebinding, producer retirement and
separate untyped private Notice-cell ownership retain their existing rules.
The [FQN stdClass review](../../coverage/semantics/cv-fqn-stdclass-producer-reference-notice-review.json)
keeps five native originals once (three Notice, one RECEIVE-priority and one
RETURN-priority), author295/peer156 and prelaw145/80 fixture-SL507 cuts separate
from the sole composed actual1e7ec939d SL508 load. The first peer elaboration
failure and unexecuted controller/Make recipe retain zero credit. Nullable,
union, plain/imported and wider class types, broader contexts and all exact held
dependencies remain partial; V110 gains no lifecycle or operation coverage.

Raw nullable fully qualified `?\stdClass` formals and returns also retain
exact decoded class-name bytes and exactly `[class,null]` normalized order.
Only NULL or the admitted real stdClass payload passes, without weak scalar
coercion. Ordinary BYREF rebinding, actual entry/return verification, producer
retirement and separate untyped Notice-cell ownership remain unchanged.
The [nullable FQN review](../../coverage/semantics/cv-nullable-fqn-stdclass-producer-reference-notice-review.json)
keeps native6 once/source6 (four Notice, one RECEIVE-priority and one RETURN-priority),
author403/peer303 and prelaw145/155 fixture-SL507 cuts separate from the sole
actualcc316d31b3 SL508 load. Six exact current77 header expectations are exercised
on fresh78 reached states without historical renewal. The first403 elaboration
failure and unexecuted controller/Make retain zero credit. Explicit unions,
plain/imported or wider class types and all exact held dependencies stay partial.

Explicit `\stdClass|null` and `null|\stdClass` required formals and returns
retain exactly two raw/normalized members in source order. Decoded FQN bytes
match the class branch exactly before case-insensitive stdClass matching; the
raw null Identifier casefolds to null. Actual NULL/object checks, ordinary BYREF
rebinding, producer retirement and private Notice-cell ownership stay unchanged.
The [ordered FQN/null review](../../coverage/semantics/cv-union-fqn-stdclass-producer-reference-notice-review.json)
keeps native6 once/source6 (four Notice and separate RECEIVE/RETURN priorities),
first-run author479/peer308 and prelaw145/159 fixture-SL507 cuts separate from the
sole batchcfb37f6ef SL508 load. Seven exact current78 header corrections use fresh79
states without historical renewal. Controller/Make remain unexecuted/source0;
wider class/builtin unions, plain/imported class forms and every exact hold stay partial.

Two-member unions also pair fully qualified `\stdClass` with one of `array`,
`int`, `float`, `bool`, `string`, `null`, `false` or `true`, in either source
order. Raw and normalized branches retain exact order; decoded class-name bytes
must agree before stdClass casefolding, while builtin Identifiers casefold to
their exact normalized tag. Exact class/scalar membership precedes weak scalar
conversion; strict integer-to-float promotion remains admitted. Actual reception
and return verification, ordinary BYREF rebinding, producer retirement and the
fresh untyped private Notice cell retain their existing rules. The
[FQN/builtin review](../../coverage/semantics/cv-builtin-fqn-stdclass-producer-reference-notice-review.json)
keeps eight native originals once/source8 (six Notices and separate RECEIVE/RETURN
priorities), author461/peer770 and genuine prelaw209/267 fixture-SL507 cuts
separate from the actual `79e3f78b48` production-SL508 load. The first source
setup failure retains zero credit; controller/Make remain unexecuted/source0.
Larger class unions, other class forms, Stringable callbacks, wider contexts and
every exact held dependency remain partial.

Ordered FORMAL/RETURN unions of three through seven members also admit exactly
one raw fully qualified `\stdClass` and two through six distinct members from
`array`, `int`, `float`, `bool`, `string`, `null`, `false` and `true`. Only one
Boolean kind is allowed. Exact raw/normalized order and decoded class bytes remain
required; actual reception/return, frame retirement, private-cell, payload and
owner/lifetime rules stay unchanged. The
[larger FQN/primitive review](../../coverage/semantics/cv-primitive-fqn-stdclass-producer-reference-notice-review.json)
keeps native8 once/source8 (six Notices and separate RECEIVE/RETURN priorities),
author501/peer869 and genuine prelaw201/273 fixture-SL507 cuts separate from the
sole actual `7ff30694c0` production-SL508 load. Controller/Make remain unexecuted
with source credit zero. Other class forms, Stringable callbacks, wider contexts
and every exact held dependency, including V110, remain partial.

Canonical standalone `callable` formals and returns also admit existing registered
USER-function name strings, preserving casefolding and an optional leading
backslash without invoking the target. Ordinary BYREF reception adds no persistent
cell constraint. Actual type verification, producer retirement, authentic
non-NUL INTERNED/REQUEST carriers and separate private Notice-cell owners retain
their existing rules. The
[callable review](../../coverage/semantics/cv-callable-producer-reference-notice-review.json)
keeps native6 once/source6 (four Notices and separate RECEIVE/RETURN priorities),
author366/peer249 and genuine prelaw182/138 fixture-SL507 cuts separate from the
sole actual `7abd726dd5` production-SL508 load. Original fixture failures and
diagnostics retain zero credit; controller/Make remain unexecuted/source0.
Nullable/union headers, wider callable forms, contexts and lifetimes remain
partial at this cut; every exact held dependency stays unchanged.

Raw `?callable` required formals and returns retain exactly `[callable,null]`
normalized order and Identifier casefolding. NULL passes directly; the existing
registered USER-name string checks retain authenticated carriers without target
invocation. Ordinary BYREF body writes, actual reception/return checks, producer
retirement and the separate untyped private Notice cell keep their existing rules.
The [nullable callable review](../../coverage/semantics/cv-nullable-callable-producer-reference-notice-review.json)
keeps native6 once/source6 (four Notices and separate RECEIVE/RETURN priorities),
author366/peer252 and genuine prelaw169/136 fixture-SL507 cuts separate from the
sole actual `6baec57dcf` production-SL508 load. Two exact REF82 helper promotions
use fresh REF83 reached states without historical renewal. Controller/Make remain
unexecuted/source0. Explicit unions, wider callable forms, contexts and lifetimes
remain partial; every exact held dependency stays unchanged.

Explicit `callable|null` and `null|callable` required formals and returns also
retain exactly two raw Identifiers and normalized branches in the same order.
Casefolding, actual NULL/name verification, ordinary BYREF body writes, producer
retirement and separate private Notice-cell ownership keep their existing rules.
The [ordered callable/null review](../../coverage/semantics/cv-union-callable-producer-reference-notice-review.json)
keeps native6 once/source6 (four Notices and separate RECEIVE/RETURN priorities),
author408/peer272 and genuine prelaw175/139 fixture-SL507 cuts separate from the
sole actual `871aa5f5bd` production-SL508 load. Exact promotions in three old
helper files use fresh REF84 states without historical renewal. Derived-control
bindings were corrected before the first full run. Controller/Make remain
unexecuted/source0. Other callable unions, forms, contexts and lifetimes remain
partial; every exact held dependency stays unchanged.

Ordered `callable|string` and `string|callable` required formals and returns also
retain exact raw/normalized order. Exact string membership bypasses callable
lookup; weak integer returns create authenticated REQUEST strings before frame
retirement and private Notice-cell allocation. Ordinary BYREF body writes remain
unconstrained. The [string/callable review](../../coverage/semantics/cv-string-callable-producer-reference-notice-review.json)
keeps native6 once/source6 (Notice4/RECEIVE1/RETURN1), author419/peer319 and
genuine prelaw191/144 fixture-SL507 cuts separate from actual `258e1d27c7` and
its sole production-SL508 load. Two REF84 helpers promote only exact string-pair
expectations using fresh states. Two elaboration-only failures remain preserved
at zero credit; controller/Make remain unexecuted/source0. Wider callable unions,
forms, contexts, lifetimes and every exact held dependency remain partial.

Ordered `callable|int` and `int|callable` required formals and returns retain the
same raw/normalized authority. Exact integers bypass callable lookup; registered
USER names precede weak numeric-string integer conversion. BYVAL preserves the
caller snapshot; ordinary BYREF conversion changes the shared cell without a
persistent constraint. Return checks and frame retirement still precede separate
private Notice cells. The [integer/callable review](../../coverage/semantics/cv-int-callable-producer-reference-notice-review.json)
keeps native6 once/source6 (Notice4/RECEIVE1/RETURN1), author544/peer292 and genuine
prelaw220/135 fixture-SL507 cuts separate from actual `d92a64df05` and its sole
production-SL508 load. Four current helper files promote only exact int-pair
expectations using fresh states. The first author elaboration failure remains
zero credit; controller/Make remain unexecuted/source0. Wider callable unions,
forms, contexts, lifetimes and every exact held dependency remain partial.

Ordered `callable|float` and `float|callable` required formals and returns retain
that raw/normalized authority. Exact FLOATs bypass callable lookup; registered
USER names precede weak numeric-string conversion, while strict integers retain
PHP's FLOAT widening exception. Caller snapshots, transient ordinary BYREF writes,
return checks, producer retirement and separate private Notice cells stay intact.
The [float/callable review](../../coverage/semantics/cv-float-callable-producer-reference-notice-review.json)
keeps native6 once/source6 (Notice4/strict RECEIVE1/RETURN1), author538/peer304 and
genuine prelaw220/135 fixture-SL507 cuts separate from actual `7619c8d7c8` and its
sole production-SL508 load. The precise peer86 helper promotions use fresh states;
all REF87 runs pass first time. Controller/Make remain unexecuted/source0. Wider
callable unions, forms, contexts, lifetimes and every exact held dependency remain
partial.

Ordered `callable|bool` and `bool|callable` required formals and returns also
retain exact raw/normalized order. BOOL supplies both Boolean bits: exact Booleans
bypass callable lookup; registered USER names precede weak scalar truth conversion.
Strict scalar mismatches reject. BYVAL snapshots, ordinary transient BYREF writes,
producer retirement and separate private Notice-cell ownership stay intact.
The [Boolean/callable review](../../coverage/semantics/cv-bool-callable-producer-reference-notice-review.json)
keeps native6 once/source6 (Notice4/strict RECEIVE1/RETURN1), author556/peer338 and
genuine prelaw220/135 fixture-SL507 cuts separate from actual `05864a15d8` and its
sole production-SL508 load. Twelve precise helper promotions use fresh states.
The first author front's wrong REQUEST identity for `(string)0` stays zero credit;
only carrier metadata/fixture expectations changed, preserving PHP/native bytes.
Controller/Make remain unexecuted/source0. Wider callable unions, forms, contexts,
lifetimes and every exact held dependency remain partial.

Ordered `callable|true`/`true|callable` and `callable|false`/`false|callable`
required formals and returns retain the same exact raw/normalized authority.
Exact singleton Booleans bypass callable lookup; registered USER names remain
callable, while opposite Booleans and other scalar mismatches reject in both
strict modes. Ordinary transient BYREF writes, producer retirement and separate
unconstrained private Notice cells retain their existing bounds. The
[literal-Boolean/callable review](../../coverage/semantics/cv-literal-bool-callable-producer-reference-notice-review.json)
keeps native6 once/source6, author741/peer371 and genuine prelaw217/131
fixture-SL507 cuts separate from actual `2ad613104c` and its sole production-SL508
load. Controller/Make remain unexecuted/source0; wider forms and exact holds stay
partial.

Canonical runtime `iterable` parameters and returns now accept arrays and modeled
Traversable objects, including fresh named Generators and inherited USER Iterators.
Nullable and ordered-union checks preserve identity and strictness. The compiler
whitelist and existing pointwise class view authenticate the alias without invoking
Iterator methods or Generator bodies. The [runtime iterable review](../../coverage/semantics/runtime-iterable-alias-review.json)
keeps native3+3 once/source6, author253/peer251 fixture-SL507 and prelaw104/102
separate. Initial Unsupported and gate-only wrong NORMAL/TypeError cuts retain0.
Actual2a4c9b927 and its sole production-SL508 load pass16.592779634s/source0,
independently closed. Other Notice-producer iterable headers, wider producers,
protocol execution and lifetimes remain partial;90/207/138, typed calls, ownership
and every exact hold are unchanged. The private controller packet passed; the Make
target and joined source replay remain unexecuted. Metadata adds no source credit.

Completed one-CV producers now admit a canonical bare `iterable` return across
all previously admitted required fixed formal shapes. Exact raw/normalized return
authority reuses the existing argument proof; return verification and frame
retirement precede finite array Notice operands and separate unconstrained private
cells. The [singleton iterable-return review](../../coverage/semantics/singleton-cv-iterable-return-producer-reference-notice-review.json)
keeps native4+3 once/source7 (five admissions/two priority controls), author308 and
corrected peer230 fixture-SL507 cuts separate. The first controller exit1 and peer
fixture failure remain0; only that fixture changed to prove its authentic retained
literal-pool root, preserving private-cell retirement. Actuale81b75b3 and its sole
production-SL508 load pass16.186114022s/source0, independently closed. Nullable,
union and multiple-CV iterable returns, new iterable formals, Traversable Notice
payloads, wider lifetimes and exact holds remain partial. Make/joined source
replay remain unexecuted; metadata adds no source credit.

Completed one-CV producers also admit raw `?iterable`, `iterable|null` and
`null|iterable` returns over the existing required formal shapes. Exact normalized
order, return verification and frame retirement precede finite array/NULL Notice
operands and separate unconstrained private cells. The
[nullable iterable-return review](../../coverage/semantics/singleton-cv-nullable-iterable-return-producer-reference-notice-review.json)
retains accepted native4+3 once/source7 (five admissions/two priority controls),
author327/peer240 fixture-SL507 and the READY `3ab066f12` source signature.
Actual `734571e0c` composition and the sole joined `0d0f5d75b` SL508 load
(16.642528873 s/source0) are independently clear and retain separate cuts. Metadata adds no execution credit. Multiple-CV iterable
returns, new iterable formals, Traversable Notice payloads, wider lifetimes and
every exact hold remain partial at this cut.

Canonical bare `iterable` required formals also use the completed one-CV route.
Raw Identifier casefolding agrees pointwise with the normalized builtin tag;
ordinary CV, BYREF, required/default and nonvariadic guards remain. Genuine
Generator inputs stay retained by outside caller roots and return NULL before the
Notice; their bodies remain unentered. Array/NULL Notice payloads, actual return
verification, producer retirement and separate private cells keep their bounds.
The [iterable-formal review](../../coverage/semantics/singleton-cv-iterable-formal-producer-reference-notice-review.json)
binds native4+3 once/7 unique originals to author and independent whole packets,
with separate author326/peer283 fixture-SL507 suites. Prelaw fronts174/143,
the initial Unsupported source and two binding diagnostics retain zero credit.
Actual `6e59bd311` composition and its sole SL508 load17.034237165s/source0
are independently clear and retain separate cuts. Nullable/union
and multiple-CV iterable formals are extended below. Ordered multiple-CV iterable returns,
Traversable Notice payloads, wider producers/lifetimes and every exact hold remain partial.

Raw `?iterable`, `iterable|null` and `null|iterable` required one-CV formals now
retain canonical nullable order or exact ordered raw/normalized pairs. Two
dedicated argument arms preserve the shared multi-CV lists and existing default,
source, return, payload and ownership guards. Array, NULL and genuinely retained
Generator inputs preserve ordinary BYREF writes and separate private Notice cells;
Generator bodies stay unentered. The
[nullable/ordered iterable-formal review](../../coverage/semantics/singleton-cv-nullable-iterable-formal-producer-reference-notice-review.json)
binds native4+3 once/7 unique originals to independent whole packets and separate
352/292 fixture-SL507 suites. Prelaw fronts179/150 and first-source Unsupported
retain zero credit; no new failures occur. One prior derived nullable-header
control is promoted using current reached states, without historical replay.
Actual `045573120` and sole joined `d124d90a` SL508 loading
(16.332717621 s/source0) are independently clear and remain separate from
the original source and fixture cuts.
Multiple-CV iterable formals are extended below. Iterable returns with multiple
CVs, Traversable Notice operands, wider headers, owners/lifetimes and every exact
hold remain partial.

Multiple required ordinary-CV formals can now include raw bare `iterable`
Identifiers, authenticated against normalized builtin tags by the existing
pointwise fold. Mixed positions and duplicate CVs preserve BYREF/BYVAL reception,
array COW, retained Generator identity, return verification and producer retirement.
Generator bodies stay unentered; finite array/NULL Notice payloads retain separate
private cells. Multiline originals retain the argument-list line through existing
compiler metadata, distinct from the final physical CV line. The
[multiple-CV iterable-formal review](../../coverage/semantics/multi-cv-iterable-formal-producer-reference-notice-review.json)
records seven originals, native4+3 once and separate 451/345 fixture-SL507 suites.
The first Unsupported source, original line-expectation failure and stale literal
occurrence assertion remain separate zero-credit cuts; the fixture correction
reruns only its affected suite. Bare duplicated argument controls are promoted;
canonical nullable and ordered duplicated formals are extended below;
bare and canonical nullable multi-CV iterable-return headers are extended below; ordered returns remain partial.
Wider headers, Traversable Notice operands, owners/lifetimes and exact holds remain partial.

Canonical raw `?iterable` required formals now also use the multiple-CV fold.
Exact normalized `[iterable, null]` order, raw Identifier casefolding and the
existing required, BYREF, nonvariadic, source, return and ownership guards remain.
Genuine NULL, array and retained Generator inputs preserve caller/formal identity,
array COW, receive-error priority, producer retirement and separate private Notice
cells; Generator bodies stay unentered. The
[multiple-CV nullable iterable-formal review](../../coverage/semantics/multi-cv-nullable-iterable-formal-producer-reference-notice-review.json)
records native4+3 once, seven source originals and separate 459/367 fixture-SL507
suites. Prelaw fronts269/205 and first-source Unsupported keep zero credit.
Canonical nullable duplicated/forged argument controls are promoted; the ordered
counterparts are extended below without replaying older campaigns. Ordered
multiple-CV iterable returns, broader headers, Traversable Notice operands, owners/lifetimes
and all exact holds remain partial.

Exact raw two-member `iterable|null` and `null|iterable` required formals now use
that multiple-CV fold through one dedicated arm. The existing generic union lists
stay unchanged. Pointwise raw/normalized order, Identifier casefolding, BYREF and
required/nonvariadic guards preserve mixed positions and duplicate CVs. Array,
NULL and retained Generator inputs preserve return checks, producer retirement,
COW and separate private Notice cells; Generator bodies stay unentered.
The [ordered-null multiple-CV iterable-formal review](../../coverage/semantics/multi-cv-union-null-iterable-formal-producer-reference-notice-review.json)
records native4+3 once, seven source originals and separate author505/peer381
fixture-SL507 suites in both independently passed whole packets. Prelaw fronts
273/205, first-source Unsupported and the literal projection comparison failure
keep zero credit. Only five affected older fixture bridges and the Makefile entry
change alongside the new tests; historical campaigns are not renewed. Wider
iterable unions, ordered multiple-CV iterable returns, headers, Notice
payloads, owners/lifetimes and every exact hold remain partial.

Bare `iterable` returns now authenticate for completed multi-CV producers through
the existing required ordinary-CV formal fold. Exact raw Identifier casefolding,
one normalized return branch, pointwise BYREF and ordinary return verification
preserve frame retirement before private Notice-cell creation. Seven originals
cover alias/COW, retained Generator inputs returning arrays, handler throws and
return/receive-error priority. The
[multiple-CV iterable-return review](../../coverage/semantics/multi-cv-iterable-return-producer-reference-notice-review.json)
binds native4+3 once, retained author source7/fixture442, corrected peer fixture399
and an independent full source7/442/399 packet. The first peer-fixture failure and
prelaw Unsupported remain separate zero-credit cuts; only that affected suite
reran. Ordered returns, Traversable Notice operands, wider headers, payloads
and lifetimes remain partial; every exact hold stays unchanged.

Canonical raw `?iterable` returns now also authenticate for those completed
multi-CV producers, with exact normalized `[iterable, null]` order. The existing
formal fold, return verification, frame retirement and private-cell/payload guards
remain. Array and NULL results preserve identity and error priority; retained
Generator inputs stay unentered. The
[multiple-CV nullable iterable-return review](../../coverage/semantics/multi-cv-nullable-iterable-return-producer-reference-notice-review.json)
records native4+3 once and two independently passed source7/fixture463/395 packets.
At that cut, five canonical-only fixture bridges retain ordered-return refusals.
Prelaw Unsupported and the corrected pure preparation assertion keep zero credit.
Wider return unions, headers, payloads and lifetimes remain partial; every exact
hold stays unchanged.

Exact raw two-member `iterable|null` and `null|iterable` returns now also
authenticate for those completed multi-CV producers through a dedicated header
arm. Matching ordered normalized singleton branches and raw Identifier
casefolding reuse the existing required ordinary-CV argument proof. Return
verification, frame retirement and private Notice-cell/payload guards remain.
Seven originals cover alias/COW, NULL results, unentered retained Generator
inputs, handler throws and receive/return-error priority. The
[ordered-null multiple-CV iterable-return review](../../coverage/semantics/multi-cv-union-null-iterable-return-producer-reference-notice-review.json)
records native4+3 once and two independently passed source7/fixture497/409
packets. Prelaw fronts259/207 and the first source Unsupported keep zero credit.
Six scoped older fixture bridges and the Makefile entry accompany the new tests;
generic union lists remain unchanged. Other iterable unions, wider headers,
payloads, lifetimes and every exact hold remain partial.

Exact raw two-member `iterable|int` and `int|iterable` returns now authenticate
for completed multi-CV producers through a separate dedicated arm. Matching
ordered normalized branches and Identifier casefolding reuse the existing
required ordinary-CV formal proof. Weak numeric-string returns become integers
before private Notice-cell creation while caller values remain unchanged;
the returned alias has no persistent return-type constraint. Strict return
rejection precedes the outer Notice and assignment. The
[multiple-CV integer/iterable-return review](../../coverage/semantics/multi-cv-union-int-iterable-return-producer-reference-notice-review.json)
records native4+3 once and two independently passed source7/fixture525/285
packets. Prelaw fronts260/172, the first source Unsupported and the corrected
peer-fixture failures keep zero credit. Only two older fixture bridges for
matching integer-pair HEADERs and the Makefile entry change alongside the new tests; generic
union lists and all return/frame/private-cell/payload guards remain. At that cut,
the one-CV counterpart, other partners, wider headers and lifetimes remain partial;
every exact hold stays unchanged.

One-CV producers now also admit exact raw `iterable|int` and `int|iterable`
returns through the same ordered-pair arm. Generic singleton formal fallback
excludes exactly normalized `[iterable]`, `[iterable, null]` and
`[null, iterable]`; their dedicated raw bare, nullable and ordered checks remain
the sole routes. A genuine nullable-union source exposed their previous overlap.
Four source-reached derived checks cover those raw forms under SL determinism.
The [single-CV integer/iterable-return review](../../coverage/semantics/singleton-cv-union-int-iterable-return-producer-reference-notice-review.json)
records native4+3 once and two independently passed source7/fixture388/256
packets, including weak conversion, strict rejection, alias/COW and throw cleanup.
Author front182, the incomplete peer-front failure and both first-source
Unsupported results keep zero credit. One older singleton HEADER bridge and
the Makefile entry accompany the new tests. Existing zero-argument admission,
generic union lists and private-cell/payload/owner bounds remain unchanged.
Other partners, wider headers and lifetimes remain partial; every exact hold
stays unchanged.

Exact FQN stdClass/callable unions of two through eight members also admit
required ordinary-CV producer formals and returns. Raw/normalized class bytes,
case-folded stdClass identity, member order, unique builtins, one class and at
most one Boolean kind remain required; builtin object stays excluded.
The [FQN class/callable review](../../coverage/semantics/cv-fqn-stdclass-callable-union-producer-reference-notice-review.json)
keeps native6 once/source6, author437/peer218 and genuine prelaw247/102 separate.
Six precise helper shapes use fresh93 states. Actualb2f2e9497ce and its sole
production-SL508 load pass in16.240492338s/source0, independently closed.
Controller/Make remain unexecuted/source0; wider class spellings, contexts and
every exact hold stay partial.

Exact ordered FQN `stdClass`/`iterable` unions of two through eight members also
admit fixed required ordinary-CV formals. The unchanged structural return fold
preserves decoded class bytes, raw/normalized order, unique permitted builtins and
one Boolean kind. Pointwise BYREF, ordinary-CV/source authority, actual reception
and return verification, frame retirement and finite private Notice-cell bounds
remain required. The [formal-union review](../../coverage/semantics/cv-fqn-stdclass-iterable-formal-producer-reference-notice-review.json)
keeps seven native originals once and separate author/independent source7 with
942/759 fixture-SL507 cuts distinct from the actual composition and sole joined
production-SL509 load. Original fixture failure, Unsupported and unrun cuts retain
zero credit. Wider class names, Traversable Notice payloads and lifetimes remain
partial; every exact hold stays unchanged.

Fixed required ordinary-CV formals also admit exact ordered builtin unions of two
through eight members containing `iterable`. Raw Identifier order/count, unique
permitted builtins, one Boolean kind and pointwise Param/BYREF authority remain
required. Explicit normalized exclusions preserve the existing nullable-pair arm;
the FQN class fold and RETURN/runtime/payload/owner/lifetime rules stay unchanged.
The [builtin formal-union review](../../coverage/semantics/cv-builtin-union-iterable-formal-producer-reference-notice-review.json)
keeps native7 once and separate author/independent source7 with891/782 fixture-SL507
cuts distinct from actual composition and its sole joined production-SL509 load.
Prelaw front254/271 and first Unsupported/other unrun cuts retain zero source
credit. Wider headers, actual forms, payloads and lifetimes remain partial; all
exact holds stay unchanged.

Global producer declarations without class imports also admit a bare `stdClass`
RETURN name. The scoped header uses the producer's retained declaration
environment, exact decoded raw/normalized class bytes and case-folded `stdClass`
identity. Both Notice ingress sites reuse the existing required ordinary-CV
argument proof, return verification, frame retirement and private-cell bounds.
The [plain-name return review](../../coverage/semantics/global-plain-stdclass-return-producer-reference-notice-review.json)
records the source and state evidence. Scoped singleton RETURNs are extended below;
plain formal names, other explicit union plain returns and wider payload/lifetime
histories remain partial; the older context-independent header stays unchanged.

Nullable bare `?stdClass` RETURN names use the same bounded declaration context.
Exact decoded class bytes and normalized class-then-null order retain ordinary
return verification before producer-frame retirement. Object identity and NULL
results cross named/positional Notices through fresh unconstrained private cells;
handler caller rebinding and later private scalar writes remain separate.
The [nullable plain-name return review](../../coverage/semantics/global-plain-nullable-stdclass-return-producer-reference-notice-review.json)
records the source and state evidence; other explicit unions, wider contexts, payloads
and lifetimes remain partial.

Bare `stdClass|null` and `null|stdClass` RETURN unions retain exact raw member
order and normalized class/null identities in that same declaration context.
Each member authenticates its decoded bytes before the existing ordinary-CV
argument proof, return verification, frame retirement and private Notice cell.
The [ordered null-union return review](../../coverage/semantics/global-plain-union-null-stdclass-return-producer-reference-notice-review.json)
records the source and state evidence. Other unions, plain formals, wider
contexts, payloads and lifetimes remain partial.

Bare `stdClass|int` and `int|stdClass` RETURN unions share the same declaration
context and exact raw/normalized member authentication. The existing verifier
preserves ordinary object identity or a verified INT result before frame retirement;
later private-cell writes remain unconstrained by the producer's return type.
The [ordered int-union return review](../../coverage/semantics/global-plain-union-int-stdclass-return-producer-reference-notice-review.json)
records the source and state evidence. Wider unions, plain formals, namespace/import
contexts, payloads and lifetimes remain partial.

Bare `stdClass|float` and `float|stdClass` RETURN unions retain the same global
declaration context and exact ordered member authentication. Matched objects
retain identity, while verified FLOAT results include strict INT-to-FLOAT widening
and quiet weak scalar conversion before frame retirement and private Notice cells.
The [ordered float-union return review](../../coverage/semantics/global-plain-union-float-stdclass-return-producer-reference-notice-review.json)
records the source and state evidence. Other unions, plain formals, namespace/import
contexts, payloads and lifetimes remain partial.

Flat ordered bare-`stdClass` RETURN unions reuse that same global context.
A pure raw-shape view preserves member bytes, order and metadata, changes exactly
one bare class tag to the existing fully qualified shape, then delegates to the
established header proof. Its distinct builtin and Boolean-kind checks and separate
array/iterable folds retain their existing bounds; FORMAL and lifetime rules stay.
The [ordered plain-union review](../../coverage/semantics/global-plain-ordered-stdclass-return-producer-reference-notice-review.json)
records scalar priority, object identity, runtime-array COW and private Notice cells.
Wider class names, declaration contexts, payloads and lifetimes remain partial.

Singleton ordinary `NName` RETURN aliases also use their declaration namespace
and class imports when quiet builtin-first resolution yields exact global
`stdClass`. The existing Param-view recursion runs first; the RETURN arm requires
an unchanged parameter vector, nonempty declaration context and actuals, and the
exact canonical normalized singleton RETURN. It changes only the proof name and
tag, retaining metadata and delegating to the existing FQN header. The original
source, independent RETURN verification, frame retirement and private Notice-cell
ownership retain their rules. Exact RETURN and actual-count guards separate the
new arm from existing helper success with empty normalized RETURN types or zero
actuals.
The [scoped singleton-return review](../../coverage/semantics/scoped-stdclass-return-producer-reference-notice-review.json)
separates fresh object BYVAL and multiple-BYREF originals with FQN formal
isolators from a combined FORMAL/RETURN alias original and the unchanged NULL
TypeError-before-Notice control. Four native originals ran once; author source2
and state340, independent whole4 with state340/191, and the fixed production
load retain separate identities. One emitted-name compiler rejection and two
reader preparation assertions keep zero credit. Scoped nullable, ordered union
and empty-namespace relative singleton RETURNs are extended below; wider relative
contexts, other classes, payloads and lifetime histories remain partial, with all
exact holds unchanged.

Nullable `?Alias` RETURNs use the same quiet declaration resolution to exact
global `stdClass`, after the existing Param-view recursion. The new arm requires
an unchanged parameter vector, nonempty declaration context and actuals, and
exact canonical `[class, null]` normalized order. Its proof view preserves both
nullable/name metadata nodes before the existing FQN nullable header; independent
RETURN verification, frame retirement and private Notice-cell ownership stay.
The [scoped nullable-return review](../../coverage/semantics/scoped-nullable-stdclass-return-producer-reference-notice-review.json)
separates object and successful NULL isolators from a combined nullable
FORMAL/RETURN alias original and an unchanged scalar TypeError-before-Notice
control. Native4 ran once. Author source2/state357 and independent source4/state357
remain accepted; the first independent WHOLE retains its peer fixture compiler
rejection/runtime UNRUN0, followed only by corrected peer192. No first-WHOLE-pass
claim or accepted-source/native/author replay is made. Older pure helper
expectations in three files promote through fresh nullable/self-import proofs
without renewing their historical executions. Scoped ordered unions are extended
below; relative RETURNs, other resolved classes and wider payloads/owners/lifetimes
remain partial, with exact holds unchanged.

Flat ordered RETURN unions authenticate exactly one ordinary class name in its
declaration `PTRETURN` context, resolving quietly to canonical global `stdClass`.
A dedicated member view preserves raw order, every Identifier and all member/union
metadata before the existing FQN folds. Those folds retain their two-through-eight
member bounds, distinct builtin kinds, one Boolean kind and separate array/iterable
paths. Nonempty declaration context, actuals and normalized RETURN, together with
an unchanged Param vector, preserve Param-first normalization and disjointness
from the generic helper. Independent RETURN verification, retirement, private
Notice-cell ownership and payload bounds retain their existing rules.
The [scoped ordered-return review](../../coverage/semantics/scoped-ordered-stdclass-return-producer-reference-notice-review.json)
keeps fresh object, NULL and scalar-to-STRING isolators separate from the combined
opposite-order FORMAL/RETURN union original and unchanged TypeError control.
Native5 ran once; author source3/state729 and first independent WHOLE5 with
state729/200 retain separate SL507 cuts. The earlier peer prelaw summary corrected
only its label from86 to the already-passing raw88, with zero new runtime credit.
Pure future-helper expectations in eleven files promote through fresh alias and
self-import proofs, without renewing historical executions. Multiple nominals,
relative/DNF forms, other resolved classes and wider payloads/owners/lifetimes
remain partial; exact holds stay unchanged.

An empty declaration namespace also admits the singleton relative RETURN
`namespace\stdClass`. Quiet `PTRETURN`/`PTRELATIVE` resolution authenticates exact
canonical normalized `stdClass` before the existing FQN header, preserving the
name metadata. Relative resolution ignores class imports, including a conflicting
ordinary-name alias. Nonempty actuals and an unchanged Param view retain the
existing normalization order and generic-helper disjointness. Independent RETURN
verification, frame retirement and private Notice-cell ownership remain unchanged.
The [relative-return review](../../coverage/semantics/relative-stdclass-return-producer-reference-notice-review.json)
records native4 once, author source2/state333, retained independent source4/state333
and corrected peer181. The original WHOLE peer fixture compiler rejection retains
runtime UNRUN0; only its two negative-control metadata bindings were corrected and
the affected peer suite rerun. There is no first-WHOLE-pass claim or source/native/
author replay. Two older canonical relative helper expectations promote through
fresh import-ignorance and Param-first proofs without renewing their campaigns.
Nullable and two-member class/null relative RETURNs are extended below; other
relative unions, nonempty namespaces, other normalized classes and wider payloads/
owners/lifetimes remain partial; exact holds stay unchanged.

Nullable `?namespace\stdClass` RETURNs use the same empty declaration namespace
and quiet `PTRETURN`/`PTRELATIVE` authentication, ignoring ordinary class imports.
Exact canonical `[class, null]` order and the unchanged Param view retain the
existing normalization order and generic-helper disjointness. The FQN nullable
proof preserves both metadata nodes; independent RETURN verification, producer
frame retirement and private Notice-cell ownership keep their existing rules.
The [nullable relative-return review](../../coverage/semantics/relative-nullable-stdclass-return-producer-reference-notice-review.json)
separates object BYVAL and multiple-NULL BYREF formal isolators from an independent
named-BYREF formal-alias interaction and the unchanged scalar-return TypeError
control. Native4 ran once; author source2/state337 and the first independent
WHOLE source4 with state337/184 pass in separate SL507 cuts. Genuine prelaw158/84
and the first Unsupported observations retain zero source credit. Three older
canonical nullable-relative helper expectations promote through fresh import,
Param-first and metadata proofs without renewing their historical campaigns.
Two-member class/null relative unions are extended below; other relative unions,
nonempty namespaces, other normalized classes and wider payloads/owners/lifetimes
remain partial; all exact holds stay unchanged.

Ordered `namespace\stdClass|null` and `null|namespace\stdClass` RETURNs use
separate exact two-member proof cases under the same empty declaration namespace.
Each authenticates the matching canonical normalized order, ignores class imports
and retains Param-first normalization before the existing FQN ordered-union
delegate. Both member metadata nodes and the union metadata remain intact;
RETURN verification, frame retirement and private Notice-cell owners keep their
existing rules.
The [ordered relative class/null review](../../coverage/semantics/relative-union-null-stdclass-return-producer-reference-notice-review.json)
keeps the object BYVAL source and the NULL-return source with two CV actuals and
an ordinary BYREF formal separate from the independent named-BYREF formal alias
and unchanged scalar-return TypeError control. Native4 ran once; author source2/
state339 and the first independent
WHOLE source4 with state339/194 pass in separate SL507 cuts. Prelaw158/85 and the
first Unsupported observations retain zero source credit. Five older helper
expectations promote through fresh order/import/Param/metadata proofs without
renewing117/130/131 campaigns. Two author preparation assertions and one cached
reader schema correction retain runtime0; fixture and production code needed no
correction. Ordered class/int relative companions are extended below; other
builtin companions, wider unions, nonempty namespaces, other normalized classes
and wider payloads/owners/lifetimes remain partial; all exact holds stay unchanged.

Ordered `namespace\stdClass|int` and `int|namespace\stdClass` RETURNs extend
those two proof cases with the exact `null`/`int` builtin choice. Empty namespace,
quiet `PTRETURN`/`PTRELATIVE` resolution, matching canonical order and unchanged
Param normalization preserve import ignorance and all raw member/union metadata.
The existing FQN verifier, callee retirement and private Notice-cell owners remain.
The [ordered relative class/int review](../../coverage/semantics/relative-union-int-stdclass-return-producer-reference-notice-review.json)
separates object BYVAL and strict INT/private-array originals from the independent
named-BYREF formal alias and unchanged array-return TypeError-before-Notice
control. Native4 ran once; author source2/state408(298+110), independent source4/
author408 and corrected peer202(123+79) retain separate SL507 cuts. Prelaw212/85
and three original Unsupported observations retain zero source credit. The
original WHOLE peer202 attempted execution and failed a weak-conversion descriptor
expectation; its zero-credit nonpass remains, and only the corrected peer suite
reran. No first-WHOLE-pass claim or accepted source/author/native replay is made.
Two older pure-helper files promote through fresh133 proofs without renewing
117/132 campaigns. Syntax, cached Make-literal reader and documentation-parent preparation
incidents retain runtime0; the PHP law needed no correction. Fixed actuala780c163
and sole productionSL509 pass16.282008996931836s/cap60/source0 through one physical
report/map read each/cache thereafter; author raw reads0. Further relative unions
are extended below; wider namespaces/classes/payloads/owners/lifetimes remain
partial, with all exact holds unchanged.

Flat relative RETURN unions extend the earlier null/int cases to exactly one
canonical `namespace\stdClass` plus compatible builtin Identifier members. A
relative-only view resolves the class through quiet `PTRETURN`/`PTRELATIVE`,
ignores ordinary imports and preserves ordered fields and metadata before the
unchanged two-through-eight-member FQN folds. Empty namespace, nonempty actuals
and RETURN, unchanged Param normalization, verification, retirement and private
Notice-cell guards remain. The two older narrow arms are replaced to keep
success disjoint; plain and scoped views stay literal.
The [flat relative-union review](../../coverage/semantics/relative-ordered-stdclass-return-producer-reference-notice-review.json)
records native5 once, author source5/state667(465+202), independent source5 and
corrected affected107(69 frozen-context+38 fresh) at separate SL507 cuts. The
original WHOLE704 failed a derived alias formal-TYPE expectation and retains
zero credit; its exact class-byte mismatch is now an explicit rejection. Only
the affected fixture reran. Promoted old helper expectations are checked at
fresh134 cuts without historical renewal. Fixed actual74cb32567 and the sole
productionSL509 load pass16.943231401965022s/cap60/source0 via immutable8039655e,
with original actual/report/map read once and author raw reads0. Other classes,
nonempty namespaces, multiple nominals, DNF and wider owners/lifetimes remain
partial; all exact holds remain unchanged.

Canonical bare `namespace\stdClass` FORMALs now use a quiet
`PTPARAMETER`/`PTRELATIVE` raw Param view under an empty declaration namespace.
Ordinary class imports are ignored, while all other fields and metadata remain.
The existing empty-environment header composes the global Param view before the
scoped view, preserving old plain class bytes and disjoint success. Reception,
ordinary BYREF rebinding, FQN RETURN verification, retirement and private Notice
cells keep their existing rules. The
[relative-FORMAL review](../../coverage/semantics/relative-stdclass-formal-producer-reference-notice-review.json)
records native2 once, author source2/state416(266+150) and the first independent
source2/WHOLE442(266+150+26) at separate SL507 cuts. Fresh controls distinguish
mixed plain/Relative exact class spellings, import authority and Relative RETURN
composition; one old130 helper expectation promotes without historical renewal.
Prelaw204 and Unsupported1 retain source0; one static-slicer preparation retains
runtime0. Fixed actual36976c9a and the sole productionSL509 load pass
16.137139399070293s/cap60/source0 through immutable498f8bc6, with original
projection/report/map read once and author raw reads0. Nullable/union relative
formals are extended below; other classes/namespaces and wider owners/lifetimes
remain partial, with all exact holds unchanged.

Nullable and flat ordered canonical Relative FORMALs extend the bare case.
Nullable mapping delegates the quiet bare `PTPARAMETER`/`PTRELATIVE` proof; a
separate relative-only union view preserves exactly one nominal and all literal
Identifier fields before the unchanged two-through-eight-member FQN Param folds.
Both metadata levels, empty namespace, import ignorance and existing header
composition/reception/RETURN/retirement/private-cell guards remain. The
[nullable/ordered relative-FORMAL review](../../coverage/semantics/relative-nullable-ordered-stdclass-formal-producer-reference-notice-review.json)
records native4 once, author source4/state968(546+422) and independent
source4/first-post-WHOLE1009(546+422+41) at separate SL507 cuts. A source types the
already-NULL first argument and links its real receive0 to object/BYREF receive1;
other fresh controls cover scalar priorities, order, compatibility and view
refusals. Original prelaw422 fixture failure0 and corrected422 pass are distinct;
only the inherited generator spelling context was corrected. Unsupported1 retains
source0. Four old135 view expectations promote while stale bare-TYPE header
refusals stay literal, without135 renewal. Joined actual331d9f3f and the sole
productionSL509 load pass16.792141664074734s/cap60/source0 through immutable4def1b5d,
with original projection/report/map read once and author raw reads0. Other
spellings/classes/namespaces, mixed nominals, DNF and wider owners/lifetimes remain
partial; all exact holds remain unchanged.

Relative `stdClass` case variants now preserve their exact resolved bytes in both FORMAL and RETURN positions for bare, nullable and flat ordered union forms. Empty declaration namespaces, valid names and quiet position-specific `PTRELATIVE` resolution authenticate those exact normalized `PTCLASS` bytes; ASCII folding only recognizes the admitted class. The proof view changes only the Relative tag to FullyQualified, preserving base64 payload, metadata, member order and Param fields before the existing FQN folds. Reception, return verification, retirement and private Notice-cell ownership keep their existing guards. The [case-preserving relative review](../../coverage/semantics/relative-case-stdclass-producer-reference-notice-review.json) records native6 once, author1067 and independent source6/WHOLE1214 at separate SL507 cuts; prelaw545, Unsupported1/UNRUN5 and the original compiler-binding/phase-fixture failures retain zero credit. Fifteen old helper expectations promote through fresh137 proofs without historical renewal. Joined4eded and its sole SL509 load pass through the cached immutable tuple with author raw reads0. Ordinary aliases with other resolved spellings, other classes, nonempty Relative namespaces, mixed nominals, DNF and wider owners/lifetimes remain partial; all exact holds stay unchanged.

Scoped ordinary aliases now preserve any resolved global `stdClass` case spelling in bare, nullable and flat ordered FORMAL/RETURN types. Quiet position-specific declaration resolution supplies exact checked `PTCLASS` bytes; a local pure base64 encoder and decode witness carry those bytes into FullyQualified proof views. The original alias spelling, metadata, Param fields and union order stay intact. Existing FQN folds, exact normalized TYPE/RETURN guards, reception, return verification, retirement and private Notice-cell ownership remain authenticated; shared byte rules and Relative/global views are unchanged. The [case-preserving scoped-alias review](../../coverage/semantics/scoped-case-stdclass-producer-reference-notice-review.json) records native6 once/source6, prelaw545, corrected author1121 and independent WHOLE1305 at separate SL507 cuts. Twelve old view queries in six helpers promote while stale canonical TYPE/RETURN header refusals remain, without historical renewal. Original malformed-byte parse/preparation and inherited H9/H8 fixture failures/localizer retain zero credit; the production law needed no correction or accepted replay. Joined9081 and its sole SL509 load pass through the cached immutable tuple with author raw reads0; the main map-preparse SyntaxError retains runtime0/reportreads0 at that preparation. Other classes, multiple nominals, mixed ordinary/Relative unions, DNF and wider signatures/owners/lifetimes remain partial; all exact holds stay unchanged.

Exactly supplied ordinary-CV producers now admit an optional suffix of untyped or plain `int` formals with direct signed64 `NScalarInt` defaults. The proof checks the identical raw/checked `PSDEFAULT` AST and `int` kind, optional/nonvariadic/BYREF/type agreement, required-prefix ordering and exact actual/raw/checked counts. It erases defaults and marks parameters required only in a pure delegate view of the existing header proof; original attributes, flags, hooks, names, metadata, types and argument guards remain. The live function signature/default, reception, retirement and private Notice-cell ownership are untouched, and the zeroactual branch is literal. The [supplied optional-default review](../../coverage/semantics/supplied-optional-int-default-producer-reference-notice-review.json) records native5 once, supplied source3, existing omitted/static controls once, prelaw323 and the sole affected independent WHOLE615 at SL507. A later ordinary make() observes default7 after the supplied Notice; an incompatible array/INT default rejects before any echo. Original label/fixture errors and four peer compiler-only attempts retain zero credit without accepted replay. Fixedf505 and its sole SL509 load pass through a full parsed cache persisted before the immutable tuple; author raw reads0. Plain float/default-kind conversion, other raw defaults, nullable/union optional types and wider supply/owners/lifetimes remain partial; all exact holds stay unchanged.

Required ordinary-CV producer formals now admit canonical bare `stdClass` types
when the declaration has no namespace or class imports. A pure raw Param view
changes only the authenticated type tag and preserves every other field and
metadata. It requires nonempty actuals and a changed tag before delegating to the
existing header proof. Reception, return verification, frame retirement and private
Notice-cell ownership retain their existing rules. The
[bare-formal review](../../coverage/semantics/global-plain-stdclass-formal-producer-reference-notice-review.json)
keeps fresh BYVAL/BYREF singleton and multiple-CV originals separate from the scalar
rejection control and old pure expectation promotions, with no historical reruns.
Flat bare union formals are extended below; other names/contexts and wider owners/lifetimes remain partial.

Canonical raw `?stdClass` formals use the same global declaration context and
required ordinary-CV proof. The nullable Param view changes only the inner class
tag, preserving nullable/name/Param metadata and every other field. The existing
FQN nullable fold authenticates exact `[class, null]` order before ordinary
reception, return verification, frame retirement and private Notice cells. The
[nullable bare-formal review](../../coverage/semantics/global-plain-nullable-stdclass-formal-producer-reference-notice-review.json)
keeps object BYVAL/BYREF and NULL originals separate from the scalar reception
control and the earlier pure expectation change. Flat bare unions are extended
below; other names and declaration contexts, and wider payloads/owners/lifetimes remain partial;
exact holds stay unchanged.

Flat ordered bare `stdClass` FORMAL unions use the same global declaration context.
The Param view reuses the pure union view, preserving member bytes/order and all
member/union/Param metadata and fields before the existing FQN header proof.
Exactly one class, distinct builtin kinds and at most one Boolean kind admit the
existing two-through-eight-member forms, with `array` or `iterable`. Required
ordinary-CV reception, return verification, frame retirement and private Notice
cells retain their existing rules. The
[ordered bare-formal review](../../coverage/semantics/global-plain-ordered-stdclass-formal-producer-reference-notice-review.json)
separates object BYVAL/BYREF, array COW and eight-member source evidence from an
unchanged strict reception control and preserves all three fixture failures.
Other names/contexts and wider payloads/owners/lifetimes remain partial; exact holds stay unchanged.

Singleton `NName` FORMALs also use their declaration namespace and class imports
when valid, quiet, builtin-first type resolution yields exact global `stdClass`.
A proof-only Param view changes the authenticated alias spelling and tag to that
canonical fully qualified name, preserving every other field and all metadata;
the original source and declaration stay intact. A nonempty declaration context
keeps this arm disjoint from the unchanged global view. Nonempty actuals and a
changed parameter vector still precede the existing header proof, reception,
return verification, retirement and finite private Notice cells.
The [scoped-formal review](../../coverage/semantics/scoped-stdclass-formal-producer-reference-notice-review.json)
keeps four Notice originals and one unchanged strict reception control separate,
including the original semantic overlap failure and saved line-expectation correction.
FQN returns isolate formal authority in these originals. Scoped unions are
extended below; relative forms, other resolved spellings and wider owners/lifetimes
remain partial, with all exact holds unchanged.

Nullable `?Alias` FORMALs reuse that same quiet builtin-first declaration proof
when the ordinary name resolves to exact global `stdClass`. The nullable Param
view delegates to the existing singleton view, changing only the inner proof
name and tag while preserving nullable/name/Param metadata and every other field.
The existing fold authenticates exact class-then-null order; nonempty declaration
context, nonempty actuals and a changed parameter vector preserve disjointness
from the old global route. Caller strictness, ordinary BYREF reception, RETURN
verification, frame retirement and finite private Notice cells keep their guards.
The [scoped nullable-formal review](../../coverage/semantics/scoped-nullable-stdclass-formal-producer-reference-notice-review.json)
separates object BYVAL/BYREF and NULL Notice originals from an unchanged strict
scalar reception control. Native4 ran once; author and independent source4 plus
440/218 fixture cuts remain distinct. The old124 pure-view expectations and
matching class/null proofs are promoted through fresh125 equivalents and static
composition, without renewing124 execution. The fixed actual and one shared
production-SL509 load are independently clear. Scoped unions are extended below.
Relative names, other resolved classes and wider payloads/owners/lifetimes remain
partial, with all exact holds unchanged.

Flat ordered FORMAL unions reuse the same declaration proof for exactly one
ordinary class name resolving quietly to canonical global `stdClass`. A finite
member view canonicalizes that class proof and preserves every Identifier, raw
member order and member/union/Param field and metadata before the existing FQN
two-through-eight-member folds. The folds retain distinct builtin kinds, one
Boolean kind and the separate `array` or `iterable` companion paths. Nonempty
context, actuals and a changed vector keep the old global route disjoint.
Reception, RETURN verification, frame retirement, private Notice-cell ownership
and lifetime guards retain their existing rules; RETURN resolution remains
independent of this FORMAL view.
The [scoped ordered-formal review](../../coverage/semantics/scoped-ordered-stdclass-formal-producer-reference-notice-review.json)
keeps native4 once and three Notice originals separate from one unchanged strict
reception control. Retained source4 and author451 at bb72, corrected peer244 at
8585 and the first independent whole4+451/244 at f2f65 retain separate identities.
The original peer fixture/whole failure has zero credit: three weak-conversion
expectations confused the scheduled conversion with its later result, so only
that fixture was corrected and rerun. Old124/125 pure-view and matching class/null
proof promotions use fresh126 equivalents without renewing those campaigns;
class-only normalized mismatches remain refused. The fixed actual and one shared
production-SL509 load are independently clear through the cached family tuple.
Relative names, multi-nominal unions, wider resolved classes and wider payloads/
owners/lifetimes remain partial; all exact holds stay unchanged.

Distinct ordered builtin unions of three through eight members also admit
`callable` in required ordinary-CV producer formals and returns. Raw/normalized
order, unique members and at most one Boolean kind remain required. Exact tags
bypass callable lookup; registered USER names precede weak Boolean conversion.
The [builtin-union review](../../coverage/semantics/cv-builtin-callable-union-producer-reference-notice-review.json)
keeps native6 once/source6, author422/peer214, genuine prelaw247/102 and the first
fixture's corrected bool-mask expectation separate. Twenty-six precise helper
promotions use fresh92 states. Actual4c4678a5bdc and its sole production-SL508 load
pass in16.138253193s/source0, independently closed. Controller/Make remain
unexecuted/source0; wider contexts and every exact hold stay partial.

Ordered `callable|object` and `object|callable` required formals and returns retain
the same raw/normalized authority. Exact quiet stdClass values bypass callable
lookup; registered USER names retain their callable route, while scalar mismatches
reject in both strict modes. Existing real object edges, transient ordinary BYREF
writes, producer retirement and separate unconstrained private Notice cells remain.
The [object/callable review](../../coverage/semantics/cv-object-callable-producer-reference-notice-review.json)
records six native-once source agreements and separate author597/peer307 fixture
cuts; prelaw231/140 retain zero agreement credit. Actual38a6e31833 and its sole
production-SL508 load pass in16.382436244s/source0, independently closed. Controller/
Make remain unexecuted/source0; wider forms and every exact hold stay partial.

Ordered `callable|array` and `array|callable` required formals and returns retain
the same raw/normalized authority. Exact arrays bypass callable lookup;
registered USER names retain their callable route, while scalar mismatches reject
in both strict modes. Existing finite array graphs, ordinary BYREF writes,
producer retirement and separate untyped private Notice cells retain their bounds.
The [array/callable review](../../coverage/semantics/cv-array-callable-producer-reference-notice-review.json)
keeps native6 once/source6, author595/peer300 and genuine prelaw229/137
fixture-SL507 cuts separate from actual `8490ca0c88` and its sole production-SL508
load. Ten old-header controls use fresh90 states; controller/Make remain
unexecuted/source0. Wider forms and every exact held boundary remain partial.

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

Completed required ordinary-CV producers admit exact ordered `iterable|float`
and `float|iterable` returns for one or multiple positions. Raw/normalized order,
formal authentication, actual return conversion, frame retirement and finite
private Notice cells remain required. Weak numeric text converts to FLOAT; strict
INT widens to FLOAT, while strict numeric text rejects before the outer Notice.
The [float/iterable-return review](../../coverage/semantics/cv-union-float-iterable-return-producer-reference-notice-review.json)
keeps seven originals/native4+3 once and separate author/independent source7 with
477/351 fixture-SL507 cuts distinct from actual `dd3e79342` and joined SAME
`fde250339`. Its sole saved production-SL508 load passes in16.732132342s/source0.
Other iterable union partners, wider headers, payloads and lifetimes remain partial;
every exact hold stays unchanged.

Completed required ordinary-CV producers admit exact ordered `iterable|bool`
and `bool|iterable` returns for one or multiple positions. Raw/normalized order,
formal authentication, return verification, frame retirement and finite private
Notice cells remain required. Weak text `0` returns false and nonempty `false`
returns true while caller copies retain their String tags; strict numeric text
rejects before the Notice. The [Boolean/iterable-return review](../../coverage/semantics/cv-union-bool-iterable-return-producer-reference-notice-review.json)
keeps seven originals/native4+3 once and separate author/independent source7 with
477/376 fixture-SL507 cuts distinct from actual `f12c49d37` and SAME `53782e750`.
The sole saved production-SL508 load passes in16.440659384s/source0. Other iterable
union partners, wider headers, payloads and lifetimes remain partial; every exact
hold stays unchanged.

Completed one- or multiple-required ordinary-CV producers admit exact ordered iterable|string/string|iterable returns, preserving raw/normalized order, unchanged formal reception, actual return verification, frame retirement and finite private Notice cells. Wider headers, payloads and lifetimes remain partial.
[Ordered iterable/string return review](../../coverage/semantics/cv-union-string-iterable-return-producer-reference-notice-review.json).

Completed one- or multiple-required ordinary-CV producers admit exact ordered iterable|false/false|iterable and iterable|true/true|iterable returns, retaining raw/normalized order, unchanged formals, actual return verification, frame retirement and finite private Notice cells. Weak mismatched Boolean/scalar returns reject before the outer Notice; wider headers, payloads and lifetimes remain partial.
[Review](../../coverage/semantics/cv-union-literal-bool-iterable-return-producer-reference-notice-review.json).

Completed one- or multiple-required ordinary-CV producers admit exact object|iterable/iterable|object and callable|iterable/iterable|callable returns, plus longer ordered distinct builtin unions containing iterable. Dedicated RETURN-only folding preserves raw Identifier/normalized order and count, rejects array/duplicate/Boolean overlaps, and retains shared FORMALS, existing pairs/epsilon, actual return verification and finite private Notice cells. Class-bearing iterable unions and wider payload/lifetime contexts remain partial.
[Review](../../coverage/semantics/cv-builtin-union-iterable-return-producer-reference-notice-review.json).

Completed required ordinary-CV producers admit exact ordered FQN stdClass/iterable RETURN unions of2–8 members, preserving decoded class bytes, raw/normalized order, distinct permitted builtins and oneBoolean kind. Actual return verification, frame retirement and finite private Notice-cell payload/owner bounds remain; FORMALS/wider class names, Traversable payloads and lifetimes stay partial. [Review](../../coverage/semantics/cv-fqn-stdclass-iterable-return-producer-reference-notice-review.json).

Fully supplied optional plain `float` formals may retain a literal INT default.
The proof checks the same raw default AST with normalized kind `float`, then
reuses the required ordinary-CV header proof without changing the live signature.
By-value string reception preserves the caller, while by-reference reception
converts the actual cell before the producer body and leaves no persistent type
constraint. Omitted defaults still materialize as FLOAT; numeric-string defaults
remain compile-invalid. Nullable/union formals, other default expressions and
wider producers/lifetimes remain partial.
[Review](../../coverage/semantics/supplied-optional-float-int-default-producer-reference-notice-review.json).

Fully supplied optional untyped or plain `float` formals also retain literal
FLOAT defaults. The proof preserves the whole checked FLOAT AST, including its
payload and metadata, with exact `PSDEFAULT` kind `float`; the existing adapter
already validates the binary64 encoding. Actual reception, default demand and
private reference-cell ownership remain unchanged. A supplied untyped scalar
keeps its value until the body writes it, while a later omitted call observes
FLOAT `7.5`. An `int` formal still rejects even the exact FLOAT default `7.0`
before execution. Other types/default expressions and wider contexts remain partial.
[Review](../../coverage/semantics/supplied-optional-float-default-producer-reference-notice-review.json).

Fully supplied optional untyped or plain `bool` formals also retain bare
`true`/`false` defaults. The proof matches the entire `ConstFetch`/`Name` AST,
both metadata layers and the exact checked literal kind, then case-folds the
decoded name. Live signatures, reception, default demand and private Notice-cell
ownership are preserved. A later omitted call still observes Boolean identity;
an incompatible `int` formal/default pair rejects before execution. FQN/relative names,
literal Boolean formals, other defaults and wider contexts remain partial.
[Review](../../coverage/semantics/supplied-optional-bool-default-producer-reference-notice-review.json).

Fully supplied optional literal `true`/`false` formals retain matching bare
Boolean defaults. A separate admission couples the decoded raw Identifier, sole
normalized literal type and exact checked default kind, preserving the entire
constant AST and both metadata layers. Required-header proof views preserve live
signatures, reception and private ownership; the header checks returns separately
from its erased-return argument view. Literal masks reject integer `0`/`1` even
in weak calls, and a later omitted call retains Boolean identity. Other names,
nullable/union formals and wider defaults/lifetimes remain partial.
[Review](../../coverage/semantics/supplied-optional-literal-bool-default-producer-reference-notice-review.json).

Fully supplied optional untyped, plain `bool` or matched literal `true`/`false`
formals also admit fully qualified builtin Boolean defaults. The proof keeps the
exact checked ConstFetch/FullyQualified Name AST, both metadata layers, decoded
case-insensitive spelling and the same explicit `true`/`false` kind. Only the
required-header proof view erases defaults; actual reception, live signatures,
return verification and private Notice-cell ownership retain their existing rules.
Supplied calls preserve caller aliases and copied arrays, while later omitted
`\false` remains Boolean false. Relative names, general constants and wider
header/payload/lifetime contexts remain partial.
[Review](../../coverage/semantics/supplied-optional-fqn-bool-default-producer-reference-notice-review.json).
