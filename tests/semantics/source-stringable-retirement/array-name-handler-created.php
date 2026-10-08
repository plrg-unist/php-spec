<?php
$count350 = 0;
function warning350($c, $m, $f, $l) { global $count350; $count350++; echo 'W:', $count350, ':', $l, ':', $m, '|'; if ($count350 === 1) { $GLOBALS['missing350'] = []; } else { $GLOBALS['Array'] = 'LIVE'; } return true; }
set_error_handler('warning350');
echo 'R:', ${$missing350}, '|END';
