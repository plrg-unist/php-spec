# Progress

Target: PHP 8.5.10 syntax only; `PLAN.md` remains the scope and completion contract.

| Milestone | Gate | Status |
| --- | --- | --- |
| 1. Dependencies and inventory | Pinned local runtimes, corpora, exhaustive source inventory | Complete |
| 2. Checked path | Byte-safe transport, checked SpecTec conversion, fresh printing, negative checks | In progress |
| 3. Complete syntax | Every grammar/scanner/constructor family mapped and exercised | Pending |
| 4. Classified validation | Full corpora, generated cases, minimized discrepancies resolved | Pending |
| 5. Portable handoff | Offline copied-path build/checks and provenance audit | Pending |

Implementation owns schema, conversion, frontend, README and milestone commits.
Dependency work owns pinned inputs/runtimes, corpus imports and portability.
Independent review owns inventory, validation harness and final gate review.
No milestone is complete merely because an upstream parser claims support.

Current decisions: reuse pinned PHP-Parser and its Standard printer; explicit
constructor/field mappings; encode source strings as bytes and numbers losslessly;
validate actual SpecTec values, including adversarial malformed cases.

Milestone 1 gate: PHP 8.5.10 tokenizer/JSON/mbstring and pinned SpecTec built
locally; 97 OCaml packages and all source inputs retained; 64,756 imported files
verified. Independent inventory review enumerated 635 grammar productions,
191 scanner rules and 169 non-recovery node contracts. Full witness mappings
remain a milestone 3 gate, rather than an assumption from enumeration.

Next gate: checked source/AST path and independent malformed-value tests.
Known targeted discrepancies awaiting resolution: clone printing stability,
negative interpolation offsets, omitted destructuring slot, __PROPERTY__ method
name, and parser-stage CompileError classification.
