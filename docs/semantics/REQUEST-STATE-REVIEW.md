# Request state and symbol-table design review

This reviews the proposed state model before runtime snapshot/unset rules exist.
It does not accept a mutable runtime candidate. The
[design evidence](../../coverage/semantics/request-state-design-review.json)
retains observed draft hashes, six additional exact native controls and the
remaining validation obligations. Existing
[GLOBALS originals](../../coverage/semantics/globals-snapshot-originals.json)
and [primitive request originals](../../coverage/semantics/request-bootstrap-independent-originals.json)
cover the adjacent boundaries.

`HTTPROOTS` must retain the original array values for GET, POST, COOKIE, SERVER,
ENV and FILES. They are separate owners from visible global-variable cells.
Promoting a visible variable to a reference, rebinding it or unsetting it cannot
retarget the hidden PG value. Consequently a user write separates a shared array
from its PG root. REQUEST uses a local merged table and has no seventh PG root.
Lazy ENV has no root until initialized; activation is request-wide and does not
rearm when a visible name is removed. Compiler activation precedes source effects.

`SYMBOLS` records table order independently of current bindings. CV names acquire
positions in compiler order even while undefined; these placeholders do not own
reference cells. Unset preserves their table positions, including dynamic unset
and GLOBALS-key unset that reach the CV's indirect entry. A solely dynamic name
instead loses its position and reappears at the end on reassignment. New native
pairs print `a3b2` for CVs and `b2a3` for non-CVs. This follows
`zend_attach_symbol_table`, `ZEND_UNSET_CV` and `zend_hash_del_ind`.

A GLOBALS snapshot omits absent/undefined values and converts numeric string keys
to integer keys. Ordinary values are copied; reference wrappers survive only
when ownership requires sharing. Count live incoming edges and roots, including
held operands and uncollected cycles, rather than only environment aliases.
Singleton references detach even in the numeric-key conversion path: changing
snapshot key1 leaves its original value1; with a second reference owner the same
write changes the shared value to7. Existing array copy/merge helpers provide the
relevant ownership distinctions. Building a snapshot must retain all captured
values until its result is owned.

The proposed optional primitive request record and value-based root list can
express these rules. Final review must check repeated snapshot COW, alias and
rebind behavior, both unset paths, missing-name omission, hidden-root retention,
heap validity and complete budget resumption. Protocol controls must reject
untransportable byte strings and clock ranges before PHP semantics. The initial
absolute-file CLI profile must be explicit: invocation spelling and resolved
script filename need separate facts when that profile expands.
