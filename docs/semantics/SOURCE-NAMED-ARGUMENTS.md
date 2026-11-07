# Named arguments for direct user functions

This checkpoint binds positional and named sends to declared user functions, including typed/reference parameters, omitted defaults and variadic tails. Argument expressions execute in source order. Fixed names select case-sensitive parameter destinations; extra names retain insertion order in a variadic tail. Unknown and duplicate names fail at SEND. Literal CV reads occur after destination validation; computed variable and dimension fetches occur before it. Writable acquisition can create storage before a failed send, but reference promotion occurs only after the destination succeeds. Deferred literal-CV sends use their compiled emission line, which can differ from the original variable source line; the same correction applies to positional deferred sends. Actual argument-root metadata is checked against the source compiler projection.

Selected error handlers now receive the `Only variables should be passed by
reference` Notice for a bounded named call-result send. The selected ordinary
user function has an untyped fixed or variadic reference parameter; the argument
is a direct ordinary by-value user call without namespace fallback. It has no
arguments or uses the bounded
[completed CV argument](../../coverage/semantics/producer-cv-reference-notice-review.json)
route described in the reference-parameter contract. Both the selected function
and the producer have no attributes and are nongenerators.
Pending values and untyped reference payloads admit null/bool/int/float,
non-NUL interned strings and live acyclic graphs through DIRECT child arrays
and ordinary scalar/array reference cells. String and array reference cells have no
parameter-backing metadata; see the
[string extension](../../coverage/semantics/interned-reference-notice-review.json). The real
next `NAMED_ARGS` task owns the newly stored private reference before dispatch,
alongside previously sent references. Handler rebinding cannot redirect those
cells. Normal/false handling continues later arguments once; a throw cancels the
call before later sends, body entry or caller assignment. A reference return can
carry the original sent cell into an ordinary caller CV. Notice validation binds
the exact argument destination, source prefix, emission line, severity and event;
duplicate destinations still fail after their argument effects and before private
reference creation or handler entry. Validation does not reconstruct earlier
values or add a historical owner. Other producers,
request/raw/NUL strings, objects, constrained sources, wider positional/unpacked
sends and callback lifetimes remain partial. See the
[focused review](../../coverage/semantics/named-reference-send-notice-review.json).

The [array-cell review](../../coverage/semantics/alias-child-reference-notice-review.json)
records real private-cell, table and CELL payload edges. A shared cell owns its
current array once; root COW preserves repeated cell identity, while a singleton
unwraps into a DIRECT child. Deep COW preserves outside copies, and throw cleanup
releases only last owners. The ancestor path crosses DIRECT and ALIAS edges to
allow sibling sharing and reject cycles. Cell and child-header history bounds
remain explicit in the [reference-parameter contract](SOURCE-REFERENCE-PARAMETERS.md).
Objects and wider callback lifetimes remain partial. Earlier
[DIRECT-graph](../../coverage/semantics/direct-child-reference-notice-review.json),
[flat-array](../../coverage/semantics/array-reference-notice-review.json) and
[scalar-reference](../../coverage/semantics/alias-array-reference-notice-review.json)
reviews keep their original cuts.

The same bounded completed-producer route now uses the inner CV's compiled line
for default Notices without a selected handler and for duplicate-name Errors.
Producer effects finish before a duplicate is rejected; that failure still
precedes private-reference creation, Notice emission and caller assignment.
The call instruction keeps its own line. Other SEND contexts retain their prior
line path; see the [default-line review](../../coverage/semantics/default-reference-line-review.json).

Pending positional slots distinguish an absent hole from a supplied PHP null. Entering the callee preserves the effective positional extent, including positional tail arguments, separately from ordered extra names. Interior fixed holes below that extent are filled before ordinary parameter type receives. Deferred hole values are cached before coercion, and omitted reference parameters receive independent cells. Trailing defaults use the existing receive schedule. Failed preflight has a callee trace whose remaining absent slots render as NULL; that rendering does not fill their storage.

Fixed and variadic type checks remain sequential and can change a shared alias before a later argument fails. Extra named SEND diagnostics use fixed_count+1; named-tail type checks use the constant index max(fixed_count, effective positional ARGC)+1. Collected arrays and the sent tail operand slots retain owning references through normal and abrupt cleanup. Trace arguments preserve ordered extra names. Suppression scopes, caller frames and returned-cell ownership follow the earlier accepted contracts.

Public resume checks bind the selected call, original source argument prefix, slot destinations, ordered names, operand modes and stage metadata. Preflight may safely revisit supplied slots, but cannot skip an unfilled hole or enter ordinary typed receives early. Pending default binding requires its final continuation and exact source origin. Partial variadic arrays bind cursor, keys and next-index metadata. Arbitrary consistent runtime values and aliases remain valid; the guard does not reconstruct execution history.

Direct builtin named source handling is the next required compiler prerequisite; builtin name inventories do not establish builtin body execution. Array/Traversable unpack, first-class callable and closure integration, object-dependent defaults and exception handling remain separate core obligations. Future object default side effects also require the pinned distinction between hole-preflight caching and trailing RECV_INIT caching. This checkpoint does not close the complete calls family.

The [author evidence](../../coverage/semantics/named-runtime.json) binds70 source cases,55 compiler phases plus6 boundaries/129 projections,44 resume controls/935 assertions,12 adjacent runtime cases and2 dense states/373 assertions. The [independent review](../../coverage/semantics/named-review.json) adds5 source profiles,4 dense states/731 assertions and two complete959 compatibility bridges at seven cuts; only empty NAMED context fields are removed. Counts overlap. Semantic/source/protocol gates retain968/55cd; final968/ab389 changes only the regression test selection, preserving967 files and all modes. The [compiler contract](NAMED-ARGUMENT-COMPILER.md) records the source-line repair and retained earlier failures.
