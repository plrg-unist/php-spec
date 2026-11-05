<?php
#[Deprecated('old',since:'8.5')]
const X=7;
#[Deprecated('other')]
const Y=8;
set_error_handler(function(){echo "H|",Y,"|",constant("X"),"|";return false;});
echo constant("X"),"|";
