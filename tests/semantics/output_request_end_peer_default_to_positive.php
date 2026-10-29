<?php
function lowerPositiveOB01(string $bytes, int $phase): string {
    return '[' . $phase . ':' . $bytes . ']';
}
ob_start('lowerPositiveOB01', 2);
ob_start();
echo 'ab';
