<?php
class Operand361 {
    public function __toString(): string {
        echo 'CAST|';
        return "\n\n\necho\n    call361\n    (\n    );\necho 'BODY|';\nreturn 86;";
    }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':eval|';
        echo 'K:', $trace[1]['function'], ':', $trace[1]['line'], '|';
        function call361() { echo 'CALL|'; return $GLOBALS['late361']; }
        $GLOBALS['late361'] = 'EVAL-LIVE|'; echo 'INSTALL|';
    }
}
$value = eval(new Operand361()); echo 'V:', $value, '|END';
