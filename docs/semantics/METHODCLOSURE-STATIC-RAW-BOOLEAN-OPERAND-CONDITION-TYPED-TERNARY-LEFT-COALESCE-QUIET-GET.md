# Quiet typed Boolean operands and FULL conditions

The quiet static USER methodclosure selector certificate admits `&&`, `and`,
`||`, `or` and `xor` over closed typed children beyond the existing byte proof.
Each result is an exact BOOL, including when used as a FULL condition. For
example, `true and ((true ? null : false) ?? false)` yields FALSE; a surrounding
coalesce retains FALSE rather than selecting its right operand.

Five constructor-specific operand clauses require old byte-proof `None`,
authenticate the root and both proper SOURCE children, and require typed
`Some(value)` for each child. Closed NULL, BOOL, range-checked INT and non-NUL
STRING values have no callbacks, owners or warnings. Their echo bytes are falsey
exactly when empty or STRING0; STRING00 remains truthy. AND/OR/XOR return `PBOOL`
from these truths. Certifying a skipped AND/OR child proves its closed SOURCE
without executing it; unsupported or owning skipped children still reject.

Five constructor-specific FULL fallbacks require the same old refusal and typed
BOOL result, then return its echo. `Some(empty)` is a successful false condition,
distinct from failed `None`. Every old byte/typed/helper branch, including NOT,
remains literal. Each new recursion cycle descends proper children, so induction
preserves every old positive value. Shared trees, SHORT/non-NUL/truth rules,
receipt/46 guards, caches and owner/lifetime bodies remain literal; no runtime
carrier or native evaluation fallback is added.

The target is PHP 8.5.10 CLI NTS64. Pinned routes are
`zend_compile_short_circuiting`, the parser's AND/OR spellings,
`ZEND_JMPZ_EX`, `ZEND_JMPNZ_EX`, `ZEND_BOOL`, `ZEND_BOOL_XOR` and
`boolean_xor_function`. Four fresh originals change only their FCC selector
lines, preserving callback bodies, profile, streams and cache/owner histories.
Native originals run once; exact bytes/path/CWD/profile are reused afterward.
Source-first Unsupported4 and Boolean40 snapshots remain distinct from complete
Boolean SOURCE29 facts, alongside TERNARY77/82 and COALESCE87/96. SHORT snapshots
separate completed BOOL skips from queued-right PNULL; finished truth coercions
include compiler redirects, and XOR snapshots observe both resolved inputs and
the completed BOOL. A v1 observer syntax failure occurred before execution and
is retained with zero credit; the corrected observer records remain separate.

Six maintained assertion tails in four older protocols are promoted. Static CASE
bridges preserve every other source, stage, count and check, and the fresh values
cuts exercise all six exact old ASTs/callees. Old raw-byte assertions remain
literal and historical campaigns are not rerun. The original values fixture hit
the 3 GB allocation limit before producing an assertion result. Its 117 checks
are partitioned without changes into two cuts, repeating only binding
prerequisites and standard fixture checks; all other CASEs remain literal.
Source, actual-site, value, selected/skipped SOURCE, bounds and authority checks
retain the original caps. Fixtures and the production load check carry zero
source-agreement credit.
The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-boolean-operand-condition-typed-ternary-left-coalesce-quiet-get-review.json)
binds the source, validation and fixed integration identities.

Other condition roots beyond the existing proof, typed UnaryPlus/UnaryMinus,
FLOAT/CV, nonquiet or NUL-bearing operands, owning values, wider parents/selectors
and lifetimes remain partial. The full-core objective and inventory status remain
unchanged; this bounded certificate is not a general PHP expression evaluator.
