"""Independent empty-input and abrupt-target foreach Tick observations."""

CASES = {
    'review-empty-foreach-compiles-value-before-key-without-evaluation': (b'''<?php
function t() { echo 'T'; }
$keys = [];
$values = [];
register_tick_function('t');
declare(ticks=1) {
    echo 'P';
    foreach ([] as
        $keys[(function () { declare(ticks=2); echo 'BADK'; return 'k'; })()] =>
        $values[(function () { declare(ticks=3); echo 'BADV'; return 'v'; })()]
    ) {
        echo 'BADB';
    }
    echo 'Z';
}
''', b'PTZT'),
    'review-abrupt-value-target-skips-key-body-and-releases-iterator': (b'''<?php
function t() { echo 'T'; }
$keys = [];
$values = [];
register_tick_function('t');
try {
    declare(ticks=1) {
        foreach ([7 => 9] as
            $keys[(function () { declare(ticks=2); echo 'BADK'; return 'k'; })()] =>
            $values[(function () {
                declare(ticks=1) {
                    echo 'V';
                    throw new Exception('target');
                }
            })()]
        ) {
            echo 'BADB';
        }
    }
} catch (Exception $e) {
    echo 'C';
}
echo $keys['k'] ?? 'K';
echo $values['v'] ?? 'W';
echo 'Z';
''', b'VTCKWZ'),
}
