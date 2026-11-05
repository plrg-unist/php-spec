<?php
set_error_handler(function($n,$s){echo "HANDLER|";return true;});
echo "M|";
try { include __DIR__."/unit.php"; echo "BAD|"; } catch (Throwable $e) { echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|"; } finally { echo "F|"; }
echo "A|";
