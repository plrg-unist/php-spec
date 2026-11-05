<?php
#[Deprecated("old")]const X=7;
set_error_handler(function(&$n){echo "H|",$n,"|";return true;});
echo constant("X"),"|";
