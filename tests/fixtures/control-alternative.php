<?php
if ($x): echo 1; elseif ($y): echo 2; else: echo 3; endif;
while ($x): break; endwhile;
for (;;): break; endfor;
foreach ($xs as $v): echo $v; endforeach;
switch ($x): ; case 1: break; default: break; endswitch;
declare(ticks=1): echo 1; enddeclare;
declare(ticks=1) { echo 1; }
declare(ticks=1);
