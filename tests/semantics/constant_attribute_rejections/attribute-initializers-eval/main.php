<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('#[A(function(){declare(encoding=1);})] const X=(function(){declare(encoding=2);}),Y=(function(){declare(encoding=3);});
declare(encoding=4);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
