<?php
$a = [$x => &$x];
echo $a[""] === null;
