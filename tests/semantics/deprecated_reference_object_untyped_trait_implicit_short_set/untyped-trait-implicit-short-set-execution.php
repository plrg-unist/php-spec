<?php
namespace Ns274UntypedTraitImplicitShortSetExecution;
trait Tag274 {
    public $tag = 17 {
        set => ($GLOBALS['count274execution'] = $GLOBALS['count274execution'] + 1) ? ($value === false ? true : $value) : $value;
    }
}
class Box274 {
    use Tag274;
}
$count274execution = 0;
$box274 = new Box274();
echo $box274->tag === 17 ? 'D|' : 'BAD|';
$result274 = $box274->tag = false;
echo $result274 === false && $box274->tag === true && $count274execution === 1 ? 'B|' : 'BAD|';
$result274 = $box274->tag = 23;
echo $result274 === 23 && $box274->tag === 23 && $count274execution === 2 ? 'I|' : 'BAD|';
$result274 = $box274->tag = 'plain';
echo $result274 === 'plain' && $box274->tag === 'plain' && $count274execution === 3 ? 'T|' : 'BAD|';
echo $count274execution === 3 ? 'C|' : 'BAD|';
echo 'Z|';
