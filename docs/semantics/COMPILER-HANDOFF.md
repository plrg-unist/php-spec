# Compiler continuation

Read PLAN, current PROGRESS and the php/php-spec/p4-spectec skills first. Never
push. Use only pinned PHP 8.5.10 CLI NTS64 and vendor/php-src as the oracle;
meaning belongs in pure `.watsup`, not host eval. Original sources, raw failures
and current fingerprints are required. Unsupported/tool failure/budget exhaustion
are not passes. No PHP constructor or semantic family is closed; only the oracle
pin obligation closes. Final complete syntax and fresh offline rebuild audits remain.

## Accepted state and ownership

See PROGRESS for current source counts and exact implementation/review commits.
Truth, comparisons and explicit reference-wrapper fetch history are source-active.
The wrapper correction is `3585707a`/`eebf79e9`, reviewed in `5b0dc0f2`; singleton
explicit wrappers survive owner-count changes and generic FETCH differs from final
ASSIGN_DIM. Runtime REF marker history is not an extra memory root.
Ordinary computed-name write fetching is corrected separately in `84d70299`,
reports `fa691044`, reviewed in `24c681d7`: creating a writable location does
not itself create an explicit reference wrapper. Preserve this distinction when
adding compound, destructuring, argument and frame acquisition paths.

Destructuring prerequisites preserve nested unpack (`d4706937`), original array
kind (`09f33419`) and leading-hole line (`87341500`). Genuine-list early conversion
is `5c756e5e`, reviewed in `861020db`: 20 exact skipped sources pass, while 14
retained reached targets remain explicitly Unsupported. Callable creation-line
metadata is `c6a7d67d`, reviewed in `1d32e9be`; two identical old checked trees
need different native diagnostic lines. No call execution was admitted by metadata.

Inc/dec/global-this source activation is `7d5718fb`, author reports `5b24a5f8`:
**1,484 exact sources +25 outcome negatives**, independently accepted on closure
`d399263a1c9f33bb445c958d624392ffc83d49df1c247df72b0c23ce59855d35`.
Compiler gates pass 1,526 native lints/15 emission observations and dedicated
108 lints/32 access paths/eight emission observations/12 context checks. Runtime
validates 154 source/state programs; independent dense resumption covers eight
programs/4,152 assertions at all 101 budgets. Final review checkpoint: `a3cee6bd`.


Compiler owns 11/15–19/21–23/45-constant-context/46/47, checked metadata/schema,
compiler helpers and docs. Runtime owns 20/30–44/45-dimension-write/50–53 and source
execution. Reviewer owns independent evidence, PROGRESS, inventory and discrepancy
history. Coordinate shared CASES/Makefile edits, Git index and Dune build starts.
Save all watched inputs, then run full evidence/inventory preflight before expensive
source campaigns; adding an archive without seeding isolated evidence fixtures
previously forced an entire final comparison rerun.

## Retained interfaces

- Occurrence identity is compiled-instance ID plus FIELD/INDEX path, never AST
  equality or filename. 11 retains exact checked nodes and structural occurrence
  catalogs. 21/22/23 carry lexical namespace/import/compiler order; no AST-wide
  declaration registry. Existing unmodeled names never fall through as missing.
- 45 separates partial FACTS, raw selected-child REDIRECTS and queued WARNINGS.
  Array prepass visits logical children eagerly; ordinary short-circuit compilation
  may skip them. Prepass ternary selects even a dynamic child; ordinary ternary
  compiles both. Variables, assignments/references and all four updates are explicit
  nontraversing prepass barriers, followed by ordinary child compilation if reached.
- 46 exports expression(path,endline,value?), ACCESS modes and executable redirects.
  Only visited PPR reads export redirects/use constants. Raw facts under folded
  parents are roots, not executable entries. Ordinary ternary copies selected
  values; raw prepass redirect preserves delayed CV/reference access.
- 33 resolves same-unit redirect targets in canonical source catalogs; pooled values
  precede redirects. Permanent POOLS differ from HELD temporaries. Constant export
  rejects conflicting scalar/array identities and missing operand/fact lines.
- PPRW update targets preserve nested base modes, read keys and allow append [].
  Direct call-return rejection precedes nullsafe-chain rejection and operand visits;
  a separate fallback makes those rules disjoint. `$this++` lint is accepted;
  missing object context is a runtime acquisition error, never a static rejection.
  Direct/literal assignment/reference rebinding and final unset reject statically
  before operands, while dimension bases/reference RHS retain runtime FETCH_THIS.
- `callableExprLine` is the actual argument-list opening token line for dynamic
  function calls, matching Zend's explicit `callable_expr` mid-rule capture.
  Named calls use the name line. Missing/nonpositive context is Unsupported;
  an edited positive value changes the diagnostic line. 20 includes the required
  call/static/nullsafe/property-chain line projections, not only admitted runtime
  value forms. Ordinary call execution remains a separate obligation.

Read SOURCE-COMPILER, CONSTANT-CONTEXT, COMPARISONS, CONTROL-COMPILER and
COMPILED-POOLS for tested rules. 47 preserves loop legality, compiler order and
restored loop context. Checked position type/range is not source authenticity.

## Next compiler work

1. Pair compound operators with runtime captured locations and remaining numeric/
   string operations. Fresh `.tools/{20,45,46}-compound-compiler.watsup` drafts,
   generated by `.tools/rebase-compound-compiler.py`, rebase onto the current incdec
   accepted incdec files. A paired private runtime replay passes 81 originals/1,204 assertions
   (`.tools/compound-rebased-source.json`), but independent and dedicated compiler
   phase/access/PFSTOP gates remain pending. Runtime's 588-source value expansion
   (`.tools/probe-compound-values.py`) is active at turnover; coordinate its finish
   before changing these draft hashes. Old `.tools/46-update-compiler.watsup` and
   its generator predate incdec/this/nullsafe corrections and must not overwrite
   accepted files. The fresh draft adds 12 explicit PFSTOP barriers and temporary
   shapes. Target is PPRW before RHS; keys are PPR, direct `$this` rebinding rejects
   (unlike inc/dec), parent ending line follows RHS, and existing potential-self
   DIM/CV handling remains. Runtime distinguishes direct-CV RHS reading, dynamic-name
   FETCH_RW before delayed RHS CV reading and final DIM location acquisition before delayed
   RHS read. Gate these against retained `.tools/update-compiler-originals.json`.
   Four `.tools/compound-fetch-timing-originals.json` sources confirm eager RHS
   `$missing+1` diagnostics precede dynamic-name/DIM target fetch; the paired
   timing report passes 56 assertions, still pending independent review.
   `??=` needs separate quiet-read and memoized-write semantics.
   `coverage/semantics/concat-cv-originals.json` records an existing literal-concat
   CV gap. Zend's parser folds concat when both operands satisfy its ZVAL predicate
   and `zend_binary_op_produces_error` guard (zend_ast.c484ff); ternary/compiler
   FACTS are not equivalent. Probe unary/folded literal contexts too. Preserve exact
   parser-created ZVAL line and classification when activating concat names.
2. Reached destructuring remains open. Preserve the 16 exact originals in
   `coverage/semantics/destructuring-list-target-originals.json` and their explicit
   14 reached Unsupported observations. `zend_verify_list_assign_target` validates
   RHS/referenceability before RHS compilation; outer mixed style, spread, RHS
   static read and referenceability can precede nested long-array rejection.
   Propagate nested reference requirements, evaluate RHS once, then process keys/
   fetches/targets with exact copy/reference ownership and emission-line changes.
   Converted Expr_List keeps List.kind plus destructuringArrayKind (original long1,
   short2); long-array rejection must precede mixed-style classification. First-hole
   compiler consumption remains pending, despite accepted metadata transport.
3. Ordinary Array_ omissions need a separate schema/compiler phase repair. Six
   immutable originals in `coverage/semantics/array-hole-phase-originals.json`
   include native-valid skipped logical/prepass branches. Do not exclude them as
   parser failures. Reviewer/root favor nullable Array_.items plus exact initial
   omission context; an ArrayHole constructor has no demonstrated need.
   Zend `zend_try_ct_eval_array` visits values before keys, continues past dynamic
   entries, and reports a visited null using the previous nonempty element's
   ORIGINAL AST line, or current compiler line when first. Do not use comma line
   for every hole or a folded child line. Add multiline keyed/unpack/folded/first
   nested-array witnesses before selecting the exact context transport. The 16
   author-only observations `.tools/array-hole-line-originals.json` now retain
   those cases: keyed value4, unpack3, original arithmetic2, parser-folded concat4
   or grouped concat5, nested first omission outercontext2 versus assignment
   barrier4. Repeat independently and archive unchanged before implementation.
4. Nullable schema change is manageable but cross-cutting. Current Array_.items is
   phpType12=list(ArrayItem), item phpType13; List.items is nullable phpType26/27.
   Making Array_.items nullable merges old26->new12 and old27->new13; later numbered
   domains shift by two (currently maximum71, 72 total domains including statement/
   expression). Confirm by normalized domain keys after generating; never assume
   IDs from position. Old13 widens and array consumers need explicit ABSENT handling.
   Remap both bare type names and variable suffixes. At least 18 production semantic/
   helper files mention old26+ types, including 11/16–18/20–21/30/36–37/40–41/45–47/50.
   Also regenerate schema/occurrence walkers and inspect all repository consumers.
   Preserve nullable item indices and fresh trailing-hole commas, with no invented
   expression values. Gate original→checked→printer→frontend and exact skipped/
   visited compiler behavior together; syntax acceptance change is intentional.
5. Unpack drafts `.tools/45-unpack-compiler.watsup`, `46-unpack-compiler.watsup` and
   18 originals predate comparisons; rebase before use. Prepass all values/unpack
   operands before constant construction. Scalar unpack fails statically only for
   a fully constant array; dynamic/reference entries defer to runtime. Integer keys
   append, string keys replace, append overflow defers, partial facts remain roots.
   Foreach requires persistent buckets/cursors and mutation/COW/reference lifetime.
6. Declaration/default/frame and call integration follows LINKING-HANDOFF and the
   reviewed pure static/signature helpers. Actual functions/closures/classes,
   properties, exceptions/unwinding, generators/Fibers, dynamic sources, callbacks
   and collection remain open; helper success is not source activation.

## Evidence and scope discipline

The incdec compiler helper embeds original bytes rather than reading oracle archives;
source catalog copies those literals to avoid a `source_compiler` import cycle.
Keep author and independent source/state/resumption gates separate. Retained prepass,
callable-line and nullsafe-overlap failures must remain immutable with explicit
resolution evidence. Header assignment flags, computed plain-write/reference/unset environment-name
protocols and broad frame/object contexts are still assigned obligations, not inferred from update tests.

The namespace-relative `static` discrepancy remains the sole intentional divergence,
with source activation evidence pending. All other irregularities follow the pin.
The historical 30,980-record syntax audit must be rerun at final closure after all
metadata/schema changes; copied binaries do not establish offline portability.
