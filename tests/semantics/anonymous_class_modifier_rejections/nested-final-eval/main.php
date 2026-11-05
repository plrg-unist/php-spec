<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('$o=new class(function(){declare(encoding=1);return new final class{function f(){declare(encoding=2);}};}){};
declare(encoding=3);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
