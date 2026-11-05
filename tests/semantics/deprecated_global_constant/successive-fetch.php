<?php
#[Deprecated('old',since:'8.5')]
const X=7;
set_error_handler(function(){echo "H|";return true;});echo X,"|",constant("X"),"|",X,"|";
