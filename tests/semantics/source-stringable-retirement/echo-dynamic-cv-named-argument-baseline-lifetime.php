<?php
class InvokerDynamicNamed {
    public function __invoke($prefix = 'P', $sent = 'D') { echo 'CALL:', $prefix, ':', ($sent === null ? 'NULL' : 'WRONG'), '|'; return 'OK|'; }
    public function __destruct() { echo 'INVOKER-D|'; }
}
function wrongDynamicNamed($prefix = 'P', $sent = 'D') { echo 'WRONG|'; return 'WRONG|'; }
$calleeDynamicNamed = new InvokerDynamicNamed();
set_error_handler(function($no, $message, $file, $line) { echo 'W:', $message, ':', $line, '|'; $GLOBALS['calleeDynamicNamed'] = 'wrongDynamicNamed'; $GLOBALS['argumentDynamicNamed'] = 'HANDLER'; return true; });
echo (
    $calleeDynamicNamed
)
(

    sent:

    $argumentDynamicNamed
);
echo 'LIVE:', $argumentDynamicNamed, '|END';
