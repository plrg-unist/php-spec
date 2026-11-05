<?php
#[Deprecated('old',since:'8.5')]
const X=7;
$v=99;set_error_handler(function(){echo "H|";throw new Exception("stop");});try{$v=X;}catch(Throwable $e){echo "C|",$v,"|";}set_error_handler(function(){echo "R|";return true;});echo X,"|";
