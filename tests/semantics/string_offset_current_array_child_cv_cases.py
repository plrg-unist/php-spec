"""Count the current outer ARRAY without converting a DIRECT child ARRAY."""

CASES = [{
    'id': 'undefined-current-array-direct-child',
    'source': '''<?php
function currentArrayChild($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $GLOBALS[$name] = [[]];
    }
    return true;
}
set_error_handler("currentArrayChild", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}, {
    # Independently proposed by resume_dynamic_alias_review before execution.
    'id': 'undefined-current-array-repeated-child-review',
    'source': '''<?php
function currentNestedArrayReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $empty = [];
        $GLOBALS[$name] = [0, $empty, $empty];
    }
    return true;
}
set_error_handler("currentNestedArrayReview", 2);
echo "R:", "abcd"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}]
