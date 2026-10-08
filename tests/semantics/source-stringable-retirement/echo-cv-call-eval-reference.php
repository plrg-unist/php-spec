<?php
class Returned365 {
    public function __toString(): string { echo 'REF-TEXT|'; $GLOBALS['argument365'] = 'AFTER-CAST'; return 'REF-BYTES|'; }
    public function __destruct() { echo 'REF-D|'; }
}
class Operand365 {
    public function __toString(): string {
        echo 'CAST|';
        return "\n\n\necho\n    call365\n    (\n\n        \$argument365\n    );\necho 'BODY|';\nreturn 97;";
    }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':eval|';
        function &call365(&$value) { echo 'CALL:', $value, '|'; $value = 'CHANGED'; echo 'MUTATED:', $value, '|'; $result = new Returned365(); return $result; }
        $GLOBALS['argument365'] = 'LIVE'; echo 'INSTALL|';
    }
}
$value = eval(new Operand365()); echo 'V:', $value, '|A:', $argument365, '|END';
