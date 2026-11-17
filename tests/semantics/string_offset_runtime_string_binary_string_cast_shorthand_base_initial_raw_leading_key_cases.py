"""One-byte emitted STRING AND/OR/XOR retains the selected shorthand header."""

CASES = [dict(
    id='runtime-string-binary-string-cast-shorthand-and-truthy-current-key',
    source=r'''<?php
function runtimeStringBinaryStringCastShorthandAndTruthyBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeStringBinaryStringCastShorthandAndTruthyBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((string)"c") & ((string)"b")) ?: ((string)(string)"X"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-string-binary-string-cast-shorthand-and-falsey-reference-key',
    source=r'''<?php
function runtimeStringBinaryStringCastShorthandAndFalseyBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeStringBinaryStringCastShorthandAndFalseyBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((string)"1") & ((string)"0")) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-string-binary-string-cast-shorthand-or-truthy-current-key',
    source=r'''<?php
function runtimeStringBinaryStringCastShorthandOrTruthyBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeStringBinaryStringCastShorthandOrTruthyBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((string)"b") | ((string)"b")) ?: ((string)(string)"X"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-string-binary-string-cast-shorthand-or-falsey-reference-key',
    source=r'''<?php
function runtimeStringBinaryStringCastShorthandOrFalseyBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeStringBinaryStringCastShorthandOrFalseyBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((string)"0") | ((string)"0")) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='runtime-string-binary-string-cast-shorthand-xor-truthy-current-key',
    source=r'''<?php
function runtimeStringBinaryStringCastShorthandXorTruthyBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeStringBinaryStringCastShorthandXorTruthyBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((string)"3") ^ ((string)"Q")) ?: ((string)(string)"X"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-string-binary-string-cast-shorthand-xor-falsey-reference-key',
    source=r'''<?php
function runtimeStringBinaryStringCastShorthandXorFalseyBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeStringBinaryStringCastShorthandXorFalseyBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((((string)"3") ^ ((string)"\x03")) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
