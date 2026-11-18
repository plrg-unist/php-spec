"""Quiet falsey shorthands select certified allocated fallback headers."""

WATCHED = []

CASES = [
    dict(id="runtime-allocated-falsey-shorthand-base-initial-raw-leading-current-key",
         source='''<?php
function runtimeAllocatedFalseyShorthandBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedFalseyShorthandBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((int)0 ?: ((string)10 . "bc" . "de"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:1;K:Illegal string offset "0x";Z;'),
    dict(id="runtime-allocated-falsey-shorthand-base-initial-raw-leading-reference-key",
         source='''<?php
function runtimeAllocatedFalseyShorthandBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 4;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("runtimeAllocatedFalseyShorthandBaseInitialRawReferenceLeading");
trigger_error("3x", E_USER_WARNING);
$got = ((string)0 ?: ((string)(-10.5) . "bc" . "de"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:3x;2:Illegal string offset "3x";R:.;K:4;A:Illegal string offset "3x";Z;'),
]
