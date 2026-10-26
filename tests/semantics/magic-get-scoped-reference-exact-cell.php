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
class ReferenceHolder127 { public int|string $value = 7; }
$receiver = new ScopedReferenceChild127();
$receiver->clear();
$holder = new ReferenceHolder127();
$slot =& $holder->value;
echo 'K:';
$result = $receiver->read();
echo $result === 7 ? 'int7|' : 'bad|';
$slot = 'free';
echo $holder->value === 'free' ? 'free|' : 'bad|';
echo $receiver->ghost, '|';
unset($receiver, $holder, $slot, $result);
echo 'E|';
