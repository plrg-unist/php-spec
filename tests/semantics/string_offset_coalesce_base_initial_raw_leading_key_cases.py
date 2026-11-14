"""A literal coalesce selects its interned base before a raw leading-key Warning."""

CASES = [dict(
    id='coalesce-base-initial-raw-leading-current-key',
    source='''<?php
function coalesceBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("coalesceBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ("0" ?? "abc")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='coalesce-base-initial-raw-leading-reference-key',
    source='''<?php
function coalesceBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("coalesceBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (null ?? "abc")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18)]
