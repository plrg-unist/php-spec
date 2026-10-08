<?php
class WarningResult361 {
    public function __toString(): string { echo 'WARN-TEXT|'; return 'WARN-BYTES|'; }
    public function __destruct() { echo 'WARN-D|'; echo $missing361; echo 'WARN-END|'; }
}
class ThrowResult361 {
    public function __toString(): string { echo 'THROW-TEXT|'; return 'THROW-BYTES|'; }
    public function __destruct() { echo 'THROW-D|'; throw new Exception('result'); }
}
class Borrowed361 {
    public function __toString(): string { echo 'BORROW-TEXT|'; unset($GLOBALS['value361']); return 'BORROWED|'; }
    public function __destruct() { echo 'BORROW-D|'; }
}
function warning361() { echo 'WARN-CALL|'; return new WarningResult361(); }
function throwing361() { echo 'THROW-CALL|'; return new ThrowResult361(); }
set_error_handler(function ($severity, $message, $file, $line) { echo 'W:', $line, ':', $message, '|'; return true; });
echo warning361();
try { echo throwing361(); } catch (Exception $e) { echo 'CAUGHT:', $e->getMessage(), '|'; }
$value361 = new Borrowed361(); echo $value361; echo 'END';
