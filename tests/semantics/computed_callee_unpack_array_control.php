<?php
class ComputedArrayReceiver123 {
    public function __destruct() { echo "D|receiver|"; }
    public function take($item) { echo "B|", $item, "|"; return 23; }
}
class ComputedArrayIterator123 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$result = ([new ComputedArrayReceiver123(), "take"])(...new ComputedArrayIterator123());
echo "R|", $result, "|A|";
