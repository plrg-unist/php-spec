<?php
function warn121($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class DeniedParent121 {
    public function __get($name) { echo 'G|'; return $this->ghost; } // READ121
}
class DeniedChild121 extends DeniedParent121 {
    private int $ghost = 0;
    public function clear() { unset($this->ghost); }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn121');
$expectedLine = 4;
$child = new DeniedChild121();
$child->clear();
$result = 42;
echo 'P:';
try { $result = $child->ghost; echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Cannot access private property DeniedChild121::$ghost' ? 'private|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
