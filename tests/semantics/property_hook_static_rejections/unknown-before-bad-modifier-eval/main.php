<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('declare(encoding=1);
class C{public int $x{foo=>1; public get=>2;}}
declare(encoding=3);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
