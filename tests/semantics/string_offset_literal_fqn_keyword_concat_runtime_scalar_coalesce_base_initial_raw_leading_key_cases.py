"""Fully qualified reserved tags and direct signs in folded CONCAT coalesce bases."""

WATCHED = []

CASES = [
    dict(id="literal-fqn-keyword-concat-runtime-scalar-coalesce-base-initial-raw-leading-current-key",
         source=r'''<?php
function literalFqnKeywordConcatRuntimeScalarCoalesceBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("literalFqnKeywordConcatRuntimeScalarCoalesceBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((+\false . "") ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:Illegal string offset "0x";Z;',
         left_value='PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))',
         value='PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))'),
    dict(id="literal-fqn-keyword-concat-runtime-scalar-coalesce-base-initial-raw-leading-reference-key",
         source=r'''<?php
function literalFqnKeywordConcatRuntimeScalarCoalesceBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 8;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("literalFqnKeywordConcatRuntimeScalarCoalesceBaseInitialRawReferenceLeading");
trigger_error("7x", E_USER_WARNING);
$got = (((\false . \null) . ((\true . (+\true . -\true)) . ((-\false . +\null) . (-\null . "bc")))) ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:7x;2:Illegal string offset "7x";R:b;K:8;A:Illegal string offset "7x";Z;',
         left_value='PSTRING_CARRIER INTERNED_STRING ($ptascii("11-1000bc"))',
         value='PSTRING_CARRIER INTERNED_STRING ($ptascii("11-1000bc"))'),
]
