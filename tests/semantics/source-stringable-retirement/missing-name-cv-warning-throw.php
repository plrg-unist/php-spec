<?php
function warning339($c, $m, $f, $l) { global $missing339, $target339; echo 'W:', $l, ':', $m, '|'; $missing339 = 'target339'; $target339 = 'WRITTEN'; throw new Exception('stop'); }
set_error_handler('warning339');
try { echo 'R:', ${$missing339}, '|AFTER|'; } catch (Throwable $e) { echo 'CAUGHT|'; }
echo 'G:', $missing339, ':', $target339, '|END';
