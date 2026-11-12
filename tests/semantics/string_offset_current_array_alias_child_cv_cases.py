"""Count the current outer ARRAY without converting an ALIAS child ARRAY."""

CASES = [{
    'id': 'undefined-current-array-alias-child',
    'source': '''<?php
function currentArrayReferenceChild($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $empty = [];
        $GLOBALS[$name] = [&$empty];
    }
    return true;
}
set_error_handler("currentArrayReferenceChild", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}, {
    # Independently proposed by resume_dynamic_array_values_review.
    'id': 'undefined-current-array-repeated-alias-child-review',
    'source': '''<?php
function currentArrayReferenceChildReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $empty = [];
        $GLOBALS[$name] = [0, &$empty, &$empty];
    }
    return true;
}
set_error_handler("currentArrayReferenceChildReview", 2);
echo "R:", "abcd"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}]
