# Quiet typed UnaryPlus operands and FULL conditions

The quiet static USER methodclosure selector certificate admits UnaryPlus when
its closed typed child converts without warning to a signed 64-bit integer. The
result is exact `PINT`, including NULL/FALSE to INT0, TRUE to INT1, preserved INT
and full numeric INT STRING conversions. STRING00 is truthy, while its UnaryPlus
result INT0 is falsey; a surrounding coalesce still retains that nonnull INT0.

One constructor-new operand clause authenticates the UnaryPlus root and proper
SOURCE child, requires typed `Some(value)`, and reuses the existing pure
`coerce_number(value) = COERCED (NINT i) false` and `long_range(i)` premises.
The typed helper previously had no UnaryPlus clause. Its new clause also admits
exact INT tags for old byte-positive leaves such as `+1`, `+0` and `+'00'`.
Their existing byte proofs remain literal.

One dedicated FULL fallback requires old byte-proof `None` and the typed PLUS
result, then returns its echo. Every old `Some(bytes)` remains unchanged. Each
new recursion cycle descends the PLUS proper child, so induction preserves old
typed and byte positives. Shared trees, all other operand/FULL branches,
SHORT/non-NUL/truth rules, receipt/46 guards, caches and owner/lifetime bodies
remain literal. No new arithmetic helper, runtime carrier or native evaluation
fallback is added; UnaryMinus remains held.

The target is PHP 8.5.10 CLI NTS64. Pinned `zend_compile_unary_pm` and
`zend_try_ct_eval_unary_pm` lower unary plus to multiplication by integer one;
the quiet NINT premises therefore preserve the exact integer. Existing positive
INT/keyword/STRING byte clauses use the same coercion premises. Source-first
PLUS28 snapshots versus complete SOURCE32 facts distinguish finished exact
coercion from folded or skipped nodes; completed condition/coalesce values supply
the folded results. The complete selected/skipped SOURCE authority remains.

One draft literal used negative INTMIN text with trailing whitespace. The pinned
numeric classifier's documented `strcmp` suffix behavior makes that value FLOAT,
which stays outside this certificate. Its original bytes/native/model/observer
remain a boundary control with zero source-agreement credit. A fresh core strict
type discriminator confirms INT for bare/leading-only text and FLOAT for trailing
whitespace. Only that trailing space was removed for a new in-domain original;
only its native, source and observer checks were renewed. All other source
records remain inherited, and no numeric semantics or target behavior changed.

Eighteen maintained operand/FULL assertions in four older protocols are promoted
with exact old AST/callee equivalents in the fresh value groups. Old raw-byte
assertions and every unrelated CASE field remain literal; historical campaigns
are not rerun. Separate source, actual-site, scalar/numeric/legacy values,
selected/skipped SOURCE, bounds and authority records retain the original caps.
Fixtures, the FLOAT Unsupported control and the production load check carry zero
source-agreement credit. The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-plus-operand-condition-typed-ternary-left-coalesce-quiet-get-review.json)
binds the source, validation and fixed integration identities.

UnaryMinus, FLOAT/numeric-float/overflow, leading-number warnings, nonnumeric,
NUL/CV/owning values, wider parents/selectors and lifetimes remain partial. The
full-core objective and inventory status remain unchanged; this bounded
certificate is not a general PHP expression evaluator.
