<?php
$object = new stdClass();
$scalar = 'S|';
function globalRetirementFinalOB01(string $bytes, int $phase): string {
    global $object, $scalar;
    return ($object === null ? 'gone|' : 'live|') . $scalar . '[' . $bytes . ']';
}
ob_start('globalRetirementFinalOB01', 0);
echo 'X|';
