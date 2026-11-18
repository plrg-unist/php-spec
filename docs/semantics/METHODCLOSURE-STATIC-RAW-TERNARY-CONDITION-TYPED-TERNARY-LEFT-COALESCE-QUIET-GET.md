# Typed TERNARY roots in quiet FULL conditions

The quiet static USER methodclosure selector certificate admits FULL and
shorthand TERNARY roots as FULL conditions when the existing typed operand proof
succeeds and the old byte proof does not. For example,
`true ? ((true ? null : false) ?? true) : false` is a truthy condition whose
COALESCE child requires the typed proof. A plain primitive ternary already
admitted by the old byte grammar adds no behavior here.

The dedicated condition helper returns every old `Some(bytes)` unchanged and
retains its COALESCE clause literally. One constructor-disjoint TERNARY clause
requires old `None` and typed `Some(value)`, then returns `Some(echo(value))`.
`Some(empty)` is a successful false condition, distinct from failed `None`.
NULL, FALSE, INT0, empty STRING and STRING0 remain distinct inside the typed
selection; truthy shorthand retains its original scalar value. The existing
non-NUL and empty/STRING0 truth test remains unchanged.

Every typed TERNARY authenticates its root, condition and both FULL arms, or its
SHORT condition and fallback, including skipped SOURCE and keyword NAME facts.
Typed COALESCE children likewise authenticate both proper children and retain a
nonnull left value; only NULL selects the right. Each new recursion cycle
descends proper condition or arm children before returning to the helper.
Proper-child induction preserves every old positive value. The shared byte
trees, SHORT rule, receipt/46 guards, caches and owner/lifetime bodies remain
literal; no runtime carrier or native evaluation fallback is added.

The target is PHP 8.5.10 CLI NTS64. Relevant pinned engine routes remain
`zend_compile_conditional`, `zend_compile_shorthand_conditional` and
`zend_compile_coalesce`, with `ZEND_QM_ASSIGN`, `ZEND_JMP_SET` and
`ZEND_COALESCE` preserving selected values. Four fresh original sources preserve
the previous callback bodies, profile and streams while changing only the FCC
selector line. Native originals run once; saved bytes/path/CWD/profile are reused.
Source-first current-law Unsupported4 and dynamic64 TERNARY/75 COALESCE snapshots
are distinct from complete SOURCE65/80 facts. Immediate AFTER PNULL queues work;
completed tags come from resolved conditions or enclosing COALESCE left values.
UnaryPlus +1/+0 and supported SHORT controls carry zero new behavior credit.

One maintained condition-helper refusal is promoted to `Some(ASCII1)`. Its static
CASE bridge preserves all other sources, stages, membership and checks; the exact
old AST/callee is exercised as `ternary_condition_value_10` in the fresh values
cut. Historical campaigns are not rerun. Separate source, actual-site, value,
selected/skipped SOURCE, bounds and authority records use the original limits;
fixtures and the production load check carry zero source-agreement credit. The
[review](../../coverage/semantics/magic-property-methodclosure-static-raw-ternary-condition-typed-ternary-left-coalesce-quiet-get-review.json)
records the fixed source/integration identities and external evidence.

Other condition roots beyond the existing byte proof, UnaryMinus, FLOAT/CV,
nonquiet or NUL-bearing operands, owning values, wider parents/selectors and
lifetimes remain partial. The full-core objective and inventory status are
unchanged; this bounded certificate is not a general PHP expression evaluator.
