"""Inherited method defaults keep lexical Closure scope and callback authority."""

SOURCE = b'''<?php
$n=0;
function t(){
    global $n,$receiver;
    $n=$n+1;
    echo 'T';
    echo $receiver->value;
    if($n===1){throw new Exception('stop');}
}
class Parent50 {
    private const TOKEN='A';
    public $value=9;
    public function take($cb=static function(){
        declare(ticks=1){echo self::TOKEN;}
        return get_called_class();
    }){return $cb;}
}
class Child50 extends Parent50 {}
register_tick_function('t');
$receiver=new Child50;
$a=$receiver->take();$b=$receiver->take();
echo $a===$b?'BAD':'F';
try{echo $a();}catch(Exception $e){echo 'C';}
echo $b();
echo $n;
echo 'Z';
'''

CASES = {
    'review-inherited-method-default-closure-lexical-scope-and-callback-abort':
        (SOURCE, b'FAT9CAT9Parent502Z'),
}
