<?php
class GC50Value { public $number = 1.25; public $child = null; }
class GC50Child { public function __destruct() { echo 'C|'; } }
$map = new WeakMap;
$key = new stdClass;
$moreKey = new stdClass;
$objectKey = new stdClass;
$value = new GC50Value;
$value->child = new GC50Child;
echo 'B|';
$map[$key] = -0.0;
$copy = $map[$key];
echo 'Z|', (int) isset($map[$key]), '|', (int) empty($map[$key]), '|', $copy, '|';
$written = $map[$key] = NAN;
$again = $map[$key] = $written;
echo 'N|', (int) ($again !== $again), '|',
     (int) isset($map[$key]), '|', (int) empty($map[$key]), '|';
$map[$moreKey] = INF;
echo 'I|', (int) ($map[$moreKey] === INF), '|',
     (int) isset($map[$moreKey]), '|', (int) empty($map[$moreKey]), '|',
     (int) (($map[$moreKey] ?? 0) === INF), '|';
$map[$objectKey] = $value;
unset($value);
unset($map[$key]);
echo 'U|', (int) !isset($map[$key]), '|', (int) empty($map[$key]), '|';
unset($map);
echo 'A|';
