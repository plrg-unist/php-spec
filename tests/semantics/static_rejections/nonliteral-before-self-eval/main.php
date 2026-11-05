<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval("declare(encoding=1,encoding=true);\nclass self{}\ndeclare(encoding=2);\necho ;");} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
