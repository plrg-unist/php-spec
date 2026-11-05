<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('#[A(function(){declare(encoding=1);})] const X=1,Y=2;
class C{readonly function f(){declare(encoding=2);}}
declare(encoding=3);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
