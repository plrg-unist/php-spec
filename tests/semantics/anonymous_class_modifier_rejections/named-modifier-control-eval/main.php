<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('abstract class C{function f(){declare(encoding=1);}} final class D{function g(){declare(encoding=2);}}
declare(encoding=3);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
