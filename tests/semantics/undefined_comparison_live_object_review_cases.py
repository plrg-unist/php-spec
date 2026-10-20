"""Current direct-CV objects, handler destruction and retained global effects."""

CASES = {
    'peer-live-object-equal-replace-scalar': b'''<?php
class OldEqualObject115 {
    public function __destruct() { echo "D:", $GLOBALS["result"] === 41, ";"; }
}
$source = new OldEqualObject115();
$calls = 0;
$result = 41;
function warnEqualObject115($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo "B;";
    $GLOBALS["source"] = 0;
    $GLOBALS["missing"] = 9;
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    return true;
}
set_error_handler("warnEqualObject115");
$result =
    $missing
    == $source;
echo "R:", $result === true, ":", $calls === 1, ":", $source === 0, ":", $missing === 9, ";END;";
''',
    'peer-live-object-greater-target-default': b'''<?php
class OldTargetObject115 {
    public $tag = 4;
    public function __destruct() { echo "O:", $GLOBALS["result"] === true, ";"; }
}
class NewTargetObject115 {
    public $tag = 7;
    public function __destruct() { echo "N:", $GLOBALS["result"] === true, ";"; }
}
$target = new OldTargetObject115();
$copy = $target;
$source = 0;
$calls = 0;
$result = 41;
function warnGreaterObject115($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS["source"] =& $GLOBALS["target"];
    $GLOBALS["target"] = new NewTargetObject115();
    $GLOBALS["missing"] = 9;
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    return false;
}
set_error_handler("warnGreaterObject115");
$result =
    $source
    > $missing;
echo "R:", $result === true, ":", $calls === 1, ":", $source === $target, ":", $source->tag === 7, ":", $copy->tag === 4, ":", $missing === 9, ";";
unset($source);
unset($target);
unset($copy);
echo "END;";
''',
    'peer-live-object-checked-and-unread-removal': b'''<?php
class CheckedObject115 {
    public function __destruct() { echo "K:", $GLOBALS["space"] === 41, ";"; }
}
class UnreadObject115 {
    public function __destruct() { echo "U:", $GLOBALS["less"] === 41, ";"; }
}
class LateObject115 {
    public $tag = 7;
    public function __destruct() { echo "V:", $GLOBALS["less"] === false, ";"; }
}
$source = new CheckedObject115();
$unread = new UnreadObject115();
$space = 41;
$less = 41;
$calls = 0;
function warnRemovalObject115($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    if ($calls === 1) {
        unset($GLOBALS["source"]);
        $GLOBALS["missing"] = 9;
        $wanted = 'Undefined variable $missing';
    } elseif ($calls === 2) {
        unset($GLOBALS["unread"]);
        $wanted = 'Undefined variable $first';
    } else {
        $GLOBALS["unread"] = new LateObject115();
        $wanted = 'Undefined variable $unread';
    }
    echo "H:", $errno === 2, ":", $message === $wanted, ":", $line, ":", $calls, ";";
    return true;
}
set_error_handler("warnRemovalObject115");
$space = $source <=> $missing;
$less = $first < $unread;
echo "R:", $space === 0, ":", $less === false, ":", $calls === 3, ":", $missing === 9, ":", !isset($first), ":", $unread->tag === 7, ";";
unset($unread);
echo "END;";
''',
    'peer-live-object-spaceship-supplied-throw': b'''<?php
class OldThrowObject115 {
    public function __destruct() { echo "O:", $GLOBALS["result"] === 41, ";"; }
}
class NewThrowObject115 {
    public $tag = 7;
    public function __destruct() { echo "N:", $GLOBALS["result"] === 41, ";"; }
}
$source = new OldThrowObject115();
$chosen = new Exception("chosen115");
$calls = 0;
$result = 41;
function warnThrowObject115($errno, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo "B;";
    $GLOBALS["source"] = new NewThrowObject115();
    $GLOBALS["missing"] = 9;
    echo "H:", $errno === 2, ":", $message === 'Undefined variable $missing', ":", $line, ":", $calls, ";";
    throw $GLOBALS["chosen"];
}
set_error_handler("warnThrowObject115");
try {
    $result =
        $missing
        <=> $source;
    echo "BAD;";
} catch (Exception $caught) {
    echo "C:", $caught === $chosen, ":", $result === 41, ":", $calls === 1, ":", $source->tag === 7, ":", $missing === 9, ";";
} finally {
    echo "F;";
}
unset($source);
echo "END;";
''',
}
