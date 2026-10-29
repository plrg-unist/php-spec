"""Frozen nonpublic cached clone and per-copy type-source ownership."""

CASES = {
    'nonpublic-cached-clone-types': br'''<?php
class Plain159 {
    private array $data = [];
    protected int $tail = 0;
    public function bind(array &$value): void { $this->data =& $value; }
    public function tail(int $value): void { $this->tail = $value; }
}
class Callback159 {
    private int $data = 1;
    protected int $tail = 0;
    public function __clone(): void { echo 'G|'; $this->data = 2; }
}
function outer159($x): Exception { return new Exception('outer', 7); }
$live = [1]; $original = new Plain159; $original->bind($live); foreach ($original as $ignored) {}
$copy = clone $original; $a = outer159($original); $b = outer159($copy);
echo 'B|', $a <=> $b, ':', (int)($original === $copy), '|';
$view = (array)$original; $live = [2]; echo 'A|', $a <=> $b, ':', $live[0], '|';
$original->tail(7); echo 'T|', $a <=> $b, ':', $b <=> $a, '|';
$weak = WeakReference::create($original); $original = null; $a = null; echo 'H|', (int)($weak->get() === null), '|';
try { $live = 3; echo 'BAD|'; } catch (TypeError $e) { echo 'C|', get_class($e), ':', $live[0], '|'; }
$weakCopy = WeakReference::create($copy); $copy = null; $b = null; echo 'D|', (int)($weakCopy->get() === null), '|';
$live = 3; echo 'R|', $live, '|';
$source = new Callback159; foreach ($source as $ignored) {} $cloned = clone $source;
$c = outer159($source); $d = outer159($cloned); echo 'K|', $c <=> $d, ':', $d <=> $c, '|';
''',
}
