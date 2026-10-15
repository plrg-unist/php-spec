<?php
class MagicFloatParent85 {
    private int $pluszero = 1;
    private int $minuszero = 2;
    private int $positive = 3;
    private int $negative = 4;
    private int $tiny = 5;
    private int $minustiny = 6;
    private int $largest = 7;
    private int $infinity = 8;
    private int $minusinf = 9;
    public function __isset(string $name): bool {
        echo 'I:', $name, '|';
        return true;
    }
    public function __get($name) {
        echo 'G:', $name, '|';
        return match ($name) {
            'pluszero' => 0.0,
            'minuszero' => -0.0,
            'positive' => 1.5,
            'negative' => -2.5,
            'tiny' => 5e-324,
            'minustiny' => -5e-324,
            'largest' => 1.7976931348623157e308,
            'infinity' => INF,
            'minusinf' => -INF
        };
    }
}
class MagicFloatChild85 extends MagicFloatParent85 {}
$child = new MagicFloatChild85();
echo 'A:', empty($child->pluszero) ? 'T' : 'F', '|';
echo 'B:', empty($child->minuszero) ? 'T' : 'F', '|';
echo 'C:', empty($child->positive) ? 'T' : 'F', '|';
echo 'D:', empty($child->negative) ? 'T' : 'F', '|';
echo 'E:', empty($child->tiny) ? 'T' : 'F', '|';
echo 'F:', empty($child->minustiny) ? 'T' : 'F', '|';
echo 'G:', empty($child->largest) ? 'T' : 'F', '|';
echo 'H:', empty($child->infinity) ? 'T' : 'F', '|';
echo 'I:', empty($child->minusinf) ? 'T' : 'F', '|';
$raw = (array) $child;
echo 'R:', $raw === ["\0MagicFloatParent85\0pluszero" => 1, "\0MagicFloatParent85\0minuszero" => 2, "\0MagicFloatParent85\0positive" => 3, "\0MagicFloatParent85\0negative" => 4, "\0MagicFloatParent85\0tiny" => 5, "\0MagicFloatParent85\0minustiny" => 6, "\0MagicFloatParent85\0largest" => 7, "\0MagicFloatParent85\0infinity" => 8, "\0MagicFloatParent85\0minusinf" => 9] ? 'ONLY' : 'BAD', '|';
