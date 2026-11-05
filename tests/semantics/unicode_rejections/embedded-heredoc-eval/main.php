<?php
set_error_handler(function($n,$s){echo "HANDLER|";return true;});
echo "M|";
try { eval("declare(encoding=1);\n\$x=<<<TXT\n{\$a[(function(){\n declare(encoding=2);\n return 0;\n})()]}\\u{}\nTXT;\ndeclare(encoding=3);\necho ;"); echo "BAD|"; } catch (Throwable $e) { echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|"; } finally { echo "F|"; }
echo "A|";
