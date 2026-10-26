<?php
class Receiver119 {
    public function __construct(public string $name) {}
    public function __destruct() { echo "D|", $this->name, "|"; }
    public function take($item) { echo "T|", $this->name, "|", $item, "|"; }
}
class SelectionIterator119 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed {
        global $cb, $owner;
        echo "K|";
        $cb = [new Receiver119("new"), "take"];
        $owner = null;
        return 0;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$owner = new Receiver119("old");
$cb = [$owner, "take"];
$it = new SelectionIterator119();
$cb(...$it);
echo "A|";
$cb = null;
echo "Z|";
