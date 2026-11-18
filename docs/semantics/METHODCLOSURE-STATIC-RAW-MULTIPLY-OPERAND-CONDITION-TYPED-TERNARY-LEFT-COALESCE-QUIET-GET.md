# Quiet integer multiplication

The quiet static USER methodclosure selector certificate admits Multiply when
both closed typed children convert without warning to signed64 integers and the
product fits signed64. Results retain exact INT tags, including NULL/BOOL and
full numeric INT STRING conversion. Arithmetic INT0 stays nonnull in COALESCE;
when used as a falsey SHORT condition it selects the fallback and its exact tag.

One constructor-new operand clause authenticates the root and both proper SOURCE
children, requires both typed `Some(value)` results and independent
`coerce_number(value) = COERCED (NINT i) false` conversions, then guards the direct
product with `long_range`. One dedicated FULL fallback requires old byte-proof
`None`, preserving every old `Some(bytes)` result. Every cycle descends proper
children. All old helpers, shared trees, SHORT/truth/non-NUL, receipt/46, cache
and owner/lifetime bodies remain literal; no arithmetic helper, runtime carrier
or native evaluation fallback is added.

Both proofs and conversions remain mandatory when one factor is zero: `0*bad`
and `bad*0` cannot suppress unsupported input or warnings. MIN*0/0*MIN are INT0;
MIN*1/1*MIN are INTMIN. The target is pinned PHP 8.5.10 CLI NTS64. Zend
`mul_function_fast` uses `ZEND_SIGNED_MULTIPLY_LONG` and produces DOUBLE only on
overflow; its slow route converts both scalar operands independently. The
existing numeric multiplication performs the same integer/product-range split.

Four positive originals change only their selector lines, preserving callbacks,
profile, streams and cache/owner histories. Two separate originals intentionally
exercise MIN*(-1)/(-1)*MIN and MAX*2/MIN*2 overflow. Those six originals run natively
once; exact saved bytes/path/CWD/profile are reused. Source-first observations
contain 27 completed products and 29 complete product SOURCE nodes, within
39 arithmetic snapshots/41 SOURCE nodes including retained Add/Sub controls.
All four deliberate overflows have the expected FLOAT bits; eleven inherited
fitting arithmetic observations in those controls remain separate. Folded and
skipped SOURCE facts remain distinct from completed runtime observations, and
both emitted CONCAT roots retain their established authority receipts.

The original CV post-law rejection reached the inner 280-second timeout; its
unchanged source, native/pre-law observations and failed control retain zero
agreement credit. A fresh CV control moves the first overflow to the earliest
class condition and swaps its arms to preserve the selected value, then restores
the former method point to a fitting product. Both overflow domains and every
other body/profile/stream byte remain unchanged. Its native original runs once
(seven unique originals overall), with only current-law observation/rejection
measurements at the original caps. It has no historical pre-law claim and does
not renew the original source-first evidence or passed comparisons/fixtures.

Actual-site, scalar/numeric, selected/skipped SOURCE, fence, child-valid overflow,
compatibility and authority fixtures retain the original caps. The compatibility
cut admits typed Mul(0,0) while the old raw NOT/CONCAT grammar and wider typed
CONCAT parent still refuse it. No maintained assertion changes or historical
campaign renewal are needed. Fixtures, overflow Unsupported controls and the
production load carry zero source-agreement credit. The
[review](../../coverage/semantics/magic-property-methodclosure-static-raw-multiply-operand-condition-typed-ternary-left-coalesce-quiet-get-review.json)
binds source, validation and fixed integration identities.

FLOAT/numeric-float, output overflow, warnings, nonnumeric/NUL/CV/owning values,
other operators and wider raw parents/selectors/lifetimes remain partial. The
full-core objective, inventory and exact holds are unchanged; this remains a
bounded selector certificate.
