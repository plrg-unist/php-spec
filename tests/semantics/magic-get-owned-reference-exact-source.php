<?php
class OwnedExactParent128 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public static function readOwned() {
        return exactReferenceFactory128()->ghost; // READ128
    }
}
class OwnedExactChild128 extends OwnedExactParent128 {
    public string $ghost = 'hidden';
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() {
        global $slot;
        echo 'D|';
        echo $slot === 7 ? 'exact7|' : 'bad-source|';
        $slot = 'free';
    }
}
class OwnedExactHolder128 { public int|string $value = 7; }
function exactReferenceFactory128() {
    $receiver = new OwnedExactChild128();
    $receiver->clear();
    return $receiver;
}
$holder = new OwnedExactHolder128();
$slot =& $holder->value;
echo 'T:';
$result = OwnedExactParent128::readOwned();
echo $result === 7 ? 'int7|' : 'bad|';
echo $holder->value === 'free' ? 'free|' : 'bad|';
$slot = 'later';
echo $holder->value === 'later' ? 'later|' : 'bad|';
unset($result, $slot, $holder);
echo 'E|';
