<?php
class RejectIncludeOperand {
    public function __toString(): string {
        $GLOBALS['rejected'] = 'mutated';
        ini_set('include_path', '/changed-path');
        ini_set('display_errors', '0');
        trigger_error('hidden-converter', E_USER_NOTICE);
        echo 'X|';
        throw new Exception('converter-failed');
    }
}
$rejected = new RejectIncludeOperand;
try {
    require $rejected;
    echo 'BAD|';
} catch (Exception $e) {
    echo 'M[', $e->getMessage(), ']|L[', $e->getLine(), ']|T[', $e->getTraceAsString(), ']|';
}
echo 'PATH[', ini_get('include_path'), ']|MODE[', ini_get('display_errors'), ']|REF[', $rejected, ']|END';
