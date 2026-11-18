# Quiet integer UnaryMinus operands and FULL conditions

The quiet static USER methodclosure selector certificate admits UnaryMinus when
its closed typed child converts without warning to an integer and the negated
result fits signed 64-bit range. Results retain exact INT tags: NULL/FALSE and
INT0 become INT0, TRUE becomes INT(-1), and signed numeric INT STRING values
are converted before negation. Nested minus can restore a selected positive
integer while preserving its class/method name bytes.

One constructor-new operand clause authenticates the root and proper SOURCE
child, requires typed `Some(value)`, reuses
`coerce_number(value) = COERCED (NINT i) false`, and requires
`long_range(0 - i)` before returning `PINT (0 - i)`. One dedicated FULL fallback
requires old byte-proof `None`, then returns the typed result's echo. All old
typed and byte positives remain literal. Each new cycle descends the proper
child; shared trees, every other operand/FULL branch, SHORT/non-NUL/truth rules,
receipt/46 guards, caches and owner/lifetime bodies remain unchanged. No new
arithmetic helper, runtime carrier or native evaluation fallback is added.

The target is PHP 8.5.10 CLI NTS64. Pinned `zend_compile_unary_pm` and
`zend_try_ct_eval_unary_pm` lower unary minus to multiplication by integer -1;
the existing numeric semantics performs that operation. The output range guard
is essential: quiet INTMIN is a valid integer input, but negation produces FLOAT
`2^63`. A separate original, native observation, compiler/runtime observer and
post-law Unsupported control retain this boundary with zero agreement credit.
Its direct STRING and typed PLUS child are explicitly valid in bounds fixtures,
so rejecting the outer minus cannot be explained by a failed child proof.

Four positive originals change only their selector lines, preserving prior
callback bodies, profile, streams and cache/owner histories. Positive originals
and the intentional overflow original run natively once each; saved exact
bytes/path/CWD/profile are reused. Source-first MINUS30 completed snapshots and
complete SOURCE32 facts remain separate, alongside retained PLUS12/14 controls.
Completed integer results, folded/skipped SOURCE and queued FULL/coalesce work
retain their established distinctions; no source correction is needed here.

Fourteen maintained assertions in five older protocols are promoted, with exact
old AST/callee/argument expressions exercised in the fresh legacy value group.
Old raw-byte `None` assertions and every unrelated CASE field remain literal;
historical campaigns are not rerun. Separate source, actual-site, scalar/numeric/
legacy values, selected/skipped SOURCE, bounds and authority records retain the
original caps. Fixtures, the overflow Unsupported control and the production
load check carry zero source-agreement credit. The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-minus-operand-condition-typed-ternary-left-coalesce-quiet-get-review.json)
binds the source, validation and fixed integration identities.

INTMIN negation overflow, FLOAT/numeric-float, leading-number warnings, nonnumeric,
NUL/CV/owning values, wider parents/selectors and lifetimes remain partial. The
full-core objective and inventory status remain unchanged; this bounded
certificate is not a general PHP expression evaluator.
