<?php
set_error_handler(function(){echo "H|";return true;});
echo "M|";
try {eval('#[A]
const X=1,Y=2;');}catch(Throwable $e){echo "C|";}finally{echo "F|";}echo "A|";
