<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('namespace N;
#[A,B] const X=1,Y=2,Z=3;
declare(encoding=1);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
