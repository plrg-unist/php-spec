"""Warning-handler exit before captured scalar restoration."""

STATUS = 'explicit_exit'

CASES = {
    'handler-exit-bool': b'''<?php
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['x'] === 41, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$x = true; $v = 100;
try { $v = ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C;'; } finally { echo 'F;'; }
echo 'END;';
''',
    'handler-exit-bool-local-destructor': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ':', $GLOBALS['x'] === true, ';'; } }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$x = true; $v = 100;
$v = ++$x; echo 'END;';
''',
    'handler-exit-bool-kept-cell-rebind': b'''<?php
function done() { echo 'S:', $GLOBALS['x'] === 73, ':', $GLOBALS['peer'] === 73, ':', $GLOBALS['keep'] === true, ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] =& $GLOBALS['peer']; $GLOBALS['keep'] = 41; exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$x = true; $keep =& $x; $peer = 73; $v = 100;
$v = ++$x; echo 'END;';
''',
    'handler-exit-bool-unset': b'''<?php
function done() { echo 'S:', isset($GLOBALS['x']), ':'; if (isset($GLOBALS['x'])) { echo $GLOBALS['x'] === true; } else { echo 'missing'; } echo ':', $GLOBALS['v'] === 100, ';'; }
function h($n, $m) { echo 'H:', $n, ';'; unset($GLOBALS['x']); exit('E;'); }
register_shutdown_function('done'); set_error_handler('h');
$x = true; $v = 100;
$v = ++$x; echo 'END;';
''',
}
