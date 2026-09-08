<?php
$x = 1;
$a = [&$x];
unset($x);
$b = [1 => 2] + $a;
$b[0] = 9;
echo $a[0], $b[0];
