<?php
$x=1;$a=[&$x,&$x];unset($x);$b=$a;$b[0]=2;echo $a[0],$a[1],$b[0],$b[1];
