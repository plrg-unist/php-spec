<?php
$x = 1;
$a = [&$x];
unset($x);
$b = $a + [1 => 2];
$b[0] = 9;
echo $a[0], $b[0];
