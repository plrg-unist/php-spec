<?php
$v=1;$a=['x'=>&$v];unset($v);$o=(object)$a;$c=clone $o;
$o->x=2;$b=(array)$o;$b['x']=3;unset($a,$o,$c,$b);
