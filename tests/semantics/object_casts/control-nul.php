<?php
$source=['first'=>1,"\0bad"=>2];$object=(object)$source;
set_error_handler(function($level,$message){
    echo 'H:',$level,':',$message,'|';
    return true;
});
foreach($object as $key=>&$value){
    if($key==='first'){
        $copy=clone $object;
        echo 'first:',$value,'|';
    }else{
        $value=3;
        echo 'nul:',$value,'|';
    }
}
unset($value);
restore_error_handler();
$array=(array)$copy;
echo $array["\0bad"],':',$copy->first,'|END';
