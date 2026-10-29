<?php
class StaticLeaf126 implements Iterator {
    public $index = 0;
    public function rewind(): void { echo 'R|'; $this->index = 0; }
    public function valid(): bool { return $this->index < 2; }
    public function current(): mixed { return $this->index === 0 ? 'first' : 'second'; }
    public function key(): mixed { return $this->index === 0 ? '8' : 'tail'; }
    public function next(): void { ++$this->index; }
    public function __destruct() { echo 'D|leaf|'; }
}
class StaticAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|'; return new StaticLeaf126(); }
    public function __destruct() { echo 'D|aggregate|'; }
}
class StaticParent126 {
    public static function __callStatic(string $name, array $arguments) {
        echo 'H|', $name, '|', $arguments[0], '|', $arguments['tail'], '|';
        return 40;
    }
}
class StaticChild126 extends StaticParent126 {}
$answer = StaticChild126::missing(...new StaticAggregate126());
echo 'A|', $answer, '|';
