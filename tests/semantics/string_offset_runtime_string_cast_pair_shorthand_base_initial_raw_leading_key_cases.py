"""Both shorthand condition and fallback are emitted string casts before raw-key Warnings."""

CASES = [dict(
    id='runtime-string-cast-pair-shorthand-base-initial-raw-leading-current-key',
    source=r'''<?php
function runtimeStringCastPairShorthandBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeStringCastPairShorthandBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((string)"b") ?: ((string)MissingFallback))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-string-cast-pair-shorthand-base-initial-raw-leading-reference-key',
    source=r'''<?php
function runtimeStringCastPairShorthandBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeStringCastPairShorthandBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((string)(string)"") ?: ((string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
