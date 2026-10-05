# Container initialization and array-reference writes

Module276 extends writable dimension continuations to undefined, null and false
CV-rooted ordinary containers. W initialization is quiet; a nonreference undefined
RW CV warns before installing a fresh array binding. Callback-created references
are detached rather than overwritten through their constraints. This initialization
also happens before unwinding a throwing handler. The post-callback value decides
whether normal execution then emits the false-to-array deprecation. Quiet probes
retain their existing read behavior without initializing storage.

An unwrapped false container installs an empty array before its deprecation and
holds one real table protection across the callback. Survival is sufficient at
that boundary; a handler-created table copy does not itself abort a literal-key
FETCH. FETCH follows the current borrowed container, final ASSIGN separates that
current container again, and DIM_OP retains the originally allocated table. Later
key conversions retain242's own protection and acquisition checks. A wrapped false
FETCH skips the deprecation and checks array assignability before key demand.
Final assignment and compound operations follow their distinct Zend paths.

Throwing callbacks retain those distinctions. Undefined RW still installs an
array; plain W keys can precreate a selected entry, and a final literal-key ASSIGN
can write its delayed RHS before unwind. Missing RW insertion and slow null/float
key conversion stop. An illegal array/object key can replace the handler error
with a restored-emitter TypeError retaining the original previous chain. Expiry
still demands a missing key CV, then retains null without refetching a container
recreated by that callback. Nested final assignments preserve eager RHS computation
before initial false/container and key notices.

Array assignment by reference keeps a genuinely acquired source CELL alive while
fetching its target. A simple source CV remains delayed until target acquisition;
its current binding is then acquired. An aborted target still acquires or initializes that
source CV before the invalid-reference-target Error. Source operands and unnamed
abort temporaries have one genuine owner; captured places and bindings add none.

The pinned DIM_OP path can initialize an array through a bool property reference
without the usual array-assignability check. `CONTAINERINITS` records only that actual
source opcode, cell and array backing. It permits state validation, adds no owner
and grants no ordinary type conversion. Pointer COW transports the original source
certificate to the separated array; whole-cell stores clear it and retain normal
type checks. Source/consumer, line, mode, operand and compiled-constant guards
remain checked. Consistent dynamic places and values are runtime facts, without
invented callback history.

The pinned contracts are `zend_fetch_dimension_address` and the `FETCH_DIM_W/RW`,
`ASSIGN_DIM`, `ASSIGN_DIM_OP` and `ASSIGN_REF` handlers in `vendor/php-src/Zend`.
Author12 source agreements include three independent originals. Independent21
retains those three and adds18 fresh comparisons:30 distinct private programs.
Author74/72/96=242 and independent69/72/68/66=275 reached assertions keep their
separate cuts. One actualae0 source at851 retains private Owner/Child selection, captured
source-cell lifetime and live caller/static17. The [ledger](../../coverage/semantics/container-warning-review.json)
keeps original failures, corrected native predictions and the latera692
publication bridge distinct from executed results.

The catalogue and reached fixtures are `tests/semantics/container_warning_cases.py`
and `container_warning_protocol.py`. `python3 -B tests/semantics/container_warning_prepare.py
[fixture-id ...]` compiles selected reached fixtures; original runner commands
and runtime/environment identities remain in raw records. Production comparisons use SL_mode; reached
fixtures use AL_mode and existing local tools, with no rebuild/portability claim.
Wider read/quiet/memoized/unset containers, string/object/key producers and GLOBALS
siblings remain required core work. Paused return verification remains separate.
