"""An imported Trait method keeps its real Tick through callback abort/retry."""

CASES = {
    'review-imported-method-tick-abort-preserves-receiver-and-retry': (b'''<?php
$n=0;
function t(){
    global $n,$object;
    $n=$n+1;
    echo 'T';
    if($n===3){
        echo $object->other;
        throw new Exception('stop');
    }
}
register_tick_function('t');
declare(ticks=1);
trait TickMethod44 {
    public function run(){
        declare(ticks=1){echo 'M';}
        return $this->value;
    }
}
class TickUse44 {
    use TickMethod44;
    public $value=7,$other=9;
}
$object=new TickUse44;
try{echo $object->run();echo 'BAD';}
catch(Exception $e){echo 'C';}
echo $object->run();
echo 'Z';
''', b'TTMT9CTMT7TZT'),
}
