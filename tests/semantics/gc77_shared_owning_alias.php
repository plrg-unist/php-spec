<?php
class GC77SharedChild {
    public function __destruct() {
        global $kept, $slot;
        echo 'D|', $kept[0], '|', $kept[2], '|', $slot, '|';
    }
}
class GC77SharedOldName {
    public function __destruct() {
        global $name, $kept, $slot;
        $slot = new GC77SharedChild;
        $kept = [&$slot, 17, &$slot];
        $name = $kept;
        echo 'O|';
    }
}
function gc77SharedTarget() {}
$name = new GC77SharedOldName;
echo 'B|';
$ok = is_callable('gc77SharedTarget', false, $name);
echo 'N|', (int) $ok, '|', $name, '|';
$kept[0] = 23;
echo 'W|', $slot, '|', $kept[0], '|', $kept[2], '|';
unset($kept, $name, $slot);
echo 'U|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
