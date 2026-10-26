<?php
function warn125($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class InitialParent125 {
    private int $ghost;
    public function readParent() {
        $receiver = $this;
        return $receiver->ghost; // READ125
    }
    public function __destruct() { echo 'D|'; }
}
class InitialChild125 extends InitialParent125 {
    public string $ghost = 'hidden';
    public function __get($name) { echo 'G|'; return '7'; }
}
set_error_handler('warn125');
$expectedLine = 7;
$child = new InitialChild125();
$result = 42;
echo 'I:';
try { $result = $child->readParent(); echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Typed property InitialParent125::$ghost must not be accessed before initialization' ? 'initial|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
