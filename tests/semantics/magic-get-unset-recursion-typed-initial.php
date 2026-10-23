<?php
class TypedInitial120 {
    public int $ghost;
    public function __get($name) { echo 'bad-get|'; return 7; }
}
$child = new TypedInitial120();
echo 'I:';
try { $value = $child->ghost; echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Typed property TypedInitial120::$ghost must not be accessed before initialization' ? 'typed|' : 'bad-message|';
}
unset($child, $caught);
echo 'E|';
