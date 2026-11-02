<?php
$seed = 11;
$token = [];
$token[0] = 11;
$collector = static function () use ($seed, $token) { echo $seed, '|', $token[0]; };
$captures = (new ReflectionFunction($collector))->getStaticVariables();
echo implode('|', array_keys($captures)), '|';
$collector();
