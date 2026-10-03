"""Original safe CV/reference warning reads and the remaining plain-CV gap."""

CASES = [
    ('reference-rebind-both-identities', b'''<?php
error_reporting(0);
$x = null;
$a =& $x;
$y = 9;
function warningReadRebind13($severity, $message, $file, $line) {
    $GLOBALS['a'] =& $GLOBALS['y'];
}
set_error_handler('warningReadRebind13', 2);
echo ($a === $missing_first ? 1 : 0), ':', $a, ':', ($x === null ? 1 : 0), ';';
$a =& $x;
echo ($a !== $missing_second ? 1 : 0), ':', $a, ':', ($x === null ? 1 : 0);
restore_error_handler();
''', b'1:9:1;0:9:1', 'normal'),
    ('globals-root-and-handler-local', b'''<?php
error_reporting(0);
$x = null;
$a =& $x;
$y = 9;
function warningReadGlobals13($severity, $message, $file, $line) {
    $a = 5;
    $GLOBALS['a'] =& $GLOBALS['y'];
    echo $a, ':', $GLOBALS['a'], ';';
}
set_error_handler('warningReadGlobals13', 2);
echo ($a === $missing ? 1 : 0), ':', $a, ':', ($x === null ? 1 : 0);
restore_error_handler();
''', b'5:9;1:9:1', 'normal'),
    ('same-cell-local-caller', b'''<?php
error_reporting(0);
$x = null;
set_error_handler(function($severity, $message, $file, $line) use (&$x) {
    $x = 9;
}, 2);
function warningReadLocal13(&$a) {
    echo ($a !== $missing ? 1 : 0), ':', $a, ';';
}
warningReadLocal13($x);
echo $x;
restore_error_handler();
''', b'1:9;9', 'normal'),
    ('nested-borrow-normal', b'''<?php
error_reporting(0);
$x = null;
$a =& $x;
set_error_handler(function($severity, $message, $file, $line) {
    $local = null;
    $p =& $local;
    set_error_handler(function($severity, $message, $file, $line) use (&$local) {
        echo func_num_args(), ';';
        $local = 7;
    }, 2);
    $r = $p === $inner_missing;
    echo 'I', ($r ? 1 : 0), ':', $local, ';';
    restore_error_handler();
    $GLOBALS['x'] = 5;
}, 2);
$r = $a === $outer_missing;
echo 'O', ($r ? 1 : 0), ':', $a, ':', $x;
restore_error_handler();
''', b'4;I0:7;O0:5:5', 'normal'),
    ('nested-borrow-throw', b'''<?php
error_reporting(0);
$x = null;
$a =& $x;
set_error_handler(function($severity, $message, $file, $line) {
    $local = null;
    $p =& $local;
    set_error_handler(function($severity, $message, $file, $line) use (&$local) {
        $local = 8;
        throw new Error('inner');
    }, 2);
    try {
        echo ($p !== $inner_missing ? 1 : 0), 'bad';
    } catch (Error $e) {
        echo 'C', $local, ';';
    }
    restore_error_handler();
    $GLOBALS['x'] = 6;
}, 2);
echo ($a !== $outer_missing ? 1 : 0), ':', $a, ':', $x;
restore_error_handler();
''', b'C8;1:6:6', 'normal'),
    ('no-handler-and-mask-miss', b'''<?php
error_reporting(0);
$x = null;
$a =& $x;
echo ($a === $missing_first ? 1 : 0), ';';
$called = 0;
set_error_handler(function() use (&$called) { $called++; }, 512);
echo ($a !== $missing_second ? 1 : 0), ':', $called;
restore_error_handler();
''', b'1;0:0', 'normal'),
    ('plain-cv-reference-wrapper-pending', b'''<?php
error_reporting(0);
$a = null;
$y = 9;
set_error_handler(function($severity, $message, $file, $line) {
    $GLOBALS['a'] =& $GLOBALS['y'];
}, 2);
echo ($a === $missing ? 1 : 0), ':', $a;
restore_error_handler();
''', b'0:9', 'unsupported'),
]
