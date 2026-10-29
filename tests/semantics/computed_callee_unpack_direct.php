<?php
class ComputedDirectReceiver123 {
    public function __construct() { echo "F|"; }
    public function __destruct() { echo "D|receiver|"; }
    public function __invoke($item) { echo "B|", $item, "|"; return 23; }
}
class ComputedDirectIterator123 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$result = (new ComputedDirectReceiver123())(...new ComputedDirectIterator123());
echo "R|", $result, "|A|";
