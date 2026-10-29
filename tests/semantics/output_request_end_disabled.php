<?php
function disabledFinalOB01(string $bytes, int $phase): string|false {
    if (($phase & 8) !== 0) { return 'BAD|final-called|'; }
    return false;
}
ob_start('disabledFinalOB01', 2);
echo 'ab';
echo 'c';
