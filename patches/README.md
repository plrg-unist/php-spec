# PHP-Parser corrections

The runtime distribution is pinned v5.8.0 plus the corrections below. The
unchanged distribution archive and full upstream grammar/tests remain in
`vendor/archives` and `vendor/php-parser-source`. Patches preserve upstream's
BSD-3-Clause license.

| Correction | Evidence |
| --- | --- |
| Add `T_PROPERTY_C` to semi-reserved identifiers; regenerate the PHP 8 tables | Valid `function __PROPERTY__()` in a class; target Zend grammar and `reserved-identifiers.php` |
| Defer four import-alias semantic checks from grammar reductions to compilation | `imports-reserved-*`: function/constant `Self` and `Parent` aliases compile; class aliases parse but fail compilation, matching `zend_compile_use` |
| Retain ternary grouping as checked boolean metadata at the actual grouping reduction | `ternary_metadata.py`: parentheses in calls/control headers are not expression grouping; independent compiler checks consume the distinction |
| Select PHP 8 concatenation precedence between shifts and pipe | `precedence.php`: `('x' . 1) + 2` previously changed grouping |
| Retain a trailing comma for singleton positional `clone` call nodes | `clone85.php`: `clone($a,)` otherwise reparsed as unary clone |
| Retain original array syntax on converted destructuring lists and print it faithfully | `destructuring_metadata.py`: nested `array(...)` otherwise became square syntax, erasing a distinct compiler rejection; list storage retains omitted slots |
| Preserve the first omitted list slot's comma line before removing its placeholder | `list_line_metadata.py`: otherwise identical checked trees need different compiler diagnostic lines; empty `list()` is a closing-token control |
| Preserve nested destructuring spread flags when converting array nodes into lists | `destructuring_metadata.py`: nested spreads otherwise became ordinary list entries before checked transport |
| Retain final omitted destructuring slots | `optional` fixture: `[,]` otherwise printed `[]` |
| Preserve signed integer offsets in simple interpolation | `interpolation.php`, Zend `bug72918.phpt`: braced interpolation otherwise becomes UnaryMinus |
| Preserve comments on every node, including grouping, attributes and nonfinal empty statements | `comments-attachments.php`, generated operand combinations and minimized corpus regressions |
| Attach otherwise unassigned token comments deterministically without losing declaration doc comments | `comments-parentheses.php`; independent token-comment retention assertion |
| Keep interpolation comments inside the expression braces with a stable attachment | Seven `comments-interpolation-*` fixtures and the CodeMirror application example |

`php-parser-grammar.patch` changes the source grammar. Run
`scripts/rebuild-parser.sh` to regenerate in a disposable directory and compare
the checked-in runtime parser; `--write` replaces it. The local pinned generator
and its prerequisites are recorded in `dependencies/README.md`.
`php-parser-printer.patch` records the hand-edited parser, printer and comment-attachment changes against the
unchanged distribution. No P4-SpecTec or PHP engine runtime patch is needed.
