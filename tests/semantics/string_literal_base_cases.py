"""Literal string bases use the existing cast/bounds Warning continuations."""

CASES = [
    {
        'id': 'literal-base-cast-and-bounds',
        'source': '''<?php
function literalBaseHandler($level, $message, $file, $line) {
    echo "H:", $level, ";";
    return true;
}
set_error_handler('literalBaseHandler', 2);
$offset = 1.5;
echo "R:", "abc"[$offset], ";";
$offset = 5;
echo "B:", "abc"[$offset], ";";
''',
        'expected_stdout': 'R:H:2;b;B:H:2;;',
    },
    {
        'id': 'literal-base-live-cast-key-fixed-bounds',
        'source': '''<?php
function literalBaseWriteHandler($level, $message, $file, $line) {
    $name = 'offset';
    $GLOBALS[$name] = 2;
    echo "H:", $level, ";";
    return true;
}
set_error_handler('literalBaseWriteHandler', 2);
$offset = 1.5;
echo "R:", "abc"[$offset], ";K:", $offset, ";";
$offset = 5;
echo "B:", "abc"[$offset], ";K:", $offset, ";";
''',
        'expected_stdout': 'R:H:2;c;K:2;B:H:2;;K:2;',
    },
]
