<?php
#[Deprecated("old")]const X=7;register_shutdown_function(function(){echo "S|",X,"|";});set_error_handler(function(){echo "H|";exit;});echo X;
