<?php
$a=1; $f=function()use($a){echo $a;}; $g=function()use(&$a){echo $a;}; $h=fn()=>$a; $a=2; $f();$g();echo $h();
