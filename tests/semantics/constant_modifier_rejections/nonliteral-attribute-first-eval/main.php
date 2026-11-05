<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval("class C{#[A(function(){declare(encoding=1,encoding=true);})] abstract const X=(function(){declare(encoding=2);});}\ndeclare(encoding=3);\necho ;");} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
