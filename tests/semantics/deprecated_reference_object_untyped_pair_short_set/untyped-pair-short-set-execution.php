<?php
namespace Ns277UntypedPairShortSetExecution;
class Box277 {
    public $tag {
        get {
            $GLOBALS['gets277execution'] = $GLOBALS['gets277execution'] + 1;
            return $this->tag;
        }
        set => ($GLOBALS['sets277execution'] = $GLOBALS['sets277execution'] + 1) ? ($value === false ? true : $value) : $value;
    }
}
$gets277execution = 0;
$sets277execution = 0;
$box277 = new Box277();
echo $box277->tag === null ? 'D|' : 'BAD|';
$result277 = $box277->tag = false;
echo $result277 === false && $box277->tag === true && $sets277execution === 1 && $gets277execution === 2 ? 'B|' : 'BAD|';
$result277 = $box277->tag = 23;
echo $result277 === 23 && $box277->tag === 23 && $sets277execution === 2 && $gets277execution === 3 ? 'I|' : 'BAD|';
$result277 = $box277->tag = 'plain';
echo $result277 === 'plain' && $box277->tag === 'plain' && $sets277execution === 3 && $gets277execution === 4 ? 'T|' : 'BAD|';
echo $sets277execution === 3 && $gets277execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
