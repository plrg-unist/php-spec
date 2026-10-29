<?php
class ComputedClosureHeld123 {
    public function __destruct() { echo "D|capture|"; }
}
class ComputedClosureIterator123 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
function computedClosureCallee123() {
    echo "F|"; $held = new ComputedClosureHeld123();
    return function ($item) use ($held) { echo "B|", $item, "|"; return 23; };
}
$result = (computedClosureCallee123())(...new ComputedClosureIterator123());
echo "R|", $result, "|A|";
