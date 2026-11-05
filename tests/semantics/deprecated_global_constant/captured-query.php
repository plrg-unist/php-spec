<?php
#[Deprecated('old',since:'8.5')]
const X=7;
const Y=9;$name="X";set_error_handler(function()use(&$name){$name="Y";echo "H|";return true;});echo constant($name),"|",constant($name),"|";
