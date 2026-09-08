<?php
function &f(&$x){return $x;} $a=1; $b=&f($a); $b=8; echo $a,$b;
