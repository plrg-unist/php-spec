<?php
function reference120(&$item) { echo "F|", $item, "|"; $item = 17; }
class ReferenceIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
set_error_handler(static function ($severity, $message, $file, $line) {
    echo "H|", $severity, "|", $message, "|", $line, "|";
    return true;
});
$callback = reference120(...);
$iterator = new ReferenceIterator120();
$callback(...$iterator);
