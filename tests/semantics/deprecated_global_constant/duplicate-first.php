<?php
set_error_handler(function($n,$m){echo $n,"|",$m,"|";return true;});
#[Deprecated('first')]
const X=1;
#[Deprecated('second')]
const X=2;
echo constant("X"),"|";
