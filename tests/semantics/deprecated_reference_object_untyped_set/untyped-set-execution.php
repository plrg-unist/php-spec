<?php
namespace Ns267UntypedSetExecution;
class Box267 {
    public $tag = 17 {
        set {
            echo 'S|';
            $this->tag = $value;
        }
    }
}
$box267 = new Box267();
echo $box267->tag === 17 ? 'D|' : 'BAD|';
$result267 = $box267->tag = false;
echo $result267 === false && $box267->tag === false ? 'B|' : 'BAD|';
$result267 = $box267->tag = 23;
echo $result267 === 23 && $box267->tag === 23 ? 'I|' : 'BAD|';
$result267 = $box267->tag = 'plain';
echo $result267 === 'plain' && $box267->tag === 'plain' ? 'T|' : 'BAD|';
echo 'Z|';
