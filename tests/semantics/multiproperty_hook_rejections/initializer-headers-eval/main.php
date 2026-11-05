<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('class C{public $p=(function(){declare(encoding=1);}),$q=(function(){declare(encoding=2);}) {
get{declare(encoding=3);return 1;}
}}
declare(encoding=4);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
