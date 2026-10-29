<?php
class OrdinaryLeaf126 implements Iterator {
    public $index = 0;
    public function rewind(): void { echo 'R|'; $this->index = 0; }
    public function valid(): bool { echo 'V', $this->index, '|'; return $this->index < 2; }
    public function current(): mixed {
        global $value;
        echo 'C', $this->index, '|';
        return $value;
    }
    public function key(): mixed {
        global $value;
        echo 'K', $this->index, '|';
        if ($this->index === 0) { $value = 'after-key'; }
        return $this->index === 0 ? 'left' : 'right';
    }
    public function next(): void { echo 'N', $this->index, '|'; ++$this->index; }
    public function __destruct() { echo 'D|leaf|'; }
}
class OrdinaryAggregate126 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $receiver, $aggregate;
        echo 'G|';
        $receiver = null;
        $aggregate = null;
        return new OrdinaryLeaf126();
    }
    public function __destruct() { echo 'D|aggregate|'; }
}
class OrdinaryReceiver126 {
    public function take($left, $right) {
        echo 'H|', $left, '|', $right, '|';
        return 37;
    }
    public function __destruct() { echo 'D|receiver|'; }
}
$value = 'before-key';
$receiver = new OrdinaryReceiver126();
$aggregate = new OrdinaryAggregate126();
$keep = $aggregate;
$answer = $receiver->take(...$aggregate);
echo 'A|', $answer, '|', $value, '|';
unset($keep);
echo 'Z|';
