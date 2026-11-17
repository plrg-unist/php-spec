"""Direct reserved-tag signs in folded CONCAT retain an immutable coalesce base."""

WATCHED = []

CASES = [
    dict(id="literal-unary-keyword-concat-runtime-scalar-coalesce-base-initial-raw-leading-current-key",
         source='''<?php
function literalUnaryKeywordConcatRuntimeScalarCoalesceBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("literalUnaryKeywordConcatRuntimeScalarCoalesceBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = ((+false . "") ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:Illegal string offset "0x";Z;',
         left_value='PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))',
         value='PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))'),
    dict(id="literal-unary-keyword-concat-runtime-scalar-coalesce-base-initial-raw-leading-reference-key",
         source='''<?php
function literalUnaryKeywordConcatRuntimeScalarCoalesceBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 7;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("literalUnaryKeywordConcatRuntimeScalarCoalesceBaseInitialRawReferenceLeading");
trigger_error("6x", E_USER_WARNING);
$got = (((+true . -true) . ((-false . +null) . (-null . "bc"))) ?? ((int)1 ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:6x;2:Illegal string offset "6x";R:b;K:7;A:Illegal string offset "6x";Z;',
         left_value='PSTRING_CARRIER INTERNED_STRING ($ptascii("1-1000bc"))',
         value='PSTRING_CARRIER INTERNED_STRING ($ptascii("1-1000bc"))'),
]
