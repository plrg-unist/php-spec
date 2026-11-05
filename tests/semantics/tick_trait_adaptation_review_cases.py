"""An aliased method Tick exposes its alias name while retaining source state."""

CASES = {
    'review-aliased-method-tick-source-name-and-callback-abort': (b'''<?php
$n=0;
function t(){
    global $n,$object;
    $n=$n+1;
    echo 'T';
    if($n===3){
        $at=new Exception;
        echo $at->getTrace()[1]['function'];
        echo $object->other;
        throw new Exception('stop');
    }
}
register_tick_function('t');
declare(ticks=1);
trait TickMethod45 {
    public function run(){
        declare(ticks=1){echo 'M';}
        return $this->value;
    }
}
class TickUse45 {
    use TickMethod45 { run as aliased; }
    public $value=7,$other=9;
}
$object=new TickUse45;
try{echo $object->aliased();echo 'BAD';}
catch(Exception $e){echo 'C';}
echo $object->aliased();
echo 'Z';
''', b'TTMTaliased9CTMT7TZT'),
}
