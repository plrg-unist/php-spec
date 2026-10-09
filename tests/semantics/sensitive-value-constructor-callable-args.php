<?php
function sensitive_ctor_arg26($value) { echo "A", $value, "|"; return $value; }
$value = 7;
$alias =& $value;
$wrapper = new \SensitiveParameterValue($alias);
$method = "__CoNsTrUcT";
$constructor = $wrapper->$method(...);
$method = "missing";
$value = 17;
echo $wrapper->getValue(), "|", $alias, "|";
try { $constructor(); }
catch (\ArgumentCountError $error) { echo $error->getMessage(), "|"; }
try { $constructor(sensitive_ctor_arg26(23), sensitive_ctor_arg26(29)); }
catch (\ArgumentCountError $error) { echo $error->getMessage(), "|"; }
try { $constructor(value: sensitive_ctor_arg26(31)); }
catch (\Error $error) { echo $error->getMessage(), "|"; }
echo $wrapper->getValue();
