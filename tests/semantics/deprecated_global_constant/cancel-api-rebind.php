<?php
#[Deprecated("old")]const X=7;const Y=9;class D{function __destruct(){echo "D|";throw new Exception("local");}}$name="X";$v=99;set_error_handler(function()use(&$name){$name="Y";echo "H|";$d=new D;exit;});try{$v=constant($name);}catch(Exception $e){echo "C|",$name,"|",$v,"|";}echo "A|",constant($name),"|";
