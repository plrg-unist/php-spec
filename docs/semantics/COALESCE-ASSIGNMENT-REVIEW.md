# Coalescing assignment review

Code `f073c750` admits variable and dimension `??=` through checked source
execution. [Independent review](../../coverage/semantics/coalesce-assignment-review.json)
binds 137 exact sources and 18 separate outcome controls, eight author state
programs/3,760 assertions, seven independent programs/3,024 assertions, and nine
edited-descriptor controls/74 assertions. Eighteen fresh canonical CLI comparisons
pass; the named-GLOBALS original stays explicitly Unsupported. Object access and
request environment remain required work. Earlier full campaigns are historical.

The initial quiet read and the later write have distinct compiler occurrence
lines. `WRITES` records and exported `CODEWRITE` markers retain this distinction;
ordinary expression/effect walkers skip those markers. The writable compiler walk
uses original AST lines and memoized child facts without recompiling effects.
Constant names can emit the second conversion warning required by Zend. See
`zend_compile_assign_coalesce` and its expression memoization in the pinned
`Zend/zend_compile.c`.

Runtime module72 retains the prepared target while evaluating the RHS. Simple CV
keys/names are delayed reads, so `$a[$i] ??= ($i=2)` can write at key2. An evaluated
temporary is reused. A temporary containing a REFERENCE retains its acquired cell:
RHS mutation changes its refetched value, while source rebinding leaves the old
cell captured. A ternary can instead copy the resolved value. `ZEND_COPY_TMP` uses
`ZVAL_COPY`; dereferencing every saved temporary would lose these distinctions.
The [reference originals](../../coverage/semantics/coalesce-assignment-reference-originals.json)
retain matching source/lint outcomes.

Non-null results skip the RHS and release saved operands. The absent branch owns
the prepared base through `COALESCE_ASSIGN_WRITE`, then uses existing variable or
array writes and assignment-to-self handling. Dense checks compare complete resumed
states across budgets, unchanged CODE/POOLS, heap/source validity, and final empty
TODO/ORIGIN/HELD/ITERATORS, including nested tables, COW, cycles and throw/loop cleanup.

The original832 prototype accepted missing, zero and duplicate internal write
markers. All three raw states remain preserved and were reproduced exactly.
Guarded834 requires one positive write descriptor at every nested VAR/DIM
occurrence before the quiet read or RHS. Invalid internal code returns Unsupported
and clears continuations; this is an internal integrity check, not a PHP source
agreement. Seven earlier reviewer fixture-setup failures remain separate from the
corrected state runs. Parser-rejected temporary-target probes likewise remain
parser controls, not admitted source execution.

Canonical826 preserves every guarded834 semantic module and executable byte.
Only source/test orchestration differs; the final137 source multiset matches the
prior independent137 exactly. Historical state runs retain their own identities;
the author also reran the durable eight-program harness on current canonical
inputs. Focused compiler gates pass84 traces/22 descriptor controls/8 malformed
metadata cases, plus current quiet240, foreach90 and list111 checks. These do not
replace the eventual full quiet/CV checkpoint or full-core/syntax/offline closure.

The retained guarded GLOBALS boundary now has an explicit-request source witness
in [request publication](../../coverage/semantics/request-environment-review.json)
at652d10b7. Its original absent-request outcome is unchanged historical evidence.
