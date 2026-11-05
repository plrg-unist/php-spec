<?php
#[Deprecated("old")]const X=7;const Y=9;class D{function __destruct(){echo "D|";throw new Exception("local");}}$f=constant(...);$name="X";$v=99;set_error_handler(function()use(&$name,&$f){$name="Y";$f=null;echo "H|";$d=new D;exit;});try{$v=$f($name);}catch(Exception $e){echo "C|",$name,"|",$v,"|";if($f===null){echo "cleared|";}}echo "A|",constant($name),"|";
