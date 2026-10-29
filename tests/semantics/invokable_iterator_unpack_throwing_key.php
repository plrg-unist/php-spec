<?php
class InvokableThrowReceiver121 {
    public function __destruct() { echo "D|receiver|"; }
    public function __invoke($item) { echo "BAD|"; }
}
class InvokableThrowIterator121 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed {
        global $callback;
        echo "K|";
        $callback = null;
        throw new Exception("stop", 17);
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$callback = new InvokableThrowReceiver121();
$iterator = new InvokableThrowIterator121();
try { $callback(...$iterator); }
catch (Exception $error) { echo "E|", $error->getCode(), "|"; }
echo "A|";
