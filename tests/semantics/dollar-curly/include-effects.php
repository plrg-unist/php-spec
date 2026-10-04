<?php
$n=0;
set_error_handler(function($level,$message,$file,$line){global $n;++$n;echo 'H'.$n.':'.$line.'|';if($n===1){error_reporting(0);ini_set('display_errors','stdout');}elseif($n===2){error_reporting(8192);}return false;});
include __DIR__.'/included-multiline.php';
echo '|DONE';
