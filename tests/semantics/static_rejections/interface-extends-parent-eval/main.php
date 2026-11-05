<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval("interface I extends parent{}\ndeclare(encoding=1);\necho ;");} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
