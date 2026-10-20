<?php
#[AllowDynamicProperties]
class MixedHeld116 { public int $declared = 1; }
echo 'H:';
$source = new MixedHeld116();
$source->extra = 1;
$alias =& $source->extra;
foreach ($source as $key => $value) {}
unset($key, $value);
$copy = clone $source;
$copy->extra = 7;
echo $source->extra, '/', $copy->extra, '/', $alias, '|';
unset($source->extra);
$alias = 9;
echo $copy->extra, '/', $alias, '|';
unset($source);
unset($copy->extra);
$alias = 'free';
echo $alias, '|';
unset($copy, $alias);
echo 'E|';
