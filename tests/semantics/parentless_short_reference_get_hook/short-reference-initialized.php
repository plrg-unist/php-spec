<?php
namespace Ns292ShortReferenceInitialized;
class Middle292 {
    public function __destruct() { echo 'M|'; }
}
class Tail292 {
    public function __destruct() { echo 'T|'; }
}
class Leaf292 {
    public function __destruct() { echo 'U|'; }
}
class Box292 {
    public $middle;
    public $tag = 17 {
        &get =>
            $this->tag;
    }
    public $tail;
}
$box292 = new Box292();
$initial292 = (array)$box292;
echo $initial292['tag'] === 17 && $initial292['middle'] === null && $initial292['tail'] === null ? 'N|' : 'BAD|';
unset($initial292);
$alias292 =& $box292->tag;
echo $alias292 === 17 ? 'G|' : 'BAD|';
$box292->middle = new Middle292();
$alias292 = new Leaf292();
$box292->tail = new Tail292();
$copy292 = $box292->tag;
echo $alias292 instanceof Leaf292 && $copy292 === $alias292 ? 'B|' : 'BAD|';
unset($copy292);
unset($alias292);
unset($box292);
echo 'Z|';
