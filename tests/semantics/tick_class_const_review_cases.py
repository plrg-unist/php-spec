"""Invoked class-constant Closure ticks retain reads, returns and abrupt cleanup."""

CASES = {
    'review-invoked-const-closure-tick-reads-installed-sibling-constant': (b'''<?php
$n = 0;
function t() {
    global $n;
    $n = $n + 1;
    echo 'T';
    if ($n === 3) { echo TickConstInvoke41::VALUE; }
}
register_tick_function('t');
declare(ticks=1);
class TickConstInvoke41 {
    public const VALUE = 7, F = static function() {
        declare(ticks=1) { echo 'V'; }
        return 9;
    };
}
$f = TickConstInvoke41::F;
echo $f();
echo 'Z';
''', b'TTVT79TZT'),
    'review-invoked-const-closure-callback-abort-skips-return-output': (b'''<?php
$n = 0;
function t() {
    global $n;
    $n = $n + 1;
    echo 'T';
    if ($n === 3) {
        echo TickConstAbort41::VALUE;
        throw new Exception('stop');
    }
}
register_tick_function('t');
declare(ticks=1);
class TickConstAbort41 {
    public const VALUE = 7, F = static function() {
        declare(ticks=1) { echo 'V'; }
        return 9;
    };
}
$f = TickConstAbort41::F;
try { echo $f(); echo 'BAD'; }
catch (Exception $e) { echo 'C'; }
echo TickConstAbort41::VALUE;
echo 'Z';
''', b'TTVT7CT7TZT'),
}
