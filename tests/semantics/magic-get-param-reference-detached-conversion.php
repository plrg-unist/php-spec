<?php
class ParamDetachedHolder130 { public object $value; }
class ParamDetachedString130 {
    public function __toString(): string { global $slot, $holder; $holder->value =& $slot; echo 'S|'; return '7'; }
}
class ParamDetachedTarget130 {
    public int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
}
function paramDetached130(string &$cell, $target) {
    global $holder;
    echo 'R|';
    unset($holder->value);
    echo 'u|';
    $got = $target->ghost; // READ130
    echo $got === 7 ? 'int7|' : 'bad-get|', $cell === 7 ? 'cell7|' : 'bad-cell|';
    $cell = 'free';
    echo 'write|';
    return $got;
}
$holder = new ParamDetachedHolder130();
$target = new ParamDetachedTarget130();
$target->clear();
$slot = new ParamDetachedString130();
echo 'D:';
$result = paramDetached130($slot, $target);
echo $result === 7 ? 'result7|' : 'bad-result|', $slot === 'free' ? 'free|' : 'bad-cell|';
unset($slot, $holder, $target, $result);
echo 'Z|';
