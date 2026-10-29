<?php
class ByrefLeaf126 implements Iterator {
    public $index = 0;
    public function rewind(): void { echo 'R|'; $this->index = 0; }
    public function valid(): bool { return $this->index < 2; }
    public function current(): mixed { echo 'C', $this->index, '|'; return $this->index === 0 ? 11 : 12; }
    public function key(): mixed { return $this->index === 0 ? '0' : 'last'; }
    public function next(): void { ++$this->index; }
    public function __destruct() { echo 'D|leaf|'; }
}
class ByrefAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|'; return new ByrefLeaf126(); }
    public function __destruct() { echo 'D|aggregate|'; }
}
function ordinary126(&$first, $last) { $first = 21; echo 'H|', $first, '|', $last, '|'; return 39; }
$aggregate = new ByrefAggregate126();
$answer = ordinary126(...$aggregate);
echo 'A|', $answer, '|';
unset($aggregate);
echo 'Z|';
