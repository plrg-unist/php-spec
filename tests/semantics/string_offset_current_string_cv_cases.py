"""Strings written after an undefined-CV Warning use the later silent cast."""

CASES = [{
    'id': 'undefined-current-string-leading',
    'source': '''<?php
function currentString($level, $message) {
    $name = "missing";
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $GLOBALS[$name] = "1";
    } elseif ($message === "String offset cast occurred") {
        $GLOBALS[$name] = "2tail";
    }
    return true;
}
set_error_handler("currentString", 2);
echo "R:", "abc"[$missing], ";K:", $missing, ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;c;K:2tail;Z;',
}, {
    # Independently authored: the first handler leaves the CV undefined.
    'id': 'undefined-current-string-nonnumeric-review',
    'source': '''<?php
function currentStringReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $GLOBALS[$name] = "noise";
    }
    return true;
}
set_error_handler("currentStringReview", 2);
echo "R:", "abc"[$missing], ";K:", $missing, ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;a;K:noise;Z;',
}]
