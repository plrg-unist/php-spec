"""Direct allocated string bases retain their raw leading CV offset."""

WATCHED = []

CASES = [
    dict(id="runtime-direct-allocated-string-base-initial-raw-leading-current-key",
         source='''<?php
function runtimeDirectAllocatedStringBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeDirectAllocatedStringBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((string)10)[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:1;K:Illegal string offset "0x";Z;'),
    dict(id="runtime-direct-allocated-string-base-initial-raw-leading-reference-key",
         source='''<?php
function runtimeDirectAllocatedStringBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeDirectAllocatedStringBaseInitialRawReferenceLeading");
trigger_error("2x", E_USER_WARNING);
$got = ((string)10 . "bc")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:2x;2:Illegal string offset "2x";R:b;K:3;A:Illegal string offset "2x";Z;'),
]
