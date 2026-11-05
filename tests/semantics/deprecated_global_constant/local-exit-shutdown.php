<?php
#[Deprecated("old")]const X=7;register_shutdown_function(function(){echo "S|",X,"|";});class R{function __destruct(){echo "D|";trigger_error("local",E_USER_WARNING);}}set_error_handler(function($n){if($n===E_USER_WARNING){echo "BAD|";return true;}$x=new R;echo "H|";exit;});echo X;
