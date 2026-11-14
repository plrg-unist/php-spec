<?php
namespace Ns289UnbackedChildSlotShort;
class Middle289 {
    public function __destruct() { echo 'M|'; }
}
class Tail289 {
    public function __destruct() { echo 'T|'; }
}
class Leaf289 {
    public function __destruct() { echo 'U|'; }
}
class Parent289 {
    public $anchor = 31;
    public $tag = 99;
}
class Box289 extends Parent289 {
    public $tag {
        get =>
            ($GLOBALS['gets289execution'] = $GLOBALS['gets289execution'] + 1)
                ? 41
                : 41;
    }
    public $middle;
    public $tail;
}
$gets289execution = 0;
$box289 = new Box289();
$initial289 = (array)$box289;
echo $initial289['tag'] === null && $initial289['middle'] === null && $initial289['tail'] === null && $box289->anchor === 31 && $box289->tag === 41 && $gets289execution === 1 ? 'N|' : 'BAD|';
unset($initial289);
$box289->middle = new Middle289();
$box289->tag = new Leaf289();
$box289->tail = new Tail289();
echo $box289->tag === 41 && $gets289execution === 2 ? 'B|' : 'BAD|';
unset($box289);
echo 'Z|';
