<?php
function warning350($c, $m, $f, $l) { echo 'W:', $l, ':', $m, '|'; $GLOBALS['name350'] = 'other350'; $GLOBALS['Array'] = 'GLOBAL-WRITE'; return false; }
function local350() { $name350 = []; $Array = 'LOCAL'; return ${$name350}; }
set_error_handler('warning350');
$name350 = []; $Array = 'GLOBAL'; $other350 = 'WRONG';
echo 'R:', local350(), '|G:', $Array, '|END';
