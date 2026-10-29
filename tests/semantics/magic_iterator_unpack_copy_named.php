<?php
$value = 7;
class MagicCopyBase124 {
    public function __destruct() { echo "D|receiver|"; }
    public function __call(string $name, array $arguments) {
        global $value;
        echo "B|", __CLASS__, "|", static::class, "|", $name, "|", $arguments["arguments"], "|", $value, "|";
        $arguments["arguments"] = 33;
        echo "T|", $arguments["arguments"], "|", $value, "|"; return 23;
    }
}
class MagicCopyChild124 extends MagicCopyBase124 {}
class MagicCopyIterator124 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { global $value; echo "C|"; return $value; }
    public function key(): mixed { global $value, $receiver; echo "K|"; $value = 9; $receiver = null; return "arguments"; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new MagicCopyChild124();
$answer = $receiver->MiSs(...new MagicCopyIterator124());
echo "R|", $answer, "|A|";
