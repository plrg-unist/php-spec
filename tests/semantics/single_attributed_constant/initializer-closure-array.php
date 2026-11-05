<?php
#[A]
const X=[static function(){return 2;},static function(){return 3;}];
$f=X[0];$g=X[1];echo $f(),$g();
