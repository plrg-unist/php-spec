# Readonly clone-with updates

Module305 opens a fresh per-object readonly allowance after the genuine
`__clone` callback returns. Empty updates use only the callback window. Nonempty
updates visit entries in table order, enforce the saved cloning caller's setter
scope, and perform weak typed writes even for strict callers. A successful write
consumes that physical key; return or abrupt cleanup relocks every unused key.
Already committed entries remain visible when a later update fails.

Stringable conversion captures its admitted destination and value, runs user
code with its own lexical scope, and resumes the saved cloning caller. An inner
write can consume the allowance before the admitted outer write commits. Mutable
property aliases keep their real cell and type sources; a rejected alias store
produces the cloning TypeError and unwinds its window. Live references in the
update array are rejected, while singleton wrappers are read by value.

Visited readonly entries retain their actual received value and a positive
physical write revision. A visit must still match the original DIRECT input's
typed reception. Its value equals the live DIRECT slot when its revision is
current; a later successful preadmitted write may replace the slot and advance
the revision. This matters when an earlier callback write parks in a Fiber and
resumes during a later update's Stringable conversion. Mutable visits do not
claim immutable slot values.

A cached callback created by an implicit clone keeps its selected effective
nonstatic `__clone` maker, physical source, original clone call site and
lexical/called scope. Production requires the genuine callback continuation.
Admission checks the retained compiled opcode or fixed intrinsic clone site,
so it remains valid after the clone window and maker's heap owner retire.
The proof records create no heap owners. Ordinary manual method calls keep their
own invocation admission.

[Sources](../../tests/semantics/readonly_clone_updates_sources.py) and
[reached controls](../../tests/semantics/readonly_clone_updates_protocol.py)
cover update windows, prefix failures, conversion reentry, mutable aliases,
caller/source authentication and Fiber sharing.
[Producer and revision controls](../../tests/semantics/readonly_clone_producer_protocol.py)
freshly parse and check the parked-prior-write source; regenerate with
`--group cache --sl` or `--group revisions --sl`. Retired and manual maker
originals live in the [callback source suite](../../tests/semantics/readonly_clone_sources.py). The
[ledger](../../coverage/semantics/readonly-clone-updates-review.json) separates
the accepted twelve-source/468-condition cut from later alias, revision and
cached-producer checks. Earlier failures, excluded library observers and
interrupted runs retain zero agreement credit.

One direct private shutdown callback original also agrees exactly after both
clone objects retire at the separately recorded367e581df cut. Dynamic/FCC clone
maker selection is implemented in the separate follow-on below. Receiver-release,
implicit Generator callbacks, Deprecated dispatch, promotions, hooks, enums and
wider lifecycle behavior remain open. This slice does not complete readonly or
clone semantics.

A separate private follow-on captures the actual selected dynamic/pipe name
before argument effects and copies only site/name/Closure identity into a maker
receipt. Genuine callback entry records that selection independently under the
physical maker identity; its immediate marker distinguishes implicit computed
calls from manual calls, with disjoint source-selection guards. Consumer birth
keys bind actual Fiber objects, shutdown positions and autoload candidates to
that entry. Autoload registry bucket stamps
and selected-call stamps distinguish fresh manual registrations after removal;
genuine selected snapshots and declaration history retain their own stamps. These records create no heap
owner. Immutable intrinsic Closure bodies and compiled sites check mismatches.
At function/pipe sites, ordinary bare clone-method makers
must match the effective object `__invoke`; saved access remains with the
historical capture checks. The [selection originals](../../tests/semantics/readonly_clone_selection_cases.json)
cover lifetime, manual dispatch, dynamic/FCC pipes, callee mutation during
arguments, private autoload and shutdown. The [source driver](../../tests/semantics/readonly_clone_selection_sources.py)
regenerates exact comparisons with `--select` after numeric allocation. This
follow-on has 20 distinct source agreements, with three affected repeats
recorded separately. Production SL277/application0 passes at e74802804; seven
source-reached groups have 665 accepted clauses at their recorded cuts. The
[state builder](../../tests/semantics/readonly_clone_selection_protocol.py)
recreates nine exact checked programs and all accepted clauses;
`--group GROUP --prepare` checks preparation, and `--group GROUP --sl` evaluates
one group after numeric allocation. Independent bucket
and selected-call stamps authenticate stored/selected consumers; coherent
pending-candidate identity rewrites before storage remain open. The
[selection ledger](../../coverage/semantics/readonly-clone-selection-review.json)
records these cuts and limits. Original compiler, fixture and runtime failures
remain preserved; prepare-only parity adds no model credit. This follow-on does not
renew the frozen305 evidence above.

Current290 composition on c54cc0ff8 preserves the installed source, Generator,
Fiber and destruction protocols. Its two new exact originals pass after private
clone maker retirement and while a live callback window is parked in the real
Fiber-close caller VM. The independent `closer-window` group passes79 strict-SL
premises for that sole carrier, heap-identical source-line forgeries, budget
resumption and terminal retirement. Regenerate it with `--group closer-window
--sl`; this cut does not renew the earlier20/665 evidence.

Matching pinned engine routes: `zend_objects_clone_obj_with` and
`zend_objects_clone_members` in `Zend/zend_objects.c`; `zend_std_write_property`
in `Zend/zend_object_handlers.c`; property Stringable verification in
`Zend/zend_execute.c`; and `ZEND_FUNCTION(clone)` in
`Zend/zend_builtin_functions.c` under `vendor/php-src`.
