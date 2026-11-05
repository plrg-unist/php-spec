"""Independent tick placement and request counters across Generator pauses."""

CASES = {
    'review-counter-across-yield-and-from': (b'''<?php
function t() { echo 'T'; }
function seq() {
    declare(ticks=2) {
        echo 'A';
        yield 1;
        echo 'B';
        yield from [2, 3];
        echo 'C';
    }
}
register_tick_function('t');
$g = seq();
echo 'I';
echo $g->current();
declare(ticks=1) { echo 'O'; }
$g->next(); echo $g->current();
$g->next(); echo $g->current();
$g->next(); echo 'Z';
''', b'IA1OTBT23CTZ'),
    'review-bare-yield-send-discards-input': (b'''<?php
function t() { echo 'T'; }
function seq() {
    declare(ticks=1) {
        echo 'A';
        yield 1;
        echo 'B';
        yield 2;
        echo 'C';
    }
}
register_tick_function('t');
$g = seq();
echo $g->current(), '|';
echo $g->send(9), '|';
$g->next(); echo 'Z';
''', b'AT1|TBT2|TCTZ'),
    'review-assigned-yield-send-preserves-target': (b'''<?php
function t() { echo 'T'; }
function seq() {
    declare(ticks=1) {
        echo 'A';
        $seen = yield 1;
        echo $seen;
        yield 2;
        echo 'C';
    }
}
register_tick_function('t');
$g = seq();
echo $g->current(), '|';
echo $g->send(9), '|';
$g->next(); echo 'Z';
''', b'AT1|T9T2|TCTZ'),
    'review-key-before-value-declarables': (b'''<?php
function t() { echo 'T'; }
declare(ticks=0) {
    function seq() {
        yield (static function () { declare(ticks=1); return 'K'; })()
            => (static function () { declare(ticks=3); return 'V'; })();
        echo 'Z';
    }
}
register_tick_function('t');
$g = seq();
echo $g->current(), '|';
$g->next(); echo 'E';
''', b'TV|ZTE'),
    'review-nullary-yield-delayed-marker': (b'''<?php
function t() { echo 'T'; }
function seq() {
    declare(ticks=1) {
        echo 'A';
        yield;
        echo 'B';
        yield 7;
        echo 'C';
    }
}
register_tick_function('t');
$g = seq();
echo $g->current() === null ? 'N' : 'BAD', '|';
echo $g->send(9), '|';
$g->next(); echo 'Z';
''', b'ATN|TBT7|TCTZ'),
}
