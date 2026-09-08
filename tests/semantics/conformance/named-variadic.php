<?php
function f($a,$b=2,...$rest){echo $a,$b;foreach($rest as $k=>$v)echo $k,":",$v;} f(b:4,a:3,z:5);
