<?php
class ThrowReceiver119 {
    public function __construct(public string $name) {}
    public function __destruct() { echo "D|", $this->name, "|"; }
    public function take($item) { echo "BAD|"; }
}
class ThrowKeyIterator119 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed {
        global $cb;
        echo "K|";
        $cb = null;
        throw new Exception("stop", 17);
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$cb = [new ThrowReceiver119("old"), "take"];
$it = new ThrowKeyIterator119();
try { $cb(...$it); }
catch (Exception $error) { echo "E|", $error->getCode(), "|"; }
echo "A|";
