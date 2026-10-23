<?php
function warn119($severity, $message, $file, $line) {
    global $child, $error;
    echo 'W|';
    $child = null;
    echo 'w|';
    throw $error;
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
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn119');
$error = new Exception('same119');
$child = new RecursiveGet119();
$make = true;
$result = 42;
echo 'X:';
try { $result = $child->ghost; echo 'bad|'; }
catch (Throwable $caught) {
    echo 'C|', $caught === $error ? 'same|' : 'wrong|', $result, '|';
}
unset($child, $caught, $error);
restore_error_handler();
echo 'E|';
