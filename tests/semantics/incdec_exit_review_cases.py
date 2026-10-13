"""Independent exit restoration and callback-cleanup counterexamples."""

STATUS = 'explicit_exit'
EXIT_CODES = {'review-exit-null-status23': 23}

CASES = {
    'review-exit-null-status23': b'''<?php
function done() { echo 'S:', $GLOBALS['x'] === null, ':', $GLOBALS['keep'] === null, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit(23); }
register_shutdown_function('done'); set_error_handler('h');
$x = null; $keep =& $x; $v = 100;
try { $v = --$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-exit-empty-postdec': b'''<?php
function done() { echo 'S:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === '', ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$x = ''; $v = 100;
$v = $x--; echo 'END;';
''',
    'review-exit-string-helper': b'''<?php
function done() { echo 'S:', $GLOBALS['x'] === 41, ':', $GLOBALS['v'] === 100, ';'; }
function bye() { echo 'B;'; $GLOBALS['x'] = 41; exit('E;'); }
function h($n, $m) { echo 'H:', $n, ';'; try { bye(); } finally { echo 'HF;'; } }
register_shutdown_function('done'); set_error_handler('h');
$x = 'Ba!'; $v = 100;
try { $v = $x++; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-exit-caller-destructor': b'''<?php
class Outer { function __destruct() { echo 'O:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 41, ';'; } }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
function run() { global $x, $v; $outer = new Outer; $v = ++$x; echo 'R;'; }
register_shutdown_function('done'); set_error_handler('h');
$x = true; $v = 100;
run(); echo 'END;';
''',
    'review-exit-registry-replacement': b'''<?php
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() { $probe = false; ++$probe; echo 'S:', $GLOBALS['x'] === true, ':', $probe === false, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$x = true; $v = 100;
$v = ++$x; echo 'END;';
''',
    'review-exit-callable-owner': b'''<?php
class H {
    function __invoke($n, $m) { echo 'H:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; exit('E;'); }
    function __destruct() { echo 'D:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; }
}
function h2($n, $m) { echo 'B:', $n, ';'; return true; }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler(new H);
$x = true; $v = 100;
$v = ++$x; echo 'END;';
''',
    'review-exit-handler-local-throw': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; throw $GLOBALS['second']; } }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = true; $v = 100;
try { $v = ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $x === true, ':', $v === 100, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-exit-nested-handlers': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ':', $GLOBALS['y'] === false, ';'; } }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['y'] === false, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['w'] === 200, ';'; }
function h2($n, $m) { echo 'B:', $n, ';'; $GLOBALS['y'] = 73; exit('E;'); }
function h1($n, $m) { global $y, $w; $local = new Local; echo 'A:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; $w = ++$y; echo 'HR;'; }
register_shutdown_function('done'); set_error_handler('h1');
$x = true; $y = false; $v = 100; $w = 200;
try { $v = ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-exit-parent-temporary': b'''<?php
class T { function __destruct() { echo 'T:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 41, ';'; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; } }
function done() { echo 'S:', $GLOBALS['x'] === true, ';'; }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$x = true;
(new T) === ++$x; echo 'END;';
''',
    'review-exit-parent-throw': b'''<?php
class T { function __destruct() { echo 'T:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['second']; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; } }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
function uncaught($e) { echo 'U:', $e === $GLOBALS['second'], ':', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h'); set_exception_handler('uncaught');
$second = new Exception('second'); $x = true; $v = 100;
try { $v = (new T) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $x === true, ':', $v === 100, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
}

BOUNDARIES = {
    'review-exit-callable-owner': 'increment/decrement warning exit continuation',
    'review-exit-handler-local-throw': 'increment/decrement warning exit cleanup throw',
    'review-exit-parent-throw': 'increment/decrement warning exit parent cleanup throw',
}
