<?php
function lowOB01(string $bytes, int $phase): string {
    echo 'L:', $phase, ':', ob_get_level(), '|';
    return '<' . $bytes . '>';
}
function highOB01(string $bytes, int $phase): string {
    echo 'U:', $phase, ':', ob_get_level(), '|';
    return '{' . $bytes . '}';
}
ob_start('lowOB01', 0);
ob_start('highOB01', 2);
echo 'ab';
echo 'c';
