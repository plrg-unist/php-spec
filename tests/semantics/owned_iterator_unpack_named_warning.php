<?php
$value = 7;
$failure = new Exception("saved");
class OwnedNamedIterator122 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function &current(): mixed { global $value; echo "C|"; return $value; }
    public function key(): mixed { global $callback; echo "K|"; $callback = null; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
function ownedNamedInput122() { echo "P|"; return new OwnedNamedIterator122(); }
function ownedNamedReferenceTarget122(&$item) { echo "BAD|"; }
$callback = ownedNamedReferenceTarget122(...);
set_error_handler(function ($level, $message, $file, $line) {
    global $failure; echo "H|", $message, "|", $line, "|"; throw $failure;
});
try { $callback(...ownedNamedInput122()); }
catch (Throwable $error) { echo "E|", (int)($error === $failure), "|"; }
restore_error_handler();
echo "A|";
