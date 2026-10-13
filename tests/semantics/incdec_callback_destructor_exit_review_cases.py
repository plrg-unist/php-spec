"""Independent callback-destructor exits and borrowed-target/registry observers."""
CASES = {
    'review-callback-dexit-null-rebind': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['keep'] === 41, ':', $GLOBALS['x'] === 73, ';'; } }
class ParentT { function __destruct() { echo 'P:', $GLOBALS['keep'] === null, ':', $GLOBALS['x'] === 73, ':', $GLOBALS['v'] === 100, ';'; } }
class H {
    function __invoke($n, $m) {
        $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2');
        $GLOBALS['keep'] = 41; $GLOBALS['x'] =& $GLOBALS['peer']; exit(23);
    }
    function __destruct() { echo 'D:', $GLOBALS['keep'] === 41, ':', $GLOBALS['x'] === 73, ';'; $GLOBALS['keep'] = 99; exit(17); }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() {
    $probe = false; ++$probe;
    echo 'S:', $GLOBALS['keep'] === null, ':', $GLOBALS['x'] === 73, ':', $GLOBALS['peer'] === 73, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ';';
}
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = null; $keep =& $x; $peer = 73; $v = 100;
try { $v = (new ParentT) === --$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-callback-dexit-cleared-registry': b'''<?php
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ':', get_error_handler() === null, ';'; } }
class H {
    function __invoke($n, $m) { echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ':', $GLOBALS['v'] === 100, ';'; $GLOBALS['x'] = 99; set_error_handler(null); exit('D-E;'); }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ':', get_error_handler() === null, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-callback-dexit-pending-local-throw': b'''<?php
class Local {
    function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['second']; }
}
class ParentT {
    function __destruct() { echo 'P:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 99, ':', $GLOBALS['v'] === 100, ';'; }
}
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 99; exit(17); echo 'D-END;'; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() {
    echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 99, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ':', $GLOBALS['second']->getPrevious() === null, ';';
}
register_shutdown_function('done'); $second = new Exception('second');
$h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
}
STATUS = 'explicit_exit'
EXIT_CODES = {'review-callback-dexit-null-rebind': 17, 'review-callback-dexit-cleared-registry': 23, 'review-callback-dexit-pending-local-throw': 17}
BOUNDARIES = {'review-callback-dexit-pending-local-throw': 'increment/decrement warning exit continuation'}
