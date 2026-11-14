<?php
namespace Ns300NullObjectShortReference;
class Box300 {
    public null|object $item {
        &get =>
            $this->item;
    }
    public function __destruct() { echo 'D|'; }
}
class Leaf300 { public $tag = 149; }
$box300 = new Box300();
$seed300 = new \stdClass();
$seed300->tag = 131;
$box300->item = $seed300;
unset($seed300);
$alias300 =& $box300->item;
$copy300 = $box300->item;
echo $alias300 === $copy300 ? 'I|' : 'BAD|';
$copy300->tag = 137;
echo $alias300->tag === 137 && $box300->item === $copy300 ? 'M|' : 'BAD|';
$alias300 = null;
echo $box300->item === null && $copy300->tag === 137 ? 'N|' : 'BAD|';
$alias300 = new Leaf300();
echo $alias300 !== $copy300 && $alias300->tag === 149 && $copy300->tag === 137 ? 'L|' : 'BAD|';
try { $alias300 = 151; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns300NullObjectShortReference\Box300::$item of type ?object' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias300->tag === 149 && $copy300->tag === 137 ? 'K|' : 'BAD|';
unset($box300);
$alias300 = [];
echo $alias300 === [] && $copy300->tag === 137 ? 'R|' : 'BAD|';
unset($alias300, $copy300);
echo 'Z|';
