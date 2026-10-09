# Object property storage

Class descriptors record ordered public/protected/private instance declarations, types and
source-backed defaults. Each allocation creates owned slots: a typed property
without a default starts uninitialized, while an untyped one starts as null.
An override of an inherited nonprivate declaration must preserve its type and
reuse its slot; visibility narrowing is checked first. Inherited private
declarations retain separate declaring-class slots and impose no child type
constraint. Early and deferred links enforce the same conditions. Reads, writes,
`unset`, `isset`, `empty` and computed names use the same slots; writes apply
the declared type and report the declaring class. A simple typed property assignment
converts against its declaration before checking the current alias's other type
sources, and returns the converted value. Aliased compound updates keep the generic
reference checks. Dynamic properties use the
same storage, with the pinned deprecation on ordinary source classes and no
deprecation on `stdClass` or a source class/descendant with the single builtin
`#[AllowDynamicProperties]`. Allowed creation uses the existing slots and bypasses
deprecation capture; see the [attribute review](../../coverage/semantics/allow-dynamic-properties-review.json).
A leading-NUL computed name raises the engine error
for read, write and unset, while quiet tests remain silent.

Constructor promotion declares a property from its original parameter flags and
source occurrence. A parameter default does not initialize the property, and
promoted nonnullable types do not acquire ordinary implicit nullable widening.
All argument receives finish before promotion writes run in parameter order,
reading each current parameter cell. Value writes preserve ordinary copy behavior;
reference writes alias that cell and attach the property’s ordered type source.
Explicit constructor re-entry, inherited private slots and trait aliases use the
same declaration scope and readonly checks. The original body remains unchanged.
A promoted WeakReference property owns the wrapper while its target remains weak.
[The promotion review](../../coverage/semantics/constructor-promotion-review.json)
records nine exact sources, genuine Weak/byref steps and preserved failures.
One zero-argument builtin `#[Override]` on a promoted property resolves through
its real namespace/import context. It requires an exact-name nonprivate parent
property after ordinary inheritance compatibility. Simple root declarations fail
during compilation, including unreachable declarations; trait checks defer until
the using class links. Compatible trait collisions retain the effective property's
own source obligation. A failed check rolls back class publication. The
[Override review](../../coverage/semantics/promoted-override-review.json) records
thirteen source agreements, a separate user-attribute Unsupported control and 110
genuine certificate/write/rollback assertions.
A single builtin `#[SensitiveParameter]` on a promoted constructor parameter
belongs to the parameter target. It creates no property Override obligation;
ordinary value/reference writes precede the body, while later trace capture reads
the live CV. Queued promotions retain the authentic head and each task's source
suffix. The [Sensitive promotion review](../../coverage/semantics/sensitive-promotion-review.json)
records eight source agreements and separate source/property/wrapper controls.
Other parameter attributes/hooks remain explicit Unsupported.

Object `foreach` by value uses a live slot cursor, so later writes can affect
later iterations. Dynamic deletion leaves a cursor tombstone; reinsertion
appends a new slot. Array casts expose initialized properties. Loose comparison
uses declared offsets until a property table materializes, then compares live
table entries, including uninitialized declared slots. The object heap owns
property values and their nested arrays or objects across copies, calls and
abrupt cleanup. Paused tasks authenticate the property source occurrence and
line without reconstructing captured receiver values.

Literal undefined reads from ordinary instances and `stdClass` now resume
warning handlers with fixed null, preserving handler writes and throws. Ordinary
CV and `$this` receivers remain borrowed and may retire inside the handler;
temporary receivers retain their actual object owner until the read completes.
Unvisited, explicitly unset untyped declarations during ordinary instance
cleanup support quiet null and the same warning continuation through the
authenticated physical storage carrier. Consumed slots remain refused.

When a handler returns false, default reporting precedes return/selected-target
cleanup and raw-handler restoration. The
[undefined-property review](../../coverage/semantics/undefined-property-review.json)
keeps native/source and reached-state cuts separate. Computed names, hooks and
wider receiver forms remain required.

At PHP8.5, a literal named nonbuiltin reference-return call without name fallback,
with no arguments, one ordinary CV supplied positionally or by name, two
positional ordinary CVs, two CVs with distinct named labels, or a positional CV
followed by one named CV, keeps its returned
reference cell through callee leave. Module377 now
captures that actual cell before PROPERTY_PREP, borrows the live ordinary
instance/stdClass target and keeps the warning result null even when handler
rebinding retires that target. FETCH cleanup through270 releases the read's
returned cell owner; other aliases can keep that cell and its replacement alive.
Cell and source checks are disjoint
from the existing CV/temporary lanes; duplicate current or saved carriers are
refused. [The reference-receiver review](../../coverage/semantics/reference-property-receiver-review.json)
records exact native/source cases, reached ownership controls and the pinned8.5
engine distinction from8.6. Accepted99/79 are unchanged; wider call forms,
computed receivers and already-freeing targets remain required.
The one-CV certificate uses compiled source metadata, so callee cleanup or the
handler can unset the argument. A by-value parameter's last-owner destruction
may rebind the returned cell before lookup; a by-reference parameter may share
that same cell. The fixed warning result and existing270 cleanup remain unchanged.
For named sends, compile-known targets use the CV diagnostic line; deferred
targets use the emitted SEND line while retaining the documentary CV operand.
Module377 authenticates the literal property parent, selected reference-return
target and actual named task before capturing that deferred warning. Handler
mutation still sends fixed null, and unknown labels fail before CV demand.
Named default cleanup may replace the receiver during callee leave, so lookup
captures the returned cell's current object without rereading the argument.
For two positional CVs,377 separately authenticates both source/SEND occurrences
without widening361's ECHO certificate. A first argument Warning sends fixed
null; its handler may change or unset the second CV before the later SEND.
Deferred SEND2 preserves the already-captured prefix and documentary CV INPUT,
but reports its actual compiled line. Both last-owned parameter callbacks may
replace the returned cell during leave before property lookup. Prefix cleanup
after an argument throw and wrapper cleanup after a property throw preserve
exception chaining. Core-only companions replace the ordinary `is_null`
observers in the positive comparison set; original bytes and builtin boundaries
remain recorded separately.
Two distinct named CVs use a separate local certificate without restricting label
order. SENDs read CVs in source order; named binding puts each captured operand in
its formal slot. Known sends use individual CV lines, while both deferred
ordinals use the emitted argument-list line and preserve documentary INPUT and
already-sent slots. Skipped defaults and parameter destruction follow formal
order, so lookup captures the cell after all callee-leave callbacks. Unknown and
duplicate labels fail before that CV's demand. Captured prefix release can leave
a caller-local owner whose later frame unwind runs its destructor; the pending
label Error remains protected and may become a cleanup exception's previous.
A positional CV followed by a named CV uses the same actual named-task protocol.
Its first Warning fixes null in formal slot0; the later named CV is read after
handler effects and can bind around a skipped default. The first SEND retains
its equal documentary line, while a deferred named SEND uses the compiled
argument-list line without changing INPUT or the captured prefix. Unknown and
duplicate destinations still fail before CV demand; buffer release and later
caller-local frame cleanup keep their distinct owners and pending Error.
More than two arguments, unpacked or computed actuals and dynamic callees
remain outside this bounded lane.

Literal ordinary CV-base reads now invoke public nonstatic `__get` with one
untyped required parameter and no declared return type. The first family covers
ordinary instances, literal names and missing or publicly accessible UNSET
properties. Denied private/protected reads and ancestor-private literal fallback
also invoke the getter, with no hidden property type verification,
even for INITIAL or initialized typed backing. Allowed lexical VALUE reads the
physical key; accessible typed INITIAL raises Error without invoking the getter.
Lexically accessible nonpublic UNSET, changed Closure scopes for nonpublic access, writes, quiet probes,
wider signatures and guarded recursion remain explicit Unsupported.

Module380 owns one receiver hold while the known-instance getter frame borrows
it. The raw returned value or reference survives any captured property verification
and receiver release. Only afterward does read reception copy the reference cell's
current payload, so receiver destruction can change that result; a value return
keeps its original payload. Discarded reads still retain the getter RV through
receiver release. Public UNSET type verification uses the getter's strictness and
performs no backing-slot write or type-source attachment. An actual mismatch
raises the declaring property's TypeError before receiver cleanup; later cell
repair cannot remove it, and a successful check is not repeated after cleanup.
Verification requiring coercions or constrained returned reference cells remains
Unsupported.

Getter throws release the receiver under the pending exception. If receiver
cleanup throws after a normal return, the raw reference is materialized and its
payload released under that exception, preserving a later cleanup exception's
previous link. Current/saved carrier checks reject missing or duplicate holds;
entered continuations never reread the caller CV or property absence. The
nonpublic path authenticates the ordinary caller scope from its source site
before entry and retains that lookup history through privileged getter and
destructor contexts.
The [getter review](../../coverage/semantics/magic-property-get-review.json) records
eight exact source agreements, 1293 setup-inclusive reached premises and the
separate original failures. The
[denied-getter review](../../coverage/semantics/magic-property-denied-review.json)
separately records six exact sources and 1094 reached premises for lexical keys,
absent hidden type info, captured caller scope and reference/exception cleanup.

The compiler and runtime rules are in `135-property-compiler.watsup` and
`136-property-runtime.watsup`. [The review](../../coverage/semantics/properties-review.json)
binds source, compiler and paused-state checks. Public property references
and by-reference object traversal are documented separately in
[SOURCE-PROPERTY-REFERENCES.md](SOURCE-PROPERTY-REFERENCES.md). Protected/private access and
mangled storage keys are described in [SOURCE-PROPERTY-VISIBILITY.md](SOURCE-PROPERTY-VISIBILITY.md).
[Class static members](SOURCE-CLASS-STATICS.md) have a separate bounded storage
and access contract. Non-object casts and stdClass table sharing are described in
[OBJECT-CASTS.md](OBJECT-CASTS.md), including numeric/NUL storage keys, raw undefined
buckets and callback-sensitive iteration. Wider readonly operations, hooks,
magic setters and quiet access, and wider property consumers remain open.
Public constructors are implemented separately.
