"""Read a marked current CV after initially undefined string-key Warnings."""

CASES = [{
    'id': 'undefined-current-marked-integer-cv',
    'source': '''<?php
function currentMarkedKey($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        global $missing;
        $missing = 2;
    }
    return true;
}
set_error_handler("currentMarkedKey", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;c;Z;',
}, {
    # Independently proposed by resume_dynamic_array_values_review.
    'id': 'undefined-current-marked-float-rebind-review',
    'source': '''<?php
function currentMarkedFloatReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $name = "missing";
        $GLOBALS[$name] = 1;
    }
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $other = 3.0;
        $GLOBALS[$name] =& $other;
    }
    return true;
}
set_error_handler("currentMarkedFloatReview", 2);
echo "R:", "abcd"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;d;Z;',
}]
