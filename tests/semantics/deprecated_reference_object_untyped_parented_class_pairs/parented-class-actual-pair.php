<?php
namespace Ns287ParentedClassActualPair;
class Leaf287 {
    public function __destruct() { echo 'L|'; }
}
class Parent287 {
    public $anchor = 31;
}
class Box287 extends Parent287 {
    public $tag {
        set(
            $incoming287
        ) =>
            ($GLOBALS['sets287execution'] = $GLOBALS['sets287execution'] + 1)
                ? ($incoming287 === false ? true : $incoming287)
                : $incoming287;
        get {
            $GLOBALS['gets287execution'] = $GLOBALS['gets287execution'] + 1;
            return 41;
        }
    }
}
$gets287execution = 0;
$sets287execution = 0;
$box287 = new Box287();
echo $box287->anchor === 31 && $box287->tag === 41 && $gets287execution === 1 && $sets287execution === 0 ? 'D|' : 'BAD|';
$result287 = $box287->tag = false;
echo $result287 === false && $box287->tag === 41 && $sets287execution === 1 && $gets287execution === 2 ? 'B|' : 'BAD|';
$box287->tag = new Leaf287();
echo $box287->tag === 41 && $sets287execution === 2 && $gets287execution === 3 ? 'I|' : 'BAD|';
$result287 = $box287->tag = 'plain';
echo $result287 === 'plain' && $box287->tag === 41 && $sets287execution === 3 && $gets287execution === 4 ? 'T|' : 'BAD|';
echo $sets287execution === 3 && $gets287execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
