<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('class C{function __construct(public int $x {get(){declare(encoding=1);return 1;}}){}}
declare(encoding=2);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
