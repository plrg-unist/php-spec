<?php
class MagicAfterNamed124 {
    public function __call(string $name, array $arguments) { echo "BAD|handler|"; }
}
class MagicAfterNamedIterator124 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 2; }
    public function current(): mixed { echo "C|"; return $this->index === 0 ? 7 : 8; }
    public function key(): mixed { echo "K|"; return $this->index === 0 ? "name" : 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new MagicAfterNamed124();
try { $receiver->MiSs(...new MagicAfterNamedIterator124()); }
catch (Error $error) { echo "E|", $error->getMessage(), "|"; }
echo "A|";
