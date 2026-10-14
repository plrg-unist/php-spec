"""Last-owner pending Throwable disposal during raw callback-destructor exit."""
CASES = {
    'review-callback-dexit-pending-last-owner': b'''<?php
class Pending extends Exception {
    function __destruct() {
        echo 'Q:', $GLOBALS['x'] === 99, ':', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';';
        $GLOBALS['x'] = 73;
    }
}
class Local {
    function __destruct() {
        echo 'L:', $GLOBALS['x'] === 41, ';';
        $pending = $GLOBALS['pending']; unset($GLOBALS['pending']); throw $pending;
    }
}
class ParentT {
    function __destruct() {
        echo 'P:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 73, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak_pending']->get() === null, ':', $GLOBALS['weak_handler']->get() === null, ';';
    }
}
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 99; exit(17); echo 'D-END;'; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() {
    echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 73, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak_pending']->get() === null, ':', $GLOBALS['weak_handler']->get() === null, ':', isset($GLOBALS['pending']), ';';
}
register_shutdown_function('done'); $pending = new Pending('pending'); $weak_pending = WeakReference::create($pending);
$h = new H; $weak_handler = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
}
STATUS = 'explicit_exit'
EXIT_CODES = {'review-callback-dexit-pending-last-owner': 17}
