<?php
function exitFinalOB01(string $bytes, int $phase): string {
    return 'H|' . $phase . '|[' . $bytes . ']';
}
ob_start();
ob_start('exitFinalOB01', 0);
echo 'A|';
exit(7);
echo 'BAD|';
