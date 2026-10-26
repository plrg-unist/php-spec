<?php
class Scoped120 {
    public string $name = 'held';
    public function make(): Closure {
        return function (&$item) { echo "F|", $this->name, "|", $item, "|"; };
    }
}
class ScopedIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
set_error_handler(static function ($severity, $message) { echo "H|", $severity, "|", $message, "|"; return true; });
$receiver = new Scoped120();
$callback = $receiver->make();
$iterator = new ScopedIterator120();
$callback(...$iterator);
echo "A|";
