<?php
function warn120($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class TypedUnset120 {
    public int $ghost = 0;
    public function __get($name) { echo 'G|'; return $this->ghost; }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn120');
$child = new TypedUnset120();
unset($child->ghost);
$result = 42;
echo 'T:';
try { $result = $child->ghost; echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Typed property TypedUnset120::$ghost must not be accessed before initialization' ? 'typed|' : 'bad-message|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
