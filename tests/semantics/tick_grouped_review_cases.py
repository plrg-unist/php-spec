"""Independent grouped binding, initialization and unset-cleanup tick observations."""

CASES = {
    'review-global-tick-changes-later-dynamic-binding': (b'''<?php
$first = 10;
$later = 20;
$changed = 30;
$pick = 'later';
function t() { global $pick; $pick = 'changed'; echo 'T'; }
function f() {
    declare(ticks=1) {
        global $first, ${$GLOBALS['pick']};
    }
    echo $first;
    echo '|';
    echo $changed ?? 'U';
    echo '|';
    echo $later ?? 'U';
}
register_tick_function('t');
f();
''', b'TT10|30|U'),
    'review-static-tick-precedes-later-initializer-effects': (b'''<?php
$seed = 1;
function t() { global $seed; $seed = $seed + 1; echo 'T'; }
function init_value() { global $seed; echo 'I'; return $seed; }
function f() {
    declare(ticks=1) {
        static $first = 0, $second = init_value();
    }
    echo $second;
}
register_tick_function('t');
f();
''', b'TIT2'),
    'review-unset-cleanup-finishes-before-tick-aborts-next-target': (b'''<?php
class A { function __destruct() { echo 'A'; } }
class B { function __destruct() { echo 'B'; } }
function t() { echo 'T'; throw new Exception('tick'); }
$a = new A;
$b = new B;
register_tick_function('t');
try {
    declare(ticks=1) {
        unset($a, $b);
    }
} catch (Exception $e) {
    echo 'C';
}
echo isset($b) ? 'H' : 'G';
unset($b);
echo 'Z';
''', b'ATCHBZ'),
}
