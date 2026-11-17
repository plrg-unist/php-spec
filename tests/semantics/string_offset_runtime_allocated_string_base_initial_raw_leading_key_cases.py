"""Allocated non-NUL string casts and CONCAT bases across returning Warnings."""

WATCHED = []

CASES = [
    dict(id="runtime-allocated-string-base-initial-raw-leading-current-key",
         source='''<?php
function runtimeAllocatedStringBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedStringBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((string)10 ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:1;K:Illegal string offset "0x";Z;',
         left_value=None,
         value=None),
    dict(id="runtime-allocated-string-base-initial-raw-leading-reference-key",
         source='''<?php
function runtimeAllocatedStringBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 3;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("runtimeAllocatedStringBaseInitialRawReferenceLeading");
trigger_error("2x", E_USER_WARNING);
$got = (((string)10 . "bc") ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:2x;2:Illegal string offset "2x";R:b;K:3;A:Illegal string offset "2x";Z;',
         left_value=None,
         value=None),
]
