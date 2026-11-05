<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('echo ;
class C{public int $x{foo{declare(encoding=1);return 1;}}}
declare(encoding=2);');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
