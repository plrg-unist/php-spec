<?php
#[Deprecated('old',since:'8.5')]
const X=7;
set_error_handler(function(){echo "H|";throw new Exception("stop");});try{constant("X");}catch(Throwable $e){echo "C|";}set_error_handler(function(){echo "R|";return true;});echo constant("X"),"|";
