"""Initial reference-base CVs keep the interned header across leading Warnings."""

CASES = [dict(
    id='reference-base-initial-raw-leading-current-key',
    source='''<?php
function refBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "base";
        $GLOBALS[$name] = 99;
    }
    return true;
}
$base = "abc";
$baseAlias =& $base;
$key = 0;
$got = 99;
set_error_handler("refBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";A:", $baseAlias, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;B:99;A:99;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18),
    dict(
    id='reference-base-initial-raw-leading-reference-key',
    source='''<?php
function refBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "keyAlias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "base";
        $replacementBase = "XYZ";
        $GLOBALS[$name] =& $replacementBase;
        $name = "key";
        $replacementKey = 2;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$base = "abc";
$baseAlias =& $base;
$key = 0;
$keyAlias =& $key;
$got = 99;
set_error_handler("refBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";A:", $baseAlias, ";K:", $key, ";KA:", $keyAlias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;B:XYZ;A:abc;K:2;KA:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=23)]
