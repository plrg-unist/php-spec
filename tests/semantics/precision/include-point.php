<?php
set_error_handler(function($level,$message,$file,$line) {
    echo 'H:',$level,':',$line,'|';
    ini_set('precision','1tail');
    return true;
});
ini_set('precision','3tail');
$result=include __DIR__.'/included.php';
echo 'R:',$result,':',ini_get('precision'),'|';
restore_error_handler();
echo 'END';
