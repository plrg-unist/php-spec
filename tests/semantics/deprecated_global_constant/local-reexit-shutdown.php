<?php
#[Deprecated("old")]const X=7;class D{function __destruct(){echo "D|";exit(7);}}register_shutdown_function(function(){echo "S|",X,"|";});set_error_handler(function(){echo "H|";$d=new D;exit(3);});echo X;
