<?php
declare(strict_types=1);
function forceFinalOB01(string $bytes, string $phase): string {
    return 'F|' . ($phase === '9' ? 'weak' : 'BAD') . '|' . $bytes;
}
echo 'P|';
ob_start('forceFinalOB01', 0, 0);
echo "A\0B|";
