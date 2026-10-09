<?php
class SensitiveCtorLeaf26 {
    public function __construct(public string $label) {}
    public function __destruct() { echo $this->label, "|"; }
}
$leaf = new SensitiveCtorLeaf26("O");
$weak = \WeakReference::create($leaf);
$wrapper = new \SensitiveParameterValue($leaf);
$constructor = $wrapper->__construct(...);
unset($leaf, $wrapper);
echo $weak->get() === null ? "NO|" : "LO|";
$replacement = new SensitiveCtorLeaf26("R");
$replacementWeak = \WeakReference::create($replacement);
try { $constructor($replacement); }
catch (\Error $error) { echo "E|"; }
unset($replacement);
echo $replacementWeak->get() === null ? "NR|" : "LR|";
unset($constructor);
echo $weak->get() === null ? "NO|" : "LO|";
echo $replacementWeak->get() === null ? "NR|" : "LR|";
unset($error);
echo $replacementWeak->get() === null ? "NR|" : "LR|";
