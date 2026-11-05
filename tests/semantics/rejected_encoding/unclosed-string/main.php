<?php
set_error_handler(function($n,$s){echo "HANDLER|";return true;});
echo "M|";
try { eval("declare(encoding=1);\n\"unfinished"); echo "BAD|"; } catch (Throwable $e) { echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|"; } finally { echo "F|"; }
echo "A|";
