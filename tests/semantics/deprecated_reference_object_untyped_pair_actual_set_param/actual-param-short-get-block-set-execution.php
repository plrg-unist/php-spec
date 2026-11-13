<?php
namespace Ns279UntypedPairActualParamBlockExecution;
class Box279 {
    public $tag {
        get =>
            ($GLOBALS['gets279execution'] = $GLOBALS['gets279execution'] + 1)
                ? $this->tag
                : $this->tag;
        set(
            $input279block
        ) {
            $GLOBALS['sets279execution'] = $GLOBALS['sets279execution'] + 1;
            $this->tag = $input279block === false ? true : $input279block;
        }
    }
}
$gets279execution = 0;
$sets279execution = 0;
$box279 = new Box279();
echo $box279->tag === null ? 'D|' : 'BAD|';
$result279 = $box279->tag = false;
echo $result279 === false && $box279->tag === true && $sets279execution === 1 && $gets279execution === 2 ? 'B|' : 'BAD|';
$result279 = $box279->tag = 23;
echo $result279 === 23 && $box279->tag === 23 && $sets279execution === 2 && $gets279execution === 3 ? 'I|' : 'BAD|';
$result279 = $box279->tag = 'plain';
echo $result279 === 'plain' && $box279->tag === 'plain' && $sets279execution === 3 && $gets279execution === 4 ? 'T|' : 'BAD|';
echo $sets279execution === 3 && $gets279execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
