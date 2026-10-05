<?php
function precisionCompiledUnused($value) { return "${value}"; }
$value = 12.3456789;
echo 'P:', 12.3456789 . 'L', '|C:', (12.3456789 + 0) . 'L', '|V:', $value, '|';
