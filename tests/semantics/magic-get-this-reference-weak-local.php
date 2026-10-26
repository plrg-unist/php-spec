<?php
class ThisWeakProbe129 { public function __destruct() { global $slot; $slot = '9'; echo 'L|'; } }
class ThisWeakParent129 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function readThis() {
        global $owner, $slot;
        $value = $this->ghost; // READ129
        echo 'r|';
        $owner = null;
        $slot = 'free';
        echo $value === 9 ? 'copied9|' : 'bad-copy|';
        return $value;
    }
}
class ThisWeakChild129 extends ThisWeakParent129 {
    public string $ghost = 'hidden';
    public function &__get($name) { global $slot; echo 'G|'; $probe = new ThisWeakProbe129(); return $slot; }
    public function __destruct() { global $slot; echo 'D|', $slot === 'free' ? 'free|' : 'bad-source|'; }
}
$slot = '7';
$owner = new ThisWeakChild129();
$owner->clear();
echo 'W:';
$result = $owner->readThis();
echo $result === 9 ? 'int9|' : 'bad-result|', $owner === null ? 'null|' : 'bad-owner|';
unset($owner, $slot, $result);
echo 'E|';
