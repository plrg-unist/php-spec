<?php
class MagicEmpty124 {
    public function __call(string $name, array $arguments) {
        echo "B|", $name, "|", (int)($arguments === []), "|";
        $arguments[] = 5; echo "T|", $arguments[0], "|"; return 23;
    }
}
class MagicEmptyIterator124 implements Iterator {
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return false; }
    public function current(): mixed { echo "BAD|current|"; return 7; }
    public function key(): mixed { echo "BAD|key|"; return 0; }
    public function next(): void { echo "BAD|next|"; }
}
$receiver = new MagicEmpty124();
$answer = $receiver->MiSs(...new MagicEmptyIterator124());
echo "R|", $answer, "|A|";
