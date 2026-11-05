<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval("trait T{function f(){}}\nclass C{use T{f as final g;}}\ndeclare(encoding=2);\necho ;");} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
