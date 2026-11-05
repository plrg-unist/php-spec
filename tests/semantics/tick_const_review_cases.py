"""Independent global-constant initializer lines and complete-group abort observations."""

CASES = {
    'review-constant-closure-order-keeps-final-initializer-marker-line': (b'''<?php
function t() { $e = new Exception; echo '[' . $e->getTrace()[0]['line'] . ']'; }
register_tick_function('t');
declare(ticks=1);
const TickFirst38 = static function () {
    declare(ticks=2);
},
TickLast38 = static function () {
    declare(ticks=1);
};
echo 'Z';
''', b'[4][10]Z[11]'),
    'review-constant-group-commits-before-tick-aborts-later-declaration': (b'''<?php
$count = 0;
function t() {
    global $count;
    $count = $count + 1;
    if ($count === 2) {
        echo TickA38;
        echo TickB38;
        throw new Exception('tick');
    }
}
function h($e) {
    echo 'C';
    echo TickA38;
    echo TickB38;
    echo defined('TickLate38') ? 'L' : 'N';
    echo 'Z';
}
set_exception_handler('h');
register_tick_function('t');
declare(ticks=1);
const TickA38 = 1, TickB38 = 2;
const TickLate38 = 3;
echo 'BAD';
''', b'12C12NZ'),
}
