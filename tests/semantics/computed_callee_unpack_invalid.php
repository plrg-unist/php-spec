<?php
class ComputedInvalidReceiver123 {
    public function __destruct() { echo "D|receiver|"; }
    public function __invoke($item) { echo "BAD|"; }
}
class ComputedInvalidCurrent123 {
    public function __destruct() { echo "D|current|"; }
}
class ComputedInvalidIterator123 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return new ComputedInvalidCurrent123(); }
    public function key(): mixed { echo "K|"; return false; }
    public function next(): void { echo "N|"; $this->index++; }
}
function computedInvalidCallee123() { echo "F|"; return new ComputedInvalidReceiver123(); }
function computedInvalidInput123() { echo "P|"; return new ComputedInvalidIterator123(); }
try { (computedInvalidCallee123())(...computedInvalidInput123()); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
