<?php
#[Deprecated('old',since:'8.5')]
const X=7;
set_error_handler(function(){echo "H|";error_reporting(0);return false;});
echo X,"|";
