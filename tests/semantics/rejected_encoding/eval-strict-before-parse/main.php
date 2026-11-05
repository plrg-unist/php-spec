<?php
set_error_handler(function($n,$s){echo "HANDLER|";return true;});
echo "M|";
try { eval("declare(strict_types=2); declare(encoding=1); echo ;"); echo "BAD|"; } catch (Throwable $e) { echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|"; } finally { echo "F|"; }
echo "A|";
