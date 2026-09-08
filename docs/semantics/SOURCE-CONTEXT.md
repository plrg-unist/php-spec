# Checked source occurrences

The first source-context gate supplies structural identities over the complete
checked PHP syntax. The next helper processes namespace/import compiler prefixes
and stops at explicit ordinary-statement compilation work. Neither helper
allocates runtime literals or activates declarations.
The source machine does not load these helpers yet. PHP 8.5.10 remains the target;
see [the plan](../../PLAN.md) and [static helper handoff](LINKING-HANDOFF.md).

`scripts/generate-occurrences.py` derives
`spec/semantics/11-source-occurrences.watsup` from the ordered contracts in
`spec/schema.json`. `make schema` regenerates both. The generated module loads
after `spec/php.watsup`; no numeric or runtime machine modules are required.
`python3 scripts/generate-occurrences.py --check` rejects generation drift.
The generated node union contains the exact 169 checked constructors with their
existing field domains and metadata. There is no opaque or unknown-node case.

The interface is:

| Value or helper | Contract |
| --- | --- |
| `pcstep` | `PCFIELD nat` selects a zero-based schema field ordinal; `PCINDEX nat` selects a zero-based sequence element. These are distinct constructors. |
| `pcpath` | Ordered steps from the source-unit root. A top-level statement starts with its `PCINDEX`. |
| `PCOCCURRENCE pcpath pcnode` | A node occurrence retaining all original typed fields and metadata. |
| `pcunit` | `ID` is a compiled-source-instance number, `AST` is the unchanged checked `program`, and `OCCURRENCES` is its structural preorder enumeration. |
| `$pcchildren(node, path)` | Immediate child nodes, in schema field order followed by sequence order, with extended paths. |
| `$pcmetadata(node)` | Exact original metadata, including absence and ordering. Metadata is not traversed for children. |
| `$pcwalk(occurrences)` | Recursive structural preorder enumeration. |
| `$pcsource(id, program)` | Constructs the retained source unit and its occurrence enumeration. |

Scalar field payloads, `ABSENT`, sequence wrappers and comments are not node
occurrences. Their complete values still reside in each original node and in
`AST`. Sequence indices count every entry, including null entries; a missing list
item therefore leaves an index gap. Empty lists remain distinguishable from
`ABSENT` in retained syntax. Encoded source metadata, preamble and halt payloads
remain in the unchanged `program` as well.

The caller allocates `ID` for a compiled source instance. It is neither a content
hash nor a pathname: independently compiling identical source bytes can produce
distinct units. Reexecuting a compiled occurrence retains the same unit ID and
path. Distinct positions retain distinct paths even when their complete checked
subtrees, including metadata, are equal. Metadata changes alone do not change
paths. Future runtime literal pools can key by `(ID, pcpath)`; this helper does
not allocate or share runtime values. An occurrence's identity is this pair;
the path inside `PCOCCURRENCE` is only unit-local. The reviewed runtime CV classification
continues to come from the shared checked-expression helper, not annotations
stored by this structural traversal.

Structural order is deliberately separate from PHP compilation and execution
order. For example, the schema lists array-item key before value, while pinned
reference acquisition precedes delayed key consumption/conversion; function return types compile
before parameters despite their schema order. A future compiler consumes the
typed nodes using authored, source-evidenced ordering rules. It must not use this
enumeration as a schedule, build an AST-wide visible class table, or publish
every encountered declaration.

Source evidence constraining that next step is `zend_compile_top_stmt`,
`zend_compile_stmt`, `zend_compile_namespace`, `zend_compile_use`,
`zend_compile_group_use`, `zend_compile_declare`, `zend_compile_func_decl` and
`zend_compile_params` in pinned `vendor/php-src/Zend/zend_compile.c`.
Namespace boundaries reset import tables; class/function/constant imports have
distinct lookup behavior; top-level compilation differs from nested statement
compilation. Exact compiler keyword lines, compile-time constant effects,
declaration visibility, strictness and per-function assigned-name flags remain
obligations for that subsequent pass. Parser metadata is retained without being
presented as a substitute for those compiler contexts.

Run `python3 tests/semantics/source_occurrences.py`, also included in
`make test-semantics`. It checks all constructor shapes and every schema-domain
alternative through executable rules, plus original sources passed through the
frontend and strict checked adapter. Source cases cover namespace/function/class
nesting, optional and empty bodies, list holes, closures, loops, binary payloads,
comments, encoded programs and halt payloads. Separate metamorphic checks retain
duplicate equal trees at distinct paths and preserve paths after metadata removal.
Every source unit is checked for exact AST retention and a separate unit ID with
identical occurrences. The runner elaborates, checks algorithmic executability,
structures and executes with encountered-path determinism checking.

`coverage/semantics/source-occurrences.json` records the bounded structural
checks, original source and AST hashes, and unchanged implementation/binary
fingerprints. These are representation checks, not Zend execution comparisons or
evidence that any unfinished language constructor has acquired semantics.

## Ordered namespace and import context

`21-source-context.watsup` loads after the occurrence module, `10-bytes.watsup`
and `16-static-types.watsup`. `$plstart(id, program, original-file)` constructs
its own canonical source unit from the checked program, then processes the
namespace/import prefix. It does not ingest a caller-supplied occurrence table.
The ID allocator still belongs to the future source compiler/runtime integration.

`plenv` contains namespace bytes, separate class/function/constant import maps,
previously registered compiler symbol keys, and strictness. Class and function
alias keys are lowercase ASCII; constant alias keys remain case sensitive. Import
targets retain their spelling and need not exist. Imports cause no class lookup,
autoload, runtime constant lookup, or declaration publication. Entering a new
namespace resets all three maps and the seen-symbol collection. Braced namespace
exit also clears them; strictness survives these file-context changes.

Use lists and mixed/single-kind group imports are processed in order. A global
implicit non-compound import emits its warning before reserved-name and conflict
checks. Only class imports apply the special-class-name check. A repeated alias
in the same map conflicts even if its target is unchanged. Previous declaration
keys can permit the same resolved name, but their collection is not a class
registry. Declaration compilation must register each key at the pinned compiler
phase. The helper never discovers them by scanning future declarations.

The pin has a case irregularity: import conflict checks lowercase the namespace
prefix even for constant imports, while a constant declaration registers its
original namespace spelling. Thus `namespace Ns; const X=1; use const Other\Y
as X;` is accepted, while lowercase `ns` conflicts. The reverse order conflicts
in both namespaces. These rules follow the pinned source and observations; see
the [discrepancy ledger](DISCREPANCIES.md). They do not impose a repaired model.

`plstate` retains the canonical unit, original file, lexical environment, ordered
tasks, namespace style, whether compilation is inside a namespace, and whether
only declares/nops precede the first namespace. Namespace entry checks mixed
styles, braced nesting, first-statement restrictions and the reserved namespace
name in source order. Root declare statements do not invalidate the first
namespace position, even if their bodies contain executable statements. This
matches `zend_is_first_statement`'s root-AST test.

The results separate completed lexical prefixes from unfinished compiler work:

| Result | Meaning |
| --- | --- |
| `PLDONE state diagnostics` | These lexical tasks are exhausted. This is not declaration activation or full-core compilation coverage. |
| `PLWORK occurrence state diagnostics` | Compile this exact ordinary statement before proceeding. Its state is the continuation and current lexical environment. |
| `PLERROR diagnostics` | Earlier nonfatal diagnostics followed by the first compiler error. |
| `PLUNSUPPORTED reason` | Missing context, an unsupported edited shape, or an invalid/incomplete compiler resumption; no completed diagnostic trace is claimed. |

Every ordinary statement, including declarations, declares, expressions, control
and halt, is a work barrier. No traversal into its body or expression occurs here.
Consequently an earlier body error or constant-compilation effect cannot be
bypassed to report a later import conflict. Runtime execution ordering and the
runtime owner's bounded `zend_eval_const_expr` prepass remain separate; this
helper does not duplicate them as a whole-tree scan.

`$plresume(state, compiled-result)` is an internal compiler continuation interface.
`PLCOMPILED location environment` asserts that the requested work completed and
supplies its resulting file environment and final compiler line. The unit ID,
occurrence path and file must match the pending work; a missing/nonpositive line,
wrong occurrence or nonpending state is rejected. `PLCOMPILEERROR diagnostics`
and `PLCOMPILEUNSUPPORTED reason` propagate unsuccessful work without advancing.
The eventual compiler must construct this result only after compiling the work;
the helper does not establish that assertion itself. A caller accumulates the
previous `PLWORK` diagnostics, any warnings from successful ordinary compilation,
and the next result's diagnostics; `PLCOMPILED` itself carries no diagnostics.

Post-statement namespace verification occurs after successful ordinary work and
uses its final compiler line. Halt has an explicit exception, matching
`zend_compile_top_stmt`; an outer halt after a braced namespace must not acquire
the outside-namespace-code error. The halt work itself still must be compiled,
including its payload/offset and outermost-scope obligations. No halt semantics
are supplied merely by this continuation exception.

Diagnostics retain severity, symbolic code, byte arguments and `pllocation`
(unit ID, path, original file and compiler line). `$plmessage` renders their exact
message bytes. A use list inherits the first imported name's line, and a group
use inherits its prefix name's line. Later items and aliases do not update that
compiler line. A named namespace inherits its name's line. These follow the
grammar's AST construction and `zend_ast_create*`/`zend_ast_create_list*`, not
the PHP-Parser statement's keyword start line. Mandatory multiline regressions
retain the independently discovered [line disagreements](../../coverage/semantics/compiler-context-line-disagreement.json).

An anonymous namespace inherits its statement-list creation line at the opening
brace. Current metadata generally lacks that brace location. A one-line namespace
can establish it from equal start/end lines; otherwise the helper does not guess.
If a namespace diagnostic needs that missing line, the source entry returns
Unsupported. An explicitly supplied helper context can exercise the rule, but is
not original-source diagnostic agreement. Valid namespace transitions needing no
diagnostic can still proceed. Adding checked brace metadata and repeating the
original-source cases remain required before this source-context gap closes.
`$pltypecontext` supplies the class-import subset and namespace to the reviewed
type helper, retaining explicit scope/position/owner/member/location inputs.
This is a type-helper consumer, not automatic signature compilation: general
constant-import defaults and exact function/class keyword lines remain pending.

Run `python3 tests/semantics/source_context.py`, included in `make test-semantics`.
`coverage/semantics/source-context.json` distinguishes original checked
namespace/import-only compiler comparisons, explicit seen-symbol helper inputs,
environment/type descriptors, body barriers, edited namespace/context tests,
supplied successful-work resumptions, and Unsupported cases. Sources, AST hashes,
raw pinned lint channels, exact events, runtime profile and unchanged fingerprints
are retained. A supplied completion in an interface test is never evidence that
the missing ordinary compiler executed.

The frontend currently rejects `Self`/`Parent` aliases even for function and
constant imports, although pinned parsing and compilation accept those imports.
It also rejects class aliases at an earlier phase than Zend compilation. Exact
sources and frontend/native-parser/lint outcomes remain separate, with equivalent
checked edited alias fixtures labeled as helper evidence. Grammar rejections for
`static`, `array` and `callable` aliases are separately counted. None count as
original-source prefix agreement. A bounded frontend repair and full classified
syntax validation remain required; the lexical helper does not repair the source
pipeline by receiving edited syntax.

Strict-types compilation, encoding/tick declare effects, function/class/declaration
contexts, keyword/brace metadata, body compilation, default compilation, registration,
linking and source-machine integration remain pending. These are core obligations,
not exclusions. The next stage must consume and resume the work descriptors with
source-evidenced compiler rules before claiming that these contexts drive ordinary
source execution.
