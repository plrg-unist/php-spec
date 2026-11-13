<?php
namespace Ns281TraitImplicitBlockShort;
trait Pair281 {
    public $tag = 17 {
        get {
            $GLOBALS['gets281execution'] = $GLOBALS['gets281execution'] + 1;
            return $this->tag;
        }
        set =>
            ($GLOBALS['sets281execution'] = $GLOBALS['sets281execution'] + 1)
                ? ($value === false ? true : $value)
                : $value;
    }
}
class Parent281 {
    public $parentPad = 31;
}
class Box281 extends Parent281 { use Pair281; }
$gets281execution = 0;
$sets281execution = 0;
$box281 = new Box281();
echo $box281->tag === 17 ? 'D|' : 'BAD|';
$result281 = $box281->tag = false;
echo $result281 === false && $box281->tag === true && $sets281execution === 1 && $gets281execution === 2 ? 'B|' : 'BAD|';
$result281 = $box281->tag = 23;
echo $result281 === 23 && $box281->tag === 23 && $sets281execution === 2 && $gets281execution === 3 ? 'I|' : 'BAD|';
$result281 = $box281->tag = 'plain';
echo $result281 === 'plain' && $box281->tag === 'plain' && $sets281execution === 3 && $gets281execution === 4 ? 'T|' : 'BAD|';
echo $sets281execution === 3 && $gets281execution === 4 ? 'C|' : 'BAD|';
echo $box281->parentPad === 31 ? 'P|' : 'BAD|';
echo 'Z|';
