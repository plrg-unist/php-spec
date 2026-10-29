<?php
class MagicCrossBase124 {
    public static function __callStatic(string $name, array $arguments) {
        echo "B|", __CLASS__, "|", static::class, "|", $name, "|";
        foreach ($arguments as $key => $value) { echo $key, "=", $value, "|"; }
        return 23;
    }
}
class MagicCrossChild124 extends MagicCrossBase124 {}
class MagicCrossNamed124 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "D|named|"; }
    public function rewind(): void { echo "W|named|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { echo "K|"; return "arguments"; }
    public function next(): void { echo "N|"; $this->index++; }
}
class MagicCrossPosition124 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "D|position|"; }
    public function rewind(): void { echo "W|position|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 8; }
    public function key(): mixed { echo "K|"; return 100; }
    public function next(): void { echo "N|"; $this->index++; }
}
$answer = MagicCrossChild124::MiSs(...new MagicCrossNamed124(), ...new MagicCrossPosition124());
echo "R|", $answer, "|A|";
