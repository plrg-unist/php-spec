<?php
function warn123($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class RejectParent123 {
    private int $ghost = 0;
    public function clearParent() { $receiver = $this; unset($receiver->ghost); }
    public function readParent() {
        $receiver = $this;
        return $receiver->ghost; // READ123
    }
    public function __destruct() { echo 'D|'; }
}
class RejectChild123 extends RejectParent123 {
    private string $ghost = 'hidden';
    public function __get($name) { echo 'G|'; return 'bad'; }
}
set_error_handler('warn123');
$expectedLine = 8;
$child = new RejectChild123();
$child->clearParent();
$result = 42;
echo 'B:';
try { $result = $child->readParent(); echo 'bad|'; }
catch (TypeError $caught) {
    echo $caught->getMessage() === 'Value of type string returned from RejectParent123::__get() must be compatible with unset property RejectParent123::$ghost of type int' ? 'typed|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
