<?php
#[Deprecated("old")]const X=7;class L{function __destruct(){echo "L|";throw new Exception("local");}}class R{function __destruct(){echo "R|",X,"|";}}function b(){echo "B|";return true;}$r=new R;set_error_handler(function()use($r){echo "H|";set_error_handler("b");$l=new L;exit;});unset($r);try{echo X;}catch(Exception $e){echo "C|",$e->getMessage(),"|";}echo "A|",X,"|";
