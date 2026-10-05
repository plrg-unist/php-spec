<?php
$value = 12.3456789;
echo 'B:', ini_get('precision'), '|', (string) $value, '|', (12.3456789 . 'L'), '|';
ini_set('precision', '1');
echo 'R:', (string) $value, '|', (12.3456789 . 'L'), '|';
eval('echo "E:", (12.3456789 . "L"), "|END";');
