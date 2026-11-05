<?php
class GC34IncomingThrow { public function __destruct() { echo 'M1|'; throw new Exception('first'); } }
class GC34IncomingLater { public function __destruct() { echo 'M2|'; } }
$t = new stdClass; $key = WeakReference::create($t); $m1 = new WeakMap; $m2 = new WeakMap; $m1[$key] = new GC34IncomingThrow; $m2[$key] = new GC34IncomingLater; echo 'B|'; try { unset($key); echo 'AFTER|'; } catch (Throwable $e) { echo 'C|',$e->getMessage(),'|'; } echo 'T|',count($m1),'|',count($m2),'|';
