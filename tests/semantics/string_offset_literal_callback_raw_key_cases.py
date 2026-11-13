"""Late raw key payloads are converted against a selected literal string base."""

CASES = [dict(
    id='literal-callback-raw-key-current-cell',
    source='''<?php
function literalRawKey($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    restore_error_handler();
    return true;
}
$key = true;
$got = 99;
set_error_handler("literalRawKey");
$got = "abc"[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='2:String offset cast occurred;R:a;K:String offset cast occurred;Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='literal-callback-raw-key-initial-reference',
    source='''<?php
function literalRawReferenceKey($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    $name = "key";
    $replacementKey = 2;
    $GLOBALS[$name] =& $replacementKey;
    restore_error_handler();
    return true;
}
$key = true;
$alias =& $key;
$got = 99;
set_error_handler("literalRawReferenceKey");
$got = "abc"[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='2:String offset cast occurred;R:a;K:2;A:String offset cast occurred;Z;',
    expected_warnings=[], read_line=16)]
