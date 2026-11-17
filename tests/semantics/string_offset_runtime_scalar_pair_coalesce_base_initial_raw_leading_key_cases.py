"""Quiet emitted coalesce operands preserve a selected full-ternary header."""

WATCHED = []

CASES = [
    dict(id="runtime-scalar-pair-coalesce-base-initial-raw-leading-current-key",
         source='''<?php
function runtimeScalarPairCoalesceBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeScalarPairCoalesceBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((int)1 ? null : 1) ?? ((int)1 ? "abc" : "XYZ"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
         left_value="PNULL", value='PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))'),
    dict(id="runtime-scalar-pair-coalesce-base-initial-raw-leading-reference-key",
         source='''<?php
function runtimeScalarPairCoalesceBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeScalarPairCoalesceBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((int)null ? "XYZ" : "abc") ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
         left_value='PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
         value='PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))'),
]
