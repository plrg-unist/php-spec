<?php
namespace Ns271UntypedTraitSetExplicitExecution;
trait Tag271 {
    public $tag = 17 {
        set($input271) {
            $GLOBALS['count271execution'] = $GLOBALS['count271execution'] + 1;
            $this->tag = $input271 === false ? true : $input271;
        }
    }
}
class Box271 {
    use Tag271;
}
$count271execution = 0;
$box271 = new Box271();
echo $box271->tag === 17 ? 'D|' : 'BAD|';
$result271 = $box271->tag = false;
echo $result271 === false && $box271->tag === true && $count271execution === 1 ? 'B|' : 'BAD|';
$result271 = $box271->tag = 23;
echo $result271 === 23 && $box271->tag === 23 && $count271execution === 2 ? 'I|' : 'BAD|';
$result271 = $box271->tag = 'plain';
echo $result271 === 'plain' && $box271->tag === 'plain' && $count271execution === 3 ? 'T|' : 'BAD|';
echo $count271execution === 3 ? 'C|' : 'BAD|';
echo 'Z|';
