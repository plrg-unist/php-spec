"""Pending-exit caller cleanup cancellation and post-commit writes."""
STATUS = 'normal'
EXIT_CODES = {'parent-exit-int23-write': 23}

CASES = {
    'parent-exit-original': b'''<?php
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
    'parent-exit-int23-write': b'''<?php
class ParentT { function __destruct() { echo 'T:', $GLOBALS['x'] === true, ';'; $GLOBALS['x'] = 99; throw $GLOBALS['second']; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; } }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit(23); }
function done() { echo 'S:', $GLOBALS['x'] === 99, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $x === 99, ':', $v === 100, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'parent-exit-kept-cell-write': b'''<?php
class ParentT { function __destruct() { echo 'T:', $GLOBALS['keep'] === true, ':', $GLOBALS['x'] === 73, ';'; $GLOBALS['keep'] = 99; throw $GLOBALS['second']; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['keep'] === 41, ':', $GLOBALS['x'] === 73, ';'; } }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] =& $GLOBALS['peer']; $GLOBALS['keep'] = 41; exit('E;'); }
function done() { echo 'S:', $GLOBALS['x'] === 73, ':', $GLOBALS['keep'] === 99, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $peer = 73; $x = true; $keep =& $x; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $x === 73, ':', $peer === 73, ':', $keep === 99, ':', $v === 100, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'parent-exit-function-catch': b'''<?php
class ParentT { function __destruct() { echo 'T:', $GLOBALS['x'] === true, ';'; $GLOBALS['x'] = 99; throw $GLOBALS['second']; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; } }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
function done() { echo 'S:', $GLOBALS['x'] === 99, ':', $GLOBALS['v'] === 100, ';'; }
function run_case() {
    $x = true; $GLOBALS['x'] =& $x; $v =& $GLOBALS['v'];
    try { $v = (new ParentT) === ++$x; echo 'R;'; }
    catch (Throwable $e) { echo 'C:', $e === $GLOBALS['second'], ':', $e->getPrevious() === null, ':', $x === 99, ':', $v === 100, ';'; }
    finally { echo 'F;'; }
    return $x;
}
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $v = 100;
$r = run_case(); echo 'RET:', $r === 99, ';END;';
''',
}
