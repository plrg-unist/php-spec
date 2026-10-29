<?php
class Captured120 {
    public function __destruct() { echo "D|"; }
}
class InvalidIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed {
        global $callback, $captured;
        echo "K|";
        $callback = null;
        $captured = null;
        return false;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$captured = new Captured120();
$callback = function ($item) use ($captured) { echo "BAD|"; };
$iterator = new InvalidIterator120();
try { $callback(...$iterator); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
