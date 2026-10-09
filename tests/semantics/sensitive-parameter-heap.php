<?php
class SensitiveLeaf22 { public function __destruct() { echo "D|"; } }
function sensitiveHeap22(#[\SensitiveParameter] $secret) { return new \Error("E"); }
$secret = new SensitiveLeaf22;
$weak = \WeakReference::create($secret);
$error = sensitiveHeap22($secret);
unset($secret);
echo $weak->get() === null ? "N|" : "L|";
$trace = $error->getTrace();
$wrapper = $trace[0]["args"][0];
echo $wrapper->getValue() === $weak->get() ? "S|" : "F|";
unset($trace, $error);
echo $weak->get() === null ? "N|" : "L|";
unset($wrapper);
echo $weak->get() === null ? "N|" : "L|";
