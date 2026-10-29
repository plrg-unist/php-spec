<?php
class OwnedArrowIterator122 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$callback = fn($item) => $item + 1;
$result = $callback(...(true ? new OwnedArrowIterator122() : null));
echo "R|", $result, "|A|";
