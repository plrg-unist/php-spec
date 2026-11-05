"""Independent Match tick compiler order and selected-result observations."""

CASES = {
    'review-later-condition-before-selected-callable-body': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=0) {
    $value = match (0) {
        0 => (static function () { echo 'A'; return 1; })(),
        (static function () { declare(ticks=2); return 1; })() => 0,
    };
    echo 'Z';
    echo 'W';
}
''', b'ATZWT'),
    'review-unselected-body-declarables': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=0) {
    $value = match (0) {
        0 => print 'A',
        default => (static function () { declare(ticks=3); return 0; })(),
    };
    echo 'Z';
    echo 'W';
    echo 'Y';
}
''', b'AZWTY'),
    'review-table-assignment-restores-marker-line': (b'''<?php
function t() { $e = new Exception; echo 'T', $e->getTrace()[0]['line'], ';'; }
register_tick_function('t');
declare(ticks=1) {
    $value = match (0) {
        0, 1 => print 'A',
        default => print 'BAD',
    };
    echo 'Z';
}
''', b'AT5;ZT9;'),
    'review-table-discard-keeps-final-arm-line': (b'''<?php
function t() { $e = new Exception; echo 'T', $e->getTrace()[0]['line'], ';'; }
register_tick_function('t');
declare(ticks=1) {
    match (0) {
        0, 1 => print 'A',
        default => print 'BAD',
    };
    echo 'Z';
}
''', b'AT7;ZT9;'),
    'review-callback-throw-follows-result-assignment': (b'''<?php
function t() { throw new Exception('tick'); }
register_tick_function('t');
$value = 'old';
try {
    declare(ticks=1) {
        $value = match (0) { 0 => 'new' };
        echo 'BAD';
    }
} catch (Exception $e) {
    echo $value;
}
echo 'Z';
''', b'newZ'),
}
