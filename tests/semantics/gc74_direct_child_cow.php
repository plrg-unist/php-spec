<?php
function gc74TargetAuthor() {}
class GC74ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
class GC74OldNameAuthor {
    public function __destruct() {
        global $name, $kept;
        $kept = [new GC74ChildAuthor];
        $name = $kept;
        echo 'O|';
    }
}
$kept = null;
$name = new GC74OldNameAuthor;
echo 'B|';
$ok = is_callable('gc74TargetAuthor', false, $name);
echo 'N|', (int) $ok, '|', $name, '|';
$kept[0] = 23;
echo 'W|', $kept[0], '|';
unset($kept, $name);
echo 'U|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
