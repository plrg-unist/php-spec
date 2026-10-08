<?php
class ReturnedEchoDynamic {
    public function __toString(): string { echo 'TEXT|'; return 'BYTES|'; }
    public function __destruct() { echo 'RESULT-D|'; throw new Exception('result-stop'); }
}
function selectedEchoDynamic() { echo 'SELECTED|'; return new ReturnedEchoDynamic(); }
$calleeEchoDynamic = 'selectedEchoDynamic';
try { echo ($calleeEchoDynamic)(); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), '|'; }
echo 'END';
