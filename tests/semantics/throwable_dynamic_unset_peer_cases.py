"""Current independent dynamic-deletion originals; failed setup stays external."""
CASES = {
    'dynamic-unset-count-key-reinsert-cow': br'''<?php
#[AllowDynamicProperties]
class Packet161 {
    public function unused(): void { echo 'BAD|'; }
}
function outer161($x): Exception { return new Exception('outer', 7); }
$left = new Packet161; $right = new Packet161;
$left->gone = 9; $left->first = 1; $left->tail = 9;
$right->gone = 9; $right->first = 2; $right->tail = 0;
unset($left->gone, $right->gone);
$a = outer161($left); $b = outer161($right); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$left->gone = 99; echo 'C|', $a <=> $b, ':', $b <=> $a, '|';
$right->other = 0; echo 'K|', $a <=> $b, ':', $b <=> $a, '|';
$left->first = 2; echo 'T|', $a <=> $b, ':', $b <=> $a, '|';
$left->tail = 0; echo 'M|', $a <=> $b, ':', $b <=> $a, '|';
unset($left->gone); echo 'D|', $a <=> $b, ':', $b <=> $a, '|';
$left->other = 0; echo 'E|', $a <=> $b, '|';
$view = (array)$left; $snapshot = $view; unset($left->first);
echo 'V|', $snapshot['first'], ':', (int)isset($view['gone']), ':', $a <=> $b, '|';
$left->first = 2; $left->tail = 1; $right->first = 9;
echo 'R|', $a <=> $b, ':', $b <=> $a, '|';
$snapshot['first'] = 77; echo 'S|', $snapshot['first'], ':', $view['first'], '|';
''',
    'dynamic-unset-alias-cycle-owners-v2': br'''<?php
#[AllowDynamicProperties]
class Packet161 {
    public function __get($name) { echo 'BAD|'; return 0; }
}
readonly class Other161 { private int $uninitialized; }
function outer161($x): TypeError { return new TypeError('outer', 7); }
$left = new Packet161; $right = new Packet161;
$left->gone = 1; $right->gone = 1; unset($left->gone, $right->gone);
$live = [1]; $snapshot = $live; $left->data = []; $left->data =& $live; $right->data = [2];
$left->tail = 9; $right->tail = 0;
$a = outer161($left); $b = outer161($right); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
foreach ($left as $ignored) {} foreach ($right as $ignored) {} $view = (array)$left;
$snapshot[0] = 99; $live = [3]; echo 'C|', $snapshot[0], ':', $view['data'][0], ':', $a <=> $b, '|';
unset($left->tail); echo 'D|', $a <=> $b, ':', $view['tail'], '|';
$left->tail = 0; $discard = new stdClass; $weakDiscard = WeakReference::create($discard);
$left->gone = $discard; $discard = null; unset($left->gone);
echo 'U|', (int)($weakDiscard->get() === null), '|';
$live = [$left]; $right->data = [$right]; $left->stop = 0;
echo 'S|', $a <=> $b, ':', $b <=> $a, '|';
unset($left->stop); $hold = 'hold'; echo 'X|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right->data = [$left]; echo 'R|', $a <=> $b, ':', (int)($a == $b), '|';
$live = []; $right->data = []; $weak = WeakReference::create($left); $saved = $a->getTrace(); $a = null; $left = null;
echo 'H|', (int)($weak->get() !== null), '|';
$saved[0]['args'][0] = null; echo 'D|', (int)($weak->get() === null), '|';
$live = [4]; echo 'A|', $view['data'][0], ':', $snapshot[0], '|';
$other = new Other161; $c = outer161($right); $d = outer161($other); echo 'K|', $c <=> $d, ':', $d <=> $c, '|';
''',
}
