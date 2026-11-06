"""Short GET retains its receiver through a nested Closure Tick callback."""

SOURCE = b'''<?php
$n=0;
function t(){
    global $n,$object;
    $n=$n+1;
    echo 'T';
    echo $object->other;
    if($n===1){unset($GLOBALS['object']);echo 'R';throw new Exception('stop');}
}
class ShortGet51 {
    public $other=7;
    public int $value {
        get => (function(){
            declare(ticks=1){echo 'G';}
            return $this->other;
        })();
    }
    public function __destruct(){echo 'D';}
}
register_tick_function('t');
$object=new ShortGet51;
try{echo $object->value;}catch(Exception $e){echo 'C';}
$object=new ShortGet51;
echo $object->value;
unset($object);
echo 'Z';
'''

CASES = {
    'review-short-get-nested-tick-retains-receiver-through-abort-and-retry':
        (SOURCE, b'GT7RDCGT77DZ'),
}
