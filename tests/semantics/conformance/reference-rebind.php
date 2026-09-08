<?php
$a=1; $b=&$a; $c=2; $b=&$c; $b=3; echo $a, $b, $c;
