# Syntax validation

The reference is the local PHP 8.5.10 source-file parser, invoked by the narrow
native helper without compilation or evaluation. PHP-Parser receives a separate
raw file-lexer token stream and applies its own grammar. Lint adds separate
compilation checks. The worker also offers optional `oracle-string` diagnostics
using `TOKEN_PARSE`; that operation differs on BOMs, shebangs and encoding
profiles and is not the corpus reference or a retained full-corpus observation.
The parsers share the lexer, so agreement is not independent lexical validation.
Use the pinned `vendor/php-src/Zend/zend_language_parser.y`, scanner and AST
actions to resolve syntax questions; other PHP releases are not substitutes.
The scope includes syntax in valid programs under the supported configuration
profiles, even when invalid-program checks occur at different phases.

Run `python3 tests/validate.py --elaborate` for targeted checked round trips and
`python3 tests/malformed.py` for malformed-value rejection and
`python3 tests/wire_negative.py` for malformed deep-transport rejection.
The corpus run adds `--corpus --lint-all --output coverage/results-corpus.jsonl`
to `tests/validate.py`; bounded interaction cases use `--generated`.
`python3 tests/parallel_validate.py --corpus --lint-all` runs the same checks
in four isolated worker shards. It verifies every eligible source ordinal
exactly once, matching fingerprints and counts, and restores the sequential
record order. A failed or incomplete shard fails the combined run.
Reports distinguish passes, parser rejections, compilation-phase differences,
acceptance disagreements, conversion failures, and AST/printing instability.
An interrupted run is exploratory evidence, never the completion report.
Missing fixtures, crashes, timeouts and resource failures remain unresolved
failures, not reasons to exclude supported syntax.
For direct SpecTec CLI calls, inspect diagnostics as well as exit status:
some framework errors can exit zero. The project drivers return failure exits.
Compilation-phase discrepancies require an exact source/configuration match
in `tests/phase-discrepancies.json`, the reviewed frontend restriction and
matching pinned lint diagnostic. An unrelated compilation error cannot excuse
a frontend rejection; an unreviewed discrepancy fails the gate.

Each successful source passes through fresh PHP-Parser nodes, a real SpecTec
value checked against elaborated declarations, fresh reconstructed nodes, and
the standard printer. The harness checks exact transport preservation in both
directions on both branches, records original and printed parser observations,
and checks output acceptance, printing idempotence, and normalized AST
equality. Targeted runs additionally elaborate typed `.watsup` fixtures.
Every parsed source compares its raw comment-token inventory with retained AST
comments, preventing simultaneous loss in both round-trip branches.
Malformed tests exercise the strict checker and typed elaboration separately;
they also change a checked scalar and require changed output.

Canonical syntax equality ignores source positions (including `namespaceBraceLine`, `statementTerminatorLine` and `statementBodyLine`), ternary grouping and original destructuring array kind, literal spelling/kind,
heredoc delimiters/indentation, and the inline-HTML leading-newline printing
hint. These remain in the transport. `tests/source_context_metadata.py` checks exact
namespace-brace, control-body and break/continue/empty-for terminator metadata
across ASCII, CRLF,
UTF-16LE and a converted single-byte encoding, including nested nodes and
closing-tag newlines, brace/colon versus single-statement bodies and punctuation
inside header literals/comments. It checks fresh reconstruction, absent fields and malformed
payload rejection.
`tests/ternary_metadata.py` independently distinguishes expression grouping from
call/control parentheses, retains the boolean through checked reconstruction,
and rejects malformed payloads across plain and encoded source profiles.
`tests/destructuring_metadata.py` checks nested spread fields and long/short/list
syntax through actual source, checked values and fresh printing, including omitted
slots, edited kind fields and invalid payloads in plain and encoded sources.
The compiler-context campaign separately mutates a positive brace line and requires
the diagnostic location to change; semantic validation does not normalize it away.
The ordinary compiler rejects missing, nonpositive and out-of-range terminator
lines; valid edited positions remain explicit checked input.
Comment equality ignores positions,
CRLF versus LF, a common indentation prefix on continuation lines, and
indentation before conventional leading `*` markers. Substantive text,
relative indentation within the content, ordering, and doc-comment identity
are compared. This accounts for Standard's documented comment reformatting;
the exact original comment bytes remain in the transport.
Initial encoding selection, original spelling provenance and BOM spelling are
ignored by canonical equality:
Filtered wide canonical output gains a BOM to prevent Zend's content-sensitive heuristic
from selecting a different character width after formatting. Retained original-spelling bytes
and encoding/BOM metadata still pass through the checked value and reverse conversion.
Candidate-list detection can select another initial encoding after byte escapes
make a literal ASCII; decoded AST payloads and declaration literals remain strict.
Two exact compiler-invalid encoding-rescan cases have hash-pinned dispositions
in `tests/invalid-discrepancies.json`; raw failures and pinned lint evidence stay
in reports. An unlisted failure is never classified through that ledger.
Each run fingerprints implementation, tests and runtime binaries before and after
execution; a changing implementation makes the run fail.
Generated `_build` trees are omitted from source scans; the executed adapter and
the semantic helper (when built) are explicitly hashed. Helper campaigns also
require and hash their executable directly. Dune log/lock churn therefore does
not invalidate evidence, while binary changes still do.

`tests/corpus.py` extracts `FILE`, `FILEEOF`, and `FILE_EXTERNAL` according to
the matching runner, retaining source/configuration provenance. It does not
run `SKIPIF`, `CLEAN`, redirects, or application code. Application candidates
include PHP/include extensions and other files containing PHP opening tags.
PHPT `EXPECT*` sections describe runtime outcomes, not syntax acceptance labels.
Retain error tests and extension-dependent sources; runtime skip conditions do
not imply parser rejection.
Parsing outer source does not cover dynamically generated code or `eval`
strings; static additional cases must have their own provenance.
`tests/validate_extraction.py` compares every PHPT extraction with the pinned
runner's trusted container parser; it never runs the extracted test programs.

`coverage/grammar.json` enumerates all Bison productions; `coverage/scanner.json`
enumerates all state-prefixed scanner rules. Optional disposable instrumentation
records actual parser reductions and scanner rule actions on source fixtures.
The ordinary oracle and vendored sources remain unchanged. Coverage of a rule
is evidence of exercising it, not proof of parser or semantic correctness.
