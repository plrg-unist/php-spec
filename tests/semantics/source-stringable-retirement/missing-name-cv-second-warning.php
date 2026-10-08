<?php
function warning339($c, $m, $f, $l) { echo 'W:', $l, ':', $m, '|'; if ($m === 'Undefined variable $') { $GLOBALS[''] = 'LATE'; } return true; }
set_error_handler('warning339');
echo 'R:', ${$missing339}, '|A:', $GLOBALS[''], '|END';
