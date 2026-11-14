"""Quiet integer sign chains over numeric strings keep the shorthand fallback before a Warning."""

CASES = [dict(
    id='boolean-not-numeric-string-unary-shorthand-base-initial-raw-leading-current-key',
    source='''<?php
function booleanNotNumericStringUnaryShorthandBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("booleanNotNumericStringUnaryShorthandBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = (!(-(+(' 1 '))) ?: "abc")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='boolean-not-numeric-string-unary-shorthand-base-initial-raw-leading-reference-key',
    source='''<?php
function booleanNotNumericStringUnaryShorthandBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 2;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("booleanNotNumericStringUnaryShorthandBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (!(+('-9223372036854775808')) ?: "abc")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18)]
