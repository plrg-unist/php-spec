<?php
$next = 'old';
set_error_handler(function ($level, $message, $file, $line) { global $missing, $next; echo 'H:', $line, '|'; $missing = 'defined'; $next = 'new'; return true; });
echo "{$missing}", '|';
unset($missing); $next = 'old';
echo "{$missing}{$next}", '|';
unset($missing); $next = 'old';
echo "P{$missing}{$next}", '|END';
