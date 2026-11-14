<?php
namespace Ns290BackedChildSlotShort;
class Middle290 {
    public function __destruct() { echo 'M|'; }
}
class Tail290 {
    public function __destruct() { echo 'T|'; }
}
class Leaf290 {
    public function __destruct() { echo 'U|'; }
}
class Parent290 {
    public $anchor = 31;
    public $tag = 99;
}
class Box290 extends Parent290 {
    public $middle;
    public $tag = 17 {
        get =>
            ($GLOBALS['gets290execution'] = $GLOBALS['gets290execution'] + 1)
                ? $this->tag
                : $this->tag;
    }
    public $tail;
}
$gets290execution = 0;
$box290 = new Box290();
$initial290 = (array)$box290;
echo $initial290['tag'] === 17 && $initial290['middle'] === null && $initial290['tail'] === null && $box290->anchor === 31 && $box290->tag === 17 && $gets290execution === 1 ? 'N|' : 'BAD|';
unset($initial290);
$box290->middle = new Middle290();
$box290->tag = new Leaf290();
$box290->tail = new Tail290();
echo $box290->tag instanceof Leaf290 && $gets290execution === 2 ? 'B|' : 'BAD|';
unset($box290);
echo 'Z|';
