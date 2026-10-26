<?php
class ScopedReferenceParent127 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function read() {
        $receiver = $this;
        return $receiver->ghost; // READ127
    }
}
class ScopedReferenceChild127 extends ScopedReferenceParent127 {
    public string $ghost = 'hidden';
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() { echo 'D|'; }
}
class ReferenceHolder127 { public string $value = '7'; }
$receiver = new ScopedReferenceChild127();
$receiver->clear();
$holder = new ReferenceHolder127();
$slot =& $holder->value;
$result = 42;
echo 'C:';
try { $result = $receiver->read(); echo 'bad|'; }
catch (TypeError $caught) {
    echo $caught->getMessage() === 'Reference with value of type string held by property ReferenceHolder127::$value of type string is not compatible with property ScopedReferenceParent127::$ghost of type int' ? 'conflict|' : 'bad-message|';
    echo $caught->getLine() === 7 ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
    echo $holder->value === '7' ? 'held7|' : 'bad|';
    $slot = '8';
    echo $holder->value === '8' ? 'held8|' : 'bad|';
}
echo $receiver->ghost, '|';
unset($receiver, $holder, $slot, $result, $caught);
echo 'E|';
