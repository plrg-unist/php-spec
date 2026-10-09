<?php
class DynamicPlain27 {}
#[\AllowDynamicProperties]
class DynamicAllowed27 {}
set_error_handler(function($level, $message) { echo "W|", $message, "|"; return true; });
$plain = new DynamicPlain27();
$plain->extra = 7;
$plain->extra = 9;
echo "P", $plain->extra, "|";
$allowed = new DynamicAllowed27();
$allowed->extra = 17;
$allowed->extra = 19;
echo "A", $allowed->extra, "|";
