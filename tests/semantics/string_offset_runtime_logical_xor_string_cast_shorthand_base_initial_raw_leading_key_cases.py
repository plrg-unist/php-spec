"""Quiet emitted false logical XOR selects emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-logical-xor-string-cast-shorthand-current-key',
    source=r'''<?php
function runtimeLogicalXorStringCastShorthandBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeLogicalXorStringCastShorthandBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null xor 0) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
dict(
    id='runtime-logical-xor-string-cast-shorthand-reference-key',
    source=r'''<?php
function runtimeLogicalXorStringCastShorthandBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeLogicalXorStringCastShorthandBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((float)0 xor false) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
