# Compiler continuation

Continue the complete-core goal from PROGRESS and PLAN; never push. Read the
php/php-spec/p4-spectec skills, DESIGN/VALIDATION and
[LINKING-HANDOFF](LINKING-HANDOFF.md). Use only the pinned local PHP 8.5.10 CLI NTS, 64-bit
oracle and vendor/php-src. Model semantics in pure executable `.watsup`; engine
compile/eval answers never enter the specification. Preserve original bytes,
raw process outcomes, stable fingerprints and independent review. Source, helper
and edited checked-input evidence remain distinct.

Source control is accepted in `d87f3f9f`: **747 original-source comparisons and
25 explicit negatives**, plus compiler/metadata/order and runtime resumption gates.
See [source evidence](../../coverage/semantics/source.json) and
[control compiler evidence](../../coverage/semantics/control-compiler.json).
Only validation.oracle-pin is a closed inventory obligation; no semantic family
is complete. The 30,980-record syntax audit is historical after metadata changes; full
final syntax and offline portability audits remain required.

## Ownership and current interfaces

Compiler owns 11/15–19/21–23/45-constant-context/46/47 and compiler/static harnesses.
Runtime owns 20/30–43/44/45-dimension-write/50, execution adapter and source tests.
Coordinate narrow shared-file handoffs and runner builds. Compiler admission and
required runtime consumers commit atomically; compatible generated metadata may
land first. Do not resurrect the retired bare source/check/fold visitors.

- 11 `$pcsource(id,program)` retains exact checked AST and exhaustive generated
  occurrences. Identity is compiled-instance ID plus FIELD/INDEX path, never
  content equality or filename. Metadata does not change paths.
- 21 supplies ordered lexical work and resumes only matching successful ordinary
  compilation; callers accumulate warnings. Structural preorder is not compiler
  order. No AST-wide visible declaration registry.
- 22 retains original name, resolved bytes, qualification and optional fallback;
  23 performs only valid compile-time substitution. Namespace fallback is late.
  20's byte backend distinguishes missing from known-unmodeled: an unmodeled
  primary never falls through. See [SOURCE-CONTEXT](SOURCE-CONTEXT.md).
- 45 caches path/value/effective-line facts and binds visited paths to lexical
  contexts. Array prepass visits each value then key; VAR/ASSIGN/ASSIGN_REF stop
  that invocation, while ordinary compilation later enters their children.
  Partial facts retain roots. See [CONSTANT-CONTEXT](CONSTANT-CONTEXT.md).
- 46 exports ordinary expressions(path,endline,value?), access(PPR/PPW/PPUNSET),
  names(path,pnreference), ordered work and diagnostics. `$ppconstants` rejects
  conflicting bits/types/arrayIDs or absent required lines. Whole constant
  operands have no executable child roles. 33 retains compact descriptors and
  remapped permanent pools, never ppstate or isolated memory. Isolated HELD roots
  must become POOLS roots, not temporary runtime HELD. Only PPR consumes constants.
  See [SOURCE-COMPILER](SOURCE-COMPILER.md).
- 47 owns LOOPS context, literal jump legality and compile order: while/do body
  then condition; for init/body/step/condition; each if condition then body. It
  restores loop depth on success/error. Runtime 50 owns truth conversion, loop
  markers, origin restoration and budget resumption. See
  [CONTROL-COMPILER](CONTROL-COMPILER.md).

Bare jumps use exact terminator-token START lines, not statement end lines when a
close tag consumes a newline. Explicit depths use child AST lines. Body metadata
is positive brace/colon line or zero for a single statement. Empty bodies can be
eps or comment Nops; braced/alternative bodies can also contain one Nop. Empty
for with no Zend child uses its terminator. Type/range checks cannot authenticate
edited positions. Function/class keyword locations still need exact transport.

## Next source milestones

Runtime next owns truth/short-circuit/ternary/comparisons, then inc/dec, compound
writes and remaining numeric operators/casts. Agree a narrow 45/46 expression
handoff while compiler independently advances array and declaration contexts.
Existing access modes do not imply support for future quiet/compound/call modes.

Zend `zend_compile.c:10350` short-circuit compilation can skip RHS for constant false&&
or true||; a runtime CV holding false still compiles RHS. Full and shorthand
ternary compile both arms. Global `NAN && true` warns once at compile time,
`NAN || false` twice (10364/10366); `!NAN` and ternary warn at runtime, as does late
namespace NAN. Runtime retained 15 exact originals in `.tools/next-truth-oracle.json`
and its reproducer. Move these into canonical source evidence when implementing
exact skipped-child/folded-parent descriptors; do not use eager PFBINARY traversal.

1. Unpack: extend the single 45/46 array traversal from `zend_try_ct_eval_array` at 10085
   and `zend_compile_array` at 10935. Preserve unpack operand evaluation, integer-key
   append/string-key replacement, overflow behavior, partial facts and diagnostic
   priority. Coordinate runtime owners before source admission.
2. Destructure: follow `zend_verify_list_assign_target` at 3249 and
   `zend_compile_list_assign` at 3298 for syntax style, keys, holes, nesting, references,
   RHS acquisition and writable target order. Actual `[$a]=...` becomes Expr_List;
   Expr_Array used as a dimension base remains a temporary write error. Foreach
   additionally needs cursor/mutation ownership and loop context.
3. Declarations/defaults: collect ordered descriptors with unit/path, lexical
   namespace/import/strict context, exact compiler lines, signature and body.
   Compile body errors before runtime output, reset loops across function scope,
   and distinguish top-level binding from conditional/runtime declarations. Consume
   16/17 with explicit contexts and source-defined default materialization; do not
   assume their helper-only boundaries already support all imports/attributes/types.
4. Frames/calls: agree parameter evaluation/capture, by-reference binding, returns,
   CV scopes and frame/loop restoration. Reuse unit pools across calls; newly
   compiled instances get distinct identity. Runtime must not redo signature
   normalization. Then proceed through LINKING-HANDOFF's class/member visibility,
   publication, loading and variance protocol.

HTTP-variable assignment flags, computed variable-name warnings, source magic
constants, strict/declare effects and declaration contexts remain pending. Some
frontend namespace-placement and parameter/type checks still reject early; edited
helper success does not resolve those source-phase gaps. Preserve the exact
namespace-relative static divergence in DISCREPANCIES, with no new silent decisions.

Run source_compiler.py/control_compiler.py and relevant namespace/constant/context
helpers, then coordinated full source, ownership/pool/origin/resumption gates.
Frontend changes need make test/inventory and deterministic regeneration. Reviewer
owns raw failures/resolutions and inventory status; sampled successes do not close
families, and Unsupported/timeouts/interrupted runs never count as passes.
