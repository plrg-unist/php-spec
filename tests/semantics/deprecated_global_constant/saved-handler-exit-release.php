<?php
#[Deprecated("old")]const X=7;class D{function __destruct(){echo "D|",X,"|";}}function b(){echo "B|";return true;}$d=new D;set_error_handler(function()use($d){echo "H|";set_error_handler("b");exit;});unset($d);register_shutdown_function(function(){echo "S|",X,"|";});echo X;
