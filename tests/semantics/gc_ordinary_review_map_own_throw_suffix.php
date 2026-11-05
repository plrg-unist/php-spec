<?php
class GC34OwnThrow { public function __destruct() { echo 'OWN1|'; throw new Exception('own'); } }
class GC34OwnLater { public function __destruct() { echo 'OWN2|'; } }
class GC34IncomingLater { public function __destruct() { echo 'IN|'; } }
$map = new WeakMap; $a = new stdClass; $b = new stdClass; $outer = new WeakMap; $map[$a] = new GC34OwnThrow; $map[$b] = new GC34OwnLater; $outer[$map] = new GC34IncomingLater; echo 'B|'; try { unset($map); echo 'AFTER|'; } catch (Throwable $e) { echo 'C|',$e->getMessage(),'|'; } echo 'T|',count($outer),'|';
