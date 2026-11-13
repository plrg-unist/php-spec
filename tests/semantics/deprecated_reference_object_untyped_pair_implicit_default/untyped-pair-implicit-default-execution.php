<?php
namespace Ns276UntypedPairImplicitDefaultExecution;
class Box276 {
    public $tag {
        get {
            $GLOBALS['gets276execution'] = $GLOBALS['gets276execution'] + 1;
            return $this->tag;
        }
        set {
            $GLOBALS['sets276execution'] = $GLOBALS['sets276execution'] + 1;
            $this->tag = $value === false ? true : $value;
        }
    }
}
$gets276execution = 0;
$sets276execution = 0;
$box276 = new Box276();
echo $box276->tag === null ? 'D|' : 'BAD|';
$result276 = $box276->tag = false;
echo $result276 === false && $box276->tag === true && $sets276execution === 1 && $gets276execution === 2 ? 'B|' : 'BAD|';
$result276 = $box276->tag = 23;
echo $result276 === 23 && $box276->tag === 23 && $sets276execution === 2 && $gets276execution === 3 ? 'I|' : 'BAD|';
$result276 = $box276->tag = 'plain';
echo $result276 === 'plain' && $box276->tag === 'plain' && $sets276execution === 3 && $gets276execution === 4 ? 'T|' : 'BAD|';
echo $sets276execution === 3 && $gets276execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
