<?php
class OwnedCaptured122 {
    public function __destruct() { echo "D|captured|"; }
}
class OwnedClosureIterator122 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed {
        global $callback, $captured;
        echo "K|"; $callback = null; $captured = null; return false;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
function ownedClosureInput122() { echo "P|"; return new OwnedClosureIterator122(); }
$captured = new OwnedCaptured122();
$callback = function ($item) use ($captured) { echo "BAD|"; };
try { $callback(...ownedClosureInput122()); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
