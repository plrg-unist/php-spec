<?php
#[Deprecated('old',since:'8.5')]
const X=7;
set_error_handler(function($n){echo "H|",$n,"|",error_reporting()&$n,"|";return false;});
echo @X,"|";
