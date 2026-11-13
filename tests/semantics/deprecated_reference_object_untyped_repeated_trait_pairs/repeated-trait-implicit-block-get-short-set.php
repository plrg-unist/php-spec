<?php
namespace Ns282TraitImplicitBlockShort;
trait Pair282 {
    public $tag = 17 {
        get {
            $GLOBALS['gets282execution'] = $GLOBALS['gets282execution'] + 1;
            return $this->tag;
        }
        set =>
            ($GLOBALS['sets282execution'] = $GLOBALS['sets282execution'] + 1)
                ? ($value === false ? true : $value)
                : $value;
    }
}
class Box282 { use Pair282, Pair282; }
$gets282execution = 0;
$sets282execution = 0;
$box282 = new Box282();
echo $box282->tag === 17 ? 'D|' : 'BAD|';
$result282 = $box282->tag = false;
echo $result282 === false && $box282->tag === true && $sets282execution === 1 && $gets282execution === 2 ? 'B|' : 'BAD|';
$result282 = $box282->tag = 23;
echo $result282 === 23 && $box282->tag === 23 && $sets282execution === 2 && $gets282execution === 3 ? 'I|' : 'BAD|';
$result282 = $box282->tag = 'plain';
echo $result282 === 'plain' && $box282->tag === 'plain' && $sets282execution === 3 && $gets282execution === 4 ? 'T|' : 'BAD|';
echo $sets282execution === 3 && $gets282execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
