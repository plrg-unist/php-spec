<?php
#[Deprecated]const X=[1];set_error_handler(function(){echo "H|";throw new Exception("stop");});$v=99;try{$v=X;}catch(Exception $e){echo "C|",$v,"|";}echo "A|";
