"""Quiet emitted false comparisons select emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-comparison-string-cast-shorthand-equal-current-key',
    source=r'''<?php
function runtimeComparisonStringCastShorthandEqualBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeComparisonStringCastShorthandEqualBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null == 1) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
dict(
    id='runtime-comparison-string-cast-shorthand-not-equal-reference-key',
    source=r'''<?php
function runtimeComparisonStringCastShorthandNotEqualBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeComparisonStringCastShorthandNotEqualBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null != 0) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
dict(
    id='runtime-comparison-string-cast-shorthand-identical-current-key',
    source=r'''<?php
function runtimeComparisonStringCastShorthandIdenticalBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeComparisonStringCastShorthandIdenticalBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null === 1) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
dict(
    id='runtime-comparison-string-cast-shorthand-not-identical-reference-key',
    source=r'''<?php
function runtimeComparisonStringCastShorthandNotIdenticalBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeComparisonStringCastShorthandNotIdenticalBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null !== 0) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
dict(
    id='runtime-comparison-string-cast-shorthand-less-current-key',
    source=r'''<?php
function runtimeComparisonStringCastShorthandLessBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeComparisonStringCastShorthandLessBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((float)1 < 0.0) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
dict(
    id='runtime-comparison-string-cast-shorthand-less-equal-reference-key',
    source=r'''<?php
function runtimeComparisonStringCastShorthandLessEqualBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeComparisonStringCastShorthandLessEqualBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((float)1 <= 0.0) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18),
dict(
    id='runtime-comparison-string-cast-shorthand-greater-current-key',
    source=r'''<?php
function runtimeComparisonStringCastShorthandGreaterBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeComparisonStringCastShorthandGreaterBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((float)0 > 1.0) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
dict(
    id='runtime-comparison-string-cast-shorthand-greater-equal-reference-key',
    source=r'''<?php
function runtimeComparisonStringCastShorthandGreaterEqualBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeComparisonStringCastShorthandGreaterEqualBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((float)0 >= 1.0) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
