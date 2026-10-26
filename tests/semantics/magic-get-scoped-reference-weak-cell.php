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
$receiver = new ScopedReferenceChild127();
$receiver->clear();
$slot = '7';
echo 'U:';
$result = $receiver->read();
echo $result === 7 ? 'int7|' : 'bad|';
echo $slot === 7 ? 'cell7|' : 'bad|';
$slot = 'free';
echo $slot === 'free' ? 'free|' : 'bad|';
echo $receiver->ghost, '|';
unset($receiver, $result, $slot);
echo 'E|';
