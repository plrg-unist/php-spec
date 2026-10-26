<?php
class ParamConflictHolder130 { public object $value; }
class ParamConflictString130 {
    public function __toString(): string { global $slot, $holder; $holder->value =& $slot; echo 'S|'; return '7'; }
}
class ParamConflictTarget130 {
    public int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
}
function paramConflict130(string &$cell, $target) {
    echo 'R|';
    $got = 42;
    try { $got = $target->ghost; } // READ130
    catch (TypeError $caught) {
        echo 'typed|';
        echo $caught->getMessage() === 'Reference with value of type string held by property ParamConflictHolder130::$value of type object is not compatible with property ParamConflictTarget130::$ghost of type int' ? 'message|' : 'bad-message|';
        echo $caught->getLine() === 14 ? 'line|' : 'bad-line|', $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    }
    echo $got === 42 ? '42|' : 'bad-get|', $cell === '7' ? 'cell7|' : 'bad-cell|';
    return $got;
}
$holder = new ParamConflictHolder130();
$target = new ParamConflictTarget130();
$target->clear();
$slot = new ParamConflictString130();
echo 'C:';
$result = paramConflict130($slot, $target);
echo $result === 42 ? 'result42|' : 'bad-result|', $holder->value === '7' ? 'held7|' : 'bad-holder|';
unset($slot, $holder, $target, $result);
echo 'Z|';
