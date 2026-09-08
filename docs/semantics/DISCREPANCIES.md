# Engine discrepancies

These decisions are explicit departures from the pinned engine, separate from
ordinary differential agreement. Observed formatting and diagnostic quirks that
we reproduce are described with their respective semantics.

## Namespace-relative `static` declaration types

PHP 8.5.10 accepts the syntax `namespace\static`. In a named class without a
parent, compiling it as a return type segfaults. With a parent, it becomes the
parent type: a method may return a parent instance that a bare `static` return
type rejects. Both the frontend and native parser accept the retained sources.

The specification interprets this spelling as late-static `static`, preserving
ordinary position and class-scope restrictions. This avoids both a memory fault
and accidental parent substitution. It agrees with the engine's recognition of
the spelling as `ZEND_FETCH_CLASS_STATIC`, its handling in `new`, and the existing
relative `self`/`parent` pseudo-types. This is an intentional interpretation, not
an assertion that the pinned engine implements it.

At source pin `34308a6666b2d489c509541ea9befea9e2b42348`,
`Zend/zend_compile.c::zend_compile_single_typename` assumes every non-default
class-fetch kind is `SELF` or `PARENT`; relative `STATIC` reaches the parent branch.
Its null parent pointer causes the crash. The separate bare-type path correctly
handles `IS_STATIC`.

[Retained observations](../../coverage/semantics/engine-defects.json) include
source bytes, binary/source fingerprints, parser acceptance and exact process
outcomes. Regenerate with `python3 tests/semantics/engine_defects.py`. A reproduced
crash is recorded as `engine-crash`, never as PHP failure or conformance success.
The static helper's chosen-behavior checks are reported separately from engine
comparisons; source activation remains subject to its own integration gate.
