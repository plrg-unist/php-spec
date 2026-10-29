<?php
$failure = new Exception("key");
class MagicThrow124 {
    public static function __callStatic(string $name, array $arguments) { echo "BAD|handler|"; }
}
class MagicThrowCurrent124 {
    public function __destruct() { echo "D|current|"; }
}
class MagicThrowIterator124 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return new MagicThrowCurrent124(); }
    public function key(): mixed { global $failure; echo "K|"; throw $failure; }
    public function next(): void { echo "BAD|next|"; $this->index++; }
}
try { MagicThrow124::MiSs(...new MagicThrowIterator124()); }
catch (Throwable $error) { echo "E|", (int)($error === $failure), "|"; }
echo "A|";
