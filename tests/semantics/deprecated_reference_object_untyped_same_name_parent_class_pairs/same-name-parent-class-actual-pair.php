<?php
namespace Ns288SameNameParentClassActualPair;
class Leaf288 {
    public function __destruct() { echo 'L|'; }
}
class Parent288 {
    public $anchor = 31;
    public $tag = 99;
}
class Box288 extends Parent288 {
    public $tag {
        set(
            $incoming288
        ) =>
            ($GLOBALS['sets288execution'] = $GLOBALS['sets288execution'] + 1)
                ? ($incoming288 === false ? true : $incoming288)
                : $incoming288;
        get {
            $GLOBALS['gets288execution'] = $GLOBALS['gets288execution'] + 1;
            return 41;
        }
    }
}
$gets288execution = 0;
$sets288execution = 0;
$box288 = new Box288();
echo $box288->anchor === 31 && $box288->tag === 41 && $gets288execution === 1 && $sets288execution === 0 ? 'D|' : 'BAD|';
$result288 = $box288->tag = false;
echo $result288 === false && $box288->tag === 41 && $sets288execution === 1 && $gets288execution === 2 ? 'B|' : 'BAD|';
$box288->tag = new Leaf288();
echo $box288->tag === 41 && $sets288execution === 2 && $gets288execution === 3 ? 'I|' : 'BAD|';
$result288 = $box288->tag = 'plain';
echo $result288 === 'plain' && $box288->tag === 41 && $sets288execution === 3 && $gets288execution === 4 ? 'T|' : 'BAD|';
echo $sets288execution === 3 && $gets288execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
