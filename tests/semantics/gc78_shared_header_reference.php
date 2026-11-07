<?php
class GC78ChildPeer {
    public function __destruct() { echo 'D|'; }
}
class GC78OldPeer {
    public function __destruct() {
        global $name, $kept;
        $kept = [17, new GC78ChildPeer];
        $name = $kept;
        echo 'O|';
    }
}
function gc78AvailablePeer() {}
$kept = null;
$name = new GC78OldPeer;
echo 'B|';
$ok = is_callable('gc78AvailablePeer', false, $name);
echo 'N|', (int) $ok, '|', $name, '|';
$view = $kept;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
$ref =& $kept[0];
$ref = 23;
echo 'W|', $view[0], '|', $kept[0], '|';
unset($ref, $kept);
echo 'K|';
unset($view, $name);
echo 'V|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
