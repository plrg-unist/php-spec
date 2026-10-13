"""Independent parent cleanup order and retired temporary ownership probes."""

CASES = {
    'review-parent-exit-two-retired': b'''<?php
class First { function __destruct() { echo 'A:', $GLOBALS['x'] === true, ';'; $GLOBALS['wa'] = WeakReference::create($this); $GLOBALS['x'] = 99; } }
class Last { function __destruct() { echo 'B:', $GLOBALS['x'] === 99, ';'; $GLOBALS['wb'] = WeakReference::create($this); throw $GLOBALS['second']; } }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
function done() { echo 'S:', $GLOBALS['x'] === 99, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = true; $v = 100;
try { $v = (new First) === ((new Last) === ++$x); echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $x === 99, ':', $v === 100, ':', $wa->get() === null, ':', $wb->get() === null, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-parent-exit-alias-retirement': b'''<?php
class Kept { function __construct() { $GLOBALS['keep'] = $this; $GLOBALS['wk'] = WeakReference::create($this); } function __destruct() { echo 'K:', $GLOBALS['x'] === true, ';'; } }
class Last { function __destruct() { echo 'B:', $GLOBALS['wk']->get() !== null, ';'; unset($GLOBALS['keep']); echo 'U:', $GLOBALS['wk']->get() === null, ';'; throw $GLOBALS['second']; } }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ':', $GLOBALS['wk']->get() === null, ';'; }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = true; $v = 100;
try { $v = (new Kept) === ((new Last) === ++$x); echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $x === true, ':', $v === 100, ':', $wk->get() === null, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-parent-exit-empty-postdec': b'''<?php
class ParentT { function __destruct() { echo 'T:', $GLOBALS['x'] === 41, ';'; $GLOBALS['x'] = 73; throw $GLOBALS['second']; } }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
function done() { echo 'S:', $GLOBALS['x'] === 73, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler('h');
$second = new Exception('second'); $x = ''; $v = 100;
try { $v = (new ParentT) === $x--; echo 'R;'; } catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === null, ':', $x === 73, ':', $v === 100, ';'; } finally { echo 'F;'; }
echo 'END;';
''',
    'review-parent-exit-finally-pending': b'''<?php
class ParentT { function __destruct() { echo 'T:', $GLOBALS['x'] === true, ';'; throw $GLOBALS['second']; } }
function h($n, $m) { echo 'H:', $n, ';'; $GLOBALS['x'] = 41; exit('E;'); }
function done() { echo 'S:', $GLOBALS['x'] === true, ':', $GLOBALS['v'] === 100, ';'; }
register_shutdown_function('done'); set_error_handler('h');
$first = new Exception('first'); $second = new Exception('second'); $x = true; $v = 100;
try { try { throw $first; } finally { $v = (new ParentT) === ++$x; echo 'R;'; } }
catch (Throwable $e) { echo 'C:', $e === $second, ':', $e->getPrevious() === $first, ':', $e->getPrevious() === null, ':', $x === true, ':', $v === 100, ';'; }
finally { echo 'F;'; }
echo 'END;';
''',
}
