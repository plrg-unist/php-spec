<?php
class MagicScopedBase124 {
    public function __call(string $name, array $arguments) {
        echo "I|", __CLASS__, "|", static::class, "|", $name, "|", $arguments[0], "|"; return 23;
    }
    public static function __callStatic(string $name, array $arguments) { echo "BAD|static|"; }
    public function run($iterator) { return self::MiSs(...$iterator); }
}
class MagicScopedChild124 extends MagicScopedBase124 {}
class MagicScopedIterator124 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { echo "K|"; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new MagicScopedChild124();
$iterator = new MagicScopedIterator124();
$answer = $receiver->run($iterator);
echo "R|", $answer, "|A|";
