<?php
class ParamExactHolder130 { public object $value; }
class ParamExactString130 {
    public function __toString(): string { global $slot, $holder; $holder->value =& $slot; echo 'S|'; return '7'; }
}
class ParamExactTarget130 {
    public string $ghost = 'seed';
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
}
function paramExact130(string &$cell, $target) {
    echo 'R|';
    $got = $target->ghost; // READ130
    echo $got === '7' ? 'string7|' : 'bad-get|';
    try { $cell = 'changed'; echo 'bad-write|'; }
    catch (TypeError $caught) { echo 'blocked|'; }
    echo $cell === '7' ? 'cell7|' : 'bad-cell|';
    return $got;
}
$holder = new ParamExactHolder130();
$target = new ParamExactTarget130();
$target->clear();
$slot = new ParamExactString130();
echo 'E:';
$result = paramExact130($slot, $target);
echo $result === '7' ? 'result7|' : 'bad-result|', $holder->value === '7' ? 'held7|' : 'bad-holder|';
unset($slot, $holder, $target, $result);
echo 'Z|';
