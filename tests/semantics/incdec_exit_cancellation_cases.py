"""Supplied cleanup Throwables cancel warning-handler exit."""
STATUS = 'normal'
EXIT_CODES = {'cleanup-throw-int23': 23}

CASES = {
    'cleanup-throw-int23': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['second']; } }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit(23); }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = true; $v = 100;
try { $v = ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $x === true, ':', $v === 100, ':', $e->getPrevious() === null, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'cleanup-throw-null': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['second']; } }
function done() { echo 'S:', $GLOBALS['x'] === null, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = null; $v = 100;
try { $v = --$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $x === null, ':', $v === 100, ':', $e->getPrevious() === null, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'cleanup-throw-string-post': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['second']; } }
function done() { echo 'S:', $GLOBALS['x'] === 41, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = 'foo'; $v = 100;
try { $v = $x++; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $x === 41, ':', $v === 100, ':', $e->getPrevious() === null, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'cleanup-throw-kept-cell-rebind': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['keep'] === 41, ':', $GLOBALS['x'] === 73, ';'; throw $GLOBALS['second']; } }
function done() { echo 'S:', $GLOBALS['x'] === 73, ':', $GLOBALS['keep'] === true, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] =& $GLOBALS['peer']; $GLOBALS['keep'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $peer = 73; $x = true; $keep =& $x; $v = 100;
try { $v = ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $x === 73, ':', $peer === 73, ':', $keep === true, ':', $v === 100, ':', $e->getPrevious() === null, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
}
