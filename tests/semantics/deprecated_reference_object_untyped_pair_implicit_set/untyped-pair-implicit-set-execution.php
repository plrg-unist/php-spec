<?php
namespace Ns275UntypedPairExecution;
class Box275 {
    public $tag = 17 {
        get {
            $GLOBALS['gets275execution'] = $GLOBALS['gets275execution'] + 1;
            return $this->tag;
        }
        set {
            $GLOBALS['sets275execution'] = $GLOBALS['sets275execution'] + 1;
            $this->tag = $value === false ? true : $value;
        }
    }
}
$gets275execution = 0;
$sets275execution = 0;
$box275 = new Box275();
echo $box275->tag === 17 ? 'D|' : 'BAD|';
$result275 = $box275->tag = false;
echo $result275 === false && $box275->tag === true && $sets275execution === 1 && $gets275execution === 2 ? 'B|' : 'BAD|';
$result275 = $box275->tag = 23;
echo $result275 === 23 && $box275->tag === 23 && $sets275execution === 2 && $gets275execution === 3 ? 'I|' : 'BAD|';
$result275 = $box275->tag = 'plain';
echo $result275 === 'plain' && $box275->tag === 'plain' && $sets275execution === 3 && $gets275execution === 4 ? 'T|' : 'BAD|';
echo $sets275execution === 3 && $gets275execution === 4 ? 'C|' : 'BAD|';
echo 'Z|';
