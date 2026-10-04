<?php
set_error_handler(function(){unset($GLOBALS['x']);return true;});
$x=NAN;$o=(object)$x;$a=(array)$o;$n=['scalar'=>null];$p=(object)$n;
$again=(object)$o->scalar;$hit=isset($o?->scalar);
