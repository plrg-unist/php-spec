<?php
function warn119($severity, $message, $file, $line) {
    global $child;
    echo 'W|';
    $child = null;
    echo 'w|';
    return true;
}
class RecursiveGet119 {
    public int $tag = 1;
    public function __get($name) {
        global $make;
        echo 'G|';
        if ($make) {
            $make = false;
            $fallback = $this->ghost;
            echo $fallback === null ? 'n|' : 'bad|';
        }
        echo 'g|';
        return 7;
    }
    public function __destruct() { global $live; $live = 99; echo 'D|'; }
}
set_error_handler('warn119');
$child = new RecursiveGet119();
$make = true;
$live = 7;
echo 'S:';
$result = $child->ghost;
echo 'A|', $result, '/', $live, '|';
unset($child, $result);
restore_error_handler();
echo 'E|';
