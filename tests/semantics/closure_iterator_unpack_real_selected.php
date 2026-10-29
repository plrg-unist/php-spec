<?php
class SelectedIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed {
        global $callback;
        echo "K|";
        $callback = function ($item) { echo "BAD|"; };
        return 0;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$tag = 'old';
$callback = function ($item) use ($tag) { echo "F|", $tag, "|", $item, "|"; };
$iterator = new SelectedIterator120();
$callback(...$iterator);
echo "A|";
