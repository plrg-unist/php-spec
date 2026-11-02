"""Declared undefined slots retain physical positions and real cache buckets."""

CASES = {
    'declared-holes-physical-cache-count': br'''<?php
class Packet160 {
    public int $first;
    private int $middle;
    protected int $last;
    public function middle(int $value): void { $this->middle = $value; }
    public function last(int $value): void { $this->last = $value; }
    public function clear(): void { unset($this->first); }
    public function __get($name) { echo 'BAD|'; return 0; }
    public function __isset($name): bool { echo 'BAD|'; return false; }
}
function outer160($x): Exception { return new Exception('outer', 7); }
$left = new Packet160; $right = new Packet160; $left->middle(9); $left->last(9); $right->first = 1;
$a = outer160($left); $b = outer160($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, ':', (int)($a == $b), ':', (int)($a != $b), ':', (int)($a < $b), ':', (int)($a <= $b), ':', (int)($a > $b), ':', (int)($a >= $b), '|';
$sa = (string)$a; $sb = (string)$b; echo 'W|', (int)($sa === $sb), ':', $a <=> $b, '|';
$va = (array)$left; $vb = (array)$right; $na = 0; $nb = 0;
foreach ($va as $ignored) { $na = $na + 1; } foreach ($vb as $ignored) { $nb = $nb + 1; }
echo 'A|', $na, ':', $nb, ':', $a <=> $b, '|';
foreach ($left as $ignored) {} echo 'C|', $a <=> $b, ':', $b <=> $a, '|';
foreach ($right as $ignored) {} $right->clear(); echo 'U|', $a <=> $b, ':', $b <=> $a, '|';
$left->middle(1); $right->middle(1); $left->last(1); $right->last(1); echo 'E|', $a <=> $b, '|';
echo 'V|', $vb['first'], ':', $na, '|';
''',
    'declared-holes-previous-alias-owners': br'''<?php
class Packet160 {
    private int $hole;
    public array $data = [];
    public function __get($name) { echo 'BAD|'; return 0; }
}
function inner160($x): Exception { return new Exception('inner', 3); }
function severe160($x): ErrorException { global $severity; return new ErrorException('outer', 7, $severity); }
$left = new Packet160; $right = new Packet160; $live = [1]; $snapshot = $live; $left->data =& $live; $right->data = [2];
$p = inner160($left); $q = inner160($right); $a = new Exception('outer', 7, $p); $b = new Exception('outer', 7, $q);
$severity = 9; $c = severe160($left); $severity = 1; $d = severe160($right);
echo 'B|', $a <=> $b, ':', $b <=> $a, ':', $c <=> $d, '|';
$view = (array)$left; foreach ($left as $ignored) {} foreach ($right as $ignored) {}
$snapshot[0] = 99; $live = [3]; echo 'C|', $snapshot[0], ':', $live[0], ':', $a <=> $b, ':', $c <=> $d, '|';
$live = [2]; echo 'E|', $a <=> $b, ':', $c <=> $d, ':', $d <=> $c, '|';
$weak = WeakReference::create($left); $saved = $p->getTrace(); $left = null; $p = null; $c = null; echo 'H|', (int)($weak->get() !== null), '|';
$a = null; echo 'T|', (int)($weak->get() !== null), '|';
$saved[0]['args'][0] = null; echo 'D|', (int)($weak->get() === null), '|';
$live = 5; echo 'R|', $live, ':', $snapshot[0], '|';
''',
    'dynamic-unset-hole-control': br'''<?php
#[AllowDynamicProperties] class Packet160 {}
function outer160($x): Exception { return new Exception('outer', 7); }
$left = new Packet160; $right = new Packet160; $left->gone = 1; unset($left->gone);
$a = outer160($left); $b = outer160($right); echo 'B|', $a <=> $b, '|';
''',
    'readonly-hole-control': br'''<?php
readonly class Packet160 { public int $hole; }
function outer160($x): Exception { return new Exception('outer', 7); }
$left = new Packet160; $right = new Packet160; $a = outer160($left); $b = outer160($right); echo 'B|', $a <=> $b, '|';
''',
}

EXPECTED = {
    'declared-holes-physical-cache-count': b'B|1:1:0:1:0:0:0:0|W|1:1|A|2:1:1|C|-1:1|U|1:-1|E|0|V|1:2|',
    'declared-holes-previous-alias-owners': b'B|-1:1:-1|C|99:3:1:1|E|0:1:-1|H|1|T|1|D|1|R|5:99|',
    'dynamic-unset-hole-control': b'B|0|',
    'readonly-hole-control': b'B|0|',
}
