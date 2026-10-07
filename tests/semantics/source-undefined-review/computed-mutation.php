<?php
class CvReviewValue {
    public function __toString() { echo 'wrong-conversion|'; return 'echo "wrong-body|";'; }
}
function cvReviewHandler($level, $message, $file, $line) {
    echo 'H:', $message, ':', $line, '|';
    $GLOBALS['reviewDirect'] = new CvReviewValue;
    $GLOBALS['reviewDynamic'] = 'echo "wrong-body|";';
    $GLOBALS["review\0nul"] = 'echo "wrong-body|";';
    return false;
}
function cvReviewName() { echo 'N|'; return 'reviewDynamic'; }
ini_set('error_reporting', '0');
set_error_handler('cvReviewHandler', E_WARNING);
$value = eval($reviewDirect);
echo $value === false ? 'direct-false|' : 'wrong-result|';
unset($reviewDynamic);
$value = eval(${cvReviewName()});
echo $value === false ? 'dynamic-false|' : 'wrong-result|';
unset(${'review' . "\0nul"});
$name = 'review' . "\0nul";
$value = eval(${$name});
echo $value === false ? 'nul-false|' : 'wrong-result|';
restore_error_handler();
echo 'END';
