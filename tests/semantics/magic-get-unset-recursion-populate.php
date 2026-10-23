<?php
function warn120($severity, $message, $file, $line) {
    global $child;
    echo $severity === E_WARNING && $message === 'Undefined property: RecursiveGet120::$ghost' ? 'W|' : 'bad|';
    $child->ghost = 9;
    echo 'w|';
    return true;
}
class RecursiveGet120 {
    public $ghost = 0;
    public int $tag = 1;
    public function __get($name) {
        global $make;
        echo 'G|';
        if ($make) {
            $make = false;
            $value = $this->ghost;
        } else { $value = 7; }
        echo 'g|';
        return $value;
    }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn120');
$child = new RecursiveGet120();
unset($child->ghost);
$make = true;
echo 'P:';
$first = $child->ghost;
echo 'A|', $first === null ? 'null|' : 'bad|', $child->ghost, '|';
unset($child->ghost);
$make = true;
$second = $child->ghost;
echo 'B|', $second === null ? 'null|' : 'bad|', $child->ghost, '|';
unset($child, $first, $second);
restore_error_handler();
echo 'E|';
