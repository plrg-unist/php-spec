# Request state and symbol-table design review

The private840 runtime has [246 independent exact source comparisons](../../coverage/semantics/request-environment-independent-source-review.json)
and [eight state programs/1,936 assertions](../../coverage/semantics/request-environment-independent-state-review.json).
The [canonical publication review](../../coverage/semantics/request-environment-review.json)
accepts652d10b7/845 inputs. It checks72 old-to-new states after removing only the
new absent REQUEST.CWD field, then72 exact private-to-canonical full states without
projection. Six final author programs pass2,619 assertions, with cuts0..64 and
128/256/512, next-step equality and nine full resumed completions each. The earlier
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
separates these inputs. Combined magic file/directory controls now pass in the paired publication; their
original compiler boundary remains retained separately.

`BASE_GLOBAL` captures GLOBALS keys using variable-name conversion, including its
warnings, rather than ordinary array-key conversion. Direct or compile-time
folded literal GLOBALS remains special; runtime-computed names can refer to an
ordinary variable named GLOBALS. Compiled write metadata belongs to the actual
GLOBALS dimension occurrence. Twenty descriptor controls preserve the distinction
between required fetch/write markers and benign unused literal-base descriptors.
Computed `this` reads, assignment/reference errors, terminal unset and ancestor
unset retain their distinct source-line diagnostics.

This publication covers the top-level request symbol table. Function frame locals,
later-unit source execution, object protocols and broader services remain pending.
No inventory family closes from these bounded source/state checks.
