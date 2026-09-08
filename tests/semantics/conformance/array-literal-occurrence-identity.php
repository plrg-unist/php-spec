<?php
for ($i = 0; $i < 2; $i++) {
    $a = [NAN];
    if ($i === 0) { $first = $a; }
    else { echo $first === $a ? "1" : "0"; }
}
$b = [NAN];
$c = [NAN];
echo $b === $c ? "1" : "0";
