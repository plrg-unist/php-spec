"""A real getter Tick callback can read a sibling and abort before the return."""

CASES = {
    'review-getter-body-tick-callback-abort-preserves-backing-value': (b'''<?php
$n = 0;
function t() {
    global $n, $object;
    $n = $n + 1;
    echo 'T';
    if ($n === 3) {
        echo $object->other;
        throw new Exception('stop');
    }
}
register_tick_function('t');
declare(ticks=1);
class TickHook43 {
    public $other = 9;
    public int $value = 7 {
        get {
            declare(ticks=1) { echo 'G'; }
            return $this->value;
        }
    }
}
$object = new TickHook43;
try { echo $object->value; echo 'BAD'; }
catch (Exception $e) { echo 'C'; }
echo $object->value;
echo 'Z';
''', b'TTGT9CTGT7TZT'),
}
