<?php
class CachedHeld110 { public int $value = 1; }
$source = new CachedHeld110();
$held =& $source->value;
foreach ($source as $value) {}
unset($value);
echo 'H:';
$copy = clone $source;
$copy->value = 7;
echo $source->value, '|', $copy->value, '|', $held, '|';
$held = 8;
echo $source->value, '|', $copy->value, '|';
unset($source->value);
try { $held = 'bad'; } catch (TypeError $caught) { echo 'T|'; }
echo $held, '|', $copy->value, '|';
unset($copy->value);
$held = 'free';
echo $held, '|';
unset($caught, $held, $source, $copy);
echo 'E|';
