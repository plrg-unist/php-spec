<?php
class OwnedFileOperand {
    public function __toString(): string {
        global $operand;
        $operand = 17;
        ini_set("include_path", "/live-path");
        return "selected.php";
    }
}
$operand = new OwnedFileOperand();
include $operand;
