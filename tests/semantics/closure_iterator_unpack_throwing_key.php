<?php
class ThrowingIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed {
        global $callback;
        echo "K|";
        $callback = null;
        throw new Exception('stop', 19);
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$callback = function ($item) { echo "BAD|"; };
$iterator = new ThrowingIterator120();
try { $callback(...$iterator); }
catch (Exception $error) { echo "E|", $error->getCode(), "|"; }
echo "A|";
