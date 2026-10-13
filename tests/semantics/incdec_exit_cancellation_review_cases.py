"""Independent handler-local cancellation, reference and nested-handler probes."""

CASES = {
    'review-exit-cancel-null-late-peer': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ':', $GLOBALS['peer'] === 41, ';'; throw $GLOBALS['second']; } }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; $GLOBALS['peer'] =& $GLOBALS['x']; exit('E;'); }
function done() { echo 'S:', $GLOBALS['x'] === null, ':', $GLOBALS['peer'] === 41, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = null; $v = 100;
try { $v = $x--; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $x === null, ':', $peer === 41, ':', $v === 100, ':', $e->getPrevious() === null, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-exit-cancel-nested-catch': b'''<?php
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ':', $GLOBALS['y'] === 73, ';'; set_error_handler('h3'); throw $GLOBALS['second']; } }
function h3($n, $m) { echo 'D:', $n, ';'; return true; }
function h2($n, $m) { $local = new Local; echo 'B:', $n, ';'; $GLOBALS['y'] = 73; exit('E;'); }
function h1($n, $m) { global $y, $w; echo 'A:', $n, ';'; set_error_handler('h2'); $GLOBALS['x'] = 41; try { $w = ++$y; echo 'HR;'; } catch (Throwable $e) { echo 'C:', $e === $GLOBALS['second'], ':', $y === false, ':', $GLOBALS['x'] === 41, ':', $w === 200, ':', $e->getPrevious() === null, ';'; } finally { echo 'HF;'; } echo 'AR;'; $GLOBALS['x'] = 99; return true; }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['y'] === false, ':', $GLOBALS['v'] === true, ':', $GLOBALS['w'] === 200, ';'; }
register_shutdown_function('done'); set_error_handler('h1');
$second = new Exception('second'); $x = true; $y = false; $v = 100; $w = 200;
try { $v = ++$x; echo 'R:', $v === true, ';'; } catch (Throwable $e) { echo 'OC;'; } finally { echo 'OF;'; }
$probe = false; ++$probe; echo 'END:', $probe === false, ';';
''',
    'review-exit-cancel-parent-owner': b'''<?php
class ParentT { function __destruct() { echo 'T:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; } }
class Local { function __destruct() { echo 'L:', $GLOBALS['x'] === 41, ';'; throw $GLOBALS['second']; } }
function h($n, $m) { $local = new Local; echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = true; $v = 100;
try { $v = (new ParentT) === ++$x; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $x === true, ':', $v === 100, ':', $e->getPrevious() === null, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
}
