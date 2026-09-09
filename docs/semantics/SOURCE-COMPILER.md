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
is looked up in its installed pool; source loops and functions remain unsupported,
so their execution is not established by this installation milestone.

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
inline output and no-ops, with out-of-context bare `break` rejection. Expressions
cover the current scalar/named-constant, variable, assignment/reference,
`+ - * / === !==`, unary sign, array and dimension subset. Namespace and all import
kinds supply lexical context; admitted constant fetches and array prepasses consume
it. Compile-time computed-name warnings and HTTP-variable assignment flags remain
Unsupported. Functions/classes, declare effects, loops and other statements still
stop ordinary compilation explicitly. Declaration publication, user constants and
source magic constants remain pending core obligations. Namespace/import
diagnostics are emitted before recorded work executes. The old whole-program
check and recursive array-fold classifier are no longer the public source
compilation path. Their legacy definitions await coordinated retirement; ordinary
compilation now uses its own narrow direct-CV check and the shared source-line
error helper for bare break.
