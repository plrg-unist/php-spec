<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('class A{public int $x{}}
declare(encoding=1);
class B{public int $y{public get=>2;}}
declare(encoding=3);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
