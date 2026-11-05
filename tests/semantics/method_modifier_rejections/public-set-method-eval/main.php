<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval("class C{public(set) function f(){declare(encoding=1);}}\ndeclare(encoding=2);\necho ;");} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
