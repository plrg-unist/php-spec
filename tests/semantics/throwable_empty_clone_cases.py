"""Original independently frozen empty-cache clone dependency witness."""
CASES = {
    "empty-cached-clone-owners": br"""<?php
#[AllowDynamicProperties]
class Shared158 {}
#[AllowDynamicProperties]
class Callback158 {
    public function __clone(): void { echo 'G|'; }
}
function outer158($x): Exception { return new Exception('outer', 7); }
$original = new Shared158; foreach ($original as $ignored) {}
$copy = clone $original; $a = outer158($original); $b = outer158($copy);
echo 'B|', $a <=> $b, ':', (int)($original === $copy), '|';
$view = (array)$original; $snapshot = $view;
$original->data = 1; echo 'L|', $a <=> $b, ':', (int)(((array)$copy) === []), ':', (int)($view === []), '|';
$copy->data = 2; echo 'R|', $a <=> $b, ':', $original->data, ':', $copy->data, '|';
$view['keep'] = $original; $weak = WeakReference::create($original); $original = null; $a = null;
echo 'H|', (int)($weak->get() !== null), '|';
$view = []; echo 'D|', (int)($weak->get() === null), '|';
$callbackSource = new Callback158; foreach ($callbackSource as $ignored) {}
$callbackCopy = clone $callbackSource;
$e = outer158($callbackSource); $f = outer158($callbackCopy); echo 'Q|', $e <=> $f, ':', (int)($callbackSource === $callbackCopy), '|';
$cbView = (array)$callbackSource; $callbackCopy->data = 7;
echo 'V|', (int)($cbView === []), ':', (int)(((array)$callbackSource) === []), ':', $callbackCopy->data, '|';
""",
}
