"""A callback abort after construction preserves initialized plain properties."""

CASES = {
    'review-property-defaults-are-readable-before-assignment-tick-abort': (b'''<?php
$n = 0;
function t() {
    global $n, $object;
    $n = $n + 1;
    echo 'T';
    if ($n === 2) {
        echo $object->second;
        throw new Exception('stop');
    }
}
register_tick_function('t');
declare(ticks=1);
class TickProperty42 {
    public $first = 1, $second = 2;
}
try {
    $object = new TickProperty42;
    echo 'BAD';
}
catch (Exception $e) { echo 'C'; }
echo $object->first;
echo $object->second;
echo 'Z';
''', b'TT2CT1T2TZT'),
}
