<?php
set_error_handler(function() { unset($GLOBALS['value']); return true; });
$value = NAN;
$object = (object)$value;
restore_error_handler();
$array = (array)$object;
echo ($object->scalar === null ? 'PN' : 'PU'), '|';
echo (isset($object->scalar) ? 'PI' : 'PX'), '|';
echo ($array['scalar'] === null ? 'AN' : 'AU'), '|';
echo (isset($array['scalar']) ? 'AI' : 'AX'), '|';
echo ($array === ['scalar' => null] ? 'equal-null' : 'distinct-null'), '|';
$seen = '';
foreach ($array as $key => $item) { $seen = $seen . $key; }
echo ($seen === '' ? 'skip' : 'bad'), '|';
$copy = $array;
$copy['other'] = 1;
echo (isset($copy['scalar']) ? 'CI' : 'CX'), '|';
echo $copy['other'], '|';
echo (isset($array['scalar']) ? 'AI' : 'AX'), '|';
echo (isset($object->scalar) ? 'PI' : 'PX'), '|END';
