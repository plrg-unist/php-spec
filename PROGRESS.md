# Progress

Target: PHP 8.5.10 syntax only.

| Milestone | Status | Evidence |
| --- | --- | --- |
| 1. Dependencies and inventory | Complete | Pinned local PHP/SpecTec; 97 OCaml packages; retained source inputs |
| 2. Checked path | Complete | Actual SpecTec values, both conversions, typed positive/negative checks |
| 3. Complete syntax | Complete | [Independent gate](coverage/milestone3.json): all 635 productions, 191 scanner rules, 169 constructors mapped |
| 4. Classified validation | Complete | [Independent gate](coverage/milestone4.json): 30,976 records, zero unresolved failures |
| 5. Portable handoff | Complete | [Offline evidence](coverage/portability.json): fresh dependencies, all gates, identical ordered corpus outcomes |

Final corpus: 30,666 checked round trips, 254 matched parser rejections, 42
reviewed compilation-phase differences and 14 non-source/redirect containers.
Targeted: 93 cases (79 accepted, 14 rejected). Generated: 4,103 cases (3,781
accepted, 320 rejected, two exact compiler-invalid dispositions). Deep AST,
24 typed negatives, 33 wire negatives, three encoded mutation checks, strict
phase-ledger checks and shard-equivalence/failure checks pass. All 21,744 PHPT
extractions match the pinned runner. Imports: 64,850 verified files.
The relocated run hid `/home` and `/tmp`, disabled networking and used no Git
metadata or copied build products. All 518 source/input hashes remained intact;
all 30,976 ordered corpus records match after lint temporary-path normalization.

Decisions: explicit typed constructors and fields; lossless byte/numeric
transport; strict membership against elaborated SpecTec declarations; printing
from freshly reconstructed checked values. A bounded-depth wire handles deep
ASTs. The native helper separates file-mode raw lexing from parser-only Zend
acceptance, with no source execution. Encoding declarations drive fresh output
chunks; original spelling provenance never controls printing. Exact conversion
retains metadata while canonical equality normalizes documented spelling only.
See [design](docs/DESIGN.md), [validation](docs/VALIDATION.md) and
[patches](patches/README.md).

All five syntax milestones are complete and independently reviewed. Historical
milestone reports remain explicit; exploratory results are not completion
evidence. Evaluation semantics and BOLA proofs remain separate research work.
