<?php
class WrapperReceiver120 {
    public function take($item) { echo "F|", $item, "|"; }
}
class WrapperIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 4; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new WrapperReceiver120();
$pair = [$receiver, 'take'];
$callback = $pair(...);
$iterator = new WrapperIterator120();
$callback(...$iterator);
