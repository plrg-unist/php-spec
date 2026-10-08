<?php
class Operand353 {
    public function __toString(): string { echo 'CAST|'; return "\n\necho\n    \$rows353[\n\n        \$key353\n    ];\necho 'BODY|';\nreturn 66;"; }
    public function __destruct() {
        $e = new Exception('retire'); $trace = $e->getTrace();
        echo 'D:', $trace[0]['line'], '|K:', $trace[1]['function'], ':', $trace[1]['line'], '|';
        $GLOBALS['rows353'] = ['live' => 'EVAL-LIVE']; $GLOBALS['key353'] = 'live'; echo 'WRITE|';
    }
}
$rows353 = ['before' => 'WRONG']; $key353 = 'before';
$value = eval(new Operand353);
echo 'V:', $value, '|K:', $key353, '|END';
