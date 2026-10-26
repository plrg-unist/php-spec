<?php
class InvalidReceiver119 {
    public function __destruct() { echo "D|receiver|"; }
    public function take($item) { echo "BAD|"; }
}
class InvalidKeyIterator119 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "D|iterator|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { global $cb; echo "K|"; $cb = null; return false; }
    public function next(): void { echo "N|"; $this->index++; }
}
$cb = [new InvalidReceiver119(), "take"];
$it = new InvalidKeyIterator119();
try { $cb(...$it); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
