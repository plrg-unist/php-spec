<?php
function emptyFinalOB01(string $bytes, int $phase): string {
    return '[' . $phase . ':' . $bytes . ']';
}
ob_start('emptyFinalOB01', 2);
echo 'ab';
