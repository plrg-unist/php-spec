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
attribute-free nongenerators; the producer has no namespace fallback. Pending
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
handler. Wider producers, request/raw/NUL strings, wider owning values, typed sources,
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

Embedded cells must be live, marked and defined. Property/coercion sources,
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
