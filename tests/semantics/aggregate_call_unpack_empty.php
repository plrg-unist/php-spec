<?php
class EmptyLeaf126 implements Iterator {
    public function rewind(): void { echo 'R|'; }
    public function valid(): bool { return false; }
    public function current(): mixed { echo 'BAD|'; return null; }
    public function key(): mixed { echo 'BAD|'; return null; }
    public function next(): void { echo 'BAD|'; }
    public function __destruct() { echo 'D|leaf|'; }
}
function emptyGenerator126(): Generator { echo 'Y|'; if (false) { yield 0; } }
class EmptyIteratorAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|iterator|'; return new EmptyLeaf126(); }
    public function __destruct() { echo 'D|iterator-aggregate|'; }
}
class EmptyGeneratorAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|generator|'; return emptyGenerator126(); }
    public function __destruct() { echo 'D|generator-aggregate|'; }
}
class EmptyMagic126 {
    public function __call(string $name, array $arguments) { echo 'H|', $name, '|', $arguments === [] ? 1 : 0, '|'; return 45; }
}
$target = new EmptyMagic126();
$answer = $target->missing(...new EmptyIteratorAggregate126(), ...new EmptyGeneratorAggregate126());
echo 'A|', $answer, '|';
