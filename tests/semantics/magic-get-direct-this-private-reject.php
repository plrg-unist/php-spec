<?php
function warn124($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class RejectParent124 {
    private int $ghost = 0;
    public function clearParent() { $receiver = $this; unset($receiver->ghost); }
    public function readParent() {
        return $this->ghost; // READ124
    }
    public function __destruct() { echo 'D|'; }
}
class RejectChild124 extends RejectParent124 {
    private string $ghost = 'hidden';
    public function __get($name) { echo 'G|'; return 'bad'; }
}
set_error_handler('warn124');
$expectedLine = 7;
$child = new RejectChild124();
$child->clearParent();
$result = 42;
echo 'B:';
try { $result = $child->readParent(); echo 'bad|'; }
catch (TypeError $caught) {
    echo $caught->getMessage() === 'Value of type string returned from RejectParent124::__get() must be compatible with unset property RejectParent124::$ghost of type int' ? 'typed|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
