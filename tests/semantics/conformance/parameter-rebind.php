<?php
function f(&$x,&$y) { $x=&$y; $x=9; } $a=1; $b=2; f($a,$b); echo $a,$b;
