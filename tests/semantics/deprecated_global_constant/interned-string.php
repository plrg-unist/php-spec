<?php
#[Deprecated('old')]
const X="value";
set_error_handler(function(){echo "H|";return true;});const Y=X;echo Y,"|",constant("X"),"|";
