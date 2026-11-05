<?php
#[Deprecated("old")]const X=7;const Y=9;$f=constant(...);$name="X";set_error_handler(function()use(&$name){$name="Y";echo "H|";return true;});echo $f($name),"|",$f($name),"|";
