<?php
echo 'A|';
trigger_error('first', E_USER_NOTICE);
echo 'OLD:' . ini_set('display_errors', 'stdout') . '|';
trigger_error('second', E_USER_WARNING);
ini_set('display_errors', '0');
trigger_error('hidden', E_USER_NOTICE);
class DisplayOption {
    public function __toString(): string {
        echo 'OPT[' . ini_get('display_errors') . ']|';
        ini_set('display_errors', 'stderr');
        trigger_error('converter', E_USER_NOTICE);
        return 'display_errors';
    }
}
echo 'LATE:' . ini_set(new DisplayOption, 'stdout') . '|';
trigger_error('third', E_USER_NOTICE);
set_error_handler(function ($level, $message) {
    echo 'H[' . ini_get('display_errors') . ']|';
    ini_set('display_errors', 'stdout');
    return false;
});
ini_set('display_errors', 'stderr');
trigger_error('fallback', E_USER_NOTICE);
restore_error_handler();
ini_restore('display_errors');
echo 'RESTORED[' . ini_get('display_errors') . ']|';
trigger_error('restored', E_USER_NOTICE);
ini_set('display_errors', "stderr\0tail");
echo 'RAW[' . ini_get('display_errors') . ']|';
trigger_error('nul-hidden', E_USER_NOTICE);
echo 'Z|';
