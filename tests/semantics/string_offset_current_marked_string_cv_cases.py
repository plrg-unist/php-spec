"""Silently cast current marked string carriers after initially undefined keys."""

CASES = [{
    'id': 'undefined-current-marked-interned-string-cv',
    'source': '''<?php
function currentMarkedCarrier($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        global $missing;
        $missing = "2tail";
    }
    return true;
}
set_error_handler("currentMarkedCarrier", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;c;Z;',
}, {
    # Independently proposed by resume_dynamic_array_values_review.
    'id': 'undefined-current-marked-request-string-rebind-review',
    'source': '''<?php
function currentMarkedRequestReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $name = "missing";
        $GLOBALS[$name] = 1;
    }
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $left = "no";
        $right = "ise";
        $other = $left . $right;
        $GLOBALS[$name] =& $other;
    }
    return true;
}
set_error_handler("currentMarkedRequestReview", 2);
echo "R:", "abcd"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;a;Z;',
}]
