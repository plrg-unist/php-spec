<?php
class ReturnedDynamicArgument {
    public function __toString(): string { echo 'TEXT|'; return 'BYTES|'; }
    public function __destruct() { echo 'RESULT-D|'; throw new Exception('result-stop'); }
}
function selectedDynamicArgument($value) { echo 'CALL:', $value, '|'; return new ReturnedDynamicArgument(); }
$calleeDynamicArgument = 'selectedDynamicArgument'; $argumentDynamic = 'LIVE';
try { echo ($calleeDynamicArgument)($argumentDynamic); } catch (Throwable $e) { echo 'CATCH:', $e->getMessage(), '|'; }
echo 'END';
