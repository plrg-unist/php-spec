"""False emitted short-circuit results select emitted STRING-cast fallbacks."""

CASES = [dict(
    id='runtime-short-circuit-string-cast-shorthand-current-key',
    source=r'''<?php
function runtimeShortCircuitStringCastShorthandBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeShortCircuitStringCastShorthandBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null && (1 / 0)) ?: ((string)(string)"b"))[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
dict(
    id='runtime-short-circuit-string-cast-shorthand-reference-key',
    source=r'''<?php
function runtimeShortCircuitStringCastShorthandBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeShortCircuitStringCastShorthandBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((int)null || (bool)(int)null) ?: ((string)(string)"0"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:0;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]

CASES += [dict(case, id=case['id'].replace('short-circuit', 'keyword-short-circuit'),
               source=case['source'].replace(operator, keyword, 1))
          for case, operator, keyword in zip(CASES[:2], ('&&', '||'), ('and', 'or'))]
