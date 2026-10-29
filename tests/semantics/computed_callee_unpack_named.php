<?php
class ComputedNamedBase123 {
    public function __destruct() { echo "D|receiver|"; }
    public function __invoke($left, &$right) {
        echo "B|", static::class, "|", $left, "|", $right, "|";
        $right = 77; echo "T|", $right, "|"; return 23;
    }
}
class ComputedNamedChild123 extends ComputedNamedBase123 {}
class ComputedNamedIterator123 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 2; }
    public function current(): mixed { echo "C|"; return $this->index === 0 ? 7 : 8; }
    public function key(): mixed { echo "K|"; return $this->index === 0 ? "right" : "left"; }
    public function next(): void { echo "N|"; $this->index++; }
}
function computedNamedCallee123() { echo "F|"; return new ComputedNamedChild123(); }
$iterator = new ComputedNamedIterator123();
set_error_handler(function ($level, $message, $file, $line) {
    echo "H|", $message, "|", $line, "|"; return true;
});
$result = (computedNamedCallee123())(
    ...$iterator
);
restore_error_handler();
echo "R|", $result, "|"; unset($iterator); echo "A|";
