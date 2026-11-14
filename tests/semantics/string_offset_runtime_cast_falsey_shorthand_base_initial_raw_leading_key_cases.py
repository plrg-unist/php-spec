"""Falsey emitted scalar casts keep the fallback header before a raw-key Warning."""

CASES = [dict(
    id='runtime-cast-falsey-shorthand-base-initial-raw-leading-current-key',
    source='''<?php
function runtimeCastFalseyShorthandBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeCastFalseyShorthandBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((float)(int)(bool)"0") ?: "abc")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-cast-falsey-shorthand-base-initial-raw-leading-reference-key',
    source='''<?php
function runtimeCastFalseyShorthandBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeCastFalseyShorthandBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((string)(bool)"0") ?: "abc")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18)]
