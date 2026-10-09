<?php
class SensitiveGetterLeaf25 {
    public function __destruct() { echo "D|"; }
}
$leaf = new SensitiveGetterLeaf25();
$weak = \WeakReference::create($leaf);
$wrapper = new \SensitiveParameterValue($leaf);
$getter = $wrapper->getValue(...);
unset($leaf, $wrapper);
echo $weak->get() === null ? "N|" : "L|";
$copy = $getter();
unset($getter);
echo $weak->get() === null ? "N|" : "L|";
unset($copy);
echo $weak->get() === null ? "N|" : "L|";
