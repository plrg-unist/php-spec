# Progress

Target: PHP 8.5.10 syntax only. [PLAN.md](PLAN.md) is the completion contract.

| Milestone | Status | Evidence |
| --- | --- | --- |
| 1. Dependencies and inventory | Complete | Pinned local PHP/SpecTec; 97 OCaml packages; retained source inputs |
| 2. Checked path | Complete | Actual SpecTec values, both conversions, typed positive/negative checks |
| 3. Complete syntax | Complete | [Independent gate](coverage/milestone3.json): all 635 productions, 191 scanner rules, 169 constructors mapped |
| 4. Classified validation | In progress | Frozen full engine/application corpus run is next |
| 5. Portable handoff | Pending | Fresh offline dependency rebuild passed; complete relocated checks remain |

Milestone 3 passed 86 targeted cases (72 accepted, 14 rejected), 3,501 generated
cases (3,268 accepted, 231 rejected, two exact compiler-invalid dispositions),
the deep-AST regression, 24 typed negatives, 33 wire negatives and three encoded
mutation checks. All 21,744 PHPT extractions match the pinned runner. The complete
79-codec matrix is included in generated validation. Current imports: 64,850
verified files. Full corpus and portability gates remain separate obligations.

Decisions: explicit typed constructors and fields; lossless byte/numeric
transport; strict membership against elaborated SpecTec declarations; printing
from freshly reconstructed checked values. A bounded-depth wire handles deep
ASTs. The native helper separates file-mode raw lexing from parser-only Zend
acceptance, with no source execution. Encoding declarations drive fresh output
chunks; original spelling provenance never controls printing. Exact conversion
retains metadata while canonical equality normalizes documented spelling only.
See [design](docs/DESIGN.md), [validation](docs/VALIDATION.md) and
[patches](patches/README.md).

Implementation owns code/docs/commits; independent review owns validation and
coverage; dependency work owns provenance and portability. Preserve the stable
implementation fingerprint during final runs. Exploratory reports are not
completion evidence. Never push.
