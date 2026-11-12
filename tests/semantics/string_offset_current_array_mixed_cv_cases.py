"""Mixed entry order cannot change the current array's nonempty offset."""

CASES = [{
    'id': 'undefined-current-array-mixed-false',
    'source': '''<?php
function currentMixed($level, $message) {
    $name = "missing";
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $GLOBALS[$name] = 0;
    } elseif ($message === "String offset cast occurred") {
        $flag = false;
        $GLOBALS[$name] = [0, &$flag];
    }
    return true;
}
set_error_handler("currentMixed", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}, {
    'id': 'undefined-current-array-mixed-shared-false-review',
    'source': '''<?php
function currentMixedReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $flag = false;
        $GLOBALS[$name] = [&$flag, false, &$flag];
    }
    return true;
}
set_error_handler("currentMixedReview", 2);
echo "R:", "abcd"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}]
