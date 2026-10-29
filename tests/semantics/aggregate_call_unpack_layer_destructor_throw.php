<?php
class ThrowLayerLeaf126 implements Iterator {
    public function rewind(): void { echo 'R|'; }
    public function valid(): bool { echo 'V|'; return false; }
    public function current(): mixed { echo 'BAD|'; return null; }
    public function key(): mixed { echo 'BAD|'; return null; }
    public function next(): void { echo 'BAD|'; }
    public function __destruct() { echo 'D|leaf|'; }
}
class ThrowLayerInner126 implements IteratorAggregate {
    public function getIterator(): Traversable {
        global $receiver;
        echo 'G|inner|';
        $receiver = null;
        return new ThrowLayerLeaf126();
    }
    public function __destruct() { global $exception; echo 'D|inner|'; throw $exception; }
}
class ThrowLayerOuter126 implements IteratorAggregate {
    public function getIterator(): Traversable { echo 'G|outer|'; return new ThrowLayerInner126(); }
    public function __destruct() { echo 'D|outer|'; }
}
class ThrowLayerTarget126 {
    public function take() { echo 'BAD|'; }
    public function __destruct() { echo 'D|target|'; }
}
$receiver = new ThrowLayerTarget126();
$exception = new Exception('supplied');
try { $receiver->take(...new ThrowLayerOuter126()); }
catch (Exception $error) { echo 'E|', $error === $exception ? 1 : 0, '|'; }
echo 'Z|';
