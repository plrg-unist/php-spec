<?php
namespace Ns273UntypedTraitImplicitSetExecution;
trait Tag273 {
    public $tag = 17 {
        set {
            $GLOBALS['count273execution'] = $GLOBALS['count273execution'] + 1;
            $this->tag = $value === false ? true : $value;
        }
    }
}
class Box273 {
    use Tag273;
}
$count273execution = 0;
$box273 = new Box273();
echo $box273->tag === 17 ? 'D|' : 'BAD|';
$result273 = $box273->tag = false;
echo $result273 === false && $box273->tag === true && $count273execution === 1 ? 'B|' : 'BAD|';
$result273 = $box273->tag = 23;
echo $result273 === 23 && $box273->tag === 23 && $count273execution === 2 ? 'I|' : 'BAD|';
$result273 = $box273->tag = 'plain';
echo $result273 === 'plain' && $box273->tag === 'plain' && $count273execution === 3 ? 'T|' : 'BAD|';
echo $count273execution === 3 ? 'C|' : 'BAD|';
echo 'Z|';
