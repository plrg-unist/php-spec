<?php
namespace Ns288SameNameParentClassImplicitPair;
class Parent288 {
    public $anchor = 31;
    public $tag = 99;
}
class Box288 extends Parent288 {
    public $tag = 17 {
        get =>
            ($GLOBALS['gets288execution'] = $GLOBALS['gets288execution'] + 1)
                ? 41
                : 41;
        set {
            $GLOBALS['sets288execution'] = $GLOBALS['sets288execution'] + 1;
            $GLOBALS['before288execution'] = $this->tag;
            $this->tag = $value === false ? true : $value;
            $GLOBALS['stored288execution'] = $this->tag;
        }
    }
}
$gets288execution = 0;
$sets288execution = 0;
$before288execution = 'cold';
$stored288execution = 'cold';
$box288 = new Box288();
echo $box288->anchor === 31 && $box288->tag === 41 && $before288execution === 'cold' && $stored288execution === 'cold' && $gets288execution === 1 && $sets288execution === 0 ? 'D|' : 'BAD|';
$result288 = $box288->tag = false;
echo $result288 === false && $box288->tag === 41 && $before288execution === 17 && $stored288execution === true && $sets288execution === 1 && $gets288execution === 2 ? 'B|' : 'BAD|';
$result288 = $box288->tag = 23;
echo $result288 === 23 && $box288->tag === 41 && $before288execution === true && $stored288execution === 23 && $sets288execution === 2 && $gets288execution === 3 ? 'I|' : 'BAD|';
$result288 = $box288->tag = 'plain';
echo $result288 === 'plain' && $box288->tag === 41 && $before288execution === 23 && $stored288execution === 'plain' && $sets288execution === 3 && $gets288execution === 4 ? 'T|' : 'BAD|';
echo $sets288execution === 3 && $gets288execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
