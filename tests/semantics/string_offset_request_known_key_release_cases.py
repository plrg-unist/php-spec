"""Last-owner REQUEST death at CAST with an immutable primitive offset."""

CASES = [{
    'id': 'request-base-known-false-cast-release',
    'source': '''<?php
function requestKnownRelease($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$got = 99;
set_error_handler("requestKnownRelease");
$got = $base[false];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:null;B:99;Z;',
    'expected_warnings': [],
    'read_line': 14,
}, {
    'id': 'request-base-known-true-cast-release-prior',
    'source': '''<?php
function requestKnownPrior($level, $message, $file, $line) {
    return true;
}
function requestKnownRelease($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$got = 99;
set_error_handler("requestKnownPrior", 2);
set_error_handler("requestKnownRelease");
$got = $base[true];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:null;B:99;Z;',
    'expected_warnings': [],
    'read_line': 18,
}]
