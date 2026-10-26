<?php
class StaticBase119 {
    public static function take($first, $second) { echo "T|", $first, "|", $second, "|", static::class, "|"; }
}
class StaticChild119 extends StaticBase119 {}
class StaticNamedIterator119 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 2; }
    public function current(): mixed { echo "C|"; return $this->index === 0 ? 22 : 11; }
    public function key(): mixed { echo "K|"; return $this->index === 0 ? "second" : "first"; }
    public function next(): void { echo "N|"; $this->index++; }
}
$cb = [StaticChild119::class, "take"];
$it = new StaticNamedIterator119();
$cb(...$it);
