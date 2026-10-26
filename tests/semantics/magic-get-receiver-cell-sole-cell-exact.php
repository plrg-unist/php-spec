<?php
class CellExactHolder131 { public int|string $value = 0; }
class CellExactTarget131 {
    public int $ghost = 0;
    function clear() { $self = $this; unset($self->ghost); }
    function &__get($name) { global $slot; echo 'G|'; return $slot; }
    function __destruct() { global $slot; echo 'D|', $slot === 7 ? 'exact7|' : 'bad-source|'; $slot = '9'; echo 'd|'; }
}
function &cellExactFactory131() { $receiver = new CellExactTarget131; $receiver->clear(); echo 'F|'; return $receiver; }
$slot = 7;
$holder = new CellExactHolder131;
$holder->value =& $slot;
echo 'T:';
$result = cellExactFactory131()->ghost; // READ131
echo $result === 7 ? 'int7|' : 'bad-result|', $slot === '9' ? 'string9|' : 'bad-source|';
$slot = 'free';
echo $slot === 'free' ? 'free|' : 'bad-write|', $holder->value === 'free' ? 'heldfree|' : 'bad-held|';
unset($result, $holder, $slot);
echo 'Z|';
