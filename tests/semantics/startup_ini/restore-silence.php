<?php
function startup_review_handler($level, $message) {
    echo '|H:', error_reporting(), ':', ini_get('error_reporting'), ':', get_include_path();
    ini_restore('error_reporting');
    set_include_path('handler-live');
    echo '|HR:', error_reporting(), ':', ini_get('error_reporting'), ':', get_include_path();
    return true;
}
class StartupReviewRestoreName {
    public function __toString(): string {
        echo '|C:', error_reporting(), ':', ini_get('error_reporting'), ':', get_include_path();
        ini_set('error_reporting', '1tail');
        set_include_path('callback-live');
        return 'include_path';
    }
}
echo 'A:', error_reporting(), ':', ini_get('error_reporting'), ':', get_include_path();
echo '|EQ:', error_reporting(error_reporting()), ':', ini_get('error_reporting');
set_error_handler('startup_review_handler');
error_reporting(8);
@trigger_error('startup-review', E_USER_WARNING);
echo '|B:', error_reporting(), ':', ini_get('error_reporting'), ':', get_include_path();
restore_error_handler();
@ini_restore(new StartupReviewRestoreName());
echo '|D:', error_reporting(), ':', ini_get('error_reporting'), ':', get_include_path();
ini_restore('error_reporting');
echo '|E:', error_reporting(), ':', ini_get('error_reporting'), ':', get_include_path();
