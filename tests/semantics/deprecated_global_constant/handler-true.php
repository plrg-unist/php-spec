<?php
#[Deprecated('old',since:'8.5')]
const X=7;
set_error_handler(function($n,$m,$f,$l){echo "H|",$n,"|",$m,"|",$f===__FILE__?"F|":"bad|",$l,"|";return true;});
echo X,"|";
