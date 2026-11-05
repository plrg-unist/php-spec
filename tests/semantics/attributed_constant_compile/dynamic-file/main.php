<?php
set_error_handler(function(){echo "H|";return true;});
echo "M|";
try {include __DIR__ . "/unit.php";}catch(Throwable $e){echo "C|";}finally{echo "F|";}echo "A|";
