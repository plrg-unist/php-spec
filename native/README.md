# PHP 8.5.10 file scanner bridge

`scripts/build-file-helper.sh` builds `.tools/php-file.so` against the local
PHP headers. Load it with `php -n -d extension=/project/.tools/php-file.so`.
The bridge is pinned at compile time to PHP 8.5.10. Its lifecycle and raw lexer
loop derive from the release's `ext/tokenizer/tokenizer.c`; the PHP 3.01 license
and original attribution are retained in the C header and adjacent `LICENSE`
(copied unchanged from `vendor/php-src/LICENSE`).

- `php_spec_parse_file(path)` calls the native file scanner and `zendparse`.
  It returns true or propagates parser/static parser exceptions. It never calls
  compilation or evaluation. Compile-only errors can therefore remain accepted.
- `php_spec_lex_file(path, events = [])` returns raw tokens, their stitched bytes,
  initial/final buffers, original filter input, initial/final encodings and skipped
  shebang preamble.
  Each event is `{token: closing_parenthesis_ordinal, encoding: name}` discovered
  by the independent frontend. It changes the filter immediately after that token,
  exactly as the Zend grammar does. Raw lexing never calls the parser or uses its
  feedback; emitted event records also contain the scanner byte offset.
- `frontend/FileLexer.php` converts those tokens to PHP-Parser tokens and reuses
  upstream lexical postprocessing. Temporary files are read and then removed.

Native file scanning matters: string-mode `TOKEN_PARSE` supplies the internal
encoding as a scanner override and does not implement the same BOM/shebang/file
encoding selection. The two parsers remain independent; they share Zend lexing,
just as PHP-Parser normally shares PHP's tokenizer.

Run `tests/native-file.php` with the extension, `zend.multibyte=1` and
`internal_encoding=UTF-8`. It checks token parity, grammar versus compile phases,
BOMs, source-encoding rescanning, shebang locations, error-state recovery and
that parsing code with a file-writing statement never executes that statement.

The scanner-state audit covers every parser-driven lexical mutation in the pinned
`Zend/zend_language_parser.y`: encoding declarations (line 536) and stopping at
outer `__halt_compiler` (line 412). Document-comment backups affect metadata;
nesting and heredoc states are lexer-owned. Raw/parser-mode branches additionally
change token values and diagnostics, which the independent frontend handles.

Encoding selection follows `zend_language_scanner.l`: BOM/null-byte detection
precedes the configured encoding list; declarations subsequently change the filter.
`zend_multibyte_yyinput_again` (line 881) reconverts the whole original buffer and
keeps the numeric cursor offset. Previously emitted tokens therefore must be
retained separately from the final buffer. Multiple leading declarations are
compiler-valid; `zend_compile.c:7007` rejects late/nested declarations but its
first-statement check skips preceding declarations. The native regression includes
a non-ASCII comment before a valid declaration to detect accidental prefix rewriting.

The initial scanner buffer and original filter input are separate observations:
without an input filter, a detected BOM can remain an inline-HTML token even when
Zend has removed it from the base used by later encoding rescans. The native tests
retain this distinction explicitly.

[Configuration audit](CONFIGURATION.md) records the finite source-setting closure,
precedence, aliases, filter state and required interaction evidence.
