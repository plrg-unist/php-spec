<?php
function warning339($c, $m, $f, $l) { global $missing339, $target339; echo 'W:', $l, ':', $m, '|'; $missing339 = 'target339'; $target339 = 'GLOBAL'; return true; }
function local339() { ${''} = 'LOCAL-EMPTY'; echo 'R:', ${$missing339}, '|'; }
set_error_handler('warning339');
local339();
echo 'G:', $missing339, ':', $target339, '|END';
