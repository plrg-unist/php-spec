<?php
#[AllowDynamicProperties]
class MixedScalar116 { public int $declared = 1; }
echo 'M:';
$source = new MixedScalar116();
$source->alpha = 7;
$source->beta = 9;
foreach ($source as $key => $value) { echo $key, ':', $value, '|'; }
unset($key, $value);
$copy = clone $source;
$copy->declared = 2;
$copy->alpha = 17;
$source->beta = 19;
echo 'C|';
foreach ($copy as $key => $value) { echo $key, ':', $value, '|'; }
echo 'S|';
foreach ($source as $key => $value) { echo $key, ':', $value, '|'; }
unset($copy->alpha);
$copy->gamma = 23;
echo 'c|';
foreach ($copy as $key => $value) { echo $key, ':', $value, '|'; }
echo 's|';
foreach ($source as $key => $value) { echo $key, ':', $value, '|'; }
unset($key, $value, $source, $copy);
echo 'E|';
