<?php
#[AllowDynamicProperties]
class MixedSingleton116 { public int $declared = 1; }
echo 'U:';
$source = new MixedSingleton116();
$source->extra = 1;
$alias =& $source->extra;
unset($alias);
foreach ($source as $key => $value) {}
unset($key, $value);
$copy = clone $source;
$copy->extra = 7;
echo $source->extra, '/', $copy->extra, '|';
$source->extra = 9;
echo $source->extra, '/', $copy->extra, '|';
$copy->declared = 2;
foreach ($copy as $key => $value) { echo $key, ':', $value, '|'; }
unset($key, $value, $source, $copy);
echo 'E|';
