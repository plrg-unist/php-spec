"""Quiet complements over integer-result scalar arithmetic select literal bases before initial raw-key Warnings."""

CASES = [dict(
    id='coercive-integer-bitnot-truth-base-initial-raw-leading-current-key',
    source='''<?php
function coerciveIntegerBitnotTruthBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("coerciveIntegerBitnotTruthBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = ((~(("2" + true) * "1")) ? "abc" : "XYZ")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='coercive-integer-bitnot-truth-base-initial-raw-leading-reference-key',
    source='''<?php
function coerciveIntegerBitnotTruthBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("coerciveIntegerBitnotTruthBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = ((~((null / "2") - true)) ? "XYZ" : "abc")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18)]
