<?php
set_error_handler(function(){echo "HANDLER|";return true;});
echo "M|";
try {eval('#[A] const X=1; class C{#[A] const Y=1,Z=2;} const P=1,Q=2;
declare(encoding=1);
echo ;');} catch (Throwable $e) {echo get_class($e),"|",$e->getLine(),"|",$e->getMessage(),"|",$e->getFile(),"|";} finally {echo "F|";}
echo "A|";
