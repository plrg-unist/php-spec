<?php
class ArrowIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 8; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$tag = 'old';
$callback = fn($item) => $tag . $item;
$iterator = new ArrowIterator120();
echo $callback(...$iterator), "|";
