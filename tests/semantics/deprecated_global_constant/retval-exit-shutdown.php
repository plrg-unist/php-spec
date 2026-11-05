<?php
#[Deprecated("old")]const X=7;class D{function __destruct(){echo "D|";exit;}}register_shutdown_function(function(){echo "S|",X,"|";});set_error_handler(function(){echo "H|";return new D;});echo X;
