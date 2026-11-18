# PHP syntax in P4-SpecTec

This project provides a checked PHP syntax pipeline and partial executable PHP
core semantics in P4-SpecTec. The pinned target is **PHP 8.5.10 CLI, NTS,
64-bit**. Complete PHP core remains the objective; the current implementation,
Rocq interaction-tree semantics and BOLA/CRIS verification are unfinished.

The [feature inventory](coverage/semantics/features.json) tracks 169 syntax
constructors and 306 runtime obligations. No constructor is validated; one
runtime obligation is validated. Syntax acceptance and bounded passing semantic
slices do not establish complete runtime coverage. See [PROGRESS](PROGRESS.md)
for the current checkpoint and [PLAN](PLAN.md) for scope and exit criteria.

## Build and run

All required non-system inputs are local and pinned. The complete matching PHP
source, parser and framework are retained under `vendor/`; see
[dependencies](dependencies/README.md) for system prerequisites, provenance,
licenses and offline rebuild instructions.

```sh
./scripts/build-deps.sh
./scripts/verify-inputs.py
make build
bin/php-syntax check FILE --elaborate
bin/php-semantics FILE --steps 100000 --timeout 30
```

`bin/php-syntax parse FILE` produces checked transport;
`bin/php-syntax pretty FILE` reconstructs and prints checked nodes.
`print-ast` checks an edited transport file. `--short-tags` and repeated
`--ini KEY=VALUE` select the documented source profiles. The
[representation contract](docs/DESIGN.md) describes byte payloads, metadata,
checking and reconstruction.

`bin/php-semantics` executes checked SpecTec values and emits a structured
observation. Inspect its status: modeled PHP/static errors, Unsupported,
interpreter failure, timeout and budget exhaustion are distinct outcomes.
Arithmetic and PHP evaluation belong in authored `.watsup` rules. The sole
execution oracle is project-local `.tools/php/bin/php`; it supplies differential
evidence, never runtime semantic answers. The [core contract](docs/semantics/CORE.md)
separates required language intrinsics from ordinary libraries and services.

## Validation and coverage

`make test` runs the syntax regression checks. `make validate` performs the full
classified syntax campaign; `make inventory` updates syntax coverage evidence.
See [syntax validation](docs/VALIDATION.md) for selections and normalization.
No application or PHPT helper is executed to collect syntax. PHP-Parser and the
native parser share Zend lexing, so parser agreement is not independent lexical
validation.

`make test-semantics` selects semantic regression suites. Family records retain
original-source comparisons, compiler/state checks, independent review and
negative controls at their tested revisions. Unsupported, interrupted, timed-out
and malformed runs never become agreement credit. Metadata changes do not renew
accepted execution evidence. A final combined campaign and fresh copied-path,
network-isolated rebuild remain required before a complete-core claim.

Bounded reference Get hooks admit scoped `self` conjuncts in nominal
intersections and bare or mixed DNF types; see the [family review](coverage/semantics/self-intersection-parentless-short-reference-get-hook-review.json).
Wider hook contexts, owners and lifetimes remain partial.

Selected output-handler return casts admit emitted one-byte string complements
and single-byte STRING AND/OR/XOR, including derived NUL, with unchanged string
storage; [review](coverage/semantics/output-final-selected-emitted-byte-bitwise-cast-chain-return-modulo-error-review.json). Both binary operands must have length one.
Wider strings, owners and lifetimes remain partial.

Supplied optional plain `float` producer formals retain one unary sign over an
INT default while preserving caller copies and private reference-cell ownership;
[review](coverage/semantics/supplied-optional-unary-float-int-default-producer-reference-notice-review.json).
Wider defaults, types, owners and lifetimes remain partial.

## Project map

| Resource | Purpose |
| --- | --- |
| [PLAN](PLAN.md), [PROGRESS](PROGRESS.md), [inventory](coverage/semantics/features.json) | Agreed scope, current work and remaining obligations |
| [Semantic design](docs/semantics/DESIGN.md), [source context](docs/semantics/SOURCE-CONTEXT.md) | Machine architecture and checked source authority |
| [Numerics](docs/semantics/NUMERICS.md), [reference wrappers](docs/semantics/REFERENCE-WRAPPERS.md) | Pure values, storage and ownership contracts |
| [Core boundary](docs/semantics/CORE.md), [request inputs](docs/semantics/REQUEST-INPUTS.md) | Intrinsics, observable outcomes and explicit environment facts |
| [Artifacts](docs/ARTIFACTS.md), [milestone history](MILESTONE-HISTORY.md) | Existing family ledgers, evidence hashes and recovery locations |

Detailed feature contracts remain under `docs/semantics/`, with their source and
review links in the inventory. Large raw traces and original failures stay
outside Git. Historical evidence retains its original profile, selection and
revision; it is not a new full-core or portability result.
