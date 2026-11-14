"""A unary-minus negative-zero shorthand keeps its fallback interned base before a Warning."""

CASES = [dict(
    id='negative-zero-shorthand-base-initial-raw-leading-current-key',
    source='''<?php
function negativeZeroShorthandBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("negativeZeroShorthandBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = (-0.0 ?: "abc")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='negative-zero-shorthand-base-initial-raw-leading-reference-key',
    source='''<?php
function negativeZeroShorthandBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("negativeZeroShorthandBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (-(0e0) ?: "abc")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18)]
