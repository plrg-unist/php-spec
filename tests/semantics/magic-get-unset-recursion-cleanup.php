<?php
function warn120($severity, $message, $file, $line) {
    echo $severity === E_WARNING && $message === 'Undefined property: RecursiveGet120::$ghost' ? 'W|' : 'bad|';
    echo 'w|';
    return true;
}
class Probe120 {
    public function __destruct() {
        global $child;
        echo 'V|';
        $receiver = $child;
        $fallback = $receiver->ghost;
        echo $fallback === null ? 'n|' : 'bad|';
        unset($receiver);
        echo 'v|';
    }
}
class RecursiveGet120 {
    public $ghost = 0;
    public int $tag = 1;
    public function __get($name) {
        global $make;
        echo 'G|';
        if ($make) { $make = false; $probe = new Probe120(); }
        echo 'g|';
        return 7;
    }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn120');
$child = new RecursiveGet120();
unset($child->ghost);
$make = true;
echo 'L:';
$result = $child->ghost;
echo 'A|', $result, '|';
$result = $child->ghost;
echo 'B|', $result, '|';
unset($child, $result);
restore_error_handler();
echo 'E|';
