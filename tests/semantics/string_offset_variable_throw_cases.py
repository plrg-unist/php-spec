"""Keep a VARIABLE base header when the first undefined-key handler throws."""

CASES = [{
    'id': 'undefined-variable-base-supplied-throw-current-in-range',
    'source': '''<?php
function variableUndefinedThrow($level, $message, $file, $line) {
    global $supplied;
    echo "U|";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    $name = "key";
    $GLOBALS[$name] = 4;
    restore_error_handler();
    throw $supplied;
}
$base = "abcde";
$supplied = new Exception("supplied");
$dst = 99;
set_error_handler("variableUndefinedThrow", 2);
try {
    $dst = $base[$key];
    echo "bad";
} catch (Exception $caught) {
    echo $caught === $supplied ? "same|" : "other|";
    echo $dst, "|", $key, "|", $base, ";Z;";
}
''',
    'expected_stdout': 'U|same|99|4|99;Z;',
    'expected_warnings': ['String offset cast occurred'],
    'read_line': 18,
}, {
    # Independently proposed by resume_dynamic_base_cv_review.
    'id': 'undefined-variable-base-supplied-throw-old-bounds-review',
    'source': '''<?php
function variableUndefinedThrowReview($level, $message, $file, $line) {
    global $supplied;
    echo "U|";
    $name = "base";
    $replacement = "abcdefghij";
    $GLOBALS[$name] =& $replacement;
    $name = "key";
    $GLOBALS[$name] = 8;
    restore_error_handler();
    throw $supplied;
}
$base = "abc";
$supplied = new Exception("supplied");
$dst = 99;
set_error_handler("variableUndefinedThrowReview", 2);
try {
    $dst = $base[$key];
    echo "bad";
} catch (Exception $caught) {
    echo $caught === $supplied ? "same|" : "other|";
    echo $dst, "|", $key, "|", $base, ";Z;";
}
''',
    'expected_stdout': 'U|same|99|8|abcdefghij;Z;',
    'expected_warnings': ['String offset cast occurred', 'Uninitialized string offset 8'],
    'read_line': 18,
}]
