# Request state and symbol-table design review

The private840 runtime has [246 independent exact source comparisons](../../coverage/semantics/request-environment-independent-source-review.json)
and [eight state programs/1,936 assertions](../../coverage/semantics/request-environment-independent-state-review.json).
Canonical publication and the final magic/CWD bridge remain pending. The earlier
[design evidence](../../coverage/semantics/request-state-design-review.json)
retains the draft model and six native controls. Existing
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
A later unit can first activate ENV or REQUEST after an ordinary global binding
exists. The callback replaces that binding; aliases keep the previous cell. The
[isolated replacement review](../../coverage/semantics/request-callback-independent-review.json)
reproduces both original failures and passes28 author plus34 independent checks.
Its two native `eval` witnesses remain pending dynamic-source execution.

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

The optional primitive request record and value-based root list express these
rules. The private source/state reviews check snapshots, aliases, rebindings,
unset, omission, hidden roots, heap validity and bounded resumption. Protocol
controls must reject
untransportable byte strings and clock ranges before PHP semantics. The CLI invocation spelling and checked source filename are separate facts.
[Relative and symlink controls](../../coverage/semantics/request-path-independent-review.json)
confirm SERVER path fields and argv retain the invocation spelling while
diagnostics use the resolved source filename. The request record already
separates these inputs. A combined magic file/directory source remains an explicit
compiler boundary; it is not part of the two passing path comparisons.
