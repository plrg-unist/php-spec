<?php
namespace Ns300ObjectNullShortReference;
class Box300 {
    public object|null $item {
        &get =>
            $this->item;
    }
    public function __destruct() { echo 'D|'; }
}
class Leaf300 { public $tag = 109; }
$box300 = new Box300();
echo (array)$box300 === [] ? 'U|' : 'BAD|';
$read300 = $box300->item;
echo $read300 === null && (array)$box300 === ['item' => null] ? 'V|' : 'BAD|';
unset($read300);
$alias300 =& $box300->item;
echo $alias300 === null ? 'N|' : 'BAD|';
$alias300 = new \stdClass();
$alias300->tag = 103;
$copy300 = $box300->item;
$copy300->tag = 107;
echo $alias300 === $copy300 && $alias300->tag === 107 ? 'M|' : 'BAD|';
$alias300 = new Leaf300();
echo $box300->item === $alias300 && $alias300 !== $copy300 && $alias300->tag === 109 && $copy300->tag === 107 ? 'L|' : 'BAD|';
$alias300 = null;
echo $box300->item === null && $copy300->tag === 107 ? 'Q|' : 'BAD|';
$second300 = new \stdClass();
$second300->tag = 113;
$alias300 = $second300;
try { $alias300 = 127; } catch (\TypeError $e) {
    echo $e->getMessage() === 'Cannot assign int to reference held by property Ns300ObjectNullShortReference\Box300::$item of type ?object' ? 'T|' : 'BAD|';
}
unset($e);
echo $alias300 === $second300 && $copy300->tag === 107 ? 'K|' : 'BAD|';
unset($box300);
$alias300 = 'released';
echo $alias300 === 'released' && $copy300->tag === 107 && $second300->tag === 113 ? 'R|' : 'BAD|';
unset($alias300, $copy300, $second300);
echo 'Z|';
