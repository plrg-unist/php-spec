"""Literal NULL selects a certified emitted scalar ternary string header."""

WATCHED = []

CASES = [
    dict(id="null-runtime-scalar-coalesce-base-initial-raw-leading-current-key",
         source='''<?php
function nullRuntimeScalarCoalesceBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("nullRuntimeScalarCoalesceBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = (null ?? ((int)1 ? "abc" : "XYZ"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
         expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
         guard_value="PINT 1", selected_field=1),
    dict(id="null-runtime-scalar-coalesce-base-initial-raw-leading-reference-key",
         source='''<?php
function nullRuntimeScalarCoalesceBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("nullRuntimeScalarCoalesceBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (null ?? ((int)null ? "XYZ" : "abc"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
         expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
         guard_value="PINT 0", selected_field=2),
]
