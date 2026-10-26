<?php
function warn124($severity, $message, $file, $line) {
    global $child;
    echo 'W|';
    echo $severity === 2 ? 'severity|' : 'bad-severity|';
    echo $message === 'Undefined property: RecursiveThis124::$ghost' ? 'message|' : 'bad-message|';
    echo $line === 19 ? 'line|' : 'bad-line|';
    echo $file === __FILE__ ? 'file|' : 'bad-file|';
    $child->ghost = 9;
    echo 'w|';
    return true;
}
class RecursiveThis124 {
    public $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function readThis() { return $this->ghost; }
    public function __get($name) {
        echo 'G|';
        $value = $this->ghost; // READ124
        echo 'g|';
        return $value;
    }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn124');
$child = new RecursiveThis124();
$child->clear();
echo 'R:';
$first = $child->readThis();
echo 'A|', $first === null ? 'null|' : 'bad|', $child->ghost, '|';
$child->clear();
$second = $child->readThis();
echo 'B|', $second === null ? 'null|' : 'bad|', $child->ghost, '|';
unset($child, $first, $second);
restore_error_handler();
echo 'E|';
