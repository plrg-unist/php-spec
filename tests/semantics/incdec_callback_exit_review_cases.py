"""Independent owning callback exit lifetime and borrowed-target originals."""
CASES = {
    'review-callback-exit-retained-registry': b'''<?php
class H {
    function __invoke($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
}
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['weak']->get() !== null, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100;
try { $v = ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-callback-exit-surviving-owner': b'''<?php
class H {
    function __invoke($n, $m) { echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === true, ';'; $GLOBALS['x'] = 99; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() {
    $probe = false; ++$probe;
    echo 'S1:', $GLOBALS['x'] === true, ':', $GLOBALS['weak']->get() !== null, ';';
    unset($GLOBALS['keeper']);
    echo 'S2:', $GLOBALS['x'] === 99, ':', $GLOBALS['weak']->get() === null, ':', $GLOBALS['v'] === 100, ';';
}
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); $keeper = $h; set_error_handler($h); unset($h);
$x = true; $v = 100;
try { $v = ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-callback-exit-null-borrowed-rebind': b'''<?php
class H {
    function __invoke($n, $m) { echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['keep'] = 41; exit('E;'); }
    function __destruct() {
        echo 'D:', $GLOBALS['keep'] === 41, ';';
        $GLOBALS['x'] =& $GLOBALS['peer']; $GLOBALS['keep'] = 99; set_error_handler('h3');
    }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function h3($n, $m) { echo 'N:', $n, ';'; return true; }
function done() {
    $probe = false; ++$probe;
    echo 'S:', $GLOBALS['keep'] === null, ':', $GLOBALS['x'] === 73, ':', $GLOBALS['peer'] === 73, ':', $GLOBALS['weak']->get() === null, ':', $GLOBALS['v'] === 100, ';';
}
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = null; $keep =& $x; $peer = 73; $v = 100;
try { $v = --$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-callback-exit-owner-clears-registry': b'''<?php
class H {
    function __invoke($n, $m) { echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 99; set_error_handler(null); }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() { echo 'S:', get_error_handler() === null, ':', $GLOBALS['weak']->get() === null, ':', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); $h = new H; $weak = WeakReference::create($h); set_error_handler($h); unset($h);
$x = true; $v = 100;
try { $v = ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
}
STATUS = 'explicit_exit'
