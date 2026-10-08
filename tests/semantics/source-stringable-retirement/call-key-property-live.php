<?php
class Operand357 {
    public function __toString(): string { echo 'CAST|'; return __DIR__ . '/call-key-property-live-child.php'; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':', ($trace[0]['file'] === __DIR__ . '/call-key-property-live-child.php' ? 'child' : 'main'), '|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], ':', (isset($trace[1]['args'][0]) && $trace[1]['args'][0] === __DIR__ . '/call-key-property-live-child.php' ? 'filename' : 'none'), '|';
        $GLOBALS['rows357'] = ['chosen' => new Before357()]; echo 'RETIRE|';
    }
}
class Before357 { public $value = 'BEFORE-BAD'; }
class After357 { public $value = 'PROPERTY-LIVE'; }
function key357() { echo 'KEY|'; $GLOBALS['rows357'] = ['chosen' => new After357()]; return 'chosen'; }
$value = include new Operand357(); echo 'V:', $value, '|END';
