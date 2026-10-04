<?php
class DisplayFailure extends Exception {
    public function __toString(): string {
        echo 'T[' . ini_get('display_errors') . ']|';
        ini_set('display_errors', 'stdout');
        trigger_error('render-note', E_USER_NOTICE);
        return 'Pinned';
    }
}
register_shutdown_function(function () {
    echo 'Q[' . ini_get('display_errors') . ']|';
    ini_set('display_errors', '0');
    trigger_error('shutdown-hidden', E_USER_NOTICE);
    ini_restore('display_errors');
    trigger_error('after-freeze', E_USER_NOTICE);
    echo 'END|';
});
echo 'BEGIN|';
trigger_error('before', E_USER_NOTICE);
throw new DisplayFailure('unused');
