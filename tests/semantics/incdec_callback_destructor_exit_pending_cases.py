"""Pending user Throwables overridden by raw callback-destructor exit."""
CASES = {
    'callback-dexit-pending-original': b'''<?php
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
    'callback-dexit-pending-empty-string': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['second']; } }
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === 73, ':', $GLOBALS['x'] === -1, ':', $GLOBALS['v'] === 100, ';'; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 73; set_error_handler('h3'); exit('D-E;'); echo 'D-END;'; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function h3($n, $m) { echo 'N:', $n, ';'; return true; }
function done() {
    $probe = false; ++$probe;
    echo 'S:', $GLOBALS['x'] === 73, ':', $GLOBALS['x'] === -1, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ':', $GLOBALS['second']->getPrevious() === null, ';';
}
register_shutdown_function('done'); $second = new Exception('second');
$h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = ''; $v = 100;
try { $v = (new ParentT) === $x--; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'callback-dexit-pending-null-rebind': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['keep'] === 41, ':', $GLOBALS['x'] === 73, ';'; throw $GLOBALS['second']; } }
class ParentT { function __destruct() { echo 'P:', $GLOBALS['keep'] === null, ':', $GLOBALS['x'] === 73, ':', $GLOBALS['v'] === 100, ';'; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['keep'] = 41; $GLOBALS['x'] =& $GLOBALS['peer']; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['keep'] === 41, ':', $GLOBALS['x'] === 73, ';'; $GLOBALS['keep'] = 99; set_error_handler('h3'); exit(17); echo 'D-END;'; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function h3($n, $m) { echo 'N:', $n, ';'; return true; }
function done() {
    $probe = false; ++$probe;
    echo 'S:', $GLOBALS['keep'] === null, ':', $GLOBALS['x'] === 73, ':', $GLOBALS['peer'] === 73, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ':', $GLOBALS['second']->getPrevious() === null, ';';
}
register_shutdown_function('done'); $second = new Exception('second');
$h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = null; $keep =& $x; $peer = 73; $v = 100;
try { $v = (new ParentT) === --$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
}
STATUS = 'explicit_exit'
EXIT_CODES = {'callback-dexit-pending-original': 17, 'callback-dexit-pending-empty-string': 23, 'callback-dexit-pending-null-rebind': 17}
