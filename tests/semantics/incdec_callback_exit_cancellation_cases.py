"""Owning-handler local cleanup throws cancelling a warning-handler exit."""
CASES = {
    'callback-cancel-bool-int23': b'''<?php
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['first']; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; $GLOBALS['x'] = 99; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() { $probe = false; ++$probe; echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$first = new Exception('supplied local'); $x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; }
catch (Throwable $e) { echo 'C:', $e === $first, ':', $e->getPrevious() === null, ':', $x === true, ':', $v === 100, ':', $weak->get() === null, ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'callback-cancel-empty-postdec': b'''<?php
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === 73, ':', $GLOBALS['v'] === 100, ';'; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['first']; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 73; }
}
function h2($n, $m) { return true; }
function done() { echo 'S:', $GLOBALS['x'] === 73, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$first = new Exception('supplied local'); $x = ''; $v = 100;
try { $v = (new ParentT) === $x--; echo 'R;'; }
catch (Throwable $e) { echo 'C:', $e === $first, ':', $e->getPrevious() === null, ':', $x === 73, ':', $v === 100, ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'callback-cancel-null-both-throw-rebind': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['keep'] === 41, ':', $GLOBALS['x'] === 73, ';'; throw $GLOBALS['first']; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['keep'] = 41; $GLOBALS['x'] =& $GLOBALS['peer']; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['keep'] === 41, ':', $GLOBALS['x'] === 73, ';'; $GLOBALS['keep'] = 99; throw $GLOBALS['second']; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() { $probe = false; ++$probe; echo 'S:', $GLOBALS['keep'] === null, ':', $GLOBALS['x'] === 73, ':', $GLOBALS['peer'] === 73, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$first = new Exception('supplied local'); $second = new Exception('supplied callback');
$x = null; $keep =& $x; $peer = 73; $v = 100;
try { $v = --$x; echo 'R;'; }
catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === $first, ':', $keep === null, ':', $x === 73, ':', $peer === 73, ':', $v === 100, ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
EXIT_CODES = {'callback-cancel-bool-int23': 23}
