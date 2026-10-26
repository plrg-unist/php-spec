<?php
class CleanupReceipt118 {
    public function __destruct() { echo "D|"; }
}
class CleanupReceiver118 {
    public function take(&$item) { echo "T|", $item, "|"; }
}
class CleanupIterator118 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
set_error_handler(static function ($severity, $message) {
    echo "H|", $severity, "|", $message, "|";
    return new CleanupReceipt118();
});
$receiver = new CleanupReceiver118();
$iterator = new CleanupIterator118();
$receiver->take(...$iterator);
echo "A|";
