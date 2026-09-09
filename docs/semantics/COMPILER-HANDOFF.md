# Compiler continuation

Continue PLAN and PROGRESS toward complete core; never push. Read the php,
php-spec and p4-spectec skills and DESIGN/VALIDATION. Use only local pinned
PHP 8.5.10 CLI NTS64 and vendor/php-src. Runtime meaning belongs in pure `.watsup`;
engine compile/eval answers are differential evidence only. Retain original bytes,
raw failures and stable fingerprints. Unsupported, crashes and budget exhaustion
are not passes. No semantic family is closed; only validation.oracle-pin is closed.
The 30,980-record syntax audit is historical after metadata changes. Final complete
syntax and fresh offline rebuild audits remain required.

## Current checkpoint and ownership

Truth source activation is `e7dac829`, reviewed in `682bcba0`: 854 originals plus
25 negatives. Compatible destructuring spread preservation is `d4706937`, original
array-kind preservation `09f33419`, independently reviewed in `d4231d20` and
`b0f11653`. The reviewed comparison implementation validates 1,142 originals plus 25 negatives,
1,184 compiler lints and 48 dedicated phase lints; consult PROGRESS for its
commit and independent evidence.
First-hole metadata also preserves the actual leading comma line through checked
transport; `tests/list_line_metadata.py` covers 31 source/encoding profiles and
409 boundaries. Empty `list()` is excluded. Compiler consumption remains pending.
Dynamic calls additionally retain `callableExprLine`, the opening argument-list
token line captured by Zend's `callable_expr` reduction. Named calls use their
name line. Two archived identical old checked trees require different native
write-context errors; metadata transport alone does not admit call execution.

Compiler owns 11/15–19/21–23/45-constant-context/46/47, metadata and compiler tests.
Runtime owns 20/30–44/45-dimension-write/50–53, execution and source tests. Reviewer
owns independent evidence, PROGRESS, inventory and discrepancy status. Coordinate
shared files, Git index and Dune build starts. Source admission and its runtime
consumers commit atomically; compatible metadata prerequisites may land first.

- 11 retains exact checked AST and source occurrences. Identity is compiled-instance
  ID plus FIELD/INDEX path, never AST equality or filename.
- 21/22/23 preserve compiler order, lexical namespace/import context and exact name
  resolution. Namespace fallback is late; known-unmodeled primary names never fall
  through. Do not introduce an AST-wide visible declaration registry.
- 45 distinguishes partial prepass FACTS, raw selected-child REDIRECTS and queued
  WARNINGS. Array prepass visits logical children eagerly, but ordinary short-circuit
  compilation may skip RHS. Prepass ternary selects even a dynamic child; ordinary
  ternary compiles both arms. VAR/ASSIGN/ASSIGN_REF stop a prepass invocation.
- 46 separately exports ordinary expressions(path,endline,value?), access modes,
  executable PPR redirects(parent,target,Boolean-coercion flag), names and work.
  Skipped facts/redirects do not become executable. Ordinary ternary copies selected
  values; a raw prepass redirect preserves delayed CV/reference access. Grouping
  legality is checked only when ordinary ternary compilation is reached.
- 33 resolves redirects through canonical same-unit occurrences, not tree rewriting;
  constant pools precede redirects. Permanent POOLS remain distinct from temporary
  HELD roots. `$ppconstants` rejects conflicting bits/types/array IDs and missing
  required lines. Only PPR reads constants. New compiled instances get distinct IDs.
- 47 preserves literal loop legality, compiler order and loop-context restoration.
  Exact body/terminator metadata and effective ending lines are required; type/range
  checks do not authenticate edited positions.

See CONSTANT-CONTEXT, SOURCE-COMPILER, CONTROL-COMPILER and COMPARISONS for the
accepted rules. Comparison folding permits its engine coercion warnings while
arithmetic keeps separate error-producing operand guards. Both comparison archives
are direct helper inputs and explicit inputs of the broad source fingerprint.

## Immediate continuation

Reference-wrapper acquisition is corrected in `3585707a`, reports `eebf79e9`,
review `5b0dc0f2`: 1,163 exact sources plus 25 negatives and 1,205 compiler lints.
Singleton explicit wrapper history survives owner-count changes; generic FETCH
and final ASSIGN_DIM keep their distinct diagnostics. New mutation source
operators still need paired compiler/runtime activation.

Compiler scratch preparations, all outside watched inputs:

1. `.tools/46-incdec-compiler.watsup` adds PPRW for four updates, permits append [],
   preserves key PPR access and rejects direct call returns/nullsafe chains/GLOBALS
   before traversal. `.tools/46-update-compiler.watsup` also has 12 compound operators:
   target before RHS, RHS ending line, existing DIM self-CV special compilation.
   Coalesce assignment requires a separate memoized quiet-read/write design.
   `.tools/draft-update-compiler.py` generates both. The retained 48 originals are
   `.tools/update-compiler-originals.json`; 47 parse and pass scratch lint/invariant
   checks, one temporary target is a matching parser rejection. Additional explicit
   PPRW access probes are in `.tools/probe-update-compiler.py`. These are not runtime
   admission. Runtime must supply exact expression-line projections; call-target
   fallback zero otherwise prevents the intended static rejection.
2. Genuine-list nested array conversion now precedes the global ordinary-array
   omission check. `tests/list_target_metadata.py` binds all 16 immutable originals
   and checks plain/UTF-16BE checked and fresh-printed diagnostic families; 20
   native-valid skipped sources are in the source campaign. Reached destructuring
   compilation remains pending: preserve outer style, spread, RHS read and
   referenceability errors before long-array rejection.
3. The global empty-array checker also rejects valid skipped ordinary array holes:
   `coverage/semantics/array-hole-phase-originals.json` retains six originals, three native-valid
   short-circuit/prepass-skipped cases and three visited-error controls. After the
   first-hole/genuine-list prerequisites, introduce a faithful checked Array_
   omission representation and defer rejection to exact compiler visits. This is
   an outstanding source-completeness gap, not an acceptable parser exclusion.
4. Unpack drafts `.tools/45-unpack-compiler.watsup` and
   `.tools/46-unpack-compiler.watsup` passed 18 original lints/invariant controls;
   rebase them onto comparisons before use. Traverse every operand before constant
   construction; scalar unpack is static only for a fully constant array. A dynamic
   entry/reference defers it to runtime. Integer keys append, string keys replace,
   append overflow defers, and partial facts keep roots. Actual runtime/source
   consumers remain pending.

## Remaining source contexts

Destructuring follows zend_verify_list_assign_target / zend_compile_list_assign:
propagate references and validate RHS first, evaluate RHS once with correct
snapshot/reference ownership, then keys/fetches/targets in compiler order. Retain
per-item fetch emission lines before compiling target assignments. Converted
Expr_List keeps List.kind plus destructuringArrayKind (original long=1, short=2);
long-array rejection must precede mixed-style classification. Foreach also needs
cursor/mutation ownership and loop context.

Then activate ordered declaration/default descriptors, exact keyword lines and
lexical contexts; compile body errors before runtime output, reset loop scopes and
distinguish top-level from conditional binding. Calls need evaluation/capture,
reference binding, returns and frame restoration. Existing signature/type helpers
are not source admission. Continue LINKING-HANDOFF for classes, visibility, loading
and variance. HTTP-header assignment flags, computed-name warnings, magic constants,
strict/declare effects and remaining frontend early-check phase gaps are pending.
Preserve the intentional namespace-relative static divergence in DISCREPANCIES.
