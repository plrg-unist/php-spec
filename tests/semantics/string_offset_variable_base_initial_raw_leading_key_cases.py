"""Initial raw leading keys retain a selected ordinary INTERNED base CV."""

CASES = [dict(
    id='variable-base-initial-raw-leading-current-key',
    source='''<?php
function cvBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "base";
        $GLOBALS[$name] = "XYZ";
    }
    return true;
}
$base = "abc";
$key = 0;
$got = 99;
set_error_handler("cvBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;B:XYZ;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=17),
    dict(
    id='variable-base-initial-raw-leading-reference-key',
    source='''<?php
function cvBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "base";
        $GLOBALS[$name] = 99;
        $name = "key";
        $replacementKey = 2;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$base = "abc";
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("cvBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;B:99;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=21)]
