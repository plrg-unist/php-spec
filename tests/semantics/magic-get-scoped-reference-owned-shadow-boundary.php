<?php
class OwnedScopedReferenceParent127 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public static function readOwned() {
        return scopedReferenceFactory127()->ghost; // READ127
    }
}
class OwnedScopedReferenceChild127 extends OwnedScopedReferenceParent127 {
    public string $ghost = 'hidden';
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() { echo 'D|'; }
}
function scopedReferenceFactory127() {
    $receiver = new OwnedScopedReferenceChild127();
    $receiver->clear();
    return $receiver;
}
$slot = '7';
echo 'O:';
$result = OwnedScopedReferenceParent127::readOwned();
echo $result === 7 ? 'int7|' : 'bad|';
echo $slot === 7 ? 'cell7|' : 'bad|';
$slot = 'free';
echo $slot === 'free' ? 'free|' : 'bad|';
unset($result, $slot);
echo 'E|';
