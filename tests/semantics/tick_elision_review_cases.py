"""Independent compiled-versus-elided conditional tick observations."""

CASES = {
    'review-direct-ternary-compiles-unselected-body': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=0) {
    $value = true ? print 'A' : (static function () { declare(ticks=2); return 0; })();
    echo 'Z';
    echo 'W';
}
''', b'AZTW'),
    'review-array-prepass-erases-unselected-diagnostic': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=0) {
    $value = [true ? print 'A' : (static function ($x, $x) { declare(ticks=2); return 0; })()];
    echo 'Z';
    echo 'W';
}
''', b'AZW'),
    'review-constant-logical-aliases-preserve-prior-tick': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    echo 'P';
    false && (static function () { declare(ticks=7); return 0; })();
    true || (static function () { declare(ticks=7); return 0; })();
    false and (static function () { declare(ticks=7); return 0; })();
    true or (static function () { declare(ticks=7); return 0; })();
    echo 'Z';
}
''', b'PTZT'),
    'review-runtime-logical-aliases-compile-unselected-bodies': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
$stop = false;
$go = true;
declare(ticks=0) {
    $value = ($stop && (static function () { declare(ticks=2); return 0; })());
    echo 'A';
    $value = ($go || (static function () { declare(ticks=2); return 0; })());
    echo 'B';
    $value = ($stop and (static function () { declare(ticks=2); return 0; })());
    echo 'C';
    $value = ($go or (static function () { declare(ticks=2); return 0; })());
    echo 'D';
    echo 'Z';
}
''', b'ATBTCTDTZ'),
    'review-retained-print-does-not-publish-skipped-redirect': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    echo 'P';
    $value = [(print 'A') || (true ? (static function () { declare(ticks=2); return 0; })() : (static function () { declare(ticks=3); return 0; })())];
    echo 'Z';
}
''', b'PTATZT'),
    'review-selected-dynamic-redirect-keeps-only-selected-body': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    $value = [true ? (static function () { declare(ticks=2); echo 'A'; return 7; })() : (static function () { declare(ticks=5); return 0; })()];
    echo 'Z';
    echo 'W';
}
''', b'ATZTW'),
}

CONTROLS = {
    'review-fixed-builtin-left-has-hidden-constant-kind': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=0) {
    $value = defined('PHP_VERSION') || (static function () { declare(ticks=2); return 0; })();
    echo 'A';
    echo 'Z';
}
''', b''),
    'review-fixed-builtin-right-has-hidden-constant-kind': (b'''<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    echo 'P';
    true && defined('PHP_VERSION');
    echo 'Z';
}
''', b''),
}

CONTROL_NATIVE_EXPECTED = {
    'review-fixed-builtin-left-has-hidden-constant-kind': b'AZ',
    'review-fixed-builtin-right-has-hidden-constant-kind': b'PTZT',
}
