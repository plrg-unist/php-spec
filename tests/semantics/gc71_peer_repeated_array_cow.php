<?php
function gc71TargetPeer() {}
class GC71ChildPeer {
    public function __destruct() { echo 'D|'; }
}
class GC71OldNamePeer {
    public function __destruct() {
        global $name, $kept, $watch;
        $child = new GC71ChildPeer;
        $watch = WeakReference::create($child);
        $kept = [$child, 17, $child];
        $name = $kept;
        unset($child);
        echo 'O|';
    }
}
$name = new GC71OldNamePeer;
$ok = is_callable('gc71TargetPeer', false, $name);
echo 'B|', $ok, '|', $name, '|', $kept[1], '|',
     (int) ($watch->get() !== null), '|';
$kept[1] = 23;
echo 'W|', $kept[1], '|', (int) ($watch->get() !== null), '|';
$kept[0] = 29;
$kept[2] = 31;
echo 'R|', (int) ($watch->get() !== null), '|';
unset($kept, $name);
echo 'U|', (int) ($watch->get() !== null), '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', (int) ($watch->get() !== null), '|';
register_shutdown_function(function () {
    global $watch;
    echo 'S|', (int) ($watch->get() !== null), '|';
});
echo 'E|';
