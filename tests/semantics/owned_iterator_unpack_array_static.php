<?php
class OwnedStaticBase122 {
    public static function take($left, $right) {
        echo "B|", static::class, "|", $left, "|", $right, "|"; return 23;
    }
}
class OwnedStaticChild122 extends OwnedStaticBase122 {}
class OwnedStaticIterator122 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 2; }
    public function current(): mixed { echo "C|"; return $this->index === 0 ? 7 : 8; }
    public function key(): mixed { echo "K|"; return $this->index === 0 ? "right" : "left"; }
    public function next(): void { echo "N|"; $this->index++; }
}
function ownedStaticInput122() { echo "P|"; return new OwnedStaticIterator122(); }
$callback = [OwnedStaticChild122::class, "take"];
$result = $callback(...ownedStaticInput122());
echo "R|", $result, "|A|";
