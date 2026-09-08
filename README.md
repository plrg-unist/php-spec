# PHP syntax in P4-SpecTec

This project specifies the abstract syntax of **PHP 8.5.10** and connects
PHP-Parser 5.8.0 to checked P4-SpecTec values. Syntax work is in progress;
[PROGRESS.md](PROGRESS.md) records milestone gates and [PLAN.md](PLAN.md) defines
scope. Evaluation semantics and BOLA verification are later research phases.

All required non-system inputs are local and pinned. See
[dependencies/README.md](dependencies/README.md) for prerequisites, provenance,
licenses and offline dependency builds. The PHP source contains matching PHPT
inputs; the BolaRay archive contains the pinned application snapshots.

```sh
./scripts/build-deps.sh
./scripts/verify-inputs.py
```

Build the adapter with `make build`. Use `bin/php-syntax check FILE`,
`bin/php-syntax parse FILE` (checked transport), or `bin/php-syntax pretty FILE`.
`--elaborate` additionally checks a typed SpecTec fixture; `--short-tags` enables
short opening tags. `print-ast` checks and prints an edited transport file.
[Representation and checking](docs/DESIGN.md) explains the data path.

No application or PHPT helper code is executed to collect syntax. Parsing and
compilation checks are separate; PHP-Parser's version selection is best effort,
so validation compares its raw outcomes with the pinned Zend parser.
