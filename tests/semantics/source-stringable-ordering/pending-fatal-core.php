<?php
class PendingFatalCoreSource {
    public function __toString(): string { echo 'T|'; unset($GLOBALS['pendingFatalSource']); return 'break;'; }
    public function __destruct() { echo 'D|'; throw new Exception('DTOR'); }
}
$pendingFatalSource = new PendingFatalCoreSource();
try { eval($pendingFatalSource); } catch (Throwable $error) { echo 'CATCH|'; }
echo 'BODY|';
