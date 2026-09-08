<?php
$n = "x";
$a = [$n => &${$n = "y"}];
echo $a["y"] === null;
