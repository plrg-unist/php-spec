<?php
$name="a"; $$name=4; $b=&$$name; $name="b"; $$name=7; echo $a,$b;
