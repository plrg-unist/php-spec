<?php
function tailFinalOB01(string $bytes, int $phase): string {
    return '[' . $phase . ':' . $bytes . ']';
}
ob_start('tailFinalOB01', 2);
echo 'ab';
echo 'c';
