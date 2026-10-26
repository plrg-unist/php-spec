<?php
class BoundReceiver120 {
    public function take($item) { echo "F|", $this->tag, "|", $item, "|"; }
    public string $tag = 'bound';
}
class BoundIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 4; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new BoundReceiver120();
$callback = function ($item) { echo "F|", $this->tag, "|", $item, "|"; };
$callback = $callback->bindTo($receiver);
$iterator = new BoundIterator120();
$callback(...$iterator);
