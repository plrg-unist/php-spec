# Quiet typed NOT operands and FULL conditions

The quiet static USER methodclosure selector certificate admits NOT over closed
typed COALESCE or TERNARY operands beyond the existing byte proof. Its result is
an exact BOOL, including when used as a FULL condition. For example,
`!(true ? ((true ? null : false) ?? true) : false)` yields FALSE, so a surrounding
coalesce retains FALSE rather than selecting its right operand.

The new operand clause first requires old byte-proof `None`, authenticates the
NOT root and proper field-0 SOURCE child, and requires typed `Some(value)` for
that child. Its closed values are NULL, BOOL, range-checked INT and non-NUL
STRING. Their echo bytes are falsey exactly when empty or STRING0; negation
returns `PBOOL` rather than a string with the same echo. STRING00 remains truthy.
One constructor-specific FULL fallback requires the same old refusal and typed
NOT result, then returns its echo. `Some(empty)` is a successful false condition,
distinct from failed `None`.

Both children of typed COALESCE and all required FULL/SHORT TERNARY SOURCE remain
authenticated, including skipped nodes and keyword NAME facts. Each new cycle
descends the NOT proper child; proper-child induction preserves every old
positive result. The old operand branches, byte trees, FULL COALESCE/TERNARY
fallbacks, SHORT/non-NUL/truth rules, receipt/46 guards, caches and owner/lifetime
bodies remain literal. No runtime carrier or native evaluation fallback is added.

The target is PHP 8.5.10 CLI NTS64. Pinned engine routes are
`zend_compile_unary_op`, `zend_compile_conditional`,
`zend_compile_shorthand_conditional` and `zend_compile_coalesce`, together with
`ZEND_BOOL_NOT`, `ZEND_QM_ASSIGN`, `ZEND_JMP_SET` and `ZEND_COALESCE`.
Four fresh originals change only their FCC selector lines while preserving prior
callback bodies, profile and streams. Native originals run once, then exact
bytes/path/CWD/profile are reused. Source-first Unsupported4 and dynamic
NOT39/TERNARY62/COALESCE69 snapshots remain distinct from complete SOURCE41/64/74
facts. NOT snapshots observe completed BOOL negation; queued FULL or NULL-left
COALESCE work does not yet carry a completed child tag. Existing primitive NOT,
UnaryPlus +1/+0 and supported SHORT controls carry zero new behavior credit.

One maintained NOT-condition refusal becomes `Some(empty)`. Its static CASE
bridge preserves every other source, stage, count and check; the exact old
AST/callee is exercised as `not_condition_value_10` in the fresh values cut.
Historical campaigns are not rerun. Separate source, actual-site, value,
selected/skipped SOURCE, bounds and authority records retain the original caps;
fixtures and the production load check carry zero source-agreement credit. The
[review](../../coverage/semantics/magic-property-methodclosure-static-raw-not-operand-condition-typed-ternary-left-coalesce-quiet-get-review.json)
binds the source, validation and fixed integration identities.

Other Boolean composition and condition roots beyond the existing byte proof,
typed UnaryPlus/UnaryMinus, FLOAT/CV, nonquiet or NUL-bearing operands, owning
values, wider parents/selectors and lifetimes remain partial. The full-core
objective and inventory status are unchanged; this bounded certificate is not a
general PHP expression evaluator.
