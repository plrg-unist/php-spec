<?php
$failure = new Exception("handler");
class MagicHandlerThrow124 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) {
        global $failure;
        echo "B|", $name, "|";
        $arguments["arguments"] = null;
        echo "U|"; unset($arguments); throw $failure;
    }
}
class MagicHandlerPayload124 {
    public function __destruct() { echo "D|payload|"; }
}
class MagicHandlerIterator124 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return new MagicHandlerPayload124(); }
    public function key(): mixed { global $receiver; echo "K|"; $receiver = null; return "arguments"; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new MagicHandlerThrow124();
$answer = 42;
try { $answer = $receiver->MiSs(...new MagicHandlerIterator124()); }
catch (Throwable $error) { echo "E|", (int)($error === $failure), "|", $answer, "|"; }
echo "A|";
