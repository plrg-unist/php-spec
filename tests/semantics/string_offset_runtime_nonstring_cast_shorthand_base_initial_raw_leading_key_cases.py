"""Quiet emitted BOOL/INT/FLOAT casts select emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-nonstring-cast-shorthand-bool-current-key',
    source=r'''<?php
function runtimeNonstringCastShorthandFalseBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeNonstringCastShorthandFalseBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((bool)false ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-nonstring-cast-shorthand-int-null-reference-key',
    source=r'''<?php
function runtimeNonstringCastShorthandNullBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeNonstringCastShorthandNullBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((int)null ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-nonstring-cast-shorthand-float-zero-current-key',
    source=r'''<?php
function runtimeNonstringCastShorthandZeroBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeNonstringCastShorthandZeroBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((float)0 ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-nonstring-cast-shorthand-float-negative-zero-reference-key',
    source=r'''<?php
function runtimeNonstringCastShorthandNegativeZeroBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeNonstringCastShorthandNegativeZeroBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((float)-0.0 ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
