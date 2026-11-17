"""Quiet emitted integer operations select emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-integer-binary-string-cast-shorthand-modulo-current-key',
    source=r'''<?php
function runtimeIntegerBinaryStringCastShorthandModuloBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeIntegerBinaryStringCastShorthandModuloBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null % 2) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-integer-binary-string-cast-shorthand-shift-left-reference-key',
    source=r'''<?php
function runtimeIntegerBinaryStringCastShorthandShiftLeftBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeIntegerBinaryStringCastShorthandShiftLeftBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null << 2) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-integer-binary-string-cast-shorthand-shift-right-current-key',
    source=r'''<?php
function runtimeIntegerBinaryStringCastShorthandShiftRightBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeIntegerBinaryStringCastShorthandShiftRightBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)1 >> 2) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-integer-binary-string-cast-shorthand-bitwise-and-reference-key',
    source=r'''<?php
function runtimeIntegerBinaryStringCastShorthandBitwiseAndBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeIntegerBinaryStringCastShorthandBitwiseAndBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)1 & 2) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-integer-binary-string-cast-shorthand-bitwise-or-current-key',
    source=r'''<?php
function runtimeIntegerBinaryStringCastShorthandBitwiseOrBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeIntegerBinaryStringCastShorthandBitwiseOrBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null | 0) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-integer-binary-string-cast-shorthand-bitwise-xor-reference-key',
    source=r'''<?php
function runtimeIntegerBinaryStringCastShorthandBitwiseXorBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeIntegerBinaryStringCastShorthandBitwiseXorBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)1 ^ 1) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
