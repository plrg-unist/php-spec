# Syntax representation

The target is PHP 8.5.10 CLI, NTS, 64-bit. PHP-Parser and Standard are both
explicitly configured for PHP 8.5. The [native helper](../native/README.md) invokes
Zend's source-file parser without compilation or evaluation. Its separate raw
file lexer supplies tokens to PHP-Parser's independent grammar. This preserves
file-mode BOM, shebang and encoding behavior that `TOKEN_PARSE` string scanning
misses. Raw `TOKEN_PARSE` is an optional worker observation; lint adds
compilation checks. No input code is executed and no names are resolved.

Source INI profiles apply to the native file scanner. In particular,
`zend.script_encoding` is scoped around source reads so that it cannot decode
the tooling files themselves. Encoding declarations are interpreted lexically
without using Zend parser acceptance to gate the independent PHP-Parser parse.
Encoding names use Zend's canonical/MIME/alias registry. Only literal scalar
concatenation is folded for declaration lookup, matching Zend's parser action;
the source `precision` setting therefore also matters for float operands.

`spec/nodes.json` records explicit ordered field contracts from the pinned
PHP-Parser node classes, including inherited declarations. The reviewed generator
resolves class names, lists and unions, then emits `spec/php.watsup` and the
adapter's `spec/schema.json` mapping. Formal field domains distinguish statements,
expressions, names, auxiliary nodes, nullable bodies and ordered lists. They
include parser-accepted forms that compilation can reject. Recovered error nodes
are forbidden. Unknown nodes, fields and metadata fail visibly.
These declarations define value domains, not a PHP source parser. Keep the
explicit mappings complete; raw-source or opaque-node fallbacks cannot replace
unsupported syntax.

The transport has version `1` and a statement-list `program`. Node fields are
ordered; metadata keys are named. Byte strings use canonical base64. Integers
use canonical decimal strings within the target machine range. Float payloads
use 16 hexadecimal digits containing IEEE-754 binary64 bits, preserving overflow
infinity and avoiding JSON number conversion. Literal spellings remain metadata.
Comments retain their bytes, doc-comment distinction and six source positions.
A deterministic attachment pass retains comments that upstream leaves unattached.
The schema declares every accepted metadata key and its payload type.
Anonymous namespace nodes additionally retain integer `namespaceBraceLine`, the
opening-brace token line after whitespace and comments. It comes from the effective
lexer tokens, including encoded sources, and survives checked elaboration and fresh
node reconstruction. Compiler diagnostics consume this field; the printer does not.
Break and continue nodes similarly retain integer `statementTerminatorLine`, the
start line of their semicolon or closing-tag terminator token. The closing-tag
token can include a newline, so the statement end line is insufficient. This
field also uses effective lexer tokens, survives fresh reconstruction, and never
instructs the printer to replay source. The compiler validates the consumed line
against the statement's retained start/end range; edited syntax remains explicit
input, not authenticated source provenance.
If/elseif/else, while, do and for nodes additionally retain integer
`statementBodyLine`: the opening brace/colon token line for a synthetic Zend
statement list, or zero when the grammar uses a single statement. Header scans
match actual parenthesis tokens, ignoring punctuation inside string/comment
payloads. Empty `for(;;);` bodies have no Zend child AST and retain their semicolon
or closing-tag start line as `statementTerminatorLine`; a comment Nop alone does
not make a braced/alternative body a bare statement. These fields prepare exact
control compilation; their transport does not enable control execution.

Array-to-list conversion preserves each nested `ArrayItem.unpack` field,
including otherwise compiler-invalid spread targets. Syntax checking and fresh
printing retain these flags; compiler legality remains a separate phase.

Ternaries retain boolean `parenthesizedConditional`, set by the actual grouping
production and false at ternary construction. Call/control parentheses do not
set it. This distinguishes otherwise identical nested trees for later compiler
legality checks; printing still derives grouping from checked tree structure.

Encoded programs additionally carry initial source/lexer encoding names, BOM
and skipped shebang bytes. Noninjective or changing filters retain original byte
spelling as explicit provenance; that field is never read by the printer. Node
payloads and positions refer to actual filtered lexer bytes. The frontend checks
every token against the active conversion and native cursor, including encoding
declarations inside preceding declaration bodies.

The existing declaration nodes express each encoding switch. Fresh printing
marks generated declaration-header boundaries internally, converts each chunk
under its active source encoding, and removes the markers. It uses no original
source positions. When a new filter shortens the generated prefix, fresh spaces
after the header absorb Zend's retained numeric cursor offset; the next token
is preserved without replaying source text. Byte escapes preserve literal values
unavailable as source characters. When a codec decodes backslash as yen, an exact
representable literal spelling replaces otherwise unrepresentable escape syntax.
For configured replacement characters in comments or identifiers,
the printer derives a byte preimage using the pinned converter and checks the
entire inverse conversion; it never consults original spelling. Transfer-codec
printing likewise preserves decoded bytes, including bare newlines. Filtered wide encodings receive an unambiguous canonical BOM because Zend's
BOMless width heuristic can change after formatting; exact original BOM metadata
survives conversion, but canonical AST equality ignores this spelling choice.
Initial source/lexer encoding names are likewise decoding provenance: candidate
lists can select a different encoding after literal bytes become ASCII escapes.
Canonical equality ignores these initial names, BOM and original spelling;
exact checked conversion retains them all. Preamble and AST payload bytes,
including encoding directive literal values, remain strict.

Deep values use a bounded-depth wire table with indexed child references, keeping
the same typed AST while avoiding fixed JSON parser stack limits. All endpoints
reject malformed references and table shapes before normal schema validation.

The OCaml adapter constructs `Runtime.Value` objects, then recursively checks
**the values themselves** against elaborated `.watsup` definitions. It ignores
attached type annotations. Constructor shapes/arity, primitive payloads, lists,
options and records are checked exactly; the framework's permissive runtime
membership helper is not used. Typed fixture elaboration provides an independent
check of the same membership boundary. The schema is loaded once per worker.

Reverse conversion reads only the checked value. PHP reconstruction allocates
fresh nodes and assigns every declared field, avoiding constructor defaults or
normalizations that could change supplied values. The corrected Standard printer receives these fresh
nodes; original nodes and lexer tokens cannot bypass the adapter. The low-level
workers are test interfaces; `bin/php-syntax` provides the checked public path
and nonzero process failure exits.

This is a canonical abstract syntax, not a lossless concrete syntax tree or a
PHP compiler. Whitespace, redundant parentheses and alternative statement syntax
can normalize. Literal/identifier/inline-output bytes and halt payloads remain
explicit. Printing can change `__LINE__`, file locations and halt offsets, so
syntax round trips do not establish execution equivalence.
