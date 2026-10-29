<?php
class InvokableReceiver121 {
    public function __construct(public string $name) {}
    public function __destruct() { echo "D|", $this->name, "|"; }
    public function __invoke($item) { echo "T|", $this->name, "|", $item, "|"; }
}
class InvokableSelectIterator121 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed {
        global $callback, $owner;
        echo "K|";
        $callback = new InvokableReceiver121("new");
        $owner = null;
        return 0;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$owner = new InvokableReceiver121("old");
$callback = $owner;
$iterator = new InvokableSelectIterator121();
$callback(...$iterator);
echo "A|";
$callback = null;
echo "Z|";
