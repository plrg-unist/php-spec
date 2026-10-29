<?php
class InvokableReferenceBase121 {
    public function __invoke(&$item) { echo "T|", $item, "|"; $item = 9; }
}
class InvokableReferenceChild121 extends InvokableReferenceBase121 {}
class InvokableReferenceIterator121 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { echo "K|"; return "item"; }
    public function next(): void { echo "N|"; $this->index++; }
}
set_error_handler(static function ($severity, $message, $file, $line) {
    echo "H|", $severity, "|", $message, "|", $line, "|";
    return true;
});
$callback = new InvokableReferenceChild121();
$iterator = new InvokableReferenceIterator121();
$callback(...$iterator);
echo "A|";
