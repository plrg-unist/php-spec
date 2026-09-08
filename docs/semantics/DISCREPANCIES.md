# Engine discrepancies

This ledger separates intentional departures from observed engine irregularities
that the specification must reproduce. Only explicitly chosen departures belong
in the intentional-divergence inventory.

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

## Static-return variance: follow the pinned behavior

The pinned `Zend/zend_inheritance.c::zend_type_permits_self`, called by
`zend_perform_covariant_type_check`, treats a top-level named member matching the
child class as sufficient for a `static` return type. It does not require every
intersection member and does not inspect an intersection nested inside DNF.

The retained `variance-static-*` oracle targets establish that a child `static`
return is accepted against parent `I&J` when its class implements either I or J,
and rejected when neither matches. An accepted implementation can actually return
a value that is not J. Parent `(I&J)|null` rejects `static` even when the child
implements both interfaces. `variance-self-intersection` confirms that an ordinary
`self` return rejects the missing member in the same setting.

These are candidate engine inconsistencies, not a selected divergence. Future
variance rules must reproduce the pinned predicate instead of replacing it with
logical set inclusion. [Oracle evidence](../../coverage/semantics/conformance-oracle.json)
retains exact sources, diagnostics, process outcomes and source hashes; the
[catalog](../../tests/semantics/conformance/cases.json) names each witness. No
source-class coverage is established by these probes. Covariance helper
`8a6c5708` now reproduces the pinned predicate under supplied visible class graphs;
its checked return-type/oracle comparisons are recorded separately in
[variance evidence](../../coverage/semantics/variance.json).

## Reference-assignment result: resolved specification defect

With `$a=1`, `($x=&$a)+($a=2)` originally produced spec 3 versus PHP 4.
`ZEND_ASSIGN_REF` returns an owning reference wrapper; its consumer reads the
cell's current value. Commit `751fbcff` models that captured cell explicitly,
including survival when both variable names are rebound. Ordinary assignment
still consumes its value. The independent witness now passes in the mandatory
388-case source gate, alongside 25 negative checks.

[Raw history and resolution](../../coverage/semantics/reference-result-disagreement.json)
retain the original process observations and the accepted correction fingerprint.
This was a specification defect, with no intentional departure selected.

## CV classification and reference initialization: pending specification defects

`${$x}=&$x; echo ${""}===null;` emits an undefined `$x` warning in PHP,
but the current machine initializes the direct source variable before reading
the delayed target name and omits that warning. The multiline witness locates
the warning on the target-name expression line. A dynamic source fetch has a
different acquisition point; array-literal reference acquisition also remains
before delayed key conversion.

`${1.5}=1; echo ${1.5}+(${1.5}=2);` gives PHP 4 versus spec 3 because
literal float variable names are compiled variables at the pin. An overflowing
positive float literal has the same behavior; unary-negative and boolean
expressions are controls and must retain ordinary captured reads.

[Raw nine-case evidence](../../coverage/semantics/reference-timing-disagreement.json)
retains five disagreements and four controls, exact source bytes and both process
observations. These were newly uncovered outside the previous 421-case selection,
not excluded comparisons. The mandatory next repair precedes element references;
no intentional divergence is selected.
