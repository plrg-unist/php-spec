<?php
$n = 23; $f = 1.25; $yes = true; $no = false; $nil = null;
echo "$n|$f|$yes|$no|$nil|", "{$n}";
echo <<<TEXT

H:$n/$yes/$nil
TEXT;
echo '|END';
