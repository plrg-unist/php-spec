<?php
class FileOperand {
    public function __toString(): string { echo "C|"; return "shared.php"; }
}
echo "I:", include new FileOperand(), "|";
echo "R:", require new FileOperand(), "|";
echo "O:", include_once new FileOperand(), "|";
echo "Q:", require_once new FileOperand(), "|";
echo "S:", include "shared.php", "|END";
