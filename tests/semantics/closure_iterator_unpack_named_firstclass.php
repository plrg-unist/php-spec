<?php
function firstclass120($item) { echo "F|", $item, "|"; }
function other120($item) { echo "BAD|"; }
class FirstClassIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 9; }
    public function key(): mixed {
        global $callback;
        echo "K|";
        $callback = other120(...);
        return 0;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$callback = firstclass120(...);
$iterator = new FirstClassIterator120();
$callback(...$iterator);
echo "A|";
