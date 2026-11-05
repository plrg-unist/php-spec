"""Independent per-operand Echo tick abort, line and lexical-frequency observations."""

CASES = {
    'review-first-operand-tick-throw-skips-later-print': (b'''<?php
function t() { echo 'T'; throw new Exception('tick'); }
register_tick_function('t');
try {
    declare(ticks=1) {
        echo 'A', print 'BAD';
    }
} catch (Exception $e) {
    echo 'C';
}
echo 'Z';
''', b'ATCZ'),
    'review-multiline-operands-keep-separate-marker-lines': (b'''<?php
function t() { $e = new Exception; echo '[' . $e->getTrace()[0]['line'] . ']'; }
register_tick_function('t');
declare(ticks=1) {
    echo
        'A',
        'B';
}
''', b'A[6]B[7]'),
    'review-later-callable-declarables-do-not-retime-earlier-operand': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    echo print 'A', (static function () { declare(ticks=2); return 'B'; })();
    echo 'Z';
}
''', b'A1TBTZ'),
    'review-empty-constant-operands-break-prior-tick-adjacency': (b'''<?php
$x = 0;
function t() { global $x; $x = $x + 1; echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    echo 'P';
    echo '', null, false, $x;
}
''', b'PTTTT4T'),
}
