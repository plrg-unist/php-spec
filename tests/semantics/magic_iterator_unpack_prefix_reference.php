<?php
$prefix = 7;
$alias =& $prefix;
class MagicPrefix124 {
    public function __call(string $name, array $arguments) {
        global $prefix;
        echo "B|", $name, "|", $arguments[0], "|", $arguments[1], "|", $prefix, "|";
        $arguments[0] = 33; echo "T|", $prefix, "|"; return 23;
    }
}
class MagicPrefixIterator124 implements Iterator {
    private int $index = 0;
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 8; }
    public function key(): mixed { global $prefix; echo "K|"; $prefix = 9; return 100; }
    public function next(): void { echo "N|"; $this->index++; }
}
$receiver = new MagicPrefix124();
$iterator = new MagicPrefixIterator124();
$answer = $receiver->MiSs($alias, ...$iterator);
echo "R|", $answer, "|V|", $alias, "|A|";
