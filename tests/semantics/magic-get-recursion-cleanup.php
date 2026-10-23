<?php
function warn119($severity, $message, $file, $line) {
    echo 'W|w|';
    return true;
}
class Probe119 {
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
class RecursiveGet119 {
    public int $tag = 1;
    public function __get($name) {
        global $make;
        echo 'G|';
        if ($make) { $make = false; $probe = new Probe119(); }
        echo 'g|';
        return 7;
    }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn119');
$child = new RecursiveGet119();
$make = true;
echo 'L:';
$result = $child->ghost;
echo 'A|', $result, '|';
$result = $child->ghost;
echo 'B|', $result, '|';
unset($child, $result);
restore_error_handler();
echo 'E|';
