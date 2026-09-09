<?php
$s="-9223372036854775809e+";$r=$s+0;echo $r===PHP_INT_MIN,":",$r===PHP_INT_MAX,":",$r===($r+0.0);
