<?php
set_error_handler(function($n,$s){echo "HANDLER|";return true;});
echo "M|";
try { eval("declare(\n encoding=true,\n Foo=function(){\n  declare(encoding=1\n  );\n }\n);"); echo "BAD|"; } catch (Throwable $e) { echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|"; } finally { echo "F|"; }
echo "A|";
