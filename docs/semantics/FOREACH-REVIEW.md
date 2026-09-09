# Foreach representation review

Array foreach code **1f0e8810** has [bounded runtime acceptance](../../coverage/semantics/foreach-runtime-review.json):
155 exact sources, nine author state programs/6,498 assertions and eight independent
programs/3,096 assertions. The [full 4,997-source container audit](../../coverage/semantics/container-campaign-audit.json) passes. Object and
Traversable protocols, return/frames and header/nullsafe compiler contexts remain
unfinished. The pinned engine is PHP 8.5.10;
[18 native originals](../../coverage/semantics/foreach-independent-cursor-originals.json)
retain exact source bytes and observations before implementation. A further
[12 native originals](../../coverage/semantics/foreach-independent-copy-unwind-originals.json)
cover copy versus reconstruction, source/target overlap and nested abrupt exits.

Each active by-reference iterator needs its own class of saved positions across
copy-on-write descendants. `zend_array_dup_ht_iterators` copies each iterator's
current position. `zend_hash_iterator_find_copy_pos` selects one saved copy and
removes that iterator's other copies. It does not remove another active iterator's
saved positions. Array union preserves cursor copies from its left operand;
constructing a new array by spread or using that array as the right union operand
starts from the new table's beginning. The originals distinguish both union orders
and an empty left operand. Once a discarded descendant is selected later, the old saved
position is unavailable; `zend_hash_iterator_pos_ex` uses that table's current
internal pointer, separating a shared table as needed.

The `nested-copy-selected` original produces `o01i01i12o12o28:8`: inner progress
does not advance the outer iterator's saved position. `reference-descendant-choice`
produces `0:1;1:2;1:2;0:1;1:2;2:9;end`: selecting one descendant discards the
alternative's saved position. A single global array-ancestry cursor cannot express
both behaviors.

A by-value continuation owns the captured array. `ZEND_FE_RESET_R` stores a value
and uses its own position; references inside that captured array can still change.
The `alias-tail-byvalue` source retains the previous reference-loop value variable
and observes `x1y2z2:122`. Copying the container does not erase embedded aliases.

A by-reference continuation owns the acquired reference cell, including temporary
iterable wrappers. It must not re-read a source name or dimension path. The
`holder-replaced`, `holder-element-rebound` and `holder-element-unset` sources all
finish iterating `123` while the new holder contains `78`. Conversely, replacing
the value in the same acquired cell with an integer causes a warning at the next
fetch and leaves the last value-variable alias alive (`replace-with-scalar`).
`ZEND_FE_RESET_RW` and `ZEND_FE_FETCH_RW` distinguish these cases. An unsuccessful
scalar reset does not acquire the array wrapper used on the successful path.

Positions must distinguish insertion occurrences and the end boundary, rather
than only current keys or a count of live entries. Deleting a last bucket invokes
`zend_hash_iterators_clamp_max` for every saved position attached to that table.
Rehashing translates saved positions and the old end sentinel so subsequent
appends remain visible. Empty-array duplication does not copy iterators.
These details are in `zend_hash.c`'s deletion, rehash and array-duplication paths.

Loop continuations should own iteration roots exactly once. Break, return, throw
and multi-level continue must remove the iterator metadata whose continuation is
unwound, while preserving the last bound value variable. Continuing an outer loop
removes the inner iterator but retains the outer one. Dense state gates should
check correspondence between active continuations and iterator metadata, as well
as heap validity, source origins, held roots and exact resumed state. Saved cursor
metadata is not an additional array/reference owner.

The later object/Traversable protocol must preserve ordinary callback execution,
exceptions and cleanup. This review does not discharge that pending obligation.

## Accepted state protocol and preserved repairs

Arrays retain live `(key, serial)` insertion occurrences: overwrite preserves an
occurrence, deletion removes it, reinsertion receives a new monotonically increasing
serial. Each iterator keeps its own tagged CURSOR saved positions. These records
are metadata, not heap owners. Dead table maps are pruned; table IDs are not reused.
By-value iterators own captured arrays; by-reference iterators own the acquired
cell, including a reference-valued AssignRef temporary. Selecting one descendant
discards only that iterator's alternative positions. Completion and abrupt loop
exits release iterator metadata while leaving the last value-variable alias intact.

The [original failures](../../coverage/semantics/foreach-runtime-first-failures.json)
retain three wrong AssignRef outcomes, a dead saved map and a public raw-tuple
serialization failure. The separate [DIM origin failure](../../coverage/semantics/foreach-origin-first-failure.json)
retains exact pre-fix inputs and the final state: output agreed, but an ORIGIN
continuation was lost. Restoring the setup TODO before shared reset preserves the
caller continuation and acquired location. The unchanged failing fixture now passes.
Independent dense replay checks complete state, ownership and cleanup; only BUDGET
is changed when resuming. Earlier timeouts and tool failures remain failures.

The final catalogue adds twelve unchanged prerequisite sources to the corrected
candidate. Exact non-CASES harness bytes, selected sources, fixtures, modules and
tools bind the completed state runs to publication; this does not relabel those
runs as a fresh aggregate campaign. The later full source campaign now passes its independent ordered/raw/archive audit.
