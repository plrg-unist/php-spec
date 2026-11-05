<?php
register_shutdown_function(function(){echo "S|",E_STRICT,"|";});set_error_handler(function(){echo "H|";exit;});echo E_STRICT;
