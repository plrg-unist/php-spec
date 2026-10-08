<?php
function warning339($c, $m, $f, $l) { global $missing339, $target339; echo 'W:', $l, ':', $m, '|'; $missing339 = 'target339'; $target339 = 'FALLBACK-LIVE'; return false; }
set_error_handler('warning339');
echo 'R:', ${$missing339}, '|END';
