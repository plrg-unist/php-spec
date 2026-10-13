"""Independent owning-handler local cleanup cancellation originals."""
CASES = {
    'review-callback-cancel-retained-registry': b'''<?php
class Local {
    function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['second']; }
}
class H {
    function __invoke($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; $local = new Local; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === true, ';'; $GLOBALS['x'] = 99; }
}
function done() { echo 'S:', $GLOBALS['x'] === 99, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100; $second = new Exception('supplied local');
try { $v = ++$x; echo 'R;'; }
catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $x === true, ':', $v === 100, ':', $weak->get() !== null, ':', get_error_handler() === $weak->get(), ';'; }
finally { echo 'F;'; }
echo 'END;'; set_error_handler(null);
echo 'A:', get_error_handler() === null, ':', $weak->get() === null, ':', $x === 99, ';';
''',
    'review-callback-cancel-late-peer': b'''<?php
class Local {
    function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ':', $GLOBALS['peer'] === 41, ';'; throw $GLOBALS['second']; }
}
class H {
    function __invoke($n, $m) {
        echo 'H:', $n, ';'; set_error_handler('h2');
        $GLOBALS['peer'] =& $GLOBALS['x']; $GLOBALS['x'] = 41; $local = new Local; exit('E;');
    }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ':', $GLOBALS['peer'] === 41, ';'; $GLOBALS['peer'] = 99; set_error_handler('h3'); }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function h3($n, $m) { echo 'N:', $n, ';'; return true; }
function done() { echo 'S:', $GLOBALS['x'] === 5, ':', $GLOBALS['peer'] === 99, ':', $GLOBALS['weak']->get() === null, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100; $second = new Exception('supplied local');
try { $v = ++$x; echo 'R;'; }
catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $x === true, ':', $peer === 99, ':', $v === 100, ':', $weak->get() === null, ';'; }
finally { echo 'F;'; }
echo 'END;'; $x = 5; $probe = false; ++$probe;
echo 'A:', $peer === 99, ':', get_error_handler() === 'h3', ';';
''',
}
