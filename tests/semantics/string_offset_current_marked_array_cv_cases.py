"""Count a current marked ARRAY after initially undefined string-key Warnings."""

CASES = [{
    'id': 'undefined-current-marked-empty-array-cv',
    'source': '''<?php
function currentMarkedArray($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        global $missing;
        $missing = [];
    }
    return true;
}
set_error_handler("currentMarkedArray", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;a;Z;',
}, {
    # Independently proposed by resume_dynamic_array_values_review.
    'id': 'undefined-current-marked-array-mixture-rebind-review',
    'source': '''<?php
function currentMarkedArrayReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $name = "missing";
        $GLOBALS[$name] = 3;
    }
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $empty = [];
        $leaf = false;
        $outer = [&$empty, &$leaf, $empty, &$leaf];
        $GLOBALS[$name] =& $outer;
    }
    return true;
}
set_error_handler("currentMarkedArrayReview", 2);
echo "R:", "abcde"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}]
