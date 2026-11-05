# User constant compiler

Compiler88 prepares the initializers of ordinary user constants for runtime89.
The paired source increment is recorded in the [independent review](../../coverage/semantics/user-constant-review.json).
Defaults and the complete constant family remain open.

A `NStmtConst` walks its declaration list at field1 in order. Each `NConst`
initializer is field1 of that declaration. Existing45 folds it in the current
lexical environment, then88 validates the remaining expression, following the
original folded facts and redirects. Invalid operations in eliminated arms can
therefore disappear. Legal object, property, class-constant and callable forms
whose core consumers remain unavailable are explicitly Unsupported. Dynamic
class names and `static::` retain their separate compile errors.

Initializer compilation precedes special-name and import-conflict diagnostics.
The declared `CODENAME` belongs to the actual `NConst` origin; it preserves the
qualified source spelling, has no fallback, and is distinct from initializer
constant-fetch names. A declaration `CODEEXPR` retains the compiler's declaration
line. Runtime registration normalizes namespace prefixes and preserves terminal
case; this is not uniform lowercasing. The existing source environment's SEEN
and import rules retain their pinned compile-order case distinction.

Attributed global declarations with at least two constants enter this compiler
at the first constant-name line. Their initializers and name checks run in order
before the final multi-constant attribute error. Remaining constant reads and
compiled closure ends advance the diagnostic cursor; literals retain it. The
constant walk follows folded facts and redirects, visits array values before keys,
and checks constructor argument structure before values. It compiles reached
closure bodies once, preserving their earlier errors without emitting runtime
operands for a declaration that cannot execute. Qualified class keywords retain
their distinct folding, NEW/callable and `::class` checks.

Attribute arguments are not compiled before this error; completed parser encoding
warnings inside them still precede it. The error terminates eval/included units
before catch/finally. Compiler-only source predicates admit initializer contexts
without extending runtime constant declaration authority. Single attributed
constants, attribute compilation and the full constant family remain partial.
[COMP181 evidence](../../coverage/semantics/attributed-constant-compile-review.json).

The initializer uses ordinary source expressions and the existing unit code and
constant pool. Successful folded child values remain pool owners even when a
parent fold makes their execution unnecessary. Non-owning `PCCLASS` companions
carry the allocation provenance explained in [constant value classes](CONSTANT-VALUE-CLASSES.md).
Runtime integrity projects declaration names, lines and compiled pool class
descriptors from checked source, including units without function declarations.
Runtime value/class tags and topology are checked without reconstructing values.
A missing or duplicate descriptor is not a PHP error or successful execution.

Compiler889/cb31d858 retains 45 exact native compiler phase comparisons, ten
explicit pending legal forms and29 declaration assertions. A separate40-source
class gate checks120 descriptor assertions alongside native lint. Existing
constant-context42+5, source-context233 prefixes and additional controls, and
magic48/context regressions pass on the same frozen bytes. Historical887 and
its initial line/import failures remain separate; test setup failures and the
incorrect float-cast class expectation are retained rather than reclassified.
The float-to-string cast still follows existing45's deferred policy.

Authority: PHP8.5.10 source34308a6666b2d489c509541ea9befea9e2b42348,
`Zend/zend_compile.c` constant declarations and constant-expression folding;
`Zend/zend_constants.c` registration; `Zend/zend_vm_def.h` DECLARE_CONST.
