"""Quiet infinite PFLOAT producers allocate exact string-cast bases."""

WATCHED = []

CASES = [
    dict(id="runtime-allocated-infinite-float-producer-cast-base-initial-raw-leading-current-key",
         source='''<?php
function runtimeAllocatedInfiniteFloatProducerCastBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedInfiniteFloatProducerCastBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((string)1e999)[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:I;K:Illegal string offset "0x";Z;'),
    dict(id="runtime-allocated-infinite-float-producer-cast-base-initial-raw-leading-reference-key",
         source='''<?php
function runtimeAllocatedInfiniteFloatProducerCastBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeAllocatedInfiniteFloatProducerCastBaseInitialRawReferenceLeading");
trigger_error("3x", E_USER_WARNING);
$got = (((string)(-1e999) . "bc" . "de") ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:3x;2:Illegal string offset "3x";R:F;K:4;A:Illegal string offset "3x";Z;'),
    dict(id="runtime-allocated-infinite-float-producer-cast-base-initial-raw-leading-emitted-arithmetic-key",
         source='''<?php
function runtimeAllocatedInfiniteFloatProducerArithmeticCastBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedInfiniteFloatProducerArithmeticCastBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((string)(((int)1 ? 1.0e308 : 2.0) * 10.0) . "bc" . "de")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:I;K:Illegal string offset "0x";Z;'),
]
