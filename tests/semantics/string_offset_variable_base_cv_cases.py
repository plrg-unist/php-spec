"""Keep the selected interned base while initially undefined keys change."""

CASES = [{
    'id': 'undefined-variable-base-marked-string-current-cv',
    'source': '''<?php
function variableBaseCv($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        global $base;
        $base = "XYZ";
        $name = "missing";
        $GLOBALS[$name] = 1;
    }
    if ($message === "String offset cast occurred") {
        global $missing;
        $missing = "2tail";
    }
    return true;
}
$base = "abc";
set_error_handler("variableBaseCv", 2);
echo "R:", $base[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;c;Z;',
}, {
    # Independently proposed by resume_dynamic_array_values_review.
    'id': 'undefined-variable-base-marked-array-rebind-review',
    'source': '''<?php
function variableBaseCvReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $name = "base";
        $replacement = 99;
        $GLOBALS[$name] =& $replacement;
        $name = "missing";
        $GLOBALS[$name] = 3;
    }
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $empty = [];
        $outer = [&$empty, $empty];
        $GLOBALS[$name] =& $outer;
    }
    return true;
}
$base = "abcde";
set_error_handler("variableBaseCvReview", 2);
echo "R:", $base[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}]
