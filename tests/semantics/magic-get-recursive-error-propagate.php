<?php
function warn121($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class TypedBase121 {
    public int $ghost = 0;
    public function __get($name) {
        global $child;
        echo 'G|';
        $child = null;
        return $this->ghost; // READ121
    }
    public function __destruct() { global $live; $live = 99; echo 'D|'; }
}
class TypedChild121 extends TypedBase121 {}
set_error_handler('warn121');
$child = new TypedChild121();
unset($child->ghost);
$expectedLine = 9;
$live = 7;
$result = 42;
echo 'S:';
try { $result = $child->ghost; echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Typed property TypedBase121::$ghost must not be accessed before initialization' ? 'typed|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '/', $live, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
