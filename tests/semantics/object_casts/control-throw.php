<?php
set_error_handler(function(){throw new Exception('stop');});
$o=(object)["\0bad"=>2];
try{foreach($o as $key=>$value){echo 'unexpected';}}catch(Exception $e){echo $e->getMessage(),'|';}
restore_error_handler();echo 'END';
