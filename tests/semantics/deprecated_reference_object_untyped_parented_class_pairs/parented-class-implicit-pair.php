<?php
namespace Ns287ParentedClassImplicitPair;
class Parent287 {
    public $anchor = 31;
}
class Box287 extends Parent287 {
    public $tag = 17 {
        get =>
            ($GLOBALS['gets287execution'] = $GLOBALS['gets287execution'] + 1)
                ? 41
                : 41;
        set {
            $GLOBALS['sets287execution'] = $GLOBALS['sets287execution'] + 1;
            $GLOBALS['before287execution'] = $this->tag;
            $this->tag = $value === false ? true : $value;
            $GLOBALS['stored287execution'] = $this->tag;
        }
    }
}
$gets287execution = 0;
$sets287execution = 0;
$before287execution = 'cold';
$stored287execution = 'cold';
$box287 = new Box287();
echo $box287->anchor === 31 && $box287->tag === 41 && $before287execution === 'cold' && $stored287execution === 'cold' && $gets287execution === 1 && $sets287execution === 0 ? 'D|' : 'BAD|';
$result287 = $box287->tag = false;
echo $result287 === false && $box287->tag === 41 && $before287execution === 17 && $stored287execution === true && $sets287execution === 1 && $gets287execution === 2 ? 'B|' : 'BAD|';
$result287 = $box287->tag = 23;
echo $result287 === 23 && $box287->tag === 41 && $before287execution === true && $stored287execution === 23 && $sets287execution === 2 && $gets287execution === 3 ? 'I|' : 'BAD|';
$result287 = $box287->tag = 'plain';
echo $result287 === 'plain' && $box287->tag === 41 && $before287execution === 23 && $stored287execution === 'plain' && $sets287execution === 3 && $gets287execution === 4 ? 'T|' : 'BAD|';
echo $sets287execution === 3 && $gets287execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
