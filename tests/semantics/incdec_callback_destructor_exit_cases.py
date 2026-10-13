"""Exit during raw owning warning-callback destruction."""
CASES = {
    'callback-destructor-exit-bool-int17': b'''<?php
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 99, ':', $GLOBALS['v'] === 100, ';'; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; $GLOBALS['x'] = 99; set_error_handler('h3'); exit(17); echo 'D-END;'; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function h3($n, $m) { echo 'N:', $n, ';'; return true; }
function done() { $probe = false; ++$probe; echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 99, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; }
catch (Throwable $e) { echo 'C;'; }
finally { echo 'F;'; }
echo 'END;';
''',
    'callback-destructor-exit-empty-string': b'''<?php
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === 73, ':', $GLOBALS['x'] === -1, ':', $GLOBALS['v'] === 100, ';'; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 73; set_error_handler('h3'); exit('Z;'); echo 'D-END;'; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function h3($n, $m) { echo 'N:', $n, ';'; return true; }
function done() { $probe = false; ++$probe; echo 'S:', $GLOBALS['x'] === 73, ':', $GLOBALS['x'] === -1, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = ''; $v = 100;
try { $v = (new ParentT) === $x--; echo 'R;'; }
catch (Throwable $e) { echo 'C;'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
STATUS = 'explicit_exit'
EXIT_CODES = {'callback-destructor-exit-bool-int17': 17, 'callback-destructor-exit-empty-string': 23}
