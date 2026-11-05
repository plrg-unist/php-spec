<?php
#[Deprecated('old',since:'8.5')]
const X=7;
set_error_handler(function($n,$m){echo $n,"|",$m,"|";return true;});eval('echo X,"|",constant("X"),"|";');
