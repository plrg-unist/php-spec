<?php
class LeftText { public function __toString() { global $left, $right; $left = 17; $right = 'changed'; echo 'C|'; return 'left'; } }
$left = new LeftText; $right = 'old';
echo "{$left}{$right}", '|', $left, '|';
$left = new LeftText; $right = 'old';
echo "P{$left}{$right}", '|', $left, '|END';
