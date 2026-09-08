# PHP syntax specification plan

## Objective and scope

Build a complete syntax specification for **PHP 8.5.10** in P4-SpecTec,
together with a PHP source frontend, AST conversion, canonical pretty-printing,
and validation. Full syntax coverage is the final objective; small initial
slices are integration milestones, not a permanent subset.

This supports later research on PHP semantics: first executable semantics in
P4-SpecTec, then interaction-tree semantics in Rocq, and eventually reusable
CRIS proofs excluding the class of BOLA bugs studied by BolaRay. This phase
does not implement evaluation, built-in functions, HTTP behavior, authorization
policies, or BOLA proofs. Syntax validation does not establish any of those.

This document records the agreed scope and completion contract.
[PROGRESS.md](PROGRESS.md) records validated milestone status;
[README.md](README.md) documents the current implementation and commands.
The current user request authorizes all five milestones, including commits.

## Settled decisions and current state

- Target the released PHP **8.5.10**, selected on 2026-09-08. Its pinned source
  archive/commit and checksums are recorded in the local dependency manifests. Do not silently
  follow a moving release or branch. The workspace's pre-existing PHP engine
  is 8.6.0-dev at `1364de0472b859917f5bc0be9193bd8068fc2061`; it is not the
  selected oracle or grammar. In particular, its partial-application syntax
  must not accidentally enter the 8.5 specification.
- Use **nikic/PHP-Parser in PHP** for concrete parsing and its standard printer,
  with an **OCaml adapter/driver** integrating the P4-SpecTec value API. Sharing
  the framework's implementation language helps the adapter; it does not
  justify rewriting the entire PHP lexer/parser/printer in OCaml.
- PHP-Parser **v5.8.0**, commit
  `044a6a392ff8ad0d61f14370a5fbbd0a0107152f`, is vendored in
  [vendor/php-parser](vendor/php-parser). Its 274 distribution files are
  retained, with four [documented local corrections](patches/README.md).
  The unchanged distribution archive and BSD-3-Clause license are preserved.
  [Import provenance and reproduction instructions](vendor/php-parser.UPSTREAM.md)
  record the archive checksum and exclusions made by upstream's distribution.
- The import was checked byte-for-byte, including file modes. It contains no
  links or nested Git repository. PHP 8.5.10 and the SpecTec dependency closure
  now build from project-local sources. The schema, checked adapter, printer
  integration, corpora and validation harness are implemented; consult the
  progress gates for their current validation status.
- PHP-Parser's pinned implementation reports PHP 8.5 support and implements
  modern features; its README's 8.4 statement is stale. Its version targeting
  is explicitly best-effort and tracks major/minor versions, not patch
  releases. Support for 8.5 is not evidence of complete 8.5.10 conformance.

## Self-containment and development rules

All project sources, required libraries/specification modules, corpus inputs,
and pinned PHP/SpecTec runtime assets must reside within this directory. Do not
add operational references to sibling repositories, absolute workspace paths,
escaping symlinks, nested repositories, or new submodules. The existing `.git`
file's external submodule-metadata reference is the explicit exception.

Ordinary installed OS and build tools, such as a shell, C/OCaml compilers and
build utilities, are permitted prerequisites. Document their versions and
required packages. This project need not bundle an entire operating system or
compiler toolchain. Required non-system dependencies must be vendored or
provisioned into project-local locations from pinned, checked sources. Record
what is shipped and what is generated; build products need not be committed.
After provisioning, normal builds/tests should work offline with the documented
prerequisites and local inputs. A claim of offline rebuilding requires keeping
all non-system build inputs locally, not merely download URLs.

External URLs and source paths in provenance records are informational, not
runtime file dependencies. Existing workspace resources may be studied or
used as import sources, but copy required inputs here with versions, hashes
and license notices. Preserve upstream licenses; application snapshots can
have different licenses. Never assume the framework or PHP license covers
third-party fixtures. Keep third-party code unchanged unless a documented,
tested patch is necessary. The PHP-Parser archive omits grammar sources and
development tests; import pinned upstream material separately if needed for
the coverage audit, without inventing local replacements for missing files.

Keep changes surgical. Do not overwrite user work or implement adjacent
semantics. Never push. Make commits only when requested or authorized. A
dependency upgrade must be explicit, with refreshed provenance and validation.

## Syntax boundary and AST design

Inventory the selected release's `Zend/zend_language_scanner.l`,
`Zend/zend_language_parser.y`, AST construction actions and relevant compiler
checks. These paths refer to the imported `vendor/php-src` snapshot.
The manual explains features; the matching engine source and targeted tests
resolve implementation details and disagreements. Do not substitute PHP 5
semantics or a development grammar for the selected release.

The coverage inventory must include lexical rules, grammar productions and
formal AST constructors, with mappings between them. Cover mixed HTML/PHP,
opening/closing tags and statement termination, comments, byte-oriented
identifiers and literals, interpolation, heredoc/nowdoc, operator precedence,
alternative control syntax, declarations, names/types, references, calls,
classes/traits/interfaces/enums, attributes, property hooks, asymmetric
visibility, PHP 8.5 additions, and `__halt_compiler()` with its remaining bytes.
This list is orientation; the pinned grammar/scanner inventory is the full
checklist. Include syntax controlled by configuration, such as short tags;
record and test the relevant configuration profiles rather than declaring an
entire supported syntax family out of scope.

Distinguish lexical acceptance, grammar parsing, AST construction, static
well-formedness/compilation, and runtime behavior. Some restrictions are enforced
after parsing, and third-party parsers can perform extra checks. Do not build a
complete compiler in this phase. Document the frontend's acceptance boundary
and classify differences at the appropriate phase. Full support for syntax in
valid PHP programs remains required even when invalid-program classifications
differ between implementations.

The specification describes a canonical **abstract** syntax, not a lossless
concrete syntax tree. Equivalent source spellings may map to one constructor:
PHP-Parser already normalizes alternative `if` forms and redundant parentheses.
Track each supported source production even when it maps many-to-one. Preserve
separate form information only where it is meaningful for the specified syntax
or its later use; do not require every whitespace or delimiter choice to become
an AST constructor.

Preserve literal/identifier bytes, interpolation structure, names, modifiers,
references, omitted versus present fields, ordered lists, inline HTML and halt
payloads. Retain source locations and relevant comments/doc comments and
literal spelling metadata. Define exactly which metadata is ignored in
canonical AST equality. Whitespace normalization must not alter literal or
inline-output bytes. Canonical printing is not automatically behavior-preserving
for `__LINE__`, source file locations or halt offsets; make no semantic
equivalence claim from a syntax round trip.

## Frontend architecture

The required data path is:

```text
PHP bytes
  -> PHP-Parser AST
  -> explicit OCaml conversion
  -> checked P4-SpecTec program value
  -> reverse conversion to fresh PHP-Parser nodes
  -> Standard pretty-printer
  -> PHP bytes
```

1. Run PHP-Parser on the pinned PHP 8.5.10 CLI with tokenizer and JSON support.
   Select PHP 8.5 explicitly for both parser and printer. Use throwing error
   handling; a recovered partial AST is not successful parsing. Do not resolve
   names, perform general constant evaluation, execute includes/eval, or run
   application code. The encoding helper reproduces only Zend's parser-time
   literal-concatenation action, as documented in the design.
2. Define the project's AST domains in `.watsup`. Map every supported parser
   node and field explicitly into those domains. Unknown nodes or malformed
   payloads must produce visible failures. Do not use unrestricted raw-text or
   opaque JSON nodes, no-ops or similar fallbacks to claim full coverage.
3. Use a small, versioned transport between PHP and OCaml. Tagged JSON is a
   practical choice, but the library's default JSON dump is insufficient:
   PHP strings can contain invalid UTF-8 and floats can be non-finite. Encode
   byte strings explicitly, for example as base64; distinguish null/absent
   option fields from empty lists. Encode integer payloads as decimal strings
   rather than floating-point JSON numbers. Preserve numeric literal lexemes
   and use an explicit representation for floating-point payloads, including
   non-finite values, without silently rounding or dropping them. Define the
   normalization used when equivalent numeric spellings are compared.
4. Build values with the SpecTec constructors and validate against the declared
   `program` type. A second unchecked host AST or a type-name annotation alone
   is not validation of the formal syntax.
5. Reconstruct fresh PHP-Parser nodes solely from the checked SpecTec value and
   retained, specified metadata. Use ordinary `PrettyPrinter\Standard` with
   fixed formatting options. Do not print from the original AST or use
   format-preserving printing to bypass conversion through original tokens.

Start with this reuse architecture. Bidirectional conversion still requires
complete mappings; it is not free. Nevertheless, it reuses established printing
rules instead of implementing PHP precedence, escaping and statement formatting
again. If the coverage audit finds significant unsupported syntax or unfixable
loss of required information, minimize the cases and document the gap. Consider
a small vendor patch first when appropriate. A Zend-backed parser helper or an
OCaml lexer/Menhir parser is a fallback requiring an explicit revised design,
not a silent change of target or a blanket exclusion of missing syntax.

## P4-SpecTec integration and checks

`.watsup` syntax declarations describe specification values; they do **not**
generate a PHP source parser. Stock P4 `parse/run/sim` adapters are not PHP
frontends. Reuse the generic elaborator/runtime libraries and a small driver;
do not copy P4 architectures or evaluation phases into the syntax project.
Prioritize PHP syntax artifacts; limit framework changes to demonstrated
integration blockers rather than speculative refactoring.

The pinned framework revision is
`da36ac3c434cd291940293a63da64544307730a3`, with local provenance and a
reproduced offline build. Its core builds without the
P4 compiler submodule; the entire P4 test/compiler ecosystem is unnecessary.
Public libraries include `p4spectec.pass`, `p4spectec.runtime` and
`p4spectec.backend_boot`. The retained core and complete 97-package OCaml source
closure are documented in [dependencies/README.md](dependencies/README.md).

The studied build used OCaml 5.1.0, Dune 3.24.2, Menhir/menhirLib 20240715,
bignum/Core/core_unix v0.17.x, yojson 3.0.0 and ppx_deriving_yojson 3.9.1.
Record the actual successful dependency closure rather than treating this
orientation list as a complete lockfile.

At this pin, `Runtime.Value.Make` attaches type annotations without checking
them. The runtime membership checker also has a permissive optional-value
branch; do not assume it validates arbitrary imported values. Initially,
serialize ASTs into typed `.watsup` fixtures and elaborate them, or use an
equivalent checked elaboration API. Establish that malformed constructors,
wrong arities, payload types, options and lists are rejected. Optimize to a
direct validator only with equivalent positive/negative evidence.

Elaborate the schema and imported AST fixtures. Additional algorithmic or
structuring passes are relevant when executable specification functions are
introduced; they are not substitutes for AST membership checks. Some framework
CLI diagnostics have returned exit status zero. Prefer Result-returning APIs
mapped to failure exits, or inspect diagnostics and expected results as well
as exit status. Do not interpret a crash as expected rejection.

## Corpora and reference observations

Use two complementary corpora, copied into this project with manifests:

- **Matching PHP 8.5.10 engine tests:** obtain the release's PHPT files and
  referenced fixtures. The earlier workspace inventory of 22,878 PHPT files
  describes 8.6-dev, not the required release. Development tests can become
  separately labelled version-negative inputs but are not automatically valid
  8.5 examples.
- **BolaRay application benchmarks:** the studied artifact contains 25
  applications and 8,961 `.php` files, spanning older and newer application
  versions. Record exact application snapshots, source origins, checksums and
  licenses. These counts are inventory evidence, not a required acceptance
  count or a complete language test suite. Candidate sources can also have
  extensions such as `.inc` or template extensions; identify them explicitly.

Use the matching PHP `run-tests.php` as the PHPT format authority. Extract the
source sections instead of parsing the entire container as PHP. Support `FILE`,
`FILEEOF` and `FILE_EXTERNAL`; account for the runner's trailing-newline handling
of `FILEEOF`, relative external paths, and redirect/non-source tests. Preserve
original bytes and syntax-relevant `INI`/encoding settings. Keep source IDs,
section/file origins and configuration in each test record. Resolve external
fixtures within the imported corpus, never through a sibling checkout.

Do not execute `SKIPIF`, `CLEAN`, benchmark programs or the full PHPT runtime
suite merely to collect syntax. An extension-dependent runtime skip does not
necessarily prevent parsing its source. `EXPECT`, `EXPECTF` and `EXPECTREGEX`
describe runtime harness expectations, not a reliable parser-acceptance label.
Tests expecting an error can contain valid syntax followed by compile/runtime
failure; never exclude them all. Similarly, PHP inside `eval()` strings or
generated files is not covered by parsing the outer test. Track this gap and
extract documented static cases separately; do not claim arbitrary dynamic
code generation is covered without executing it.

Classify original inputs with the pinned engine. Preserve historical or invalid
benchmark files and their rejection categories; do not modernize them silently.
Keep syntax-accepted inputs even if they require unavailable services or removed
runtime functions. Deduplication may reduce execution cost but must retain
provenance and honest per-source coverage counts.

The initial practical oracle was `token_get_all($source, TOKEN_PARSE)`.
Validation exposed its string/file distinction for BOM, shebang and source
encodings. The revised design uses a narrow [native helper](native/README.md)
to invoke the pinned source-file `zendparse` without compilation or evaluation.
A separate raw file lexer supplies tokens to PHP-Parser's independent grammar;
raw `TOKEN_PARSE` remains an optional, separately labelled worker observation,
not the full-corpus reference. Ordinary raw
lexing does not establish acceptance. Keep `php -l` results separate: linting also
performs compilation checks. Record acceptance, parser rejection, compile
rejection where checked, adapter rejection, unsupported input, crash and
timeout separately. Compare raw frontend/oracle outcomes before applying any
production acceptance gate, so a Zend gate cannot conceal frontend errors.

PHP-Parser has its own parser but shares PHP's tokenizer. Agreement with Zend
is useful parser/adapter evidence, not independent lexical validation. If a
Zend-backed frontend is adopted, a second call to Zend is no longer an
independent parser check either. Optional normalized Zend AST comparison can
strengthen structural evidence, but its export and normalization need their
own tests; engine AST lowering does not preserve every source distinction.

## Validation and completion gates

For each accepted source `s`, let `A(s)` be its checked SpecTec AST and `P` its
canonical printer. Test both:

```text
P(A(s)) = P(A(P(A(s))))
normalize(A(s)) = normalize(A(P(A(s))))
```

The first checks printing stability; the second detects information loss that
can stabilize after the first print. Also test both conversion directions
structurally, parser/oracle acceptance agreement, output acceptance, and that
mutating a SpecTec constructor or payload affects output or is rejected.
Document normalization instead of dropping arbitrary fields until tests pass.

Add hand-authored fixtures for every grammar/constructor family, targeted
negative cases and bounded generated/mutated cases. Prioritize operator
grouping, lexical state transitions, tags/comments, interpolation/heredoc,
byte payloads, modern syntax interactions and configuration variants.
Corpora do not prove completeness, and shared upstream code can share bugs.
Keep minimized discrepancies as regression inputs with root-cause categories.

Use these ordered milestones:

1. **Reproduce dependencies and inventory.** Provision local PHP 8.5.10 with
   tokenizer/JSON and a pinned SpecTec build; wire local autoloading. Import
   matching source references and initial corpora with licenses/checksums.
   Establish the full token/production/constructor inventory, configuration
   profiles and acceptance boundary. Gate: versions verified, no sibling
   operational dependencies, and feature gaps recorded rather than assumed away.
2. **One complete path.** Define a small `.watsup` AST slice, byte-safe transport,
   checked conversion in both directions and standard printing. Include a
   nontrivial expression and a byte/lexical boundary case, plus malformed-AST
   rejection. Gate: both round-trip properties exercise the actual SpecTec
   value, parser-stage comparison is in place, and failures have reliable exits.
3. **Complete syntax.** Expand by inventory family until all target productions
   and lexical forms map to implemented, checked AST constructors. Keep schema,
   adapters and printer reconstruction synchronized. Gate: every inventory
   entry has an implementation mapping and targeted evidence; no unresolved
   supported-syntax exclusions or generic opaque fallbacks remain.
4. **Full classified validation.** Run the matching engine and application
   corpora, targeted negative cases and generated interaction tests. Investigate
   discrepancies, minimize failures and audit unexercised inventory entries.
   Gate: all applicable positive cases pass, negative classifications are
   justified, and each unsupported/excluded case has an explicit reason.
   Resource limits, missing fixtures or frontend gaps remain incomplete work,
   not evidence of full coverage.
5. **Portable handoff.** Copy the project without relying on Git metadata to a
   different path, make sibling resources unavailable, disable network access,
   and run documented checks with the declared system prerequisites. Audit
   links, source paths and dependency/corpus provenance. Gate: reproducible
   local builds/tests, documented limitations and an accurate coverage report.

Maintain a simple machine-readable coverage/corpus manifest and a concise work
log as implementation proceeds. Record feature, source evidence, implementation
location, fixture IDs, status and discrepancy reasons. Track imported, tested,
accepted, rejected, excluded and failed counts separately. An exclusion ledger
is accountability, not a mechanism for reducing the agreed full-syntax scope.
Tests provide evidence; do not claim a proof of PHP conformance or BOLA freedom.

## Starting work in a fresh session

Read this plan and the local vendor provenance. Check the user's current
authorization, repository status and any applicable repository instructions;
preserve existing changes. Inspect the implementation, manifests and work log
before selecting the next incomplete milestone. Continue from the first incomplete
validated milestone, rather than restarting dependency work or adding semantics.
Update the work log and validated status after authorized work so another agent
can resume without the original conversation or external skill files.

Useful upstream provenance, to be pinned/imported where needed:

- [PHP 8.5.10 release](https://www.php.net/releases/8_5_10.php)
- [PHP source tag](https://github.com/php/php-src/tree/php-8.5.10)
- [P4-SpecTec candidate revision](https://github.com/kaist-plrg/p4-spectec/tree/da36ac3c434cd291940293a63da64544307730a3)
- [PHP-Parser v5.8.0 source](https://github.com/nikic/PHP-Parser/tree/v5.8.0)
- [PHP-Parser v5.8.0 grammar](https://github.com/nikic/PHP-Parser/blob/v5.8.0/grammar/php.y)

These links aid acquisition and provenance; following them is not a prerequisite
for understanding the decisions or an alternative to local required inputs.
