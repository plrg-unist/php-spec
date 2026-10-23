<?php
function warn119($severity, $message, $file, $line) {
    global $child;
    echo 'W|';
    $child->ghost = 9;
    echo 'w|';
    return true;
}
#[AllowDynamicProperties]
class RecursiveGet119 {
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
set_error_handler('warn119');
$child = new RecursiveGet119();
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
