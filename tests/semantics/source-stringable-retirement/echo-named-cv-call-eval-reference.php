<?php
class ReturnedEchoNamed {
    public function __toString(): string { $e = new Exception('cast'); $trace = $e->getTrace(); echo 'REF-TEXT:', $trace[0]['line'], '|'; $GLOBALS['argumentEchoNamed'] = 'AFTER-CAST'; return 'REF-BYTES|'; }
    public function __destruct() { $e = new Exception('result'); $trace = $e->getTrace(); echo 'REF-D:', $trace[0]['line'], '|'; }
}
class OperandEchoNamed {
    public function __toString(): string {
        echo 'CAST|';
        return "\n\n\necho\n    callEchoNamed\n    (\n        sent:\n            \$argumentEchoNamed\n    );\necho 'BODY|';\nreturn 97;";
    }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], ':eval|';
        function &callEchoNamed($prefix = 'P', &$sent = null) { echo 'PREFIX:', $prefix, '|SENT:', $sent, '|'; $sent = 'CHANGED'; echo 'MUTATED:', $sent, '|'; $result = new ReturnedEchoNamed(); return $result; }
        $GLOBALS['argumentEchoNamed'] = 'LIVE'; echo 'INSTALL|';
    }
}
$value = eval(new OperandEchoNamed()); echo 'V:', $value, '|A:', $argumentEchoNamed, '|END';
