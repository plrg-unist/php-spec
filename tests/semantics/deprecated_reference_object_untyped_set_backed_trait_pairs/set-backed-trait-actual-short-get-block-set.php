<?php
namespace Ns283TraitActualSetBacked;
trait Pair283 {
    public $tag {
        set(
            $incoming283
        ) {
            $GLOBALS['sets283execution'] = $GLOBALS['sets283execution'] + 1;
            $GLOBALS['before283execution'] = $this->tag;
            $this->tag = $incoming283 === false ? true : $incoming283;
            $GLOBALS['stored283execution'] = $this->tag;
        }
        get =>
            ($GLOBALS['gets283execution'] = $GLOBALS['gets283execution'] + 1)
                ? 41
                : 41;
    }
}
class Box283 { use Pair283; }
$gets283execution = 0;
$sets283execution = 0;
$before283execution = 'cold';
$stored283execution = 'cold';
$box283 = new Box283();
echo $box283->tag === 41 && $before283execution === 'cold' && $stored283execution === 'cold' && $gets283execution === 1 && $sets283execution === 0 ? 'D|' : 'BAD|';
$result283 = $box283->tag = false;
echo $result283 === false && $box283->tag === 41 && $before283execution === null && $stored283execution === true && $sets283execution === 1 && $gets283execution === 2 ? 'B|' : 'BAD|';
$result283 = $box283->tag = 23;
echo $result283 === 23 && $box283->tag === 41 && $before283execution === true && $stored283execution === 23 && $sets283execution === 2 && $gets283execution === 3 ? 'I|' : 'BAD|';
$result283 = $box283->tag = 'plain';
echo $result283 === 'plain' && $box283->tag === 41 && $before283execution === 23 && $stored283execution === 'plain' && $sets283execution === 3 && $gets283execution === 4 ? 'T|' : 'BAD|';
echo $sets283execution === 3 && $gets283execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
