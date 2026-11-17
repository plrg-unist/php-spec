"""Certified compiled primitive conditions select emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-primitive-string-cast-shorthand-false-current-key',
    source=r'''<?php
function runtimePrimitiveStringCastShorthandFalseBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimePrimitiveStringCastShorthandFalseBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (false ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-primitive-string-cast-shorthand-null-reference-key',
    source=r'''<?php
function runtimePrimitiveStringCastShorthandNullBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimePrimitiveStringCastShorthandNullBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (null ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-primitive-string-cast-shorthand-zero-current-key',
    source=r'''<?php
function runtimePrimitiveStringCastShorthandZeroBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimePrimitiveStringCastShorthandZeroBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (0 ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-primitive-string-cast-shorthand-negative-zero-reference-key',
    source=r'''<?php
function runtimePrimitiveStringCastShorthandNegativeZeroBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimePrimitiveStringCastShorthandNegativeZeroBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (-0.0 ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
