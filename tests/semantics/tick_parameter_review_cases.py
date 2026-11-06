"""Received default Closures keep their own Tick plans through callback abort."""

SOURCE = b'''<?php
$v=1;$n=0;
function t(){
    global $n,$v;
    $n=$n+1;
    echo 'T';
    echo $v;
    if($n===1){throw new Exception('stop');}
}
function make49($cb=static function(){
    global $v;
    declare(ticks=1){$v=9;}
    return 7;
}){return $cb;}
register_tick_function('t');
$a=make49();$b=make49();
echo $a===$b?'BAD':'F';
try{echo $a();}catch(Exception $e){echo 'C';}
echo $b();
echo $n;
echo 'Z';
'''

CASES = {
    'review-fresh-parameter-default-closures-commit-before-tick-abort-and-retry':
        (SOURCE, b'FT9CT972Z'),
}
