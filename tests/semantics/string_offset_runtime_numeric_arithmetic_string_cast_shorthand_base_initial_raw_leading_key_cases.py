"""Quiet emitted numeric arithmetic selects emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-numeric-arithmetic-string-cast-shorthand-add-float-current-key',
    source=r'''<?php
function runtimeNumericArithmeticStringCastShorthandAdditionBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeNumericArithmeticStringCastShorthandAdditionBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((float)0 + 0.0) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-numeric-arithmetic-string-cast-shorthand-subtract-float-reference-key',
    source=r'''<?php
function runtimeNumericArithmeticStringCastShorthandSubtractionBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeNumericArithmeticStringCastShorthandSubtractionBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((float)1 - 1.0) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-numeric-arithmetic-string-cast-shorthand-multiply-int-current-key',
    source=r'''<?php
function runtimeNumericArithmeticStringCastShorthandMultiplicationBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeNumericArithmeticStringCastShorthandMultiplicationBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null * 2) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-numeric-arithmetic-string-cast-shorthand-divide-int-reference-key',
    source=r'''<?php
function runtimeNumericArithmeticStringCastShorthandDivisionBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeNumericArithmeticStringCastShorthandDivisionBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null / 1) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
