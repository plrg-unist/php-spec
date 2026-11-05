<?php
set_error_handler(function(){echo "W|";return true;});
#[A] const X=1;
#[B] const X=2;
echo X;
