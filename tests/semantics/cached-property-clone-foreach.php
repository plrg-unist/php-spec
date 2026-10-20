<?php
class CachedForeach110 { public int $a = 1; public int $b = 10; }
$source = new CachedForeach110();
foreach ($source as $value) {}
unset($value);
echo 'F:';
$copy = clone $source;
$copy->a = 2;
$source->b = 30;
foreach ($copy as $key => $value) { echo $key, ':', $value, '|'; }
unset($key, $value);
echo 'S|';
foreach ($source as $key => $value) { echo $key, ':', $value, '|'; }
unset($key, $value);
unset($copy->a);
echo 'U|';
foreach ($copy as $key => $value) { echo $key, ':', $value, '|'; }
unset($key, $value);
echo 'S|';
foreach ($source as $key => $value) { echo $key, ':', $value, '|'; }
unset($key, $value, $source, $copy);
echo 'E|';
