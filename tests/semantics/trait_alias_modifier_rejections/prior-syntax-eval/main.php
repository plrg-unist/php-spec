<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval("echo ;\ntrait T{function f(){}}\nclass C{use T{f as readonly g;}}\ndeclare(encoding=2);");} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
