# Checked constant-expression work

`45-constant-context.watsup` supplies an internal compiler helper for the admitted
scalar, named-constant, arithmetic, identity, Boolean, conditional, array and dimension expressions
in an explicit lexical namespace/import environment. It retains
partial constant folds as facts about exact checked source occurrences. The
ordered source compiler uses it through `46-source-compiler.watsup`, and
`33-runtime-compiler.watsup` installs and consumes its values for the admitted
source subset.

The source is PHP 8.5.10 `vendor/php-src/Zend/zend_compile.c`:
`zend_eval_const_expr` (12088 onwards), `zend_try_ct_eval_array` (10085 onwards),
and the binary/unary compile-time guards (9952 onwards). The string DIM leaf is
shared with `44-dimension-read.watsup`; array DIM separately accepts only integer
and string keys. Runtime conversion accepting a Boolean or floating-point key
does not establish that constant evaluation folds that dimension.

| Interface | Contract |
| --- | --- |
| `$pfbegin(id, program)` | Construct the canonical checked source unit, empty constant store and empty occurrence facts. The caller allocates the compiled-source-instance ID. |
| `$pfprepare(state, path, expression, environment, line)` | Perform one constant-expression invocation at the exact checked occurrence. Require a positive current compiler line and the existing lexical `plenv`. |
| `state.SOURCE` | Original checked program, unit ID and generated structural occurrences. Metadata and expression syntax remain unchanged. |
| `state.MEMORY` | Isolated pure constant store. Completion is `NORMAL`, a source-backed `STATICERROR`, or explicit `UNSUPPORTED`. |
| `state.FACTS` | Relative path, folded value and effective compiler line; their identity includes the enclosing source-unit ID. Array values designate tables in this store. |
| `state.REDIRECTS` / `state.WARNINGS` | Selected conditional occurrence replacements and ordered compiler-warning bytes/lines; ordinary compilation exports only redirects it actually visits. |
| `state.VALUE` | Optional whole-expression folded value. Its absence does not discard successfully folded children. |
| `state.ENV` / `state.CONTEXTS` | Active lexical environment and the environment first used at each visited path. Reusing a path under a changed environment is rejected, even if its prior value did not fold. |

The compiler retains states constructed by these helpers; they are not an
external serialized-state ingestion format. Entry verifies canonical source
occurrences and exact selected expression equality, including metadata. A forged
path, a changed selected expression, missing compiler line or unsupported lexical
context does not become a successful fold. Earlier unsuccessful completion is
preserved. Constant names use `22-name-resolution.watsup` and the substitution
rules in `23-named-constants.watsup`. Fully qualified, namespace-relative, imported
and ordinary names retain their qualification-dependent behavior. In a namespace,
unqualified `true`, `false` and `null` can fold before ordinary lookup; unqualified
`NAN` remains a runtime fallback. Constant aliases use exact case, while qualified
class-import prefixes use ASCII lowercase keys. No fallback lookup occurs during
constant substitution.

Each successful value is cached at its structural path. A later compiler visit
to that occurrence reuses it; a distinct occurrence has a distinct fact. Each
retained array fact also contributes a persistent `MEMORY.HELD` owner root, so
replacing the transient result or pruning the heap cannot erase an earlier pool
value. Temporary failed array construction is discarded, while its previously
folded child facts remain. Runtime installation remaps the tables once and retains
permanent compiled-unit roots separately from runtime temporary roots. Reuse is
by source occurrence, rather than by expression equality. While/do/for source
execution reuses installed pools; future function execution must preserve the
same compiled-source ownership contract.

Constant evaluation visits both operands of admitted binary operators (including
short-circuit operators), and visits
a dimension's base then key. An absent dimension key errors before either child
is visited. An array first visits each entry's value then its key, in entry order.
It processes every entry before deciding whether the array can be constant, even
when earlier values are nonconstant or an entry is by reference. The second pass
constructs a table only if all values and keys are constant and all entries are
by value. Failed arithmetic, diagnostic-producing key conversion and missing DIM
values remain for ordinary compilation/execution. An array used as a constant
array key raises the compile-time `Illegal offset type` error.

Variables, assignments, reference assignments, all twelve compound assignments
and all four increment/decrement
forms stop this constant-evaluation
invocation without visiting their children. This is not an ordinary compilation
barrier: the source compiler compiles their children using the appropriate
operand rules and invokes constant evaluation for each subsequently compiled array.
The helper does not infer ordinary compilation order from structural preorder.
Unimplemented constant-evaluation kinds, including unpacking, are explicit
Unsupported; this helper does not claim all PHP constant expressions. Empty array
holes are not representable in the current checked `NExprArray` item domain and
remain a separate frontend/compiler obligation.

Run `python3 tests/semantics/constant_context.py`. The campaign uses original
checked sources whose outer array invokes constant evaluation, then observes
values using an appended PHP test function included in that same checked source.
Whole-value comparisons, expected nonfolding cases, partial-child assertions,
assignment barriers, native compile errors, compiler-line assertions and edited
boundary inputs remain distinct in `coverage/semantics/constant-context.json`.
It checks persistent roots after clearing the transient result and pruning,
repeated occurrence reuse, and distinct paths for identical NaN array literals.
These are helper/compiler-context observations, not completed source-machine
execution comparisons.

Source-unit IDs and occurrence paths now travel through ordinary compilation and
runtime tasks. The source consumer installs the persistent pool and uses compiled
read values and ending lines before evaluating remaining children. The old
whole-program constant-read prepass and recursive array-fold classifier are no
longer the public source compilation path. The ordered compiler no longer depends
on their direct-variable/bare-break checks; obsolete definitions were retired in
`846dc3d2`. Generic scalar/string reads and while/do/for continuations consume the
compiled source descriptors. Function compilation and execution remain pending.

Each `PFFACT` retains the effective line of its constant AST node. Original integer, float and string leaves keep their source lines. Actual constant-expression rewrites use the invocation compiler line, matching `zend_eval_const_expr` replacing the node with `zend_ast_create_zval` (`zend_compile.c:12380`, `zend_ast.c:88`). The original checked syntax remains unchanged. `$pffactline` exposes this provenance to ordinary compilation; cached facts retain the first rewrite line across repeated evaluation.


Original string leaves use the shared `$string_line` rule from `20-machine.watsup`.
Quoted literals keep `startLine`; heredoc/nowdoc kinds 3 and 4 use the following
line, including empty strings, indentation, CRLF and a binary prefix. The pinned
parser returns the string-content token (or creates the empty value after the
opening newline), and the scanner stamps that token's start line
(`zend_language_parser.y:1500`, `zend_language_scanner.l:3194`). Constant-expression
rewrites still use their invocation line, independently of original string kind.
Absent kind metadata permits only a proven single-line fallback; missing multiline
kind, an explicit invalid kind, or a missing/nonpositive source line yields line0.
Ordinary checked compilation then reports missing compiler context instead of
inventing a line. `tests/semantics/string_lines.py` compares all12 retained original
source witnesses through native PHP and the source machine, two encoded profiles
through the compiler, and seven edited metadata boundaries. Encoded-profile checks
do not claim the source CLI accepts those profiles.

Boolean folding follows its compiler phase. The array prepass visits both logical
operands before selecting a result; ordinary short-circuit compilation can skip
its right operand. Constant NaN Boolean conversion warnings remain compiler events,
including the ordinary OR compiler's second conversion when it short-circuits.
Unary not defers every float operand; XOR permits constant conversion warnings.

A prepass conditional with a constant condition replaces itself with its selected
child, including a nonconstant child. `REDIRECTS` records the original and selected
paths without changing the checked AST. The selected child's cached literal line
and delayed-read/reference behavior survive. A nonconstant condition visits both
arms. Ordinary ternary compilation visits both arms and applies nested-chain
legality using checked grouping metadata; a conditional erased by prepass selection
is not checked later. `truth_compiler.py` and `truth_expressions.py` separately
validate compiler diagnostics/descriptors and actual source execution.
