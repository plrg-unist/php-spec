<?php
set_error_handler(function($n,$s){echo "HANDLER|";return true;});
echo "M|";
try { include_once __DIR__."/unit.php"; echo "BAD|"; } catch (Throwable $e) { echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|"; } finally { echo "F|"; }
echo (int)(include_once __DIR__."/unit.php"),"|";
try { include __DIR__."/unit.php"; echo "BAD|"; } catch (Throwable $e) { echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|"; } finally { echo "F|"; }
echo "A|";
