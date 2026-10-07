<?php
class BorrowedThrowEvalSource {
    public function __toString(): string {
        echo 'T|';
        unset($GLOBALS['borrowedThrow']);
        return 'function borrowedThrowCompiled(int $value = null) {} echo "BODY|"; return 77;';
    }
    public function __destruct() { echo 'D|'; throw new Exception('DTOR'); }
}
set_error_handler(function ($level, $message) { echo 'N:', $level, '|'; return true; }, E_DEPRECATED);
$borrowedThrow = new BorrowedThrowEvalSource;
try { eval($borrowedThrow); } catch (Throwable $error) { echo 'C:', $error->getMessage(), '|'; }
echo function_exists('borrowedThrowCompiled') ? 'defined|' : 'absent|';
restore_error_handler();
echo 'END';
