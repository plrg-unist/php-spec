<?php
#[Deprecated("old")]const X=7;class D{function __destruct(){echo "D|";throw new Exception("fresh");}}set_error_handler(function(){echo "H|";$d=new D;exit(3);});try{echo X;}catch(Exception $e){echo "C|";}echo "A|";
