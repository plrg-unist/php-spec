"""Current arrays convert by count only after the undefined-CV CAST Warning."""

CASES = [{
    'id': 'undefined-current-array-nonempty',
    'source': '''<?php
function currentArray($level, $message) {
    $name = "missing";
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $GLOBALS[$name] = [];
    } elseif ($message === "String offset cast occurred") {
        $GLOBALS[$name] = [7];
    }
    return true;
}
set_error_handler("currentArray", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;b;Z;',
}, {
    # Independently authored: only CAST creates a separate empty array CV.
    'id': 'undefined-current-array-empty-review',
    'source': '''<?php
function currentArrayReview($level, $message) {
    echo $level, ":", $message, ";";
    if ($message === "String offset cast occurred") {
        $name = "missing";
        $empty = [];
        $GLOBALS[$name] = $empty;
    }
    return true;
}
set_error_handler("currentArrayReview", 2);
echo "R:", "abc"[$missing], ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;a;Z;',
}]
