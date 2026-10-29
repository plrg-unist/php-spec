<?php
class InvokableTemporary121 {
    public function __invoke($item) { echo "T|", $item, "|"; }
}
class InvokableTemporaryIterator121 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
function makeInvokable121(): InvokableTemporary121 { return new InvokableTemporary121(); }
$iterator = new InvokableTemporaryIterator121();
(makeInvokable121())(...$iterator);
echo "A|";
