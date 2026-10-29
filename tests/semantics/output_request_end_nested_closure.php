<?php
echo 'P|';
ob_start();
$prefix = 'C|';
$handler = function (string $bytes, int $phase) use ($prefix): string {
    return $prefix . $phase . '|' . ob_get_level() . '|' .
           ob_get_length() . '|[' . $bytes . ']';
};
ob_start($handler, 0);
$handler = null;
echo 'A|';
