<?php
$s="9999999999999999999e+";$r=$s+0;echo $r===PHP_INT_MIN,":",$r===PHP_INT_MAX,":",$r===($r+0.0);
