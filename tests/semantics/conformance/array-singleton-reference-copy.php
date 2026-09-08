<?php
$x=1;$a=[&$x];unset($x);$b=$a;$b[0]=2;echo $a[0],$b[0];
