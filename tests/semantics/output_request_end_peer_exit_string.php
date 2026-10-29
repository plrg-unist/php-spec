<?php
function finalExitOB01(string $bytes, int $phase): string {
    echo 'H:', $phase, '|';
    return '(' . $bytes . ')';
}
ob_start('finalExitOB01', 0);
echo 'A|';
exit('X|');
echo 'BAD|';
