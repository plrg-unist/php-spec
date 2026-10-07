# Generator force close

Module303 runs pending finally bodies when an ordinary last-owner release closes
a started Generator. Unstarted bodies remain silent. This extends the reviewed
Module289 delegation baseline without using held IteratorAggregate work or
unaccepted ordinary-return changes.

Close first releases the delegated array/Iterator input or Generator graph link,
then executes the parent's pending finally bodies. Parameters and locals still
own their values; raw current and copied key caches survive until storage release
after the finally bodies. Thus a temporary delegated child closes before its parent
(`1IOZ`), while a parameter-owned child closes afterwards (`1OIZ`). A started
child held only through an array's reference cache also closes afterwards
(`OIZ`). Separately rooted children and waiting siblings remain live.

The release walk preserves physical owner order, including compiled local-slot
order and key-before-value cleanup after a forbidden keyed yield. It can close
other started Generators through ordinary reference/array/object edges. General
user destructors remain an explicit dependency; this is not cyclic collection.

Forced entry skips the unfinished body and its catches. Already-entered finally
return/throw/break/goto outcomes release their held values in the actual caller
before proceeding outwards. Normal finally completion skips the ordinary body
suffix. New explicit return or throw uses the retained outer control tail:
a new exception may be caught inside the Generator and execute that continuation.
The caller's pending exception is restored if the new one is caught, or chained
only when a new exception actually escapes. The existing Throwable audit is
unchanged; forced entry fabricates no Throwable or return.

Finally execution retains the actual function, private lexical scope, called
class and live caller trace. A finalizer can start another Generator, whose
ordinary yield remains allowed. Only the currently closing Generator forbids
yield. Complex operand effects occur before rejection. Ordinary yield rejects
before delayed CV/key reads; yield-from reads its CV first, including its real
undefined-variable handler, then rejects before iterable classification. A
throwing handler becomes the forced Error's previous exception.

Admission checks one queued/entered close claim per Generator, genuine
zero-owner release excluding only its authenticated self pin, source suspension
identity and the complete remaining finally plan. The live forced marker is
mandatory. Captured foreach cursor owners remain visible while queued and retire
through the existing cursor cleanup. Heap-valid duplicate claims/cursors,
surviving external owners, wrong scopes/callers, erased or forged finally plans,
ordinary-marker substitution and stranded input continuations reject at
full public admission.

Pinned authority is `vendor/php-src/Zend/zend_generators.c`, especially
`zend_generator_dtor_storage` and `zend_generator_free_storage`, plus authored
`ZEND_YIELD`/`ZEND_YIELD_FROM` in `Zend/zend_vm_def.h`. The target remains PHP
8.5.10 CLI NTS 64-bit with the project profile, `LC_ALL=C`, `TZ=UTC`.

Independent source review closes 40 normal tuples and two compiler rejections
across `generator-force-close-review-rlbhdmu_` (first16), `78yejgzi`
(remaining22 plus compiler2) and `k7mcky3f` (introduced foreach2). Five exact
Unsupported controls earn no agreement: request-end close, a self-cache cycle,
bare finalizer exit, exit with a started local child and warning-handler exit.
Request-end, terminal cleanup, active-Fiber destruction, cyclic GC, user
destructors and broader Generator/reference APIs remain required.

Eight ordinary source programs pass in eleven finite state groups: 88 reached
premises in `generator-force-close-protocol-9scbub2v`, 287 in `ref9gfv7` and 194
in `vx6br71h` (569 including source/phase bindings and repeated setup). These
are setup-inclusive conditions, not distinct semantic tests. Each passing group
executes its full body, full public/heap admission, exact zero-budget state and
direct/resumed normal completion. The groups include heap-valid malformed-state
rejection. Original compiler, optional-result, malformed-DONE overlap and
scope-observer failures retain zero.

Records live in `.tools/traversal-generator-force-close-xa0fu1q3/.tools` in the
main workspace. The tested copy is actual `38f1dfaa045f`/273 plus reviewed289 and
the one-clause284 property ingress (274), then303 (275). Parent composition and
union records, per-cut candidate diffs, runtime/compiler identities, commands,
exits and exact observations identify this copy; enclosing Git HEAD alone does
not. The final compiler `generator-force-close-compile-6s5b2q2l` produces
8,662,573 bytes of complete structured output with empty stderr and exit0.
Private validation reuses the maintained binaries and grants no new offline
rebuild or final combined-core credit. Canonical integration preserves the newer
eager-destruction and Fiber clauses; introduced composition checks follow with310.
Original Unsupported observations for the two now-admitted last-owner sources
remain in their earlier cuts. Request-end close retains its precise Unsupported
reason and earns zero agreement.

`python3 tests/semantics/generator_force_close_review.py --select graph-temporary-child`
compares the complete native/model tuple at source60/outer90 seconds.
`python3 tests/semantics/generator_force_close_protocol.py --mode check --sl --select graph-input`
executes source-reached state conditions through the maintained strict SL runner
at300 seconds, caching disabled and deterministic checking enabled, jobs1.
Native mode and fixture preparation earn zero model/state execution credit.
