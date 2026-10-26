<?php
function warn124($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class LifetimeThis124 {
    public $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function readThis() {
        $value = $this->ghost; // READ124
        echo 'm|';
        return $value;
    }
    public function __get($name) {
        global $child;
        echo 'G|';
        $child = null;
        echo 'g|';
        return 7;
    }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn124');
$child = new LifetimeThis124();
$child->clear();
echo 'L:';
$result = $child->readThis();
echo $result, '|', $child === null ? 'null|' : 'bad|';
unset($child, $result);
restore_error_handler();
echo 'E|';
