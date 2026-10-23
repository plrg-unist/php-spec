<?php
function warn120($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class Parent120 {
    public function __get($name) { echo 'G|'; return $this->ghost; }
}
class Child120 extends Parent120 {
    private $ghost = 0;
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn120');
$child = new Child120();
$result = 42;
echo 'N:';
try { $result = $child->ghost; echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Cannot access private property Child120::$ghost' ? 'denied|' : 'bad-message|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
