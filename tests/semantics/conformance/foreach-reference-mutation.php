<?php
$a=[1,2]; foreach($a as $k=>&$v){echo $v; if($k===0)$a[]=3;} $v=9; echo ":"; foreach($a as $x)echo $x;
