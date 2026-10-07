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

Dynamic/FCC clone maker sites require durable selected-call evidence or explicit
Unsupported admission; they are required core follow-ons. A direct private
shutdown callback companion is native-only and awaits its model gate. Receiver-release,
implicit Generator callbacks, Deprecated dispatch, promotions, hooks, enums and
wider lifecycle behavior remain open. This slice does not complete readonly or
clone semantics.

Matching pinned engine routes: `zend_objects_clone_obj_with` and
`zend_objects_clone_members` in `Zend/zend_objects.c`; `zend_std_write_property`
in `Zend/zend_object_handlers.c`; property Stringable verification in
`Zend/zend_execute.c`; and `ZEND_FUNCTION(clone)` in
`Zend/zend_builtin_functions.c` under `vendor/php-src`.
