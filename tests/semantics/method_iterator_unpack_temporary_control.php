<?php
class TemporaryMethodReceiver118 {
    public function take($item) { echo "T|", $item, "|"; }
}
class TemporaryMethodIterator118 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 6; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new TemporaryMethodReceiver118();
$receiver->take(...new TemporaryMethodIterator118());
