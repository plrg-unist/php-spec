<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('declare(encoding=1);
$o=new #[A(function(){declare(encoding=2);})] final class(function(){declare(encoding=3);}){function f(){declare(encoding=4);}};
declare(encoding=5);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
