<?php
class CaptureToken120 {
    public function __destruct() { echo "D|"; }
}
function makeCapture120() {
    $value = 3;
    $token = new CaptureToken120();
    return function ($item) use (&$value, $token) { echo "BAD|"; };
}
class CaptureIterator120 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "R|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 5; }
    public function key(): mixed {
        global $callback;
        echo "K|";
        $callback = null;
        return false;
    }
    public function next(): void { echo "N|"; $this->index++; }
}
$callback = makeCapture120();
$iterator = new CaptureIterator120();
try { $callback(...$iterator); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
