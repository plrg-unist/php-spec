"""Folded quiet scalar-CONCAT suffix trees retain an allocated base and saved raw CV offset."""

WATCHED = []

CASES = [
    dict(id="runtime-allocated-folded-scalar-concat-suffix-base-initial-raw-leading-current-key",
         source=r'''<?php
function runtimeAllocatedFoldedScalarConcatSuffixBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeAllocatedFoldedScalarConcatSuffixBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((string)10 . ("b" . 0 . (+2) . (-3) . true . false . null) . ("c" . (+\true) . (-\true) . (+\false) . (-\false) . (+\null) . (-\null)))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:1;K:Illegal string offset "0x";Z;'),
    dict(id="runtime-allocated-folded-scalar-concat-suffix-base-initial-raw-leading-reference-key",
         source=r'''<?php
function runtimeAllocatedFoldedScalarConcatSuffixBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeAllocatedFoldedScalarConcatSuffixBaseInitialRawReferenceLeading");
trigger_error("3x", E_USER_WARNING);
$got = (((string)10 . ("b" . (2 . ((+3) . ((-4) . (\TrUe . (FaLsE . NuLl)))))) . (false . \null)) ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:3x;2:Illegal string offset "3x";R:2;K:4;A:Illegal string offset "3x";Z;'),
]
