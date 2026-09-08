<?php
$a=["n"=>null,"f"=>false]; echo isset($a["n"])?"x":"N"; echo isset($a["f"])?"F":"x"; echo empty($a["missing"])?"E":"x"; echo $a["n"]??"C"; echo $a["f"]??"x";
