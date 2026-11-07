<?php
class GC79SharedChildPeer {
    public function __destruct() { echo 'D|'; }
}
class GC79SharedOldPeer {
    public function __destruct() {
        global $name, $kept, $slot;
        $slot = new GC79SharedChildPeer;
        $kept = [&$slot, 17, &$slot];
        $name = $kept;
        echo 'O|';
    }
}
function gc79AvailablePeer() {}
$kept = null;
$name = new GC79SharedOldPeer;
echo 'B|';
$ok = is_callable('gc79AvailablePeer', false, $name);
echo 'N|', (int) $ok, '|', $name, '|';
$view = $kept;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
unset($kept[0]);
echo 'C|', (int) isset($kept[0]), '|', (int) isset($view[0]), '|', $kept[1], '|';
unset($kept[2]);
echo 'R|', (int) isset($kept[2]), '|', (int) isset($view[2]), '|';
$slot = 23;
echo 'W|', $slot, '|', $view[0], '|', $view[2], '|';
unset($kept, $view, $slot, $name);
echo 'U|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
