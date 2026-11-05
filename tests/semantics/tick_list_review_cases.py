"""Independent by-value list-target compilation, laziness and partial-write observations."""

CASES = {
    'review-empty-foreach-list-compiles-key-before-nested-target': (b'''<?php
function t() { echo 'T'; }
$out = [];
register_tick_function('t');
declare(ticks=1) {
    echo 'P';
    foreach ([] as [
        (function () { declare(ticks=3); echo 'BADK'; return 'row'; })() =>
            [$out[(function () { declare(ticks=2); echo 'BADV'; return 'v'; })()]]
    ]) {
        echo 'BADB';
    }
    echo 'Z';
}
''', b'PTZT'),
    'review-defined-list-target-throw-preserves-earlier-write': (b'''<?php
function t() { echo 'T'; }
$out = [];
register_tick_function('t');
try {
    declare(ticks=1) {
        foreach ([['a' => 10, 'b' => 20, 'c' => 30]] as [
            'a' => $out['first'],
            'b' => $out[(function () {
                declare(ticks=1) {
                    echo 'V';
                    throw new Exception('target');
                }
            })()],
            'c' => $out[(function () { declare(ticks=2); echo 'BADL'; return 'last'; })()]
        ]) {
            echo 'BADB';
        }
    }
} catch (Exception $e) {
    echo 'C';
}
echo $out['first'];
echo $out['second'] ?? 'S';
echo $out['last'] ?? 'L';
echo 'Z';
''', b'VTC10SLZ'),
}
