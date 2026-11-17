"""Folded signed-integer/STRING CONCAT bases skip an emitted ternary RHS."""

WATCHED = []

CASES = [
    dict(id="literal-signed-integer-concat-runtime-scalar-coalesce-base-initial-raw-leading-current-key",
         source='''<?php
function literalSignedIntegerConcatRuntimeScalarCoalesceBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("literalSignedIntegerConcatRuntimeScalarCoalesceBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (("" . -0) ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:Illegal string offset "0x";Z;',
         left_value='PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))',
         value='PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))'),
    dict(id="literal-signed-integer-concat-runtime-scalar-coalesce-base-initial-raw-leading-reference-key",
         source='''<?php
function literalSignedIntegerConcatRuntimeScalarCoalesceBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("literalSignedIntegerConcatRuntimeScalarCoalesceBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = ((-9223372036854775807 . ("b" . "c")) ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:1x;2:Illegal string offset "1x";R:9;K:2;A:Illegal string offset "1x";Z;',
         left_value='PSTRING_CARRIER INTERNED_STRING ($ptascii("-9223372036854775807bc"))',
         value='PSTRING_CARRIER INTERNED_STRING ($ptascii("-9223372036854775807bc"))'),
]
