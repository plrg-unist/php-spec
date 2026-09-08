# Checked source occurrences

The first source-context gate supplies structural identities over the complete
checked PHP syntax. It does not yet compile declarations, generate diagnostics,
establish lexical contexts, allocate runtime literals, or activate declarations.
The source machine does not load this helper yet. PHP 8.5.10 remains the target;
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
