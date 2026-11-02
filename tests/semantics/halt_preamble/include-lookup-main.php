<?php
$n = "__COMPILER_HALT_OFFSET__";
echo "M|", (int)defined($n), "|";
$v = include __DIR__ . "/child-lookup.php";
echo "R", $v, "|", (int)defined($n), "|";
