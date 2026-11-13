<?php
namespace Ns269UntypedShortSetExplicitExecution;
class Box269 {
    public $tag = 17 {
        set($input269) => ($GLOBALS['count269execution'] = $GLOBALS['count269execution'] + 1) ? ($input269 === false ? true : $input269) : $input269;
    }
}
$count269execution = 0;
$box269 = new Box269();
echo $box269->tag === 17 ? 'D|' : 'BAD|';
$result269 = $box269->tag = false;
echo $result269 === false && $box269->tag === true && $count269execution === 1 ? 'B|' : 'BAD|';
$result269 = $box269->tag = 23;
echo $result269 === 23 && $box269->tag === 23 && $count269execution === 2 ? 'I|' : 'BAD|';
$result269 = $box269->tag = 'plain';
echo $result269 === 'plain' && $box269->tag === 'plain' && $count269execution === 3 ? 'T|' : 'BAD|';
echo $count269execution === 3 ? 'C|' : 'BAD|';
echo 'Z|';
