"""Array count ignores authenticated INTERNED and REQUEST string referents."""

CASES = [{
    'id': 'undefined-current-array-string-alias-interned',
    'source': '''<?php
function currentStringAlias($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $text = "0";
        $GLOBALS[$name] = [&$text];
    }
    return true;
}
set_error_handler("currentStringAlias", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}, {
    'id': 'undefined-current-array-string-alias-request-review',
    'source': '''<?php
function currentStringAliasReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $left = "2";
        $right = "tail";
        $text = $left . $right;
        $GLOBALS[$name] = [0, &$text, &$text];
    }
    return true;
}
set_error_handler("currentStringAliasReview", 2);
echo "R:", "abcd"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}]
