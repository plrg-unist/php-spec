"""Quiet emitted BooleanNot conditions select emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-boolean-not-string-cast-shorthand-literal-float-current-key',
    source=r'''<?php
function runtimeBooleanNotStringCastShorthandFalseBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeBooleanNotStringCastShorthandFalseBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (!1.0 ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-boolean-not-string-cast-shorthand-negative-float-reference-key',
    source=r'''<?php
function runtimeBooleanNotStringCastShorthandNullBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeBooleanNotStringCastShorthandNullBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (!-1.0 ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-boolean-not-string-cast-shorthand-cast-float-current-key',
    source=r'''<?php
function runtimeBooleanNotStringCastShorthandZeroBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeBooleanNotStringCastShorthandZeroBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (!(float)2 ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-boolean-not-string-cast-shorthand-cast-negative-float-reference-key',
    source=r'''<?php
function runtimeBooleanNotStringCastShorthandNegativeZeroBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeBooleanNotStringCastShorthandNegativeZeroBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (!((float)-2.0) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
