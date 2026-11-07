<?php
class GC79ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
class GC79OldAuthor {
    public function __destruct() {
        global $name, $kept, $slot;
        $slot = new GC79ChildAuthor;
        $kept = [&$slot, 17];
        $name = $kept;
        echo 'O|';
    }
}
function gc79AvailableAuthor() {}
$kept = null;
$slot = null;
$name = new GC79OldAuthor;
echo 'B|';
$ok = is_callable('gc79AvailableAuthor', false, $name);
echo 'N|', (int) $ok, '|', $name, '|';
unset($slot);
$view = $kept;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
unset($kept[0]);
echo 'U|', (int) isset($kept[0]), '|', $view[1], '|';
unset($kept);
echo 'K|';
unset($view, $name);
echo 'V|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
