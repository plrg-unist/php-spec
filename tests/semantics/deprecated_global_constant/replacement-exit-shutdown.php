<?php
#[Deprecated("old")]const X=7;register_shutdown_function(function(){echo "S|",X,"|";});set_error_handler(function(){echo "H|";set_error_handler(function(){echo "N|",error_reporting(),"|";return false;});error_reporting(0);exit;});echo X;
