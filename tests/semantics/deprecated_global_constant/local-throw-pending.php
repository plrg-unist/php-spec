<?php
#[Deprecated("old")]const X=7;class D{function __destruct(){echo "D|";throw new Exception("local");}}set_error_handler(function(){echo "H|";$d=new D;exit;});try{echo X;}catch(Throwable $e){echo "C|";}echo "A|";
