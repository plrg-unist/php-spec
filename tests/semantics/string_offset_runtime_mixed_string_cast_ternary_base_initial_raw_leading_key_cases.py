"""Full ternaries mix a raw string arm and an emitted string-cast arm."""

CASES = [dict(
    id='runtime-mixed-string-cast-ternary-cast-true-current-key',
    source=r'''<?php
function runtimeMixedStringCastTernaryCastTrue($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeMixedStringCastTernaryCastTrue");
trigger_error("0x", E_USER_WARNING);
$got = (((bool)1) ? ((string)(string)"b") : "unused")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12), dict(
    id='runtime-mixed-string-cast-ternary-cast-false-reference-key',
    source=r'''<?php
function runtimeMixedStringCastTernaryCastFalse($level, $message, $file, $line) {
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
set_error_handler("runtimeMixedStringCastTernaryCastFalse");
trigger_error("0x", E_USER_WARNING);
$got = (((bool)0) ? "unused" : ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18), dict(
    id='runtime-mixed-string-cast-ternary-raw-true-current-key',
    source=r'''<?php
function runtimeMixedStringCastTernaryRawTrue($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeMixedStringCastTernaryRawTrue");
trigger_error("0x", E_USER_WARNING);
$got = (((bool)1) ? "b" : ((string)MissingFallback))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12), dict(
    id='runtime-mixed-string-cast-ternary-raw-false-reference-key',
    source=r'''<?php
function runtimeMixedStringCastTernaryRawFalse($level, $message, $file, $line) {
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
set_error_handler("runtimeMixedStringCastTernaryRawFalse");
trigger_error("0x", E_USER_WARNING);
$got = (((bool)0) ? ((string)MissingFallback) : "0")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
