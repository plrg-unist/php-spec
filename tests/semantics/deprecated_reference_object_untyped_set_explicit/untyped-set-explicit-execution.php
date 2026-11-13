<?php
namespace Ns270UntypedSetExplicitExecution;
class Box270 {
    public $tag = 17 {
        set($input270) {
            $GLOBALS['count270execution'] = $GLOBALS['count270execution'] + 1;
            $this->tag = $input270 === false ? true : $input270;
        }
    }
}
$count270execution = 0;
$box270 = new Box270();
echo $box270->tag === 17 ? 'D|' : 'BAD|';
$result270 = $box270->tag = false;
echo $result270 === false && $box270->tag === true && $count270execution === 1 ? 'B|' : 'BAD|';
$result270 = $box270->tag = 23;
echo $result270 === 23 && $box270->tag === 23 && $count270execution === 2 ? 'I|' : 'BAD|';
$result270 = $box270->tag = 'plain';
echo $result270 === 'plain' && $box270->tag === 'plain' && $count270execution === 3 ? 'T|' : 'BAD|';
echo $count270execution === 3 ? 'C|' : 'BAD|';
echo 'Z|';
