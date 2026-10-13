"""Owning warning-handler callback release before the scalar helper finishes."""
CASES = {
    'callback-exit-original': b"<?php\nclass H {\n    function __invoke($n, $m) { echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit('E;'); }\n    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; }\n}\nfunction h2($n, $m) { echo 'B:', $n, ';'; return true; }\nfunction done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }\nregister_shutdown_function('done'); set_error_handler(new H);\n$x = true; $v = 100;\n$v = ++$x; echo 'END;';\n",
    'callback-exit-bool-owner-write': b'''<?php
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 99, ';'; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; $GLOBALS['x'] = 99; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() { $probe = false; ++$probe; echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'callback-exit-empty-owner-write': b'''<?php
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === 73, ':', $GLOBALS['x'] === '', ';'; } }
class H {
    function __invoke($n, $m) { echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 73; }
}
function h2($n, $m) { return true; }
function done() { echo 'S:', $GLOBALS['x'] === 73, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler(new H);
$x = ''; $v = 100;
try { $v = (new ParentT) === $x--; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'callback-exit-int23-owner-throw': b'''<?php
class ParentT { function __destruct() { echo 'P:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; } }
class H {
    function __invoke($n, $m) { $local = new Local; echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit(23); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 99; throw $GLOBALS['second']; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() { $probe = false; ++$probe; echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['weak']->get() === null, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$second = new Exception('second'); $x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $x === true, ':', $v === 100, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
}
STATUS = 'explicit_exit'
STATUSES = {'callback-exit-int23-owner-throw': 'normal'}
EXIT_CODES = {'callback-exit-int23-owner-throw': 23}
