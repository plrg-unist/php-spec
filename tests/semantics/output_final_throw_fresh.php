<?php
function freshFinalOB02(string $bytes, int $phase): string {
    throw new Exception('fresh-final');
}
ob_start('freshFinalOB02', 0);
echo 'T|';
