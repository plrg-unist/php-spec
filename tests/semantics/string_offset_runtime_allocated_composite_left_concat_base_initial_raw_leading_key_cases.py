"""Literal CONCAT suffixes extend allocated composite LEFT BASE headers."""

WATCHED = []

CASES = [
    dict(id="runtime-allocated-composite-left-concat-base-initial-raw-leading-current-key",
         source='''<?php
function runtimeAllocatedCompositeLeftConcatBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedCompositeLeftConcatBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = ((((int)1 ? (string)0.0 : "XYZ") . "YZ"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:1x;2:Illegal string offset "1x";R:Y;K:Illegal string offset "1x";Z;'),
    dict(id="runtime-allocated-composite-left-concat-base-initial-raw-leading-reference-key",
         source='''<?php
function runtimeAllocatedCompositeLeftConcatBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 10;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("runtimeAllocatedCompositeLeftConcatBaseInitialRawReferenceLeading");
trigger_error("9x", E_USER_WARNING);
$got = ((((((string)(-10.5) . "bc" . "de") ?: ((int)1 ? "XYZ" : "abc")) ?? ((int)1 ? "uvw" : "def")) . "fg"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:9x;2:Illegal string offset "9x";R:f;K:10;A:Illegal string offset "9x";Z;'),
]
