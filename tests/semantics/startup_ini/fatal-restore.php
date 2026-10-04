<?php
function startup_fatal_restore_callback() {
    ini_restore('error_reporting');
    echo '|I:', error_reporting(), ':', ini_get('error_reporting');
}
echo 'A:', error_reporting(), ':', ini_get('error_reporting');
echo '|SET:', error_reporting(8);
@startup_fatal_restore_callback();
echo '|POST:', error_reporting(), ':', ini_get('error_reporting');
ini_restore('error_reporting');
echo '|NOOP:', error_reporting(), ':', ini_get('error_reporting');
