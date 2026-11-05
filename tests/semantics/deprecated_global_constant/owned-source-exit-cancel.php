<?php
#[Deprecated]const X=[1];class D{function __destruct(){echo "D|";throw new Exception("local");}}set_error_handler(function(){echo "H|";$d=new D;exit;});$v=99;try{$v=X;}catch(Exception $e){echo "C|",$v,"|";}echo "A|";
