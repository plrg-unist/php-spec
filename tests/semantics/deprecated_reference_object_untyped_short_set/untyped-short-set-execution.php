<?php
namespace Ns268UntypedShortSetExecution;
class Box268 {
    public $tag = 17 {
        set => ($GLOBALS['count268execution'] = $GLOBALS['count268execution'] + 1) ? $value : $value;
    }
}
$count268execution = 0;
$box268 = new Box268();
echo $box268->tag === 17 ? 'D|' : 'BAD|';
$result268 = $box268->tag = false;
echo $result268 === false && $box268->tag === false && $count268execution === 1 ? 'B|' : 'BAD|';
$result268 = $box268->tag = 23;
echo $result268 === 23 && $box268->tag === 23 && $count268execution === 2 ? 'I|' : 'BAD|';
$result268 = $box268->tag = 'plain';
echo $result268 === 'plain' && $box268->tag === 'plain' && $count268execution === 3 ? 'T|' : 'BAD|';
echo $count268execution === 3 ? 'C|' : 'BAD|';
echo 'Z|';
