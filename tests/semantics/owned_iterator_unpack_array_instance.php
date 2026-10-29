<?php
class OwnedArrayReceiver122 {
    public function __destruct() { echo "D|receiver|"; }
    public function take($item) { echo "B|", $item, "|"; return 23; }
}
class OwnedArrayIterator122 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed {
        global $callback, $receiver;
        echo "K|"; $callback = null; $receiver = null; return 0;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new OwnedArrayReceiver122();
$callback = [$receiver, "take"];
$result = $callback(...new OwnedArrayIterator122());
echo "R|", $result, "|A|";
