<?php
set_error_handler(function($n,$m){echo $n,"|",$m,"|";return true;});const X=1;#[Deprecated('second')]
const X=2;
echo X,"|";
