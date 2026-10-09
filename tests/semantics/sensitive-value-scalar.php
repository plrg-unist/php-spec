<?php
$value = 7;
$alias =& $value;
$wrapper = new \SensitiveParameterValue($alias);
$value = 17;
echo $wrapper->getValue(), "|", $alias, "|";
try { $wrapper->__construct(23); }
catch (\Error $error) { echo $error->getMessage(), "|"; }
echo $wrapper->getValue();
