"""Quiet signed64 integer binary trees select literal bases before raw-key Warnings."""

CASES = [dict(
    id='integer-binary-truth-base-initial-raw-leading-current-key',
    source='''<?php
function integerBinaryTruthBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("integerBinaryTruthBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = ((((((((2 ** 3) % 3) << 1) >> 1) & 3) | 1) ^ 2) ? "abc" : "XYZ")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='integer-binary-truth-base-initial-raw-leading-reference-key',
    source='''<?php
function integerBinaryTruthBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("integerBinaryTruthBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((9223372036854775807 << 64) | ((-1 >> 64) ^ -1)) ? "XYZ" : "abc")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18)]
