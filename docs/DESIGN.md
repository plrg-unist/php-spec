# Syntax representation

The target is PHP 8.5.10 CLI, NTS, 64-bit. PHP-Parser and Standard are both
explicitly configured for PHP 8.5. `token_get_all(..., TOKEN_PARSE)` supplies a
separate parser observation; linting additionally checks compilation. The
frontend never evaluates input code or resolves names. Short tags are selected
at PHP worker startup, where the tokenizer observes the actual INI profile.

`spec/nodes.json` records explicit ordered field contracts from the pinned
PHP-Parser node classes, including inherited declarations. The reviewed generator
resolves class names, lists and unions, then emits `spec/php.watsup` and the
adapter's `spec/schema.json` mapping. Formal field domains distinguish statements,
expressions, names, auxiliary nodes, nullable bodies and ordered lists. They
include parser-accepted forms that compilation can reject. Recovered error nodes
are forbidden. Unknown nodes, fields and metadata fail visibly.

The transport has version `1` and a statement-list `program`. Node fields are
ordered; metadata keys are named. Byte strings use canonical base64. Integers
use canonical decimal strings within the target machine range. Float payloads
use 16 hexadecimal digits containing IEEE-754 binary64 bits, preserving overflow
infinity and avoiding JSON number conversion. Literal spellings remain metadata.
Comments retain their bytes, doc-comment distinction and six source positions.
The schema declares every accepted metadata key and its payload type.

The OCaml adapter constructs `Runtime.Value` objects, then recursively checks
**the values themselves** against elaborated `.watsup` definitions. It ignores
attached type annotations. Constructor shapes/arity, primitive payloads, lists,
options and records are checked exactly; the framework's permissive runtime
membership helper is not used. Typed fixture elaboration provides an independent
check of the same membership boundary. The schema is loaded once per worker.

Reverse conversion reads only the checked value. PHP reconstruction allocates
fresh nodes and assigns every declared field, avoiding constructor defaults or
normalizations that could change supplied values. Standard receives these fresh
nodes; original nodes and lexer tokens cannot bypass the adapter. The low-level
workers are test interfaces; `bin/php-syntax` provides the checked public path
and nonzero process failure exits.

This is a canonical abstract syntax, not a lossless concrete syntax tree or a
PHP compiler. Whitespace, redundant parentheses and alternative statement syntax
can normalize. Literal/identifier/inline-output bytes and halt payloads remain
explicit. Printing can change `__LINE__`, file locations and halt offsets, so
syntax round trips do not establish execution equivalence.
