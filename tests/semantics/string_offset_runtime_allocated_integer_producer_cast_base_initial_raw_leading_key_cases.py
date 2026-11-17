"""Certified quiet PINT producers allocate exact string-cast bases."""

WATCHED = []

CASES = [
    dict(id="runtime-allocated-integer-producer-cast-base-initial-raw-leading-current-key",
         source='''<?php
function runtimeAllocatedIntegerProducerCastBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedIntegerProducerCastBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((string)(+10) . "bc" . "de")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:1;K:Illegal string offset "0x";Z;'),
    dict(id="runtime-allocated-integer-producer-cast-base-initial-raw-leading-reference-key",
         source='''<?php
function runtimeAllocatedIntegerProducerCastBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 4;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("runtimeAllocatedIntegerProducerCastBaseInitialRawReferenceLeading");
trigger_error("3x", E_USER_WARNING);
$got = (((string)(-10) . "bc" . "de") ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:3x;2:Illegal string offset "3x";R:b;K:4;A:Illegal string offset "3x";Z;'),
    dict(id="runtime-allocated-integer-producer-cast-base-initial-raw-leading-emitted-arithmetic-key",
         source='''<?php
function runtimeAllocatedIntegerProducerArithmeticCastBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedIntegerProducerArithmeticCastBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((string)(((int)1 ? 20 : 30) - 10) . "bc" . "de")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:1;K:Illegal string offset "0x";Z;'),
]
