"""Independent coalesce prepass, quiet-read and memoized-key tick observations."""

CASES = {
    'review-prepass-coalesce-erases-fallback-and-preserves-adjacency': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    echo 'P';
    [7 ?? (static function ($x, $x) { declare(ticks=7); return 0; })()];
    echo 'Z';
}
''', b'PTZT'),
    'review-quiet-cv-read-and-runtime-unselected-fallback-declarables': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
set_error_handler(static function ($n, $m) { echo 'H'; return true; });
$present = 'P';
declare(ticks=0) {
    $missingValue = $missing ?? (static function () { declare(ticks=2); echo 'M'; return 'R'; })();
    $presentValue = $present ?? (static function () { declare(ticks=3); echo 'BAD'; return 'X'; })();
    echo $missingValue;
    echo $presentValue;
    echo 'Z';
}
''', b'MTRTPZ'),
    'review-missing-dimension-coalesce-assignment-memoizes-key': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
$values = [];
declare(ticks=0) {
    $values[(static function () { declare(ticks=2); echo 'K'; return 'k'; })()] ??= (static function () { declare(ticks=3); echo 'R'; return 9; })();
    echo $values['k'];
    echo 'Z';
    echo 'W';
}
''', b'KTRT9ZWT'),
    'review-present-dimension-coalesce-assignment-skips-runtime-fallback': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
$values = ['k' => 4];
declare(ticks=0) {
    $values[(static function () { declare(ticks=2); echo 'K'; return 'k'; })()] ??= (static function () { declare(ticks=3); echo 'BAD'; return 9; })();
    echo $values['k'];
    echo 'Z';
    echo 'W';
}
''', b'KT4ZTW'),
}
