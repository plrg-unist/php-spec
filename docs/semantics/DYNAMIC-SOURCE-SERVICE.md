# Checked eval parser service (transport increment)

`frontend/worker.php` accepts `parse-eval` with exact keys `op`, `id`, `mode`,
`profile`, `source`. `id` is a canonical nonnegative decimal string, `mode` is
`eval`, `profile` is `cli-raw-85`, and `source` is canonical base64 of the
original eval bytes. The worker returns those four fields and either
`accepted: true` with the existing version-1 `ast`, or `accepted: false` with
`category: parser_rejection`, base64 `message`, and positive integer `line`.
The message and line come from the pinned native after-open-tag parser. They
are parser evidence, not a modeled PHP exception.
Malformed requests produce a frontend error. A source profile outside this
helper's fixed boundary produces `helper_unsupported`, never parser rejection.

The fixed profile requires `zend.multibyte=0`, `precision=14` and
`short_open_tag=1` under the pinned PHP 8.5.10 `-n` worker. It admits raw byte
sources, including non-UTF8 comments, and performs no source transcoding.
Multibyte/encoding profiles need their own eval-mode provenance and checks;
`FileLexer` and `sourceEncoding()` describe file scanning only. `EvalLexer`
inserts one no-newline `<?php ` token to start PHP's lexer after an opening tag,
removes that token and subtracts its six bytes **before** PHP-Parser constructs
node/comment positions or reports lexer errors. The pinned parser still supplies
the AST; the synthetic prefix never appears in the checked program. Closing and
reopening tags in eval bytes remain ordinary source tokens.

`native/php_file.c:php_spec_parse_eval` separately prepares the original eval
bytes for Zend's string scanner, starts in `ST_IN_SCRIPTING`, calls `zendparse`
and discards its AST. Empty source is accepted without scanning. The helper
restores scanner and compiler state after success or rejection and never calls
Zend compilation or evaluation. A native `ParseError` supplies the rejection
message and line. A different native failure, or native acceptance followed by
PHP-Parser/target-syntax rejection, yields `helper_unsupported` without an AST
or parser-rejection payload. Joint acceptance produces the checked PHP-Parser
AST. This distinguishes native parser facts from later authored static and
runtime error rules.
Its [review ledger](../../coverage/dynamic-eval-native-diagnostics-review.json)
records the pinned binary and test fingerprints; the 30,980-entry regression
there covers existing file-mode syntax, not 30,980 eval sources.

`adapter/main.ml` has `check_source_service`: it takes an exact `pending`
record with those four fields and a disjoint accepted/rejected `response`,
compares their identity and original bytes, validates base64 and response shape,
and imports/checks/exports accepted syntax as a formal `program`. This is a
single pending-response **fixture seam**. It neither authenticates a type-correct
edited AST against source bytes nor remembers consumed request IDs. The future
orchestrator must call the trusted pinned worker for the pending request, check
its `ok`/`diagnostics` envelope, and forward its exact service payload fields.
There is no machine pause, public resume API,
dynamic source registry or eval/include execution in this increment; reached
eval/include remains explicitly Unsupported.

The [provenance ledger](../../coverage/dynamic-eval-helper-review.json) keeps
the focused eval-mode checks distinct from the full classified **file-mode**
syntax regression. Neither gate establishes dynamic-source execution.

`python3 tests/eval_source_service.py` checks accepted/raw/empty/tagged sources,
line and byte/token/comment positions, exact native rejection messages/lines,
non-ParseError Unsupported, absence of installed declarations, file parse after
eval in the same worker, the three profile guards, malformed pending/response
controls and checked-AST shape rejection. `make test` includes this gate.
Existing file syntax integration must also pass, because the worker's file-mode
`parse` shares its dispatch switch.
The next runtime increment must add an actual pending service state and retain
prior `S.SOURCES`, `S.FILES`, `S.CODE`, pools, tasks and events when compiling a
fresh source unit. `33-runtime-compiler.watsup` currently replaces source units
on abnormal compilation; that code is outside this transport increment.

## Original transport validation

This increment was built in a private nested worktree with
`./scripts/opam-exec.sh dune build --root . adapter/main.exe` and
`./scripts/opam-exec.sh dune build --root tests/semantics numeric_runner.exe`.
The first `make test` attempt stopped before tests because Dune discovered the
outer checkout as its root; explicit private build roots fixed that test setup.
Every subsequent `make test` recipe command was run in order from the private
worktree and passed. The selected `tests/validate.py --elaborate --lint-all`
reported 83 passes and 14 parser rejections; `--generated` reported 3,781
passes, 320 parser rejections and two retained invalid-program roundtrip
differences; the deep selected corpus case passed. The focused service test
passed 11 eval byte cases and 11 protocol negatives. A reached eval and include
still each returned `Unsupported` from `bin/php-semantics`.
The frozen commit also passed the full four-shard classified file-syntax gate
and targeted inventory; exact counts, hashes and the separate pre-existing
grammar-mapping drift are in the provenance ledger. Nested-worktree Dune root
discovery required explicit `--root` builds before those recipe commands.
