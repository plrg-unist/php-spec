<?php
set_error_handler(function(){echo "H|";throw new Exception("stop");});try{echo E_STRICT;}catch(Throwable $e){echo "C|";}restore_error_handler();error_reporting(0);echo E_STRICT,"|";
