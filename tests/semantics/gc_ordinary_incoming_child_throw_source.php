<?php
class GcOrdinaryIncomingHolder34 { public $child = null; }
class GcOrdinaryIncomingThrow34 {
    public function __destruct() { echo 'FIRST|'; throw new Exception('child'); }
}
class GcOrdinaryIncomingLater34 {
    public function __destruct() { echo 'LATER|'; }
}
$target = new stdClass;
$key = WeakReference::create($target);
$first = new WeakMap;
$second = new WeakMap;
$throwing = new GcOrdinaryIncomingHolder34;
$later = new GcOrdinaryIncomingHolder34;
$second[$key] = $throwing;
$first[$key] = $later;
$throwing->child = new GcOrdinaryIncomingThrow34;
$later->child = new GcOrdinaryIncomingLater34;
unset($throwing, $later);
echo 'B|';
try { unset($key); echo 'AFTER|'; }
catch (Throwable $error) { echo 'C|', $error->getMessage(), '|'; }
echo 'A|';
