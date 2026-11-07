<?php
class GC77ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
class GC77OldAuthor {
    public function __destruct() {
        global $name, $kept;
        echo 'O|';
        $slot = new GC77ChildAuthor;
        $kept = [&$slot, 17];
        unset($slot);
        $name = $kept;
    }
}
function gc77AvailableAuthor() {}
$kept = null;
$name = new GC77OldAuthor;
echo 'B|';
$result = is_callable('gc77AvailableAuthor', false, $name);
echo 'N|', $result, '|', $name, '|';
$kept[0] = 23;
echo 'W|', $kept[0], '|';
unset($kept, $name);
echo 'U|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
