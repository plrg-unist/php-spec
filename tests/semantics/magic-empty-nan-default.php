<?php
class MagicNanParent86 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        echo 'G|';
        return NAN;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicNanChild86 extends MagicNanParent86 {}
$child = new MagicNanChild86();
echo 'B:', empty($child->value) ? 'T' : 'F', '|';
$raw = (array) $child;
echo 'R:', $raw === ["\0MagicNanParent86\0value" => 1] ? 'ONLY' : 'BAD', '|';
unset($raw);
unset($child);
echo 'E|';
