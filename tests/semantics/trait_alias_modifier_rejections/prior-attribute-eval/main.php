<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval("trait T{function f(){}}\n#[A(function(){declare(encoding=1);})] class C{use T{f as readonly g;}}\ndeclare(encoding=2);\necho ;");} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
