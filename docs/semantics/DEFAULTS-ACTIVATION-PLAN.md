# User constants and untyped positional defaults

Current accepted baseline: reference code31640654, compiler7263bf5b,
author7aed92c3, independent3956fbe1, docs8eae3f4c; canonical884/7399e812.
This is the next bounded stage of the complete-core plan. Runtime6 owns runtime,
compiler5 owns compiler work, and review9 owns independent review. No default
source admission is claimed by this plan.

## Coherent acceptance units

1. Complete ordinary user-constant declaration, lookup and value ownership through
   compiler88/runtime89. Positive defaults need this prerequisite. Preserve
   declaration-time activation, sequential declarations, namespace/import/fallback
   resolution, case-sensitive names, duplicate diagnostics, selected/skipped
   constant-expression branches, original lines and abrupt cleanup. Constant table
   values must own their arrays and preserve COW across reads and function calls.
2. Integrate untyped positional defaults through compiler90/runtime91, starting
   from the accepted constant checkpoint. Supply arguments first, enter the real
   callee, receive omitted defaults in parameter order, then execute the body.
   Supplied arguments never evaluate their defaults. Defaults before a later
   required parameter are compiled and diagnosed but have no optional receive.
3. Add types and reference returns in later call milestones. Variadics,
   named/unpacked arguments, other callable forms and the remaining full core
   stay explicit; this plan supplies no family closure.

## Shared interface and constraints

The private signature17 prototype exposes a suspension after parameter guards
and before default/type/optional normalization. Start/resume reuse the existing
signature fold; legacy literal-only consumers retain their wrapper. The prototype
on historical877 is helper preparation, with357 native signatures,28 descriptors,
174 reference-return flags and eight shared-folder suspension controls. It is not
an accepted replacement for current884.

The source compiler resolves each request using existing constant compiler45 at
`declaration ++ [PCFIELD 3, PCINDEX i, PCFIELD 6]`. Parameter defaults disable
ordinary/persistent constant substitution, preserve true/false/null, and establish
original declaration magic/namespace/import context. Folding precedes validation
of the remaining constant expression, so an invalid skipped arm can disappear.
No second constant evaluator or host execution supplies semantics.

Ordered default descriptors carry parameter index, original origin and a stored
or deferred designation. Stored defaults borrow the existing unit constant pool;
deferred defaults use original source and compiled code roots. Descriptor and
root validation must be derived from checked source without reconstructing
arbitrary runtime values. Omitted reference parameters receive fresh ordinary
cells; actual alias acquisition promotes them, as in the pinned RECV_INIT.

Deferred receive caching is observable. Native originals show warnings once for
cacheable scalar/empty results and repeated warnings for refcounted array/string
results. String length alone does not identify cacheability. Resolve the precise
result/provenance contract against pinned source and original controls before
admission. Cache entries and constant values must retain their actual ownership;
failures must not install successful cache entries or execute the body.

## Evidence and review gates

Preserve native lint/run bytes, checked ASTs, complete current884 failure states,
original file/request profiles and actual executable/source hashes before edits.
Current independent originals cover omitted/supplied errors, selected/skipped
invalid defaults, required-after-optional, declaration magic/imports, repeated
array/reference defaults, escaped aliases, warning-cache result kinds and user
constant activation/fallback. Old agreeing cases remain agreements under their
original identity; Unsupported, timeouts and setup errors remain separate.

Before each acceptance unit, replay exact native sources on frozen paired inputs,
check descriptor projections and bounded public metadata corruptions, and run
meaningful owner/state cuts, adjacent resumes, selected full resumes and cleanup.
Review shared constant/compiler effects with focused existing gates; broaden only
for a concrete unresolved shared risk. Publish small code/evidence/review/docs
commits with exact production bridges. Final current-source/full-syntax/fresh
offline and complete-core validation remain required.

Authority: pinned `vendor/php-src`34308a6666b2d489c509541ea9befea9e2b42348;
Zend compiler `zend_compile_const_decl`, `zend_compile_params`,
`zend_const_expr_to_zval`, `zend_eval_const_expr`; VM DECLARE_CONST/RECV_INIT;
Zend AST evaluator and constant registration/lookup. The sibling development
source is not the oracle.
