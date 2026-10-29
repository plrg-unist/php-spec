<?php
$failure = new Exception("key");
$replacement = new Exception("receiver");
class ComputedThrowReceiver123 {
    public function __destruct() { global $replacement; echo "D|receiver|"; throw $replacement; }
    public function __invoke($item) { echo "BAD|"; }
}
class ComputedThrowIterator123 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { global $failure; echo "K|"; throw $failure; }
    public function next(): void { echo "N|"; $this->index++; }
}
try { (new ComputedThrowReceiver123())(...new ComputedThrowIterator123()); }
catch (Throwable $error) {
    echo "E|", (int)($error === $replacement), "|", (int)($error->getPrevious() === $failure), "|";
}
echo "A|";
