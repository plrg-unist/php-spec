<?php
function precisionTrace($argument) {
    return new Exception('held');
}
$value = 1.23456789;
$trace = precisionTrace(12.3456789);
echo 'A:', ($value <=> '1.22junk'), ':', ($value <=> '1.23'), '|', $trace->getTraceAsString(), '|';
ini_set('precision', '2');
echo 'B:', ($value <=> '1.22junk'), ':', ($value <=> '1.23'), '|', $trace->getTraceAsString(), '|';
ini_restore('precision');
echo 'R:', ($value <=> '1.22junk'), ':', ($value <=> '1.23'), '|', $trace->getTraceAsString(), '|END';
