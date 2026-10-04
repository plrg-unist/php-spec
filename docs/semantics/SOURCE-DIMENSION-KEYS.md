# Dynamic read keys and warning continuations

Module233 stages undefined key-CV reads and array/name conversions before the
original dimension consumer. `$GLOBALS[key]` rereads an undefined key in the
caller environment after its warning; a handler's root definition does not
change an undefined local CV. Once a global name has been selected, missing
lookup retains226's original null even if a handler creates the entry.

Ordinary arrays select their table after the key expression and before its
conversion callbacks. Undefined key CVs become the fixed empty key; null and
lossy/nonfinite float conversions retain their selected key through mutation
and rebinding. NaN emits the ordered range and precision notices. Handler false
fallback keeps that sequence; a throw skips the read and subsequent assignment,
preserving the original exception and typed destination.

Table ownership follows the source operands. Direct CV arrays remain borrowed;
computed/nested results retain their genuine temporary owner. The native
conversion protection can cause COW but does not become a permanent owner.
It lasts across both NaN notices and is dropped before lookup; a table with
only that protection then retires and yields null. Shared element references
remain live and can change the selected value. Terminal ordinary `isset` has
no protection during the initial undefined-key warning, then protects null or
float conversion. GLOBALS `isset` suppresses that CV warning while coalesce
demands it; both still perform required key conversion. Existing terminal
string `isset`/`empty` behavior is preserved with a dormant handler.

Certificates check source occurrence, line, reader mode, converted constant
keys/names and genuine CV versus temporary owners. Remaining float notices
must be an ordered suffix of the selected conversion. Consistent dynamic
selected values are runtime facts; the rules do not reconstruct their history
from a mutated CV. Saved emitters use the existing error-context validation,
and throwing cleanup releases real key/base operands without213's null write.

Author nine source comparisons and 62/59/55+70=246 reached assertions pass at
their separate original cuts. Independent fourteen originals and 76/78/81=235
checks pass at 9a8, with two NaN comparisons retained from 6f67. One actual71da
composition source passes inside a constructor in a parameter default with a captured
parent-private handler and Child called class. The
[ledger](../../coverage/semantics/dimension-key-review.json) records the original
tuples, failures, revisions and commands. The pinned engine contracts are
`zend_fetch_var_address_helper`, `slow_index_convert`, `zend_find_array_dim_slow`
and `zend_dval_to_lval_safe` in `vendor/php-src/Zend`.

The tracked source catalogue is `tests/semantics/dimension_warning_cases.py`.
`python3 -B tests/semantics/dimension_warning_prepare.py [fixture-id ...]`
compiles selected reached-state fixtures without executing native or model code.
Run the printed fixtures with the built numeric runner and current module list;
original capped launch commands, profiles and tuples are retained in the ledger.
Existing local binaries were reused; no fresh build or full-family closure is
claimed.

Read-write, reference, append/unset and compound/coalesce-assignment warning
continuations are required next. Object/magic key conversion, earlier missing
container producers, other string/scalar diagnostics and broader reference-result
consumers remain core obligations. Paused returns and request snapshot evidence
remain separate.
