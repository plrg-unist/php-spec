<?php
class MagicInvalid124 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) { echo "BAD|handler|"; }
}
class MagicInvalidCurrent124 {
    public function __destruct() { echo "D|current|"; }
}
class MagicInvalidIterator124 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return new MagicInvalidCurrent124(); }
    public function key(): mixed { global $receiver; echo "K|"; $receiver = null; return false; }
    public function next(): void { echo "BAD|next|"; $this->index++; }
}
$receiver = new MagicInvalid124();
$answer = 42;
try { $answer = $receiver->MiSs(...new MagicInvalidIterator124()); }
catch (Error $error) { echo "E|", $error->getMessage(), "|", $error->getLine(), "|", $answer, "|"; }
echo "A|";
