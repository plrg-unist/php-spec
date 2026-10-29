<?php
$value = 7;
class OwnedInvokableReceiver122 {
    public function __destruct() { echo "D|receiver|"; }
    public function __invoke(&$item) {
        global $value; echo "B|", $item, "|", $value, "|";
        $item = 77; echo "T|", $item, "|", $value, "|"; return 23;
    }
}
class OwnedInvokableIterator122 implements Iterator {
    private int $index = 0;
    public function __destruct() { global $value; $value = 11; echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function &current(): mixed { global $value; echo "C|"; return $value; }
    public function key(): mixed { global $callback; echo "K|"; $callback = null; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
function ownedInvokableInput122() { echo "P|"; return new OwnedInvokableIterator122(); }
$callback = new OwnedInvokableReceiver122();
set_error_handler(function ($level, $message, $file, $line) {
    global $value; $value = 9; echo "H|", $message, "|", $line, "|"; return true;
});
$result = $callback(...ownedInvokableInput122());
restore_error_handler();
echo "R|", $result, "|V|", $value, "|A|";
