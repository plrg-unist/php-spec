<?php
$x=1;$a=[&$x];$b=$a;unset($x);$b[0]=2;echo $a[0],$b[0];
