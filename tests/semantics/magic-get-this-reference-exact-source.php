<?php
class ThisExactHolder129 { public int|string $value = 7; }
class ThisExactParent129 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function readThis() {
        global $owner, $slot;
        $value = $this->ghost; // READ129
        echo 'r|';
        $owner = null;
        $slot = 'free';
        echo $value === 7 ? 'copied7|' : 'bad-copy|';
        $slot = 'later';
        return $value;
    }
}
class ThisExactChild129 extends ThisExactParent129 {
    public string $ghost = 'hidden';
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() { global $slot; echo 'D|', $slot === 'later' ? 'later|' : 'bad-source|'; }
}
$holder = new ThisExactHolder129();
$slot =& $holder->value;
$owner = new ThisExactChild129();
$owner->clear();
echo 'T:';
$result = $owner->readThis();
echo $result === 7 ? 'int7|' : 'bad-result|', $holder->value === 'later' ? 'heldlater|' : 'bad-source|', $owner === null ? 'null|' : 'bad-owner|';
unset($owner, $holder, $slot, $result);
echo 'E|';
