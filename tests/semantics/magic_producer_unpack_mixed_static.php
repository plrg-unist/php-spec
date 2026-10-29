<?php
class MagicMixedBase125 {
    public static function __callStatic(string $name, array $arguments) {
        echo "B|", __CLASS__, "|", static::class, "|", $name, "|";
        foreach ($arguments as $key => $value) { echo $key, "=", $value, "|"; }
        return 23;
    }
}
class MagicMixedChild125 extends MagicMixedBase125 {}
function magicMixedGenerator125() {
    try { echo "G|"; yield "arguments" => 9; echo "N|generator|"; }
    finally { echo "F|"; }
}
class MagicMixedIterator125 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "D|iterator|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 10; }
    public function key(): mixed { echo "K|"; return 900; }
    public function next(): void { echo "N|iterator|"; $this->index++; }
}
$generator = magicMixedGenerator125();
$iterator = new MagicMixedIterator125();
$answer = MagicMixedChild125::MiSs(7, ...[900 => 8], ...$generator, ...$iterator);
echo "R|", $answer, "|U|"; unset($generator, $iterator); echo "A|";
