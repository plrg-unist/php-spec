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
interned strings, the live array graphs and quiet root `stdClass` payloads
described below. String and array
reference cells have no parameter-backing metadata. The actual next
`CALL_ARGS` vector owns the new private cell before dispatch, preserving prior
sent cells through source-CV rebinding. Normal/false handling continues later
arguments once; a supplied throw cancels call entry and caller assignment, then
retires the private cell before catch. Reference returns retain their real cells.
The certificate binds the emitting origin, exact positional prefix/vector modes,
fixed or variadic destination and emitted Notice line. Actual reference producers
remain quiet, while TMP values still raise their argument Error before the
handler. Wider producers, request/raw/NUL strings, wider owning values, typed root sources,
unpack and callback lifetimes remain partial. See the
[positional Notice review](../../coverage/semantics/positional-reference-send-notice-review.json).

The named and positional Notice receipts also admit non-NUL interned string
values and untyped string reference cells without parameter-backing metadata.
A producer's by-value string stays frozen while the handler changes its global;
earlier sent reference cells follow real writes and retain identity through
rebinding/unset. The carrier adds no heap owner; the actual sent cell owns the
payload. After reception, ordinary concat may produce a request string and a
reference return carries the updated cell into the caller. Pending request/raw
or NUL strings, typed/property/coercion sources and broader lifetimes remain
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
request/raw/NUL strings and wider producer/callback lifetimes remain partial.
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
of DIRECT scalar/non-NUL interned dynamic fields and non-NUL startup names.
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

The same required untyped/`array` one-CV producers also admit raw `?array`
returns with the exact normalized `[array, null]` type. The ordinary descriptor
and return verifier retain that type. An array return owns its fresh table;
a null return has no heap child and lets an unescaped formal array retire before
Notice. The separate private reference remains untyped after handler reentry.
Three new originals agree using native observations once. Author fixture-SL182
and peer fixture-SL172 retain separate cuts; the two actual old-fence fronts and
the old null-source Unsupported control have zero source credit. Explicit union
syntax, other returns and wider headers/lifetimes remain partial. See the
[nullable array-return review](../../coverage/semantics/nullable-array-return-producer-cv-reference-notice-review.json).

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
