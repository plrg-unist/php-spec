<?php
namespace Ns291ReferenceChildSlotNull;
class Middle291 {
    public function __destruct() { echo 'M|'; }
}
class Tail291 {
    public function __destruct() { echo 'T|'; }
}
class Leaf291 {
    public function __destruct() { echo 'U|'; }
}
class Parent291 {
    public $anchor = 31;
    public $tag = 99;
}
class Box291 extends Parent291 {
    public $middle;
    public $tag {
        &get {
            $GLOBALS['gets291execution'] = $GLOBALS['gets291execution'] + 1;
            return $this->tag;
        }
    }
    public $tail;
}
$gets291execution = 0;
$box291 = new Box291();
$initial291 = (array)$box291;
echo $initial291['tag'] === null && $initial291['middle'] === null && $initial291['tail'] === null && $box291->anchor === 31 && $gets291execution === 0 ? 'N|' : 'BAD|';
unset($initial291);
$alias291 =& $box291->tag;
echo $alias291 === null && $gets291execution === 1 ? 'G|' : 'BAD|';
$box291->middle = new Middle291();
$alias291 = new Leaf291();
$box291->tail = new Tail291();
echo $alias291 instanceof Leaf291 && $gets291execution === 1 ? 'B|' : 'BAD|';
unset($alias291);
unset($box291);
echo 'Z|';
