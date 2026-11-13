"""Observe cast/bounds diagnostics after an initially undefined-key handler throws."""

CASES = [{
    'id': 'undefined-key-supplied-throw-current-in-range',
    'source': '''<?php
function initialUndefinedThrow($level, $message, $file, $line) {
    global $key, $supplied;
    echo "U|";
    $key = 1;
    restore_error_handler();
    throw $supplied;
}
$supplied = new Exception("supplied");
$dst = 99;
set_error_handler("initialUndefinedThrow", 2);
try {
    $dst = "abc"[$key];
    echo "bad";
} catch (Exception $caught) {
    echo $caught === $supplied ? "same|" : "other|";
    echo $dst, "|", $key, ";Z;";
}
''',
    'expected_stdout': 'U|same|99|1;Z;',
    'expected_warnings': ['String offset cast occurred'],
    'read_line': 13,
}, {
    # Independently proposed by resume_dynamic_base_cv_review.
    'id': 'undefined-key-supplied-throw-current-out-of-range-review',
    'source': '''<?php
function initialUndefinedThrowReview($level, $message, $file, $line) {
    global $key, $supplied;
    echo "U|";
    $key = 8;
    restore_error_handler();
    throw $supplied;
}
$supplied = new Exception("supplied");
$dst = 99;
set_error_handler("initialUndefinedThrowReview", 2);
try {
    $dst = "abc"[$key];
    echo "bad";
} catch (Exception $caught) {
    echo $caught === $supplied ? "same|" : "other|";
    echo $dst, "|", $key, ";Z;";
}
''',
    'expected_stdout': 'U|same|99|8;Z;',
    'expected_warnings': ['String offset cast occurred', 'Uninitialized string offset 8'],
    'read_line': 13,
}]
