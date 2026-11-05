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
    'review-later-literal-keeps-preceding-closure-compiler-line': (b'''<?php
function t() { $e = new Exception; echo '[' . $e->getTrace()[0]['line'] . ']'; }
register_tick_function('t');
declare(ticks=1);
const TickClosureCarry38 = static function () {
    declare(ticks=1);
},
TickScalarCarry38 = 2;
echo 'Z';
''', b'[4][7]Z[9]'),
    'review-constant-array-compiles-value-before-key-lines': (b'''<?php
const TickKeyOrder38 = 'k';
const TickValueOrder38 = 9;
function t() { $e = new Exception; echo '[' . $e->getTrace()[0]['line'] . ']'; }
register_tick_function('t');
declare(ticks=1);
const TickTableOrder38 = [
    TickKeyOrder38 =>
    TickValueOrder38
];
echo TickTableOrder38['k'];
''', b'[6][8]9[11]'),
    'review-constant-header-seeds-first-name-line': (b'''<?php
function t() { $e = new Exception; echo '[' . $e->getTrace()[0]['line'] . ']'; }
register_tick_function('t');
declare(ticks=1);
const
    TickHeaderA38 = 1, TickHeaderB38 = 2;
echo 'Z';
''', b'[4][6]Z[7]'),
}

# Boundary controls pair the source with its expected model prefix.
CONTROLS = {
    'review-callable-bearing-constant-array-order-remains-explicit': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1);
const TickArrayRefuse38 = [static function () { declare(ticks=2); }];
echo 'Z';
''', b''),
}
