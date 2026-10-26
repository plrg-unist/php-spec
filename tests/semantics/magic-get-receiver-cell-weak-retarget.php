<?php
class CellWeakTarget131 {
    public int $ghost = 0;
    function clear() { $self = $this; unset($self->ghost); }
    function &__get($name) { global $receiver, $slot; echo 'G|'; $receiver = null; return $slot; }
    function __destruct() { global $slot; echo 'D|', $slot === 7 ? 'verified7|' : 'bad-verify|'; $slot = '9'; echo 'd|'; }
}
function &cellWeakFactory131() { global $receiver; echo 'F|'; return $receiver; }
$slot = '7';
$receiver = new CellWeakTarget131;
$receiver->clear();
echo 'W:';
$result = cellWeakFactory131()->ghost; // READ131
echo $result === '9' ? 'string9|' : 'bad-result|', $receiver === null ? 'null|' : 'bad-receiver|';
$slot = 'free';
echo $slot === 'free' ? 'free|' : 'bad-source|';
unset($result, $receiver, $slot);
echo 'Z|';
