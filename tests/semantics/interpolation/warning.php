<?php
$next = 'old'; $arr = [1];
set_error_handler(function ($level, $message, $file, $line) { global $missing, $next, $arr; echo 'H:', $message, ':', $line, '|'; $missing = 'defined'; $next = 'new'; $arr = 'changed'; return true; });
echo "P{$missing}{$next}|", $missing, '|';
$arr = [1]; echo "P{$arr}|", $arr, '|';
$arr = [2]; $next = 'old';
echo "{$arr}{$next}", '|', $arr, '|END';
