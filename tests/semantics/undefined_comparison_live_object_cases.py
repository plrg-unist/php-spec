"""Live ordinary-object CVs, current bindings and owner release."""

CASES = {
    'live-object-equal-right-null': b'''<?php
class LiveEqualOld115 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ';'; }
}
$right = new LiveEqualOld115();
$calls = 0;
$result = 41;
function warnLiveEqual115($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['right'] = null;
    $GLOBALS['missing'] = 9;
    echo 'A;';
    return true;
}
set_error_handler('warnLiveEqual115');
$result = $missing == $right;
echo 'R:', $result === true, ':', $right === null, ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'live-object-spaceship-left-created': b'''<?php
class LiveSpaceNew115 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 1, ':', $GLOBALS['calls'] === 1, ';'; }
}
$left = 0;
$calls = 0;
$result = 41;
function warnLiveSpace115($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    $GLOBALS['left'] = new LiveSpaceNew115();
    $GLOBALS['missing'] = $GLOBALS['left'];
    return true;
}
set_error_handler('warnLiveSpace115');
$result = $left <=> $missing;
echo 'R:', $result === 1, ':', $calls === 1, ':', $left === $missing, ';';
unset($left);
echo 'A:', isset($missing), ';';
unset($missing);
echo 'END;';
''',
    'live-object-both-shared-no-init': b'''<?php
class LiveShared115 {
    public function __destruct() { echo 'D;'; }
}
$calls = 0;
function warnLiveShared115($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';';
    if ($message === 'Undefined variable $first') {
        $GLOBALS['later'] = new LiveShared115();
    } else {
        $GLOBALS['x'] = new LiveShared115();
    }
    return true;
}
set_error_handler('warnLiveShared115');
$a = $first == $later;
echo 'A:', $a === false, ':', !isset($first), ';';
unset($later);
$b = $x != $x;
echo 'B:', $b === true, ';';
unset($x);
$c = $x > $x;
echo 'C:', $c === true, ':', $calls === 3, ';';
unset($x);
echo 'END;';
''',
    'live-object-less-equal-default': b'''<?php
class LiveDefaultOld115 {
    public function __destruct() { echo 'D:', $GLOBALS['result'] === 41, ';'; }
}
$left = new LiveDefaultOld115();
$calls = 0;
$result = 41;
function warnLiveDefault115($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['left'] = false;
    $GLOBALS['missing'] = 9;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return false;
}
set_error_handler('warnLiveDefault115');
$result = $left <= $missing;
echo 'R:', $result === true, ':', $left === false, ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'live-object-not-equal-stdclass': b'''<?php
$right = 0;
$calls = 0;
function warnLiveStd115($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    $GLOBALS['right'] = new stdClass();
    $GLOBALS['right']->tag = 7;
    $GLOBALS['missing'] = 9;
    echo 'H:', $level === 2, ':', $message === 'Undefined variable $missing', ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnLiveStd115');
$result = $missing != $right;
echo 'R:', $result === true, ':', $right->tag === 7, ':', $missing === 9, ':', $calls === 1, ';END;';
''',
    'live-object-less-greater-equal': b'''<?php
class LiveOrdering115 {
    public function __destruct() { echo 'D;'; }
}
$right = new LiveOrdering115();
$calls = 0;
function warnLiveOrdering115($level, $message, $file, $line) {
    global $calls;
    $calls = $calls + 1;
    echo 'H:', $level === 2, ':', $line, ':', $calls, ';';
    return true;
}
set_error_handler('warnLiveOrdering115');
$a = $lessMissing < $right;
$b = $geMissing >= $right;
echo 'R:', $a === true, ':', $b === false, ':', $calls === 2, ':', !isset($lessMissing), ':', !isset($geMissing), ';';
unset($right);
echo 'END;';
''',
    'live-object-internal-entry-boundary': b'''<?php
$right = function () {};
function warnLiveInternal115($level, $message, $file, $line) { echo 'H|'; return true; }
set_error_handler('warnLiveInternal115');
echo 'B|';
$result = $missing == $right;
echo $result ? '1' : '0';
''',
    'live-object-internal-resume-boundary': b'''<?php
$right = 0;
function warnLiveClosure115($level, $message, $file, $line) {
    echo 'H|';
    $GLOBALS['right'] = function () {};
    return true;
}
set_error_handler('warnLiveClosure115');
echo 'B|';
$result = $missing <=> $right;
echo $result;
''',
}
