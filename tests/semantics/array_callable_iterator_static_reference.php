<?php
class ReferenceBase119 {
    public static function take(&$item) { echo "T|", $item, "|"; $item = 9; }
}
class ReferenceChild119 extends ReferenceBase119 {}
class StaticReferenceIterator119 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
set_error_handler(static function ($severity, $message, $file, $line) {
    echo "H|", $severity, "|", $message, "|", $line, "|";
    return true;
});
$cb = [ReferenceChild119::class, "take"];
$it = new StaticReferenceIterator119();
$cb(...$it);
