<?php
$a=["x"=>null,"y"=>false]; $a["x"]??=3; $a["y"]??=4; echo $a["x"],$a["y"]===false?"F":"X";
