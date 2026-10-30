"""Deleted dynamic mirrors stay distinct from declared UNDEF buckets."""

CASES = {
    'dynamic-deleted-empty-clone-owners': br'''<?php
#[AllowDynamicProperties] class Empty161 {
    public function __toString(): string { echo 'BAD|'; return 'bad'; }
}
#[AllowDynamicProperties] class Callback161 {
    public function __clone(): void { echo 'G|'; }
}
function outer161($x): Exception { return new Exception('outer', 7); }
$left = new Empty161; $right = new Empty161; $left->gone = 1; foreach ($left as $ignored) {} unset($left->gone);
$a = outer161($left); $b = outer161($right); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$view = (array)$left; $copy = clone $left;
$c = outer161($left); $d = outer161($copy); echo 'C|', $c <=> $d, '|';
$copy->extra = 1; echo 'W|', $c <=> $d, ':', $d <=> $c, '|';
$view['outside'] = 9; $sourceView = (array)$left; echo 'V|', (int)isset($view['extra']), ':', (int)isset($sourceView['outside']), '|';
$weak = WeakReference::create($left); $saved = $a->getTrace(); $left = null; $a = null; $c = null; echo 'H|', (int)($weak->get() !== null), '|';
$saved[0]['args'][0] = null; echo 'D|', (int)($weak->get() === null), '|';
$sourceView['after'] = 2; echo 'A|', $sourceView['after'], '|';
$target = new Callback161; $target->gone = 1; foreach ($target as $ignored) {} unset($target->gone);
echo 'Q|'; $callbackCopy = clone $target;
$e = outer161($target); $f = outer161($callbackCopy); echo 'K|', $e <=> $f, '|';
$callbackCopy->value = 4; echo 'X|', $e <=> $f, '|';
''',
    'declared-deleted-history-clone-alias': br'''<?php
#[AllowDynamicProperties] class Packet161 {
    private int $hole;
    private array $data = [];
    protected int $tail = 0;
    public function bind(&$value): void { $this->data =& $value; }
    public function put(array $value): void { $this->data = $value; }
    public function tail(int $value): void { $this->tail = $value; }
}
function outer161($x): Exception { return new Exception('outer', 7); }
$left = new Packet161; $right = new Packet161; $live = [1]; $snapshot = $live; $left->bind($live); $right->put([2]);
$left->gone = 1; foreach ($left as $ignored) {} unset($left->gone);
$a = outer161($left); $b = outer161($right); echo 'B|', $a <=> $b, ':', $b <=> $a, '|';
$view = (array)$left; $copy = clone $left;
$c = outer161($left); $d = outer161($copy); echo 'C|', $c <=> $d, '|';
$copy->tail(1); echo 'L|', $c <=> $d, ':', $d <=> $c, '|';
$snapshot[0] = 99; $live = [3]; echo 'V|', $snapshot[0], ':', $live[0], ':', $c <=> $d, '|';
try { $live = 5; echo 'BAD|'; } catch (TypeError $error) { echo 'T|', $live[0], '|'; }
$weakLeft = WeakReference::create($left); $left = null; $a = null; $c = null; echo 'H|', (int)($weakLeft->get() === null), '|';
try { $live = 5; echo 'BAD|'; } catch (TypeError $error) { echo 'P|', $live[0], '|'; }
$weakCopy = WeakReference::create($copy); $copy = null; $d = null; echo 'D|', (int)($weakCopy->get() === null), '|';
$live = 5; echo 'R|', $live, ':', $snapshot[0], '|';
''',
    'inherited-deleted-dynamic-control': br'''<?php
#[AllowDynamicProperties] class Base161 {}
class Packet161 extends Base161 { public function unused(): void { echo 'BAD|'; } }
function outer161($x): Exception { return new Exception('outer', 7); }
$left = new Packet161; $right = new Packet161; $left->gone = 1; unset($left->gone); $left->data = 1; $right->data = 2;
$a = outer161($left); $b = outer161($right); echo 'B|', $a <=> $b, '|';
''',
    'nested-readonly-deleted-control': br'''<?php
#[AllowDynamicProperties] class Outer161 {}
readonly class Inner161 { private int $hole; }
function outer161($x): Exception { return new Exception('outer', 7); }
$left = new Outer161; $right = new Outer161; $left->gone = 1; unset($left->gone); $left->data = new Inner161; $right->data = new Inner161;
foreach ($left as $ignored) {} foreach ($right as $ignored) {}
$a = outer161($left); $b = outer161($right); echo 'B|', $a <=> $b, '|';
''',
}

EXPECTED = {
    'dynamic-deleted-empty-clone-owners': b'B|0:0|C|0|W|-1:1|V|0:0|H|1|D|1|A|2|Q|G|K|0|X|-1|',
    'declared-deleted-history-clone-alias': b'B|-1:1|C|0|L|-1:1|V|99:3:-1|T|3|H|1|P|3|D|1|R|5:99|',
    'inherited-deleted-dynamic-control': b'B|-1|',
    'nested-readonly-deleted-control': b'B|0|',
}
