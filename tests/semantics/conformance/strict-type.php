<?php
declare(strict_types=1); function f(int $x):int{return $x;} try{f("12");}catch(TypeError $e){echo "T";}
