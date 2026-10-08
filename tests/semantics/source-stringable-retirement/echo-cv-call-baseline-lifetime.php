<?php
class Returned365 {
    public function __toString(): string { echo 'TEXT|'; return 'BYTES|'; }
    public function __destruct() { echo 'RESULT-D|'; throw new Exception('result'); }
}
function call365($value) { echo 'CALL:', $value, '|'; return new Returned365(); }
$argument365 = 'BASE';
try { echo call365($argument365); } catch (Exception $e) { echo 'CAUGHT:', $e->getMessage(), '|'; } echo 'END';
