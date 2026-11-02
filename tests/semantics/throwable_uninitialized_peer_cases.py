"""Frozen COMP160 independent originals; normal and boundary provenance stay separate."""
CASES = {
    'initial-hole-inline-cache-clone': br'''<?php
class Packet160 {
    public int $hole;
    public int $tail = 0;
    public function unused(): void { echo 'BAD|'; }
}
function outer160($x): Exception { return new Exception('outer', 7); }
$left = new Packet160; $right = new Packet160; $right->hole = 0;
$a = outer160($left); $b = outer160($right); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$view = (array)$left; $snapshot = $view; $view['extra'] = 9;
echo 'P|', (int)isset($snapshot['hole']), ':', $snapshot['tail'], ':', $a <=> $b, '|';
foreach ($left as $ignored) {} echo 'L|', $a <=> $b, ':', $b <=> $a, '|';
foreach ($right as $ignored) {} echo 'T|', $a <=> $b, ':', $b <=> $a, '|';
unset($right->hole); echo 'U|', $a <=> $b, ':', $b <=> $a, '|';
$copy = clone $left; $c = outer160($left); $d = outer160($copy); echo 'C|', $c <=> $d, '|';
$copy->hole = 7; echo 'D|', $c <=> $d, ':', $d <=> $c, '|';
$left->hole = 2; echo 'I|', $a <=> $b, ':', $b <=> $a, '|';
$viewCopy = (array)$copy; echo 'V|', (int)isset($snapshot['hole']), ':', (int)isset($viewCopy['hole']), ':', $snapshot['tail'], '|';
''',
    'private-hole-alias-cycle-owners': br'''<?php
class Packet160 {
    private int $hole;
    protected $payload = 0;
    public function init(int $value): void { $this->hole = $value; }
    public function clear(): void { unset($this->hole); }
    public function bind(&$value): void { $this->payload =& $value; }
    public function put($value): void { $this->payload = $value; }
    public function __get($name) { echo 'BAD|'; return 0; }
}
readonly class Other160 { private int $uninitialized; }
function outer160($x): TypeError { return new TypeError('outer', 7); }
$left = new Packet160; $right = new Packet160; $live = [1]; $snapshot = $live;
$left->bind($live); $right->put([2]); $a = outer160($left); $b = outer160($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$left->init(1); echo 'I|', $a <=> $b, ':', $b <=> $a, '|';
$left->clear(); echo 'U|', $a <=> $b, '|';
foreach ($left as $ignored) {} foreach ($right as $ignored) {} $view = (array)$left;
$snapshot[0] = 99; $live = [3]; echo 'C|', $snapshot[0], ':', $live[0], ':', $a <=> $b, '|';
$live = [$left]; $right->put([$right]); $left->init(1); echo 'S|', $a <=> $b, ':', $b <=> $a, '|';
$left->clear(); $hold = 'hold'; echo 'X|'; $site = __LINE__ + 1;
try { try { $hold = $a <=> $b; echo 'BAD|'; } finally { echo 'F|', $hold, '|'; } }
catch (Error $e) { echo get_class($e), ':', $e->getMessage(), ':', (int)($e->getFile() === __FILE__), ':', (int)($e->getLine() === $site), ':', (int)($e->getTrace() === []), '|'; }
$right->put([$left]); echo 'R|', $a <=> $b, ':', (int)($a == $b), '|';
$live = []; $right->put([]); $weak = WeakReference::create($left); $saved = $a->getTrace(); $a = null; $left = null;
echo 'H|', (int)($weak->get() !== null), '|';
$saved[0]['args'][0] = null; echo 'D|', (int)($weak->get() === null), '|';
$live = [4]; echo 'A|', $live[0], ':', $snapshot[0], '|';
$other = new Other160; $c = outer160($right); $d = outer160($other); echo 'K|', $c <=> $d, ':', $d <=> $c, '|';
''',
    'initial-hole-stringable-control': br'''<?php
class Value160 {
    public function __toString(): string { echo 'G|'; return 'x'; }
}
class Packet160 { public int $hole; public $value; }
$left = new Packet160; $right = new Packet160; $left->value = new Value160; $right->value = 'x';
foreach ($left as $ignored) {} foreach ($right as $ignored) {}
echo 'B|', $left <=> $right, '|';
''',
}
