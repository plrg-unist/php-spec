<?php
namespace Ns278UntypedPairShortGetExecution;
class Box278 {
    public $tag {
        get => ($GLOBALS['gets278execution'] = $GLOBALS['gets278execution'] + 1) ? $this->tag : $this->tag;
        set {
            $GLOBALS['sets278execution'] = $GLOBALS['sets278execution'] + 1;
            $this->tag = $value === false ? true : $value;
        }
    }
}
$gets278execution = 0;
$sets278execution = 0;
$box278 = new Box278();
echo $box278->tag === null ? 'D|' : 'BAD|';
$result278 = $box278->tag = false;
echo $result278 === false && $box278->tag === true && $sets278execution === 1 && $gets278execution === 2 ? 'B|' : 'BAD|';
$result278 = $box278->tag = 23;
echo $result278 === 23 && $box278->tag === 23 && $sets278execution === 2 && $gets278execution === 3 ? 'I|' : 'BAD|';
$result278 = $box278->tag = 'plain';
echo $result278 === 'plain' && $box278->tag === 'plain' && $sets278execution === 3 && $gets278execution === 4 ? 'T|' : 'BAD|';
echo $sets278execution === 3 && $gets278execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
