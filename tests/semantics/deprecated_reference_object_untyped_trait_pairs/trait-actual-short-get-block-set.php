<?php
namespace Ns280TraitActualShortBlock;
trait Pair280 {
    public $tag = 17 {
        set(
            $input280sb
        ) {
            $GLOBALS['sets280execution'] = $GLOBALS['sets280execution'] + 1;
            $this->tag = $input280sb === false ? true : $input280sb;
        }
        get =>
            ($GLOBALS['gets280execution'] = $GLOBALS['gets280execution'] + 1)
                ? $this->tag
                : $this->tag;
    }
}
class Box280 { use Pair280; }
$gets280execution = 0;
$sets280execution = 0;
$box280 = new Box280();
echo $box280->tag === 17 ? 'D|' : 'BAD|';
$result280 = $box280->tag = false;
echo $result280 === false && $box280->tag === true && $sets280execution === 1 && $gets280execution === 2 ? 'B|' : 'BAD|';
$result280 = $box280->tag = 23;
echo $result280 === 23 && $box280->tag === 23 && $sets280execution === 2 && $gets280execution === 3 ? 'I|' : 'BAD|';
$result280 = $box280->tag = 'plain';
echo $result280 === 'plain' && $box280->tag === 'plain' && $sets280execution === 3 && $gets280execution === 4 ? 'T|' : 'BAD|';
echo $sets280execution === 3 && $gets280execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
