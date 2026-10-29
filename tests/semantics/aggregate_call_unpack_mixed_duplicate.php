<?php
class MixedLeaf126 implements Iterator {
    public $index = 0;
    public function rewind(): void { echo 'R|'; }
    public function valid(): bool { return $this->index < 1; }
    public function current(): mixed { echo 'C|'; return 18; }
    public function key(): mixed { return 'same'; }
    public function next(): void { echo 'N|'; ++$this->index; }
    public function __destruct() { echo 'D|leaf|'; }
}
function mixedGenerator126(): Generator { try { echo 'Y|'; yield 'same' => 19; echo 'BAD|'; } finally { echo 'F|'; } }
class MixedIteratorAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|iterator|'; return new MixedLeaf126(); }
    public function __destruct() { echo 'D|iterator-aggregate|'; }
}
class MixedGeneratorAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|generator|'; return mixedGenerator126(); }
    public function __destruct() { echo 'D|generator-aggregate|'; }
}
class MixedMagic126 {
    public static function __callStatic(string $name, array $arguments) { echo 'BAD|'; }
}
try { MixedMagic126::missing(...new MixedIteratorAggregate126(), ...['other' => 20], ...new MixedGeneratorAggregate126()); }
catch (Error $error) { echo 'E|', $error->getMessage(), '|'; }
echo 'Z|';
