<?php
namespace Ns282TraitActualShortBlock;
use Ns282TraitActualShortBlock\Pair282 as Alias282;
trait Pair282 {
    public $tag {
        set(
            $input282sb
        ) {
            $GLOBALS['sets282execution'] = $GLOBALS['sets282execution'] + 1;
            $this->tag = $input282sb === false ? true : $input282sb;
        }
        get =>
            ($GLOBALS['gets282execution'] = $GLOBALS['gets282execution'] + 1)
                ? $this->tag
                : $this->tag;
    }
}
class Box282 { use Pair282, Alias282; }
$gets282execution = 0;
$sets282execution = 0;
$box282 = new Box282();
echo $box282->tag === null ? 'D|' : 'BAD|';
$result282 = $box282->tag = false;
echo $result282 === false && $box282->tag === true && $sets282execution === 1 && $gets282execution === 2 ? 'B|' : 'BAD|';
$result282 = $box282->tag = 23;
echo $result282 === 23 && $box282->tag === 23 && $sets282execution === 2 && $gets282execution === 3 ? 'I|' : 'BAD|';
$result282 = $box282->tag = 'plain';
echo $result282 === 'plain' && $box282->tag === 'plain' && $sets282execution === 3 && $gets282execution === 4 ? 'T|' : 'BAD|';
echo $sets282execution === 3 && $gets282execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
