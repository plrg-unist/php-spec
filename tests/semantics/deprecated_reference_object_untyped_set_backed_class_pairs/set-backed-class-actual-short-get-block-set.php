<?php
namespace Ns285ClassActualSetBacked;
class Box285 {
    public $tag {
        set(
            $incoming285
        ) {
            $GLOBALS['sets285execution'] = $GLOBALS['sets285execution'] + 1;
            $GLOBALS['before285execution'] = $this->tag;
            $this->tag = $incoming285 === false ? true : $incoming285;
            $GLOBALS['stored285execution'] = $this->tag;
        }
        get =>
            ($GLOBALS['gets285execution'] = $GLOBALS['gets285execution'] + 1)
                ? 41
                : 41;
    }
}
$gets285execution = 0;
$sets285execution = 0;
$before285execution = 'cold';
$stored285execution = 'cold';
$box285 = new Box285();
echo $box285->tag === 41 && $before285execution === 'cold' && $stored285execution === 'cold' && $gets285execution === 1 && $sets285execution === 0 ? 'D|' : 'BAD|';
$result285 = $box285->tag = false;
echo $result285 === false && $box285->tag === 41 && $before285execution === null && $stored285execution === true && $sets285execution === 1 && $gets285execution === 2 ? 'B|' : 'BAD|';
$result285 = $box285->tag = 23;
echo $result285 === 23 && $box285->tag === 41 && $before285execution === true && $stored285execution === 23 && $sets285execution === 2 && $gets285execution === 3 ? 'I|' : 'BAD|';
$result285 = $box285->tag = 'plain';
echo $result285 === 'plain' && $box285->tag === 41 && $before285execution === 23 && $stored285execution === 'plain' && $sets285execution === 3 && $gets285execution === 4 ? 'T|' : 'BAD|';
echo $sets285execution === 3 && $gets285execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
