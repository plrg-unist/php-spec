# Source scanner configuration audit

Authority: PHP 8.5.10, `Zend/zend_language_scanner.l`, `Zend/zend.c`,
`main/main.c`, and `ext/mbstring/mbstring.c`. This checklist concerns source
scanning, not PHP execution, request decoding, output conversion or resource limits.

| Input | Pinned `php -n` default | Source effect / authority |
|---|---|---|
| `short_open_tag` | `1` (the project explicitly chooses its profile) | `CG(short_tags)` controls `<?` and malformed full-tag fallback; scanner:2316–2357, main:820. Startup/per-directory setting. `<?=` is unconditional. |
| `zend.multibyte` | `0` | Enables source filtering and declaration effects; zend:266, scanner:548. Startup/per-directory setting. |
| `zend.detect_unicode` | `1` | BOM and NUL-byte UTF-width detection before configured candidates; scanner:376–480. |
| `zend.script_encoding` | unset | Single encoding, ordered candidate list, or `auto` expansion; scanner:459–480, mbstring:297–362. |
| `mbstring.language` | `neutral` | Selects the default candidate list expanded by `auto`; mbstring:682–695 and 332–343. |
| `mbstring.internal_encoding` | unset | Explicit internal encoding overrides the following fallback settings; mbstring:793–840. Its INI spelling is deprecated but supported. |
| `internal_encoding` | unset | Internal encoding when the mbstring override is absent; main:575–582. |
| `default_charset` | `UTF-8` | Fallback after an unset/empty `internal_encoding`; final fallback is UTF-8; main:575–582. |
| `mbstring.substitute_character` | unset, effective `?`/63 | Invalid-byte conversion mode: `none`, `long`, `entity`, or numeric character; mbstring:844–883, used by the source converter at456–468. |

The complete source-filter input closure is the nine settings above. Audited
non-inputs include `mbstring.detect_order` (the scanner passes an explicit list;
`auto` uses the language's default list), `mbstring.strict_detection` (the native
source detector passes `false, false`), HTTP/input/output encoding settings and
mbregex settings. Diagnostic presentation/error masks and resource limits can
change observations but do not select source grammar or lexical bytes.

## State and alias rules

- With multibyte disabled, no encoding conversion/declaration effect occurs.
  With it enabled, BOM/NUL detection precedes configured candidates.
- Source names/aliases come from bundled libmbfl. Deprecated transfer encodings
  (BASE64, UUENCODE, HTML-ENTITIES, Quoted-Printable) remain accepted by Zend;
  helper-owned deprecation notices must not become source diagnostics.
- A declaration passes its decoded literal to a C-string lookup, so a NUL suffix
  does not affect the selected name; the complete literal remains AST payload.
  INI lists instead use the native length-aware list parser, trim spaces/tabs,
  accept double-quoted lists, expand `auto`, and warn/retain the previous setting
  when invalid. `pass` is an invalid source encoding in the pinned PHPT regression.
- Filter selection is exactly scanner:485–523, using bundled lexer-compatibility
  flags, not guesses based on a charset name. Some apparently wide internal
  profiles therefore leave source as inline HTML; raw outcomes remain authoritative.
- Initial scanner bytes and the original filter base are distinct. A BOM can stay
  in an unfiltered initial buffer while being removed from the base for rescans.
- Every declaration header can change filtering. Rescans convert the whole
  original base while preserving the numeric cursor offset (scanner:881–911).
  Earlier emitted tokens remain unchanged. Multiple leading declarations are
  compiler-valid; placement checks skip earlier declarations (compile:6965–7012).
- Other parser-driven scanner changes are outer `__halt_compiler` termination
  (grammar:412) and doc-comment metadata backup/reset. Nesting, interpolation and
  heredoc states are owned by the scanner itself.
- Each helper call restores scanner/compiler state and temporary script profiles.
  Restoring an unset script encoding requires `ini_restore`; setting an empty
  string fails the native list setter. Frontend/helper files must load under their
  own profile, not the submitted source profile.

## Required evidence families

The targeted/generated validation gate must cover short tags on/off; UTF BOM and
BOMless detection; LF/CRLF/unterminated shebangs; internal-setting precedence;
source aliases and declaration NUL suffixes; single/multiple/auto candidate lists;
transfer encodings; every substitution mode; leading/multiple declaration changes;
non-ASCII comments/identifiers before changes; literal escapes; halt payloads;
and state recovery after invalid source/profile requests. The independent review
also runs cross-profile matrices over raw/SJIS/Latin1/UTF-8 source bytes and ordered
candidate lists. The final generated fixtures/reports, rather than this checklist,
record executed cases and outcomes. Compiler-invalid placement remains a separate
observation; it does not justify excluding compiler-valid filter transitions.
