<?php
class OwnedMethodInvalidReceiver122 {
    public function __destruct() { echo "D|receiver|"; }
    public function take($item) { echo "BAD|"; }
}
class OwnedMethodInvalidIterator122 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { global $receiver; echo "K|"; $receiver = null; return false; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new OwnedMethodInvalidReceiver122();
try { $receiver->take(...new OwnedMethodInvalidIterator122()); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
