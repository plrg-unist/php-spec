<?php
class DirectSensitiveLeaf24 {
    public function __destruct() { echo "D|"; }
}
$leaf = new DirectSensitiveLeaf24();
$weak = \WeakReference::create($leaf);
$wrapper = new \SensitiveParameterValue($leaf);
unset($leaf);
echo $weak->get() === null ? "N|" : "L|";
$copy = $wrapper->getValue();
unset($wrapper);
echo $weak->get() === null ? "N|" : "L|";
unset($copy);
echo $weak->get() === null ? "N|" : "L|";
