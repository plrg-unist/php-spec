<?php
class CachedSingleton110 { public int $value = 1; }
$source = new CachedSingleton110();
$alias =& $source->value;
unset($alias);
foreach ($source as $value) {}
unset($value);
echo 'U:';
$copy = clone $source;
$copy->value = 7;
echo $source->value, '|', $copy->value, '|';
try { $copy->value = 'bad'; } catch (TypeError $caught) { echo 'T|'; }
echo $source->value, '|';
unset($source->value);
$copy->value = 9;
echo $copy->value, '|';
unset($caught, $source, $copy);
echo 'E|';
