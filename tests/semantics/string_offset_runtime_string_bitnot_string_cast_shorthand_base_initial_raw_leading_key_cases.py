"""One-byte emitted STRING bitwise NOT retains the selected shorthand header."""

CASES = [dict(
    id='runtime-string-bitnot-string-cast-shorthand-truthy-current-key',
    source=r'''<?php
function runtimeStringBitNotStringCastShorthandTruthyBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeStringBitNotStringCastShorthandTruthyBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((~((string)"\x9d")) ?: ((string)(string)"X"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-string-bitnot-string-cast-shorthand-falsey-reference-key',
    source=r'''<?php
function runtimeStringBitNotStringCastShorthandFalseyBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeStringBitNotStringCastShorthandFalseyBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((~((string)"\xcf")) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
