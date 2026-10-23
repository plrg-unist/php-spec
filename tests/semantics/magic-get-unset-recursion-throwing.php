<?php
function warn120($severity, $message, $file, $line) {
    global $child, $error;
    echo $severity === E_WARNING && $message === 'Undefined property: RecursiveGet120::$ghost' ? 'W|' : 'bad|';
    $child = null;
    echo 'w|';
    throw $error;
}
class RecursiveGet120 {
    public $ghost = 0;
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
set_error_handler('warn120');
$error = new Exception('same120');
$child = new RecursiveGet120();
unset($child->ghost);
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
