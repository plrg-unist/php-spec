<?php
class MultilineOperand {
    public function __toString(): string { throw new Exception("multi"); }
}
try { include
    new MultilineOperand(); }
catch (Exception $e) { echo $e->getTraceAsString(), "|"; }
set_error_handler(function ($level, $message, $file, $line) { echo "LINE:", $line, "|"; return true; });
include
    "missing-multiline.php";
echo "END";
