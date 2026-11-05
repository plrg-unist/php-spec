<?php
set_error_handler(function($n,$s){echo "HANDLER|";return true;});
echo "M|";
try { eval("declare(encoding=1);\n\$x=<<<STR\n\\u{110000}\nSTR;\ndeclare(encoding=2);\necho ;"); echo "BAD|"; } catch (Throwable $e) { echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|"; } finally { echo "F|"; }
echo "A|";
