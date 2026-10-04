<?php
class CastGuard261 { public int $value = 5; }
$guard = new CastGuard261;
$source = ['link' => &$guard->value, 7 => ['n' => 1]];
$object = (object)$source;
$copy = $source;
unset($source);
try { $object->link = 'blocked'; }
catch (TypeError $error) { echo 'T|'; }
$object->link = 6;
echo $guard->value, '|';
unset($guard);
$object->link = 'free';
echo $copy['link'], '|';
$inner = $object->{'7'};
$inner['n'] = 2;
echo $object->{'7'}['n'], ':', $inner['n'], ':', $copy[7]['n'], '|';
$survivor =& $object->link;
unset($object, $copy, $inner);
$survivor = 'after';
echo $survivor, '|END';
