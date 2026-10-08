<?php
$count350 = 0;
function warning350($c, $m, $f, $l) { global $count350; $count350++; echo 'W:', $count350, ':', $l, ':', $m, '|'; if ($count350 === 1) { $GLOBALS['name350'] = 'other350'; } else { $GLOBALS['Array'] = 'LATE'; } return true; }
set_error_handler('warning350');
$other350 = 'WRONG'; $name350 = [];
echo 'R:', ${$name350}, '|T:', $Array, '|END';
