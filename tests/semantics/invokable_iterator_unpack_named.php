<?php
class InvokableNamedBase121 {
    public function __invoke($left, $right) { echo "T|", $left, "|", $right, "|"; }
}
class InvokableNamedChild121 extends InvokableNamedBase121 {}
class InvokableNamedIterator121 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 2; }
    public function current(): mixed { echo "C|"; return $this->index + 4; }
    public function key(): mixed { echo "K|"; return $this->index === 0 ? "right" : "left"; }
    public function next(): void { echo "N|"; $this->index++; }
}
$callback = new InvokableNamedChild121();
$iterator = new InvokableNamedIterator121();
$callback(...$iterator);
echo "A|";
