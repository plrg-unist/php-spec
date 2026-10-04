<?php
class LateIncludeOperand {
    public function __toString(): string {
        $GLOBALS['operand'] = 'wrong.php';
        echo 'C[', self::class, ']|';
        echo 'E[', eval('return __FILE__;'), ']|';
        chdir(__DIR__ . '/second');
        ini_set('include_path', '.');
        ini_set('display_errors', 'stdout');
        trigger_error('operand-note', E_USER_NOTICE);
        return 'piece.php';
    }
}
ini_set('include_path', __DIR__ . '/first');
$initial = include_once 'piece.php';
echo 'I[', $initial, ']|';
$operand = new LateIncludeOperand;
$first = include_once $operand;
echo 'A[', $first, ']|';
$operand = new LateIncludeOperand;
$second = include_once $operand;
echo 'B[', $second, ']|END';
