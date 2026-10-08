<?php
class Operand357 {
    public function __toString(): string { echo 'CAST|'; return '


echo
    $rows357[
        key357()
    ];
echo \'BODY|\';
return 76;
'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':eval|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], '|';
        unset($GLOBALS['rows357']); echo 'RETIRE|';
    }
}
function key357() { echo 'KEY|'; $GLOBALS['rows357'] = ['chosen' => 'EVAL-LIVE']; return 'chosen'; }
$value = eval(new Operand357()); echo 'V:', $value, '|END';
