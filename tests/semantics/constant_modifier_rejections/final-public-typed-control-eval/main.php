<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval("class C{final public const mixed X=(function(){declare(encoding=1);});}\ndeclare(encoding=2);\necho ;");} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
