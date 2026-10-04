<?php
$object=(object)['gone'=>0,'left'=>1,'right'=>2];
unset($object->gone);
foreach($object as $key=>$value){
    echo $key,':',$value,'|';
    if($key==='left'){
        $copy=clone $object;
        $array=(array)$object;
        $object->right=3;
        $object->late=4;
    }
}
echo $copy->right,':',$array['right'],'|';
$selected='old';
$source=["\0bad"=>&$selected,'tail'=>'old'];
$object=(object)$source;
set_error_handler(function($level,$message)use(&$selected,&$object,&$copy){
    echo 'H:',$level,':',$message,'|';
    $selected='new';
    $copy=clone $object;
    $object->tail='changed';
    return true;
});
foreach($object as $key=>$value){
    echo ($key==="\0bad"?'nul':$key),':',$value,'|';
}
restore_error_handler();
echo $source['tail'],':',$selected,'|END';
