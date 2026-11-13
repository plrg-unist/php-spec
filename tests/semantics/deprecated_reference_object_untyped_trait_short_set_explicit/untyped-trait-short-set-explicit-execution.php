<?php
namespace Ns272UntypedTraitShortSetExplicitExecution;
trait Tag272 {
    public $tag = 17 {
        set($input272) => ($GLOBALS['count272execution'] = $GLOBALS['count272execution'] + 1) ? ($input272 === false ? true : $input272) : $input272;
    }
}
class Box272 {
    use Tag272;
}
$count272execution = 0;
$box272 = new Box272();
echo $box272->tag === 17 ? 'D|' : 'BAD|';
$result272 = $box272->tag = false;
echo $result272 === false && $box272->tag === true && $count272execution === 1 ? 'B|' : 'BAD|';
$result272 = $box272->tag = 23;
echo $result272 === 23 && $box272->tag === 23 && $count272execution === 2 ? 'I|' : 'BAD|';
$result272 = $box272->tag = 'plain';
echo $result272 === 'plain' && $box272->tag === 'plain' && $count272execution === 3 ? 'T|' : 'BAD|';
echo $count272execution === 3 ? 'C|' : 'BAD|';
echo 'Z|';
