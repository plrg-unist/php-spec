<?php
function warn121($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class ReplaceBase121 {
    public int $ghost = 0;
    public function __get($name) {
        global $child;
        echo 'G|';
        $child = null;
        return $this->ghost; // READ121
    }
    public function __destruct() { global $failure; echo 'D|'; throw $failure; }
}
class ReplaceChild121 extends ReplaceBase121 {}
set_error_handler('warn121');
$failure = new Exception('replacement121');
$child = new ReplaceChild121();
unset($child->ghost);
$expectedLine = 9;
$result = 42;
echo 'R:';
try { $result = $child->ghost; echo 'bad|'; }
catch (Throwable $caught) {
    echo $caught === $failure ? 'same|' : 'bad-identity|';
    $previous = $caught->getPrevious();
    echo $previous->getMessage() === 'Typed property ReplaceBase121::$ghost must not be accessed before initialization' ? 'typed|' : 'bad-message|';
    echo $previous->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $previous->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($child, $caught, $previous, $failure);
restore_error_handler();
echo 'E|';
