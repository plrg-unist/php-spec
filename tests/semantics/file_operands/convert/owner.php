<?php
class RetainedOperand {
    public function __toString(): string {
        global $operand;
        $operand = 17;
        echo "OWNER:", eval('return __FILE__;'), "|";
        return "owned.php";
    }
}
$operand = new RetainedOperand();
echo "V:", include $operand, "|AFTER:", $operand, "|END";
