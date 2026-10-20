"""Captured ordinary objects keep identity and owners across a missing read."""

CASES = {
    'peer-captured-object-equal-returned': b'''<?php
class EqualObject114 {
    public $tag = 4;
    public function __destruct() {
        echo "D:", $this->tag === 7, ":", $GLOBALS["result"] === false, ";";
    }
}
$source = new EqualObject114();
$calls = 0;
$result = 41;
function capturedEqualObject114() {
    echo "P;";
    return $GLOBALS["source"];
}
function warnEqualObject114($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS["source"]->tag = 7;
    $GLOBALS["missing"] = $GLOBALS["source"];
    $GLOBALS["source"] = null;
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    return true;
}
set_error_handler("warnEqualObject114");
$result =
    capturedEqualObject114()
    == $missing;
echo "R:", $result === false, ":", $calls === 1, ":", $source === null, ":", $missing->tag === 7, ";";
unset($missing);
echo "END;";
''',
    'peer-captured-object-greater-equal-default': b'''<?php
class GreaterEqualObject114 {
    public $tag = 4;
    public function __destruct() {
        echo "D:", $this->tag === 7, ":", $GLOBALS["result"] === 41, ";";
    }
}
$source = new GreaterEqualObject114();
$calls = 0;
$result = 41;
function warnGreaterEqualObject114($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS["source"]->tag = 7;
    unset($GLOBALS["source"]);
    unset($GLOBALS["saved"]);
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    return false;
}
set_error_handler("warnGreaterEqualObject114");
$result =
    $missing
    >= ($saved = $source);
echo "R:", $result === false, ":", $calls === 1, ":", !isset($source), ":", !isset($saved), ":", !isset($missing), ";END;";
''',
    'peer-captured-object-less-throw': b'''<?php
class ThrowObject114 {
    public $tag = 4;
    public function __destruct() {
        echo "D:", $this->tag === 7, ":", $GLOBALS["result"] === 41, ";";
    }
}
$source = new ThrowObject114();
$chosen = new Exception("chosen114");
$calls = 0;
$result = 41;
function capturedLessObject114() {
    echo "P;";
    return $GLOBALS["source"];
}
function warnLessObject114($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS["source"]->tag = 7;
    unset($GLOBALS["source"]);
    $GLOBALS["missing"] = 9;
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    throw $GLOBALS["chosen"];
}
set_error_handler("warnLessObject114");
try {
    $result =
        capturedLessObject114()
        < $missing;
    echo "BAD;";
} catch (Exception $caught) {
    echo "C:", $caught === $chosen, ":", $result === 41, ":", $calls === 1, ":", !isset($source), ":", $missing === 9, ";";
} finally {
    echo "F;";
}
echo "END;";
''',
    'peer-captured-object-no-init-matrix': b'''<?php
class MatrixObject114 {
    public function __destruct() { echo "D;"; }
}
$calls = 0;
function warnMatrixObject114($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo "H:", $errno === 2, ":", $line, ":", $calls, ";";
    return true;
}
set_error_handler("warnMatrixObject114");
$a = (new MatrixObject114()) != $aMissing;
$b = (new MatrixObject114()) < $bMissing;
$c = $cMissing <= (new MatrixObject114());
$d = (new MatrixObject114()) > $dMissing;
$e = (new MatrixObject114()) <=> $eMissing;
$f = $fMissing <=> (new MatrixObject114());
echo "R:", $a === true, ":", $b === false, ":", $c === true, ":", $d === true, ":", $e === 1, ":", $f === -1, ":", $calls === 6, ";";
echo "M:", !isset($aMissing), ":", !isset($bMissing), ":", !isset($cMissing), ":", !isset($dMissing), ":", !isset($eMissing), ":", !isset($fMissing), ";END;";
''',
}
