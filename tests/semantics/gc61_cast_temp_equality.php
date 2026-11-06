<?php
class GC61Empty {}
class GC61Sentinel { public function __destruct() { echo 'D|'; } }
$sentinel61 = new GC61Sentinel;
$object61 = new GC61Empty;
echo 'B|';
echo (int) ((array) $object61 === []), '|';
(array) $object61;
$held61 = (array) $object61;
echo 'A|', (int) ($held61 === []), '|';
unset($held61, $object61);
echo 'Z|';
unset($sentinel61);
