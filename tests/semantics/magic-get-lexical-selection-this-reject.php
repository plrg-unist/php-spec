<?php
function warn125($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class RejectParent125 {
    private int $ghost = 0;
    public function clearParent() { $receiver = $this; unset($receiver->ghost); }
    public function readParent() {
        return $this->ghost; // READ125
    }
    public function __destruct() { echo 'D|'; }
}
class RejectChild125 extends RejectParent125 {
    public string $ghost = 'hidden';
    public function __get($name) { echo 'G|'; return 'bad'; }
}
set_error_handler('warn125');
$expectedLine = 7;
$child = new RejectChild125();
$child->clearParent();
$result = 42;
echo 'T:';
try { $result = $child->readParent(); echo 'bad|'; }
catch (TypeError $caught) {
    echo $caught->getMessage() === 'Value of type string returned from RejectParent125::__get() must be compatible with unset property RejectParent125::$ghost of type int' ? 'typed|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
echo $child->ghost, '|';
unset($child, $caught);
restore_error_handler();
echo 'E|';
