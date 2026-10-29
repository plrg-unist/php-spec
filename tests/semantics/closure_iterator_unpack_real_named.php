<?php
class NamedIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 2; }
    public function current(): mixed { echo "C|"; return $this->index === 0 ? 22 : 11; }
    public function key(): mixed { echo "K|"; return $this->index === 0 ? 'second' : 'first'; }
    public function next(): void { echo "N|"; $this->index++; }
}
$callback = function ($first, $second) { echo "F|", $first, "|", $second, "|"; };
$iterator = new NamedIterator120();
$callback(...$iterator);
