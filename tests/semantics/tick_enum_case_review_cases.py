"""Independent EnumCase prefix line, availability and abrupt-declaration checks."""

CASES = {
    'review-backed-case-tick-precedes-installation-and-uses-value-line': (b'''<?php
const TICK_BACKING40 = 7;
$n = 0;
function t() {
    global $n;
    $n = $n + 1;
    echo 'T';
    if ($n === 1) {
        $at = new Exception;
        echo '['.$at->getTrace()[0]['line'].']';
        try { TickAvailable40::A; echo 'BAD'; }
        catch (Error $e) { echo 'N'; }
    }
}
register_tick_function('t');
enum TickAvailable40: int {
    public function unused() { declare(ticks=1); echo 'BAD'; }
    case A =
        TICK_BACKING40;
    case B = 8;
}
echo TickAvailable40::A->value;
echo 'Z';
''', b'T[19]N7TZT'),
    'review-case-callback-abort-prevents-enum-installation': (b'''<?php
$n = 0;
function t() {
    global $n;
    $n = $n + 1;
    echo 'T';
    if ($n === 1) { throw new Exception('stop'); }
}
function h($e) {
    echo 'C';
    try { TickAborted40::A; echo 'BAD'; }
    catch (Error $missing) { echo 'N'; }
}
register_tick_function('t');
set_exception_handler('h');
enum TickAborted40 {
    public function unused() { declare(ticks=1); echo 'BAD'; }
    case A;
    case B;
}
echo 'BAD';
''', b'TCN'),
}
