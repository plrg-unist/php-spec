<?php
class CachedScalar110 { public int $value = 1; public int $other = 10; }
$cold = new CachedScalar110();
$coldcopy = clone $cold;
$coldcopy->value = 2;
echo 'S:', $cold->value, '|', $coldcopy->value, '|';
unset($cold, $coldcopy);
$source = new CachedScalar110();
foreach ($source as $value) {}
unset($value);
echo 'M|';
$copy = clone $source;
$copy->value = 2;
$source->other = 30;
echo $source->value, '|', $copy->value, '|', $source->other, '|', $copy->other, '|';
unset($copy->value);
echo isset($source->value) ? 'L|' : 'bad|';
echo isset($copy->value) ? 'bad|' : 'Z|';
$copy->value = 4;
echo $source->value, '|', $copy->value, '|';
unset($source, $copy);
echo 'E|';
