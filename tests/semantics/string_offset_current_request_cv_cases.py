"""Runtime-concatenated current keys are consumed after mandatory CAST."""

CASES = [{
    'id': 'undefined-current-request-leading',
    'source': '''<?php
function currentRequest($level, $message) {
    $name = "missing";
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $GLOBALS[$name] = 1;
    } elseif ($message === "String offset cast occurred") {
        $left = "2";
        $right = "tail";
        $GLOBALS[$name] = $left . $right;
    }
    return true;
}
set_error_handler("currentRequest", 2);
echo "R:", "abc"[$missing], ";K:", $missing, ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;c;K:2tail;Z;',
}, {
    # Independently authored: only CAST defines the key, from two nonempty CVs.
    'id': 'undefined-current-request-nonnumeric-review',
    'source': '''<?php
function currentRequestReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $left = "no";
        $right = "ise";
        $GLOBALS[$name] = $left . $right;
    }
    return true;
}
set_error_handler("currentRequestReview", 2);
echo "R:", "abc"[$missing], ";K:", $missing, ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;a;K:noise;Z;',
}]
