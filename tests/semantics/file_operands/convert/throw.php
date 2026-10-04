<?php
class ThrowingOperand {
    public function __toString(): string {
        echo "THROW|";
        throw new Exception("operand");
    }
}
function include_operand() {
    try { include new ThrowingOperand(); }
    catch (Exception $e) { echo $e->getMessage(), "|", $e->getFile(), ":", $e->getLine(), "|", $e->getTraceAsString(), "|"; }
}
include_operand();
echo "END";
