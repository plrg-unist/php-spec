<?php
class OwnedMethodThrowReceiver122 {
    public function __destruct() { echo "D|receiver|"; }
    public function take($item) { echo "BAD|"; }
}
class OwnedMethodThrowValue122 {
    public function __destruct() { echo "D|current|"; }
}
class OwnedMethodThrowIterator122 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return new OwnedMethodThrowValue122(); }
    public function key(): mixed {
        global $receiver, $failure;
        echo "K|"; $receiver = null; throw $failure;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
function ownedMethodThrowInput122() { echo "P|"; return new OwnedMethodThrowIterator122(); }
$failure = new Exception("saved");
$receiver = new OwnedMethodThrowReceiver122();
try { $receiver->take(...ownedMethodThrowInput122()); }
catch (Throwable $error) { echo "E|", (int)($error === $failure), "|"; }
echo "A|";
