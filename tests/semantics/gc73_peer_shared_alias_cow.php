<?php
function gc73TargetPeer() {}
class GC73ChildPeer {
    public function __destruct() { echo 'D|'; }
}
class GC73OldNamePeer {
    public function __destruct() {
        global $name, $kept, $watch, $slot;
        $slot = 17;
        $child = new GC73ChildPeer;
        $watch = WeakReference::create($child);
        $kept = [&$slot, 17, &$slot, $child];
        $name = $kept;
        unset($child);
        echo 'O|';
    }
}
$name = new GC73OldNamePeer;
$ok = is_callable('gc73TargetPeer', false, $name);
echo 'B|', $ok, '|', $name, '|', $slot, '|',
     (int) ($watch->get() !== null), '|';
$kept[0] = 23;
echo 'W|', $slot, '|', $kept[0], '|', $kept[2], '|',
     (int) ($watch->get() !== null), '|';
unset($kept, $name, $slot);
echo 'U|', (int) ($watch->get() !== null), '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', (int) ($watch->get() !== null), '|';
register_shutdown_function(function () {
    global $watch;
    echo 'S|', (int) ($watch->get() !== null), '|';
});
echo 'E|';
