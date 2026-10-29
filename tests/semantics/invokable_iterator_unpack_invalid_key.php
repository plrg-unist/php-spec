<?php
class InvokableInvalidReceiver121 {
    public function __destruct() { echo "D|receiver|"; }
    public function __invoke($item) { echo "BAD|"; }
}
class InvokableInvalidIterator121 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "D|iterator|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { global $callback; echo "K|"; $callback = null; return false; }
    public function next(): void { echo "N|"; $this->index++; }
}
$callback = new InvokableInvalidReceiver121();
$iterator = new InvokableInvalidIterator121();
try { $callback(...$iterator); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
