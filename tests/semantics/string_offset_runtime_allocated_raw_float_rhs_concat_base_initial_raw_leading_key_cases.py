"""Allocated direct raw-FLOAT casts on the right of CONCAT offset bases."""

WATCHED = []

CASES = [
    dict(id="runtime-allocated-raw-float-rhs-concat-base-initial-raw-leading-current-key",
         source='''<?php
function runtimeAllocatedRawFloatRhsConcatBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedRawFloatRhsConcatBaseInitialRawLeading");
trigger_error("2x", E_USER_WARNING);
$got = ((string)42 . (string)0.0)[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:2x;2:Illegal string offset "2x";R:0;K:Illegal string offset "2x";Z;'),
    dict(id="runtime-allocated-raw-float-rhs-concat-base-initial-raw-leading-reference-key",
         source='''<?php
function runtimeAllocatedRawFloatRhsConcatBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 12;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("runtimeAllocatedRawFloatRhsConcatBaseInitialRawReferenceLeading");
trigger_error("11x", E_USER_WARNING);
$got = ((((((string)(-10.5) . "bc" . "de") ?: ((int)1 ? "XYZ" : "abc")) ?? ((int)1 ? "uvw" : "def")) . (string)12.5))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:11x;2:Illegal string offset "11x";R:.;K:12;A:Illegal string offset "11x";Z;'),
]
