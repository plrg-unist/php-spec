# Ordered ordinary source compilation

`46-source-compiler.watsup` combines the checked source-unit identity, ordered
namespace/import context and constant-expression helpers for the source statements
and expressions currently admitted by the runtime. It produces compiler work and
operand descriptors from the retained AST. The source runtime invokes it before
executing recorded work through `33-runtime-compiler.watsup`.

`$ppstart(id, program, file)` constructs a checked source unit and returns:

| Field | Meaning |
| --- | --- |
| `FOLD` | Original canonical source unit, isolated constant store and partial constant-evaluation facts. Its `VALUE` is a working register, not a whole-program value. |
| `WORK` | Successfully compiled ordinary statements, in compilation order, with original paths, exact statements, lexical environments and final compiler lines. |
| `EXPRESSIONS` | Per-expression path, final compiler line and optional constant code-generation operand. |
| `ACCESS` | The corresponding ordinary compiler operand mode at each expression path, in the same order. |
| `REDIRECTS` | Executable read redirects: original path, selected path and whether the selected result is converted to bool. Raw conditional rewrites preserve operand acquisition; constant-left logical rewrites skip an already compiled truth conversion. |
| `NAMES` | Nonfolded ordinary constant reads: path and exact lexical name-resolution descriptor. Folded or unvisited children have no runtime name lookup entry. |
| `DIAGNOSTICS` | Ordered namespace/import compiler diagnostics, including exact byte messages and their source-unit locations. |
| `LOCATION` | Active or last ordinary compiler position. Lexical diagnostic locations are carried by the diagnostics themselves. |
| `ENV` | Current lexical environment returned by the namespace/import traversal. Each work descriptor retains its own environment. |
| `COMPLETION` | `PPCNORMAL`, `PPCABRUPT` with a static error or Unsupported completion, or `PPCNAMESPACE` with fatal lexical diagnostics. |

The ID is a compiled-source-instance identity allocated by the caller. It is not
a content hash or filename. Source syntax and metadata are retained unchanged.
No opcode IR, AST-wide declaration table, class registration, autoload or body
activation is inferred from these descriptors. Earlier successfully compiled work
is retained on failure for inspection, but must not execute if compilation fails.

Each `PLWORK` barrier from `21-source-context.watsup` now invokes actual ordinary
compilation for the admitted statement. Only successful work produces a
`PLCOMPILED` resumption with the matching occurrence, environment and final
compiler line. Consequently an earlier array compile error or out-of-context
`break` precedes a later import conflict or warning. Imports and namespace
containers produce lexical changes rather than executable statement descriptors.

Arrays invoke `45-constant-context.watsup` before ordinary child compilation,
matching `zend_compile_array`. If the array becomes constant, compilation uses
that value directly. Otherwise it compiles each key before its corresponding
value, using write context for by-reference values. This ordinary order differs
from the constant prepass's value-before-key order. Assignment and variable
children are compiled normally even though an enclosing constant-expression
invocation stops at those nodes. Thus an array nested beneath such a stop still
gets its own prepass when ordinary compilation reaches it.

Constant AST rewrites and constant code-generation operands remain separate.
`FOLD.FACTS` records the former. Ordinary arithmetic and identity compilation can
produce a constant operand after compiling its children without rewriting the
original AST; those results belong to `EXPRESSIONS`. The helper reuses the
reviewed binary/unary value operations without adding their code-generation
results to the AST-rewrite fact table. Ordinary DIM compilation does not use the
constant-DIM leaf. It consumes a constant DIM result only if an enclosing prepass
already retained that exact occurrence as a fact. Before consuming such a fact,
ordinary compilation selects its effective constant-node line: original scalar
leaves keep their source lines, while rewritten constants use the prepass
invocation line. Locating the retained original DIM or binary node instead would
incorrectly move later diagnostics to its old source line.

`$ppconstants(state)` merges the two value sources for runtime installation.
Matching duplicate paths coalesce only when their exact values and array IDs agree;
a conflicting value, missing operand line or unsuccessful compilation returns
`PPCINVALID`. Expression end lines remain separately available even for nonconstant
operands. This structural export check does not re-prove constant evaluation or
replace the runtime installer's checked unit/path and array-graph validation.

Both kinds of constant array value remain rooted in the isolated compiler store,
including constant array-union operands. The runtime installer remaps tables into
a disjoint allocation range and registers permanent compiled-unit roots. It keeps
compact operand metadata, not the isolated compiler state. Temporary `HELD` roots
are cleared by cleanup, while compiled pools remain rooted. A compiled occurrence
is looked up in its installed pool, including repeated while/do/for execution.
Function declaration/call execution remains a separate pending obligation.

Constant reads use the same lexical environment as their containing work.
`22-name-resolution.watsup` supplies the resolved bytes, qualification flag and
optional fallback; `23-named-constants.watsup` performs only valid compile-time
substitution. A remaining read is recorded in `NAMES`. The runtime retains compact
`CODENAME` records and calls the shared byte-keyed constant backend at the compiled
ending line after a pool miss. Fallback is attempted only when the resolved name
is absent. An existing unmodeled startup constant remains Unsupported; it does not
become a missing name or trigger fallback. Undefined-name diagnostics retain the
resolved spelling even when a fallback was attempted. The former matching
class-import-prefix admission boundary is removed by this source lookup path.

Expression records preserve the current compiler line after children, including
partial-fold line effects and assignment's explicit target-line reset. A direct
assignment-to-self dimension path preserves the compiler's special CV behavior.
Emission-line tests observe native runtime warnings because those reveal the
line attached by compilation; they do not claim that this helper executes PHP.

`$ppaccess(state, path)` exposes `PPR` (read), `PPW` (write fetch, including
reference acquisition), or `PPUNSET` for successfully compiled expressions. These
modes are recorded from the actual compiler call, independently of the retained
AST node's kind. Array keys and computed variable-name expressions are reads even
inside writable paths; DIM bases inherit the surrounding mode. The current
reference forms use the same write-fetch mode as ordinary targets. Runtime tasks
retain their separate reference-acquisition protocol.

The runtime consumer intercepts pooled values only for `PPR` occurrences with a
constant operand, preserving write and unset path preparation. Constant facts beneath an
entirely folded parent can have no ordinary expression/access descriptor because
normal compilation never enters those children. They remain constant-store
owners, not executable entry points. Missing access or unsuccessful compilation
returns no mode. The current checked compiler constructs one matching access
record per expression descriptor; this internal API does not accept arbitrary
forged compiler states. Quiet access, compound read/write operators and dynamic
argument modes require explicit later extensions.

The source anchors are the pinned PHP 8.5.10 `Zend/zend_compile.c`:
`zend_compile_expr_inner` (11804), `zend_compile_var_inner` (11955),
`zend_delayed_compile_dim` (3051), `zend_compile_assign` (3452),
`zend_compile_assign_ref` (3549), `zend_compile_unset` (5555),
`zend_compile_array` (10935), and `zend_compile_top_stmt`/`zend_compile_stmt`
(11653/11685). No Zend compilation result is consulted by the specification.

Run `python3 tests/semantics/source_compiler.py`. Its baseline campaign compiles
all current source-machine cases through the helper and compares original-source
native lint diagnostics and acceptance, independently of runtime evaluation.
Additional cases cover compiler ordering, lexical resumptions, partial facts,
constant operand descriptors, array-pool ownership and native emission-line
observations. Explicit Unsupported contexts and checked metadata mutations are
recorded separately. Reports retain source bytes, AST hashes, exact commands,
working directory, status and raw output channels.

The supported ordinary statements are expression statements, echo, unset, blocks,
inline output and no-ops, plus the control statements described below. Expressions
cover the current scalar/named-constant, variable, assignment/reference,
`+ - * / === !==`, unary sign/not, logical/short-circuit operators, ternaries,
array and dimension subset. Namespace and all import
kinds supply lexical context; admitted constant fetches and array prepasses consume
it. Compile-time computed-name warnings and HTTP-variable assignment flags remain
Unsupported. Functions/classes, declare effects and other unimplemented statements still
stop ordinary compilation explicitly. Declaration publication, user constants and
source magic constants remain pending core obligations. Namespace/import
diagnostics are emitted before recorded work executes. The old whole-program
check and recursive array-fold classifier are no longer the public source
compilation path; their obsolete definitions were retired in `846dc3d2`. Ordinary
compilation uses its narrow direct-CV check, and the control module owns jump
legality and diagnostic positions.

A bare `break` has no operand child in Zend's AST, so its compiler line is the
terminator token's start line (`zend_ast_create_1`, `zend_ast.c:173`, and
`zend_language_parser.y:521`). The frontend retains this as checked integer
`statementTerminatorLine` on break and continue nodes. It cannot be recovered
from the keyword's `startLine` or the statement's `endLine`: a closing-tag token
may consume a trailing newline. Missing, nonpositive, or out-of-range token lines
yield Unsupported instead of a guessed line. The range check uses the retained
statement start/end positions; it does not authenticate edited metadata against
unavailable original source. Syntax reconstruction retains positive edited values,
and printing derives fresh source from checked syntax rather than these positions.
The fourteen original-source regressions retain semicolon and closing-tag failures
and controls. The control compiler consumes the same token field for bare continue. Explicit
depth operands use their own Zend AST line and literal-kind checks, described in
[CONTROL-COMPILER](CONTROL-COMPILER.md).

Temporary scalar, array, named-constant, admitted arithmetic/unary and assignment
expressions cannot be used as writable or unset operands. Ordinary compilation
rejects these shapes before compiling their children, using
`zend_compile_var_inner`'s default write-context branch (`zend_compile.c:11998`).
This admits exact static rejection for literal dimension targets such as
`"abc"[0]="X"`; it does not evaluate the temporary or its dimension key. The
surrounding assignment still compiles its right operand first, so an earlier
right-side compile error retains priority. Call and property variable branches
remain separate pending syntax; the default rejection does not classify them.

The control compiler extends ordinary statement work with if/elseif/else and
while/do/for. It compiles all branches and loop children in Zend's compile order,
records existing structural occurrence paths, and validates break/continue depth
before runtime begins. [CONTROL-COMPILER](CONTROL-COMPILER.md) describes order,
metadata and remaining boundaries. Runtime continuations consume the same checked
source occurrences and installed constant pools.

Truth compilation keeps prepass replacement separate from ordinary code generation.
A constant-left logical operation can omit right-side compilation or emit only
right-side Boolean conversion; a dynamic left operand compiles both sides. Compiler
warnings are merged at their actual position among lexical diagnostics and survive
later static failure. Full and shorthand ternaries ordinarily compile all their
children; nested-chain checks consume `parenthesizedConditional` only when that
compiler invocation is reached. Array prepass can erase the conditional beforehand.

Only actually visited read replacements appear in runtime `REDIRECTS`; a partial
prepass redirect below an entirely folded parent has no executable role. Runtime
resolves the target from the same compiled unit's canonical occurrence table,
retaining origin, ending line and pool identity across resumption. Raw redirects
preserve delayed CV/reference results because prepass removed the value-copying
conditional. Logical redirects convert the right result once. These contracts are
checked by the source truth and compiler campaigns, including skipped compile
errors, NaN warning phase/count, grouping and reference/array identity interactions.
