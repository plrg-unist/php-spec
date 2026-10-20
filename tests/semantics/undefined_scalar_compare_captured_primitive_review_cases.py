"""Independent captured scalar snapshots and supplied-throw identity."""

CASES = {
    'peer-captured-equal-returned-string': b'''<?php
$source = "0";
$copy = $source;
$alias =& $source;
$calls = 0;
function capturedEqual113() {
    echo "P;";
    return $GLOBALS["source"];
}
function observeEqual113($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS["alias"] = "";
    unset($GLOBALS["source"]);
    $GLOBALS["missing"] = "0";
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    return true;
}
set_error_handler("observeEqual113");
$result =
    capturedEqual113()
    == $missing;
echo "R:", $result === false, ":", $calls === 1, ":", !isset($source), ":", $alias === "", ":", $copy === "0", ":", $missing === "0", ";END;";
''',
    'peer-captured-greater-equal-right-default': b'''<?php
$value = true;
$copy = $value;
$old =& $value;
$calls = 0;
function observeGreaterEqual113($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS["value"] = false;
    $GLOBALS["saved"] = false;
    $GLOBALS["missing"] = true;
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    return false;
}
set_error_handler("observeGreaterEqual113");
$result =
    $missing
    >= ($saved = $value);
echo "R:", $result === false, ":", $calls === 1, ":", $value === false, ":", $old === false, ":", $copy === true, ":", $saved === false, ":", $missing === true, ";END;";
''',
    'peer-captured-primitive-predicates-no-init': b'''<?php
$zero = 0;
$text = "0";
$number = 0.0;
$flag = false;
$calls = 0;
function observePredicates113($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS["zero"] = 7;
    $GLOBALS["text"] = "";
    $GLOBALS["number"] = 7.0;
    $GLOBALS["flag"] = true;
    $GLOBALS["savedA"] = 7;
    $GLOBALS["savedB"] = "";
    $GLOBALS["savedC"] = 7.0;
    $GLOBALS["savedD"] = true;
    echo "H:", $errno === 2, ":", $line, ":", $calls, ";";
    return true;
}
set_error_handler("observePredicates113");
$a = $aMissing != ($savedA = $zero);
$text = "0";
$b = $bMissing < ($savedB = $text);
$number = 0.0;
$c = ($savedC = $number) <= $cMissing;
$flag = false;
$d = ($savedD = $flag) > $dMissing;
echo "R:", $a === false, ":", $b === true, ":", $c === true, ":", $d === false, ":", $calls === 4, ";";
echo "M:", !isset($aMissing), ":", !isset($bMissing), ":", !isset($cMissing), ":", !isset($dMissing), ";";
echo "V:", $zero === 7, ":", $text === "", ":", $number === 7.0, ":", $flag === true, ":", $savedA === 7, ":", $savedB === "", ":", $savedC === 7.0, ":", $savedD === true, ";END;";
''',
    'peer-captured-less-supplied-throw': b'''<?php
$source = "0";
$copy = $source;
$alias =& $source;
$chosen = new Exception("chosen113");
$calls = 0;
$result = 41;
function capturedLess113() {
    echo "P;";
    return $GLOBALS["source"];
}
function observeLess113($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS["alias"] = "";
    unset($GLOBALS["source"]);
    $GLOBALS["missing"] = "0";
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    throw $GLOBALS["chosen"];
}
set_error_handler("observeLess113");
try {
    $result =
        capturedLess113()
        < $missing;
    echo "BAD;";
} catch (Exception $caught) {
    echo "C:", $caught === $chosen, ":", $result === 41, ":", $calls === 1, ":", !isset($source), ":", $alias === "", ":", $copy === "0", ":", $missing === "0", ";";
} finally {
    echo "F;";
}
echo "END;";
''',
}
