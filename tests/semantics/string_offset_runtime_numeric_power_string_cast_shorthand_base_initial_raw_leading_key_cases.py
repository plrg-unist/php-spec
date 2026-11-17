"""Quiet completed numeric powers select emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-numeric-power-string-cast-shorthand-float-zero-current-key',
    source=r'''<?php
function runtimeNumericPowerStringCastShorthandFloatZeroBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeNumericPowerStringCastShorthandFloatZeroBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((float)0) ** 1) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-numeric-power-string-cast-shorthand-negative-zero-reference-key',
    source=r'''<?php
function runtimeNumericPowerStringCastShorthandNegativeZeroBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeNumericPowerStringCastShorthandNegativeZeroBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((-((float)0)) ** 3) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-numeric-power-string-cast-shorthand-integer-null-current-key',
    source=r'''<?php
function runtimeNumericPowerStringCastShorthandIntegerNullBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeNumericPowerStringCastShorthandIntegerNullBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((int)null) ** 2) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-numeric-power-string-cast-shorthand-integer-false-reference-key',
    source=r'''<?php
function runtimeNumericPowerStringCastShorthandIntegerFalseBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeNumericPowerStringCastShorthandIntegerFalseBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((int)false) ** 1) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
