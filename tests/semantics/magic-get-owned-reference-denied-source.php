<?php
class DeniedReferenceOwner128 {
    private int $ghost;
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() {
        global $slot;
        echo 'D|';
        echo $slot === '7' ? 'raw7|' : 'bad-source|';
        $slot = '8';
    }
}
class DeniedReferenceHolder128 { public string $value = '7'; }
function deniedReferenceFactory128() { return new DeniedReferenceOwner128(); }
$holder = new DeniedReferenceHolder128();
$slot =& $holder->value;
echo 'X:';
$result = deniedReferenceFactory128()->ghost; // READ128
echo $result === '7' ? 'string7|' : 'bad|';
echo $holder->value === '8' ? 'held8|' : 'bad|';
unset($result, $slot, $holder);
echo 'E|';
