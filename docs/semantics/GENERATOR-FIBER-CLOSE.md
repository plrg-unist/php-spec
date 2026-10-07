# Generator close inside an active Fiber

Module310 permits ordinary last-owner release of a paused Generator on an
actively running Fiber stack. It reuses Module303's input, finally, frame and
cache release rules. The current Fiber identity, caller chain, real receiving
owners, globals and handler state remain intact throughout the close.

`Zend/zend_generators.c::zend_generator_dtor_storage` defers destruction when
the target lies on a Generator path currently executing in a Fiber.
`zend_generator_resume` sets `ZEND_GENERATOR_IN_FIBER` during execution and clears
it on return to the resumer. An unrelated paused Generator released by active
Fiber code follows the ordinary close path. A Fiber alone does not delay every
Generator finalizer.

The existing queued/entered close claims authenticate the real caller and source
finally plan. No additional metadata owns the Fiber or Generator. Parked ordinary
call frames, other suspended Fiber stacks, received cells, arrays and delegation
links retain their existing owners; only a real last-owner release can close the
Generator. A close exception can replace and chain the caller's pending exception
without changing the active Fiber.

Fiber switches while a Generator or close frame is running remain explicit
Unsupported. Parked running Generators, suspension from a finalizer, terminal
cleanup, request-end close, cyclic collection and general user destructors remain
required. Held IteratorAggregate work and user-paused return validation are not
dependencies of this increment.

The target is PHP 8.5.10 CLI NTS 64-bit, the baseline profile including
`error_reporting=30719`, `LC_ALL=C`, `TZ=UTC`, and original source bytes. Private
validation reuses the maintained compiler, adapter and strict SL runner; it adds
no offline rebuild or complete-core claim.

Author source14 and four precise required Unsupported controls pass in
`generator-force-close-review-x3fqiglh`. Four source-reached state recipes pass318
setup-inclusive premises: active queued/entered91 in
`generator-force-close-protocol-b74shves`, resumed116, pending63 and waiting48 in
`generator-force-close-protocol-tneflgf_`. Each checks full public/heap admission,
heap-valid malformed records and zero-budget/direct/resumed completion.
Independent source12 passes in `generator-force-close-review-c_zqu45e`.
Four further genuine state programs/groups pass351 setup-inclusive premises:
queued/body90 in `generator-force-close-protocol-ca1mv41y` and nested-callers70,
parked-owner119, pending-chain72 in `generator-force-close-protocol-hcby0kxg`.
The separate author/independent cuts contain26 normal sources and eight state
programs/groups with669 physical premises, including repeated setup. These are
finite observations. The four required Unsupported controls earn zero agreement.
Native-only and fixture
preparation earn zero agreement or state execution credit. The first compiler
undefined-helper failure remains raw with zero credit; the corrected declaration
placement passes all276 modules in `generator-fiber-close-compile-ofc83xvg`.
The independent initial alias-owner probes and relative-path recorder failure
remain separate raw evidence with zero agreement credit. Their reports and the
affected native correction are under the main project's
`.tools/traversal-review-310/{initial-owner-alias-observations,corrected-global-deletion,corrected-global-deletion-absolute}/report.json`,
outside this private run root. The [ledger](../../coverage/semantics/generator-fiber-close-review.json)
identifies their distinct native/preparation outcomes.

Raw records are under `.tools/traversal-generator-fiber-close-t3bnnzuc/.tools`.
The parent is the exact accepted303 publication over actual289, with275 modules.
Run records bind its composition, changed inputs, runtime/compiler identities,
commands, exits and source outcomes. Canonical integration preserves the newer
call, destruction and Fiber fields; introduced compiler/source composition checks
are pending. Full-core and final combined validation remain open.

`python3 tests/semantics/generator_fiber_close_prepare.py --mode full` compares
the author's complete native/model tuples at source60/outer90 seconds.
`python3 tests/semantics/generator_fiber_close_protocol.py --mode check --sl`
executes the genuine source-reached state recipes at300 seconds per group, jobs1,
caching disabled and encountered determinism checking enabled.
`python3 tests/semantics/generator_fiber_close_review.py --mode full` and
`python3 tests/semantics/generator_fiber_close_review_protocol.py --sl` maintain
the independent source and state selections at the same caps.
