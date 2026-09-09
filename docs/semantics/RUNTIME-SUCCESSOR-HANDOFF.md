# Runtime successor handoff

Read PLAN.md, PROGRESS.md, applicable AGENTS and php/php-spec/p4-spectec skills
first. Root orchestrates; compiler_next owns compiler/static/frontend work and
review4 performs independent review. The full-core objective remains open. Never
push. Semantics after checked AST remain pure .watsup; pinned local PHP 8.5.10 is
only the oracle. The pending comparison overflow defect must follow the pin; it is
not an intentional divergence. Existing separately documented ledger decisions,
including namespace-relative static behavior, remain unchanged.

## Accepted checkpoint

Current source implementation e7dac829 and independent review 682bcba0 passed
854 exact source observations + 25 negatives on closure 10a40a12. The final helper
archive-input hash repair and mutation rejection are included; earlier 854 evidence
is historical only. Independent 44 originals, four programs across 163 budgets
(3,316 assertions), runtime 71/1,344, compiler 79/896, constants 42+5 and canonical
origins/bridge/ownership all passed. Do not rerun unchanged accepted gates.
See [RUNTIME-BRIDGE-HANDOFF.md](RUNTIME-BRIDGE-HANDOFF.md) for precise prior
control/write/namespace/pool checkpoints, current source contracts and evidence.

Runtime 20/30/33/35–43/50/51/52, source harnesses/reports and runtime docs transfer to
successor. Coordinate any 02/04 numeric helper edits explicitly; compiler_next
owns 45/46 plus comparison mappings. Reviewer owns inventory/PROGRESS/README and
review artifacts. Stage only owned/explicitly handed files; atomic compiler/runtime
source commits prevent an intermediate wrong-admission HEAD. Serialize Dune build
starts. Freeze all watched bytes before authoritative source/helper gates.

The sole public source path is `$php_run` through ordered compilation. Old source
checkers and runners are removed; the unchecked trace wrapper is test-only. Read
[RUNTIME-BRIDGE-HANDOFF.md](RUNTIME-BRIDGE-HANDOFF.md) before changing runtime 33:
raw prepass redirects must preserve delayed CV/reference/base results, boolean
redirects consume only RHS truth, and ordinary ternary arms use VALUE_COPY. Pools,
CODE and explicit structural origins survive cleanup/resumption. No AST rewriting
or equality-based occurrence lookup is permitted.

## Immediate next source slice: comparisons

All comparison files below are **unpublished .tools drafts**. Production still
returns Unsupported for ==/!=/</<=/>/>=/<=>. Root agreed to complete comparisons
next, then increment/decrement/compound assignment and remaining numeric operators/
casts, alongside paired unpack/destructure and later foreach. Do not expand the
current comparison gate into unrelated operators.

- .tools/20-comparison.watsup: production 20 plus pbin EQUAL NOTEQUAL LESS LESSEQUAL
  GREATER GREATEREQUAL SPACESHIP and narrow first-child source-line projections.
  Apply its small delta to current 20; do not overwrite later unrelated changes.
- .tools/52-comparison.watsup: substantive six-value comparator and seven runtime
  rules. Reuses BINARY_LEFT/RIGHT delayed reads and HELD input roots. Greater forms
  evaluate original left/right order, then compare reversed values with less/<=.
  Pure porder is ORDER int or ORDERRECURSIVE. The wrapper maps recursion to the
  existing Error at the consumer line. Object/resource/callback comparisons and
  engine stack exhaustion remain separate pending scope.
- .tools/45-comparison-compiler.watsup, compiler-owned generator
  .tools/draft-comparison-compiler.py: seven pfshape mappings and warning-permitting
  compile folding. Existing 46 binary traversal is retained.
- .tools/probe-comparison-source.py and .tools/comparison-source-smoke.json:
  actual checked-source alternate 20/45/52 campaign passed 117 programs/1,638
  assertions, with actual draft-spec hashes. 91 programs compare seven operators
  in both orientations; 26 exercise constant array prepass. This is smoke, not
  acceptance of comparison semantics.
- .tools/comparison-phase-originals.json and .tools/comparison-compiler-checks.json:
  compiler_next retained 48 original phase/line programs and passed their lint
  gate plus access/export controls. Include these exact bytes in the source gate.
- .tools/COMPARISON-RUNTIME-NOTES.md: source anchors and intended type/array rules.

Critical comparison boundaries are detailed in .tools/COMPARISON-RUNTIME-NOTES.md:
NaN/missing-key arrays are non-antisymmetric; NaN/null/bool has no coercion warning;
string overflow/infinity fallbacks use scanner provenance; arrays use same-ID fast
paths, left-only recursion protection and unordered exact-key lookup. Preserve
original left-to-right evaluation even when greater compares reversed values.

## Confirmed unpublished draft defect: overflow prefix with suffix

`coverage/semantics/comparison-overflow-draft-disagreement.json` retains four exact
original sources, checked ASTs, native process bytes, model numeric-list terms and
decoded output bytes, plus the actual draft hashes. Two are disagreements:

- `echo "10000000000000000000e-19" <=> "2";`: pinned PHP outputs 1; draft outputs -1.
- `echo "-10000000000000000000e-19" <=> "-2";`: pinned PHP outputs -1; draft outputs 1.

The nineteen-digit exponent control and twenty-digit decimal-large control match.
No production behavior is affected because comparison admission is still absent.
Reproducer: .tools/capture-comparison-overflow.py. Fix only after retaining the raw
report; no fix has been made. `_is_numeric_string_ex` stops its long digit scan at
MAX_LENGTH_OF_LONG, sets oflow_info, then parses the remaining decimal/exponent
suffix as double. The suffix can rescale the final value back into integer range,
while the earlier overflow flag still controls comparison. The draft
string_integer_overflow incorrectly requires a purely integer spelling. Track the
actual scanner provenance (including leading zeros, signs, nineteen-digit bounds
and suffixes); do not infer it from final float bits.

Before source publication: fix and independently probe this edge, retain both
old mismatches as passing cases, expand recursive-array/copy/delayed greater-order
cases and source warning/line/prepass contexts. Rebase mappings as needed, register
52 and source witnesses atomically, then run exact full source plus relevant helper
and independent state/origin/ownership gates under one final frozen fingerprint.
Never relabel or discard prior disagreements, and never mutate report fingerprints.

## Parallel compiler work and next arrays

Compiler_next has .tools/45-unpack-compiler.watsup /46-unpack-compiler.watsup and
18 exact source phase originals in .tools/unpack-compiler-originals.json, with a
passing compiler probe. Unpack visits all array operands in the constant pass
before construction; scalar unpack is static only for a fully constant array,
otherwise a runtime Error. Integer keys append, string keys replace, and append
overflow defers to runtime. Rebase these drafts atop accepted comparison changes.

Reviewer deed0416 archives 28 destructuring metadata witnesses. Compiler_next is
starting compatible frontend prerequisites: nested unpack-flag preservation,
long-array syntax and first-hole comma token line. Coordinate their publication/
build/freeze windows before activating comparisons, avoiding invalidated campaigns.
Foreach subsequently needs stable bucket identity/cursors and owner semantics
under deletion/reinsertion, not a list-index iterator. Declarations/call frames and
broader object/request/callback behavior remain open core work.

At handoff all runtime-owned production changes are committed; no runtime process
or source gate remains active. Comparison drafts and the reproduced defect remain
for the successor. Compiler/reviewer may publish their explicitly owned metadata
work during rotation; preserve it.
