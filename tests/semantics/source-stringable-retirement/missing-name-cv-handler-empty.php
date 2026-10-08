<?php
function warning339($c, $m, $f, $l) { echo 'W:', $l, ':', $m, '|'; $GLOBALS[''] = 'EMPTY-LIVE'; return true; }
set_error_handler('warning339');
echo 'R:', ${$missing339}, '|END';
