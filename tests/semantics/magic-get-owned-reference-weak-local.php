<?php
class LocalReferenceProbe128 {
    public function __destruct() { global $slot; $slot = '9'; echo 'L|'; }
}
class PrivateReferenceOwner128 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public static function readOwned() {
        return localReferenceFactory128()->ghost; // READ128
    }
    public function &__get($name) {
        global $slot;
        echo 'G|';
        $probe = new LocalReferenceProbe128();
        return $slot;
    }
    public function __destruct() {
        global $slot;
        echo 'D|';
        echo $slot === 9 ? 'verified9|' : 'bad-source|';
        $slot = 'free';
    }
}
function localReferenceFactory128() {
    $receiver = new PrivateReferenceOwner128();
    $receiver->clear();
    return $receiver;
}
$slot = '7';
echo 'W:';
$result = PrivateReferenceOwner128::readOwned();
echo $result === 9 ? 'int9|' : 'bad|';
echo $slot === 'free' ? 'free|' : 'bad|';
unset($result, $slot);
echo 'E|';
