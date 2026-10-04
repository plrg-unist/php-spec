<?php
class InterpolationPropertyOwner { public int $value = 1; }
$owner = new InterpolationPropertyOwner;
$alias =& $owner->value;
$stage = 0;
set_error_handler(function ($level, $message, $file, $line) {
    global $owner, $alias, $stage, $missing;
    ++$stage;
    if ($stage === 1) {
        $missing = [$owner];
        $owner = null;
        echo 'U|';
    } else {
        $missing = null;
        $alias = 'free';
        echo 'A|';
    }
    return true;
});
echo "P{$missing}|";
echo $alias, '|END';
