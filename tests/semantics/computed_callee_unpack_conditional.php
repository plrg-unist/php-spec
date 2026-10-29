<?php
class ComputedConditionalReceiver123 {
    public $tag;
    public function __construct($tag) { $this->tag = $tag; }
    public function __destruct() { echo "D|", $this->tag, "|"; }
    public function __invoke($item) { echo "B|", $this->tag, "|", $item, "|"; return 23; }
}
class ComputedConditionalIterator123 implements Iterator {
    private int $index = 0;
    public function __destruct() { echo "I|"; }
    public function rewind(): void { echo "W|"; }
    public function valid(): bool { echo "V|"; return $this->index < 1; }
    public function current(): mixed { echo "C|"; return 7; }
    public function key(): mixed { global $old; echo "K|"; $old = null; return 0; }
    public function next(): void { echo "N|"; $this->index++; }
}
$old = new ComputedConditionalReceiver123("old");
$flag = true;
$result = ($flag ? $old : null)(...new ComputedConditionalIterator123());
echo "R|", $result, "|A|";
