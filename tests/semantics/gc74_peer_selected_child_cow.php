<?php
function gc74AvailablePeer() {}
class GC74TargetPeer {
    public function __destruct() { echo 'T|'; }
}
class GC74SiblingPeer {
    public function __destruct() { echo 'L|'; }
}
class GC74OldNamePeer {
    public function __destruct() {
        global $name, $kept, $quiet;
        $quiet = 17;
        $kept = [new GC74TargetPeer, new GC74SiblingPeer, &$quiet];
        $name = $kept;
        echo 'O|';
    }
}
$name = new GC74OldNamePeer;
$ok = is_callable('gc74AvailablePeer', false, $name);
echo 'B|', $ok, '|', $name, '|';
$kept[0] = 23;
echo 'W|', $kept[0], '|', $quiet, '|';
$kept[1] = 29;
echo 'R|', $kept[1], '|';
unset($kept, $name, $quiet);
echo 'U|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
